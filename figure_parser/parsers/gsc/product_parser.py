import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, List, Match, Optional, Pattern, Union
from urllib.parse import urlparse

import yaml
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from figure_parser.entities import OrderPeriod, PriceTag
from figure_parser.exceptions import ParserInitializationFailed
from figure_parser.parsers.base import AbstractBs4ProductParser
from figure_parser.parsers.utils import price_parse, scale_parse, size_parse

locale_file_path = Path(__file__).parent.joinpath('locale', 'gsc_parse.yml')

with open(locale_file_path, "r", encoding='utf-8') as stream:
    locale_dict = yaml.safe_load(stream)


def _extract_locale_from_url(url: str) -> str:
    matched = re.match(r"^\/(\w+)\/", urlparse(url).path)
    if not matched:
        raise ParserInitializationFailed("Extract locale from url failed.")
    return matched.group(1)


def _extract_detail_from_source(source: BeautifulSoup) -> Tag:
    detail = source.select_one(".itemDetail")
    if not detail:
        raise ParserInitializationFailed("Extract details from source failed.")
    return detail


class GSCProductParser(AbstractBs4ProductParser):
    locale: str
    detail: Tag

    def __init__(self, source: BeautifulSoup, locale: str, detail: Tag):
        self.locale = locale
        self.detail = detail
        super().__init__(source)

    @classmethod
    def create_parser(cls, url: str, source: BeautifulSoup):
        locale = _extract_locale_from_url(url)
        detail = _extract_detail_from_source(source)
        return cls(source=source, locale=locale, detail=detail)

    def _find_detail(self, name: str, text: str):
        target = self.detail.find(name=name, string=re.compile(text))
        return target

    def _find_detail_all(self, name: str, text: str) -> ResultSet:
        targets = self.detail.find_all(name=name, string=re.compile(text))
        return targets

    def _get_from_locale_dict(self, key: str) -> Any:
        return locale_dict[self.locale][key.lower()]

    def _parse_rerelease_dates(self) -> List[date]:
        resale_tag = self._get_from_locale_dict("resale")
        date_style = self._get_from_locale_dict("release_date_format")
        date_pattern: Pattern = self._get_from_locale_dict("release_date_pattern")
        resale_date_info_tag = r"{tag}".format(tag=resale_tag)
        resale_dates = self._find_detail("dt", resale_date_info_tag)
        assert resale_dates

        resale_ele = resale_dates.find_next("dd")
        assert resale_ele
        resale_dd = resale_ele.text.strip()
        resale_date_text = resale_dd or resale_dates.text.strip()

        dates = []
        found = re.finditer(date_pattern, resale_date_text)
        if found:
            for f in found:
                found_date = datetime.strptime(f[0], date_style).date()
                dates.append(found_date)
        return dates

    def parse_release_dates(self) -> List[date]:
        """
        If the product is re-saled,
        try to find past release-dates through `self._parse_resale_dates`.
        """
        date_pattern: Pattern = self._get_from_locale_dict("release_date_pattern")
        weird_date_pattern: Pattern = self._get_from_locale_dict("weird_date_pattern")

        date_ele = self.detail.find(
            "dd", {"itemprop": "releaseDate"}
        )
        assert date_ele
        date_text = date_ele.text.strip()

        if self.parse_rerelease():
            dates = self._parse_rerelease_dates()
            if dates:
                return dates

        date_list = []
        if re.match(date_pattern, date_text):
            for matched_date in re.finditer(date_pattern, date_text):
                year = int(matched_date.group('year'))
                month = int(matched_date.group('month'))
                the_datetime = datetime(year, month, 1).date()
                date_list.append(the_datetime)

        if re.match(weird_date_pattern, date_text):
            seasons = self._get_from_locale_dict("seasons")
            date_matched = re.match(weird_date_pattern, date_text)
            assert date_matched
            year = int(date_matched.group(1))
            for season, month in seasons.items():
                if season in date_text.lower():
                    the_datetime = datetime(year, month, 1).date()
                    date_list.append(the_datetime)

        return date_list

    def _parse_resale_prices(self) -> List[PriceTag]:
        price_slot: List[PriceTag] = []
        price_items = self.detail.find_all(
            name="dt", string=re.compile(r"販(\w|)価格"))

        for price_item in price_items:
            price_text: str = price_item.find_next("dd").text.strip()
            tax_feature = self._get_from_locale_dict("tax")
            tax_including = bool(re.search(f"{tax_feature}", price_text))
            price = price_parse(price_text)
            price_tag = PriceTag(price, tax_including)
            if price:
                price_slot.append(price_tag)

        return price_slot

    def parse_prices(self) -> List[PriceTag]:
        price_slot = []
        tag = self._get_from_locale_dict("price")
        last_price_target = self._find_detail("dt", f"^{tag}")

        if last_price_target:
            tax_feature = self._get_from_locale_dict("tax")
            last_price_ele = last_price_target.find_next("dd")
            assert last_price_ele
            last_price_text = last_price_ele.text.strip()
            tax_including = bool(re.search(f"{tax_feature}", last_price_text))
            last_price = price_parse(last_price_text)
            last_price_tag = PriceTag(last_price, tax_including)
        else:
            last_price_tag = PriceTag()

        if self.parse_rerelease():
            price_slot = self._parse_resale_prices()

            if not price_slot and last_price_tag:
                price_slot.append(last_price_tag)

            if price_slot and last_price_tag != price_slot[-1] and last_price_tag:
                price_slot.append(last_price_tag)

            return price_slot

        if last_price_tag.price is not None:
            if last_price_tag.price >= 0:
                price_slot.append(last_price_tag)

        return price_slot

    def parse_name(self) -> str:
        name_ele = self.source.select_one(
            "h1.title",
            {"itemprop": "price"}
        )
        assert name_ele
        return name_ele.text.strip()

    def parse_series(self) -> Optional[str]:
        tag = self._get_from_locale_dict("series")
        series_targets = self._find_detail("dt", tag)

        if not series_targets:
            return None
        series_ele = series_targets.find_next("dd")
        assert series_ele
        series = series_ele.text.strip()
        return series

    def parse_manufacturer(self) -> str:
        tag = self._get_from_locale_dict("manufacturer")
        manufacturer_targets = self._find_detail("dt", tag)

        if not manufacturer_targets:
            return self._get_from_locale_dict("default_manufacturer")
        manufacturer_ele = manufacturer_targets.find_next("dd")
        assert manufacturer_ele
        manufacturer = manufacturer_ele.text.strip()
        return manufacturer

    def parse_category(self) -> str:
        category_ele = self.detail.find("dd", {"itemprop": "category"})
        assert category_ele
        category = category_ele.text.strip()

        scale_category = self._get_from_locale_dict("scale_category")
        if re.search(scale_category, category):
            return scale_category

        return category

    def parse_sculptors(self) -> List[str]:
        tag = self._get_from_locale_dict("sculptor")
        sculptor_info = self._find_detail("dt", tag)

        if not sculptor_info:
            return []

        sculptor_ele = sculptor_info.find_next("dd")
        assert sculptor_ele
        sculptor = sculptor_ele.text.strip()
        sulptors = parse_people(sculptor)
        return sulptors

    def parse_scale(self) -> Union[int, None]:
        tag = self._get_from_locale_dict("spec")
        spec_target = self._find_detail("dt", tag)

        if not spec_target:
            return None

        description_ele = spec_target.find_next("dd")
        assert description_ele
        description = description_ele.text.strip()
        scale = scale_parse(description)
        return scale

    def parse_size(self) -> Union[int, None]:
        tag = self._get_from_locale_dict("spec")
        spec_target = self._find_detail("dt", tag)

        if not spec_target:
            return None

        description_ele = spec_target.find_next("dd")
        assert description_ele
        description = description_ele.text.strip()
        size = size_parse(description)
        return size

    def parse_releaser(self) -> Optional[str]:
        tag = self._get_from_locale_dict("releaser")
        detail_dd = self._find_detail("dt", tag)

        if not detail_dd:
            return self.parse_manufacturer()

        releaser_ele = detail_dd.find_next("dd")
        assert releaser_ele
        releaser = releaser_ele.text.strip()
        return releaser

    def parse_distributer(self) -> Optional[str]:
        tag = self._get_from_locale_dict("distributer")
        detail_dd = self._find_detail("dt", tag)

        if not detail_dd:
            return self.parse_manufacturer()

        distributer_ele = detail_dd.find_next("dd")
        assert distributer_ele
        distributer = distributer_ele.text.strip()
        return distributer

    def parse_copyright(self) -> Optional[str]:
        _copyright = self.detail.select_one(".itemCopy")

        if not _copyright:
            return None

        the_copyright = _copyright.text.strip()
        # FIXME: This is monkey patch.
        the_copyright = the_copyright.replace("\n\n", "\n")
        the_copyright = the_copyright.replace("\r", "")
        the_copyright = the_copyright.replace(u"\u3000", "\n")

        return the_copyright

    def parse_rerelease(self) -> bool:
        tag = self._get_from_locale_dict("resale")
        resale = self._find_detail("dt", tag)
        return bool(resale)

    def parse_order_period(self) -> OrderPeriod:
        period = self.detail.select_one(".onlinedates")

        if not period:
            return OrderPeriod(start=None, end=None)

        period_text = period.text.strip()
        order_period_pattern = self._get_from_locale_dict("order_period_pattern")
        period_list = [
            x for x in re.finditer(
                order_period_pattern, period_text
            )
        ]

        start = make_datetime(period_list[0], self.locale)
        end = None
        if len(period_list) == 2:
            end = make_datetime(period_list[1], self.locale)

        if not end or not start:
            return OrderPeriod(start=None, end=None)

        return OrderPeriod(start=start, end=end)

    def parse_adult(self) -> bool:
        rq_pattern = self._get_from_locale_dict("adult")
        keyword = re.compile(rq_pattern)
        info = self.source.select_one(".itemInfo")
        assert info
        detaill_adult = info.find(string=keyword)

        return bool(detaill_adult)

    def parse_paintworks(self) -> List[str]:
        tag: str = self._get_from_locale_dict("paintwork")
        paintwork_title = self._find_detail("dt", tag)

        if not paintwork_title:
            return []

        paintwork_ele = paintwork_title.find_next("dd")
        assert paintwork_ele
        paintwork = paintwork_ele.text.strip()
        paintworks = parse_people(paintwork)
        return paintworks

    def parse_images(self) -> List[str]:
        images_items = self.source.select(".itemImg")
        images = [f'https://{item["src"][2:]}' for item in images_items]
        return images

    def parse_JAN(self) -> Optional[str]:
        return None


def make_datetime(period: Match[str], locale: str) -> datetime:
    year = period.group('year')
    month = period.group('month')
    day = period.group('day')
    hour = period.group('hour')
    minute = period.group('minute')

    if locale == 'en':
        month = datetime.strptime(month, '%B').month

    return datetime(
        int(year),
        int(month),
        int(day),
        int(hour),
        int(minute)
    )


def parse_people(people_text: str) -> List[str]:
    people = []
    if re.search(r'・{2,}', people_text):
        people_text = people_text.replace("・", ".")
    people_group = re.split(r'・|、|/|\u3000', people_text)

    for p in people_group:
        p = PeopleParser.remove_cooperation(p)
        p = PeopleParser.extract_from_part_colon_worker_pattern(p)
        p = p.strip()
        people.append(p)

    return people


class PeopleParser:
    @staticmethod
    def remove_cooperation(people: str) -> str:
        """Basically I want to parse cooperation, but GSC data is too dirty."""
        return re.sub(r"\s?[\(（]?.[原型形製制作]?協力.+", " ", people, 1)

    @staticmethod
    def extract_from_part_colon_worker_pattern(people: str) -> str:
        no_brackets = re.search(r"^[\(（](.+?)[\)）]$", people)
        if no_brackets:
            people = no_brackets.group(1)
        expected_pattern = re.search(r"(?<=[:|：])(.+)", people)
        if expected_pattern:
            people = expected_pattern.group(1)
            return expected_pattern.group(1)
        return people

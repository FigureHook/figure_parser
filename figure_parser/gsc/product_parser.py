import re
from datetime import date, datetime
from pathlib import Path
from typing import (Any, AnyStr, ClassVar, Dict, List, Match, Optional,
                    Pattern, Union)
from urllib.parse import urlparse

import yaml
from bs4 import BeautifulSoup
from bs4.element import NavigableString, ResultSet, Tag

from ..abcs import ProductParser
from ..constants import BrandHost
from ..extension_class import OrderPeriod, Price
from ..utils import price_parse, scale_parse, size_parse

Bs4Element = Union[Tag, NavigableString, None]

locale_file_path = Path(__file__).parent.joinpath('locale', 'gsc_parse.yml')

with open(locale_file_path, "r", encoding='utf-8') as stream:
    locale_dict = yaml.safe_load(stream)


class GSCProductParser(ProductParser):
    __allow_domain__ = BrandHost.GSC

    locale: str
    rerelease: bool
    detail: Union[Tag, Any]
    cookies: ClassVar[Dict[str, str]] = {
        "age_verification_ok": "true"
    }

    def __init__(self, url: str, page: Optional[BeautifulSoup] = None):

        super().__init__(url, page)

        if page:
            self.locale = page.select_one("html")["lang"]
        else:
            parsed_url = urlparse(url)
            self.locale = re.match(r"^\/(\w+)\/", parsed_url.path).group(1)

        self.detail = self._parse_detail()
        self.rerelease = self._parse_rerelease()

    def _get_from_locale(self, key: str) -> Any:
        return locale_dict[self.locale][key.lower()]

    def _find_detail(self, name: str, text: AnyStr) -> Bs4Element:
        target: Bs4Element = self.detail.find(name=name, text=re.compile(text))
        return target

    def _find_detail_all(self, name: str, text: AnyStr) -> ResultSet:
        targets = self.detail.find_all(name=name, text=re.compile(text))
        return targets

    def _parse_detail(self) -> Any:
        detail: Union[Tag, None] = self.page.select_one(".itemDetail")
        return detail

    def _parse_rerelease_dates(self) -> List[date]:
        resale_tag = self._get_from_locale("resale")
        date_style = self._get_from_locale("release_date_format")
        date_pattern: Pattern = self._get_from_locale("release_date_pattern")
        resale_date_info_tag = r"{tag}".format(tag=resale_tag)
        resale_dates = self._find_detail("dt", resale_date_info_tag)

        resale_dd: str = resale_dates.find_next("dd").text.strip()
        resale_date_text: str = resale_dd or resale_dates.text.strip()

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
        date_pattern: Pattern = self._get_from_locale("release_date_pattern")
        weird_date_pattern: Pattern = self._get_from_locale("weird_date_pattern")

        date_text: str = self.detail.find(
            "dd", {"itemprop": "releaseDate"}
        ).text.strip()

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
            seasons = self._get_from_locale("seasons")
            year = int(re.match(weird_date_pattern, date_text).group(1))
            for season, month in seasons.items():
                if season in date_text.lower():
                    the_datetime = datetime(year, month, 1).date()
                    date_list.append(the_datetime)

        return date_list

    def _parse_resale_prices(self) -> List[Price]:
        price_slot = []
        price_items = self.detail.find_all(
            name="dt", text=re.compile(r"販(\w|)価格"))

        for price_item in price_items:
            price_text: str = price_item.find_next("dd").text.strip()
            tax_feature = self._get_from_locale("tax")
            tax_including = bool(re.search(f"{tax_feature}", price_text))
            price = price_parse(price_text)
            price = Price(price, tax_including)
            if price:
                price_slot.append(price)

        return price_slot

    def parse_prices(self) -> List[Price]:
        price_slot = []
        tag = self._get_from_locale("price")
        last_price_target = self._find_detail("dt", f"^{tag}")

        if last_price_target:
            tax_feature = self._get_from_locale("tax")
            last_price_text = last_price_target.find_next("dd").text.strip()
            tax_including = bool(re.search(f"{tax_feature}", last_price_text))
            last_price = price_parse(last_price_text)
            last_price = Price(last_price, tax_including)
        else:
            last_price = None

        if self.rerelease:
            price_slot = self._parse_resale_prices()

            if not price_slot and last_price:
                price_slot.append(last_price)

            if price_slot and last_price != price_slot[-1] and last_price:
                price_slot.append(last_price)

            return price_slot

        if last_price is not None and last_price >= 0:
            price_slot.append(last_price)

        return price_slot

    def parse_name(self) -> str:
        name: str = self.page.select_one(
            "h1.title",
            {"itemprop": "price"}
        ).text.strip()

        return name

    def parse_series(self) -> Union[str, None]:
        tag = self._get_from_locale("series")
        series_targets = self._find_detail("dt", tag)

        if not series_targets:
            return None

        series: str = series_targets.find_next("dd").text.strip()
        return series

    def parse_manufacturer(self) -> str:
        tag = self._get_from_locale("manufacturer")
        manufacturer_targets = self._find_detail("dt", tag)

        if not manufacturer_targets:
            return self._get_from_locale("default_manufacturer")

        manufacturer: str = manufacturer_targets.find_next("dd").text.strip()
        return manufacturer

    def parse_category(self) -> str:
        category: str = self.detail.find(
            "dd", {"itemprop": "category"}).text.strip()

        scale_category = self._get_from_locale("scale_category")
        if re.search(scale_category, category):
            return scale_category

        return category

    def parse_sculptors(self) -> List[str]:
        tag = self._get_from_locale("sculptor")
        sculptor_info = self._find_detail("dt", tag)

        if not sculptor_info:
            return []

        sculptor: str = sculptor_info.find_next("dd").text.strip()
        sulptors = parse_people(sculptor)
        return sulptors

    def parse_scale(self) -> Union[int, None]:
        tag = self._get_from_locale("spec")
        spec_target = self._find_detail("dt", tag)

        if not spec_target:
            return None

        description: str = spec_target.find_next("dd").text.strip()
        scale = scale_parse(description)
        return scale

    def parse_size(self) -> Union[int, None]:
        tag = self._get_from_locale("spec")
        spec_target = self._find_detail("dt", tag)

        if not spec_target:
            return None

        description: str = spec_target.find_next("dd").text.strip()
        size = size_parse(description)
        return size

    def parse_releaser(self) -> Union[str, None]:
        tag = self._get_from_locale("releaser")
        detail_dd = self._find_detail("dt", tag)

        if not detail_dd:
            return self.parse_manufacturer()

        releaser: str = detail_dd.find_next("dd").text.strip()
        return releaser

    def parse_distributer(self) -> Union[str, None]:
        tag = self._get_from_locale("distributer")
        detail_dd = self._find_detail("dt", tag)

        if not detail_dd:
            return self.parse_manufacturer()

        distributer: str = detail_dd.find_next("dd").text.strip()
        return distributer

    def parse_copyright(self) -> Union[str, None]:
        _copyright: Union[Tag, None] = self.detail.select_one(".itemCopy")

        if not _copyright:
            return None

        the_copyright: str = _copyright.text.strip()
        # FIXME: This is monkey patch.
        the_copyright = the_copyright.replace("\n\n", "\n")
        the_copyright = the_copyright.replace("\r", "")
        the_copyright = the_copyright.replace(u"\u3000", "\n")

        return the_copyright

    def _parse_rerelease(self) -> bool:
        tag = self._get_from_locale("resale")
        resale = self._find_detail("dt", tag)
        return bool(resale)

    def parse_rerelease(self) -> bool:
        return self.rerelease

    def parse_maker_id(self) -> str:
        return re.findall(r"\d+", self.url)[0]

    def parse_order_period(self) -> OrderPeriod:
        period: Union[Tag, None] = self.detail.select_one(".onlinedates")

        if not period:
            return super().parse_order_period()

        period_text: str = period.text.strip()
        order_period_pattern = self._get_from_locale("order_period_pattern")
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
            return OrderPeriod(None, None)

        return OrderPeriod(start, end)

    def parse_adult(self) -> bool:
        rq_pattern = self._get_from_locale("adult")
        keyword = re.compile(rq_pattern)
        info: Union[Tag, None] = self.page.select_one(".itemInfo")
        detaill_adult: Bs4Element = info.find(text=keyword)

        return bool(detaill_adult)

    def parse_paintworks(self) -> List[str]:
        tag: str = self._get_from_locale("paintwork")
        paintwork_title = self._find_detail("dt", tag)

        if not paintwork_title:
            return super().parse_paintworks()

        paintwork: str = paintwork_title.find_next("dd").text.strip()
        paintworks = parse_people(paintwork)
        return paintworks

    def parse_images(self) -> List[str]:
        images_items = self.page.select(".itemImg")
        images = [f'https://{item["src"][2:]}' for item in images_items]
        return images


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

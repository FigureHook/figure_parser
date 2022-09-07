import re
from datetime import date, datetime
from functools import cache
from typing import List, Mapping, Optional, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from figure_parser.entities import OrderPeriod
from figure_parser.exceptions import ParserInitializationFailed
from figure_parser.parsers.base import AbstractBs4ProductParser
from figure_parser.parsers.utils import price_parse, scale_parse, size_parse
from pydantic import BaseModel


class LegacyProductInfo(BaseModel):
    title_text: str
    info_text: str


def parse_legacy_info(source: BeautifulSoup) -> str:
    if source.select_one("#contents_right > .hidden"):
        info_text_ele = source.select_one("#contents_right > .hidden > p:nth-last-child(1)")
        if info_text_ele:
            info_text = info_text_ele.text.strip().replace("\n", "").replace("\t", "")
            return info_text
    else:
        info_text_ele = source.select_one("#contents_right > img:nth-of-type(3)")
        if info_text_ele:
            info_text = info_text_ele.get('alt')
            if type(info_text) is str:
                return info_text

    raise ParserInitializationFailed


def parse_legacy_title(source: BeautifulSoup) -> str:
    title = source.select_one("title")
    if title:
        title_text = title.text.strip()
        if title_text != "AMAKUNI":
            sub_pattern = r"\s?\|.+$"
            return re.sub(sub_pattern, "", title_text)

    hidden_title = source.select_one("#contents_right > .hidden > h3")
    if hidden_title:
        return hidden_title.text.strip()

    midashi_image_alt = source.select_one("#item_midashi > img")
    if midashi_image_alt:
        the_alt = midashi_image_alt.get('alt')
        if type(the_alt) is str:
            return the_alt

    raise ParserInitializationFailed


legacy_series_mapping: Mapping[str, str] = {
    "魔王黙示録": "七つの大罪 魔王黙示録",
    "クイーンズブレイド リベリオン": "クイーンズブレイド リベリオン",
    "『七つの大罪』編特別付録": "七つの大罪",
    "朧村正": "朧村正"
}


legacy_title_is_lack_of_series: Mapping[str, str] = {
    "三世村正　オアシスVer.": "装甲悪鬼村正",
    "魔王黙示録　傲慢ノ章 ～スイカ割りノ節": "七つの大罪",
    "魔王黙示録 憤怒の章 羞恥サタンクロースノ節": "七つの大罪",
    "レーシングミク2017Ver.": "初音ミク GTプロジェクト"
}


def append_the_lack_series(title: str) -> str:
    if title in legacy_title_is_lack_of_series:
        series = legacy_title_is_lack_of_series[title]
        title = title.replace(u"\u3000", " ")
        title = series + u"\u3000" + title
    return title


def legacy_get_series_by_keyword(keyword: str) -> Optional[str]:
    for key in legacy_series_mapping:
        if key in keyword:
            return legacy_series_mapping.get(key)
    return None


def remove_series(series: str, name: str) -> str:
    series_pattern = r"^.+(?<={})".format(series)
    name = re.sub(series_pattern, "", name)
    if series in name:
        name = remove_series(series, name.strip())
    return name


def parse_workers(workers_text: str) -> List[str]:
    pattern = r"[、|・]"
    return re.split(pattern=pattern, string=workers_text)


def _parse_order_period(text: str) -> OrderPeriod:
    pattern = r"●受注期間／(?P<start>(\d+)年(\d+)月(\d+)日)\uff5e(?P<end>((\d+)年)?(\d+)月(\d+)日)"
    date_format = "%Y年%m月%d日"
    matched = re.search(pattern, text)
    if matched:
        start_str = matched.group('start')
        end_str = matched.group('end')
        start_date = datetime.strptime(start_str, date_format)
        try:
            end_date = datetime.strptime(end_str, date_format)
        except ValueError:
            end_date = datetime.strptime(f"{start_date.year}年" + end_str, date_format)
        end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
        return OrderPeriod(start=start_date, end=end_date)
    return OrderPeriod()


def _parse_prices(text: str) -> List[Tuple[int, bool]]:
    prices = []
    price_pattern = r"●価格(.+?)税(抜|込)"
    matched = re.search(price_pattern, text)
    if matched:
        price = price_parse(matched.group(0))
        tax_including = "税込" in matched.group(0)
        prices.append((price, tax_including))
    else:
        prices.append((None, False))
    return prices


def _parse_release_dates(text: str) -> List[date]:
    date_pattern = r"●(発送予定|発売|発送)\uff0f(\d+)年(\d+)月"
    date_matched = re.search(date_pattern, text)
    assert date_matched
    release_date = date(int(date_matched.group(2)), int(date_matched.group(3)), 1)
    return [release_date]


class AmakuniLegacyProductParser(AbstractBs4ProductParser):
    _info: LegacyProductInfo
    _name: Optional[str]
    _series: Optional[str]

    def __init__(self, url: str, source: BeautifulSoup, info: LegacyProductInfo):
        self._source_url = url
        self._info = info
        self._name = None
        self._series = None
        super().__init__(source)

    @classmethod
    def create_parser(cls, url: str, source: BeautifulSoup):
        title_text = parse_legacy_title(source)
        title_text = append_the_lack_series(title_text)
        info_text = parse_legacy_info(source)
        product_info = LegacyProductInfo(
            title_text=title_text,
            info_text=info_text
        )
        return cls(url=url, source=source, info=product_info)

    def parse_name(self) -> str:
        name = self._info.title_text
        # pattern = r"(【|\u3000).+"
        # matched = re.search(pattern, self._info.title_text)
        # name_candidate = self._info.title_text.split(u"\u3000")

        # if matched:
        #     name = matched.group(0).strip()
        # elif len(name_candidate) > 1:
        #     name = " ".join(name_candidate[1:])
        # else:
        #     name = name_candidate[0]

        series = self.parse_series()
        if series:
            name = name.replace(u"\u3000", " ")
            name = remove_series(series, name)
        return name.strip()

    def parse_adult(self) -> bool:
        return False

    def parse_manufacturer(self) -> str:
        return "AMAKUNI"

    def parse_category(self) -> str:
        return "フィギュア"

    def parse_prices(self) -> List[Tuple[int, bool]]:
        return _parse_prices(self._info.info_text)

    def parse_release_dates(self) -> List[date]:
        return _parse_release_dates(self._info.info_text)

    @cache
    def parse_series(self) -> Optional[str]:
        series = legacy_get_series_by_keyword(self._info.title_text)

        if not series:
            pattern = r"^(.+?)(\u3000|【)"
            matched = re.search(pattern, self._info.title_text)
            if matched:
                series = matched.group(1)

        return series

    def parse_paintworks(self) -> List[str]:
        pattern = r"彩色見本製作／(.+?)(●|$)"
        matched = re.search(pattern, self._info.info_text)
        return parse_workers(matched.group(1).strip()) if matched else []

    def parse_sculptors(self) -> List[str]:
        pattern = r"●原型製作／(.+?)(●|$)"
        matched = re.search(pattern, self._info.info_text)
        return parse_workers(matched.group(1).strip()) if matched else []

    def parse_scale(self) -> Optional[int]:
        pattern = r"●フィギュア仕様／(.+?)(●|$)"
        matched = re.search(pattern, self._info.info_text)
        if matched:
            return scale_parse(matched.group(1))
        pattern = r"●仕様／(.+?)●"
        matched = re.search(pattern, self._info.info_text)
        if matched:
            return scale_parse(matched.group(1))
        return None

    def parse_size(self) -> Optional[int]:
        pattern = r"●フィギュア仕様／(.+?)●"
        matched = re.search(pattern, self._info.info_text)
        if matched:
            return size_parse(matched.group(1))
        pattern = r"●仕様／(.+?)●"
        matched = re.search(pattern, self._info.info_text)
        if matched:
            return size_parse(matched.group(1))
        return None

    def parse_copyright(self) -> Optional[str]:
        pattern = r"((©|\(C\)|\(c\)).+)"
        matched = re.search(pattern, self._info.info_text)
        if matched:
            return matched.group(0)
        return None

    def parse_releaser(self) -> Optional[str]:
        return "ホビージャパン"

    def parse_distributer(self) -> Optional[str]:
        return "ホビージャパン"

    def parse_rerelease(self) -> bool:
        return False

    def parse_images(self) -> List[str]:
        images: List[str] = []
        image_anchors = self.source.select(
            "#garrely_sum > a"
        ) or self.source.select("#contents_right .item_right a")
        if image_anchors:
            for anchor in image_anchors:
                image_src = anchor.get('href')
                if type(image_src) is str:
                    images.append(urljoin(self._source_url, image_src))
        return images

    def parse_thumbnail(self) -> Optional[str]:
        return None

    def parse_order_period(self) -> OrderPeriod:
        return _parse_order_period(self._info.info_text)

    def parse_JAN(self) -> Optional[str]:
        return None


def is_name_with_series(text: str) -> bool:
    splits = text.split(u"\u3000")
    return len(splits) > 1


class AmakuniFormalProductParser(AbstractBs4ProductParser):
    _detail_text: str
    _source_url: str

    def __init__(self, url: str, source: BeautifulSoup, detail_text: str):
        self._detail_text = detail_text
        self._source_url = url
        super().__init__(source)

    @classmethod
    def create_parser(cls, url: str, source: BeautifulSoup):
        detail_ele = source.select_one(".product_details")
        if not detail_ele:
            raise ParserInitializationFailed
        detail_text = detail_ele.text.strip()
        return cls(url=url, source=source, detail_text=detail_text)

    def parse_name(self) -> str:
        name_ele = self.source.select_one(
            ".product_name > span:nth-last-child(1)"
        ) or self.source.select_one(".product_name")
        assert name_ele
        name = name_ele.text.strip()
        if is_name_with_series(name):
            return name.split(u"\u3000")[1]
        return name

    def parse_adult(self) -> bool:
        return False

    def parse_manufacturer(self) -> str:
        return "AMAKUNI"

    def parse_category(self) -> str:
        return "フィギュア"

    def parse_prices(self) -> List[Tuple[int, bool]]:
        return _parse_prices(self._detail_text)

    def parse_release_dates(self) -> List[date]:
        return _parse_release_dates(self._detail_text)

    def parse_series(self) -> Optional[str]:
        series_ele = self.source.select_one(
            ".product_name > span:nth-child(1)"
        ) or self.source.select_one(".sakuhin_mei")
        if series_ele:
            series = series_ele.text.strip()
            return series

        possible_series_ele = self.source.select_one(
            ".product_name > span:nth-last-child(1)"
        ) or self.source.select_one(".product_name")
        if possible_series_ele:
            if is_name_with_series(possible_series_ele.text.strip()):
                return possible_series_ele.text.strip().split(u"\u3000")[0]
        return None

    def parse_paintworks(self) -> List[str]:
        pattern = r"彩色見本(?:製作)?／(.+)"
        matched = re.search(pattern, self._detail_text)
        return parse_workers(matched.group(1).strip()) if matched else []

    def parse_sculptors(self) -> List[str]:
        pattern = r"●原型製作／(.+)"
        matched = re.search(pattern, self._detail_text)
        return parse_workers(matched.group(1).strip()) if matched else []

    def parse_scale(self) -> Optional[int]:
        pattern = r"●仕様／(.+)"
        matched = re.search(pattern, self._detail_text)
        if matched:
            return scale_parse(matched.group(1))
        return None

    def parse_size(self) -> Optional[int]:
        pattern = r"●仕様／(.+)"
        matched = re.search(pattern, self._detail_text)
        if matched:
            return size_parse(matched.group(1))
        return None

    def parse_copyright(self) -> Optional[str]:
        copyright_ele = self.source.select_one(".copyright")
        if copyright_ele:
            return copyright_ele.text.strip()
        return None

    def parse_releaser(self) -> Optional[str]:
        pattern = r"●発売元／(.+)"
        matched = re.search(pattern, self._detail_text)
        if matched:
            return matched.group(1)
        return "ホビージャパン"

    def parse_distributer(self) -> Optional[str]:
        pattern = r"●販売元／(.+)"
        matched = re.search(pattern, self._detail_text)
        if matched:
            return matched.group(1)
        return "ホビージャパン"

    def parse_rerelease(self) -> bool:
        return False

    def parse_images(self) -> List[str]:
        images: List[str] = []
        image_anchors = self.source.select("[rel='lightbox[01]']")
        for a in image_anchors:
            image_src = a.get("href")
            if type(image_src) is str:
                image_src = urljoin(self._source_url, image_src)
                images.append(image_src)
        return images

    def parse_thumbnail(self) -> Optional[str]: ...

    def parse_order_period(self) -> OrderPeriod:
        return _parse_order_period(self._detail_text)

    def parse_JAN(self) -> Optional[str]: ...


class AmakuniProductParser(AbstractBs4ProductParser):
    _parser: AbstractBs4ProductParser

    def __init__(self, source: BeautifulSoup, parser: AbstractBs4ProductParser) -> None:
        self._parser = parser
        super().__init__(source)

    @classmethod
    def create_parser(cls, url: str, source: BeautifulSoup):
        if source.select_one(".name_waku"):
            parser = AmakuniFormalProductParser.create_parser(url=url, source=source)
        else:
            parser = AmakuniLegacyProductParser.create_parser(url=url, source=source)
        return cls(source=source, parser=parser)

    def parse_name(self) -> str:
        return self._parser.parse_name()

    def parse_adult(self) -> bool:
        return self._parser.parse_adult()

    def parse_manufacturer(self) -> str:
        return self._parser.parse_manufacturer()

    def parse_category(self) -> str:
        return self._parser.parse_category()

    def parse_prices(self) -> List[Tuple[int, bool]]:
        return self._parser.parse_prices()

    def parse_release_dates(self) -> List[date]:
        return self._parser.parse_release_dates()

    def parse_series(self) -> Optional[str]:
        return self._parser.parse_series()

    def parse_paintworks(self) -> List[str]:
        return self._parser.parse_paintworks()

    def parse_sculptors(self) -> List[str]:
        return self._parser.parse_sculptors()

    def parse_scale(self) -> Optional[int]:
        return self._parser.parse_scale()

    def parse_size(self) -> Optional[int]:
        return self._parser.parse_size()

    def parse_copyright(self) -> Optional[str]:
        return self._parser.parse_copyright()

    def parse_releaser(self) -> Optional[str]:
        return self._parser.parse_releaser()

    def parse_distributer(self) -> Optional[str]:
        return self._parser.parse_distributer()

    def parse_rerelease(self) -> bool:
        return self._parser.parse_rerelease()

    def parse_images(self) -> List[str]:
        return self._parser.parse_images()

    def parse_thumbnail(self) -> Optional[str]:
        return self._parser.parse_thumbnail()

    def parse_order_period(self) -> OrderPeriod:
        return self._parser.parse_order_period()

    def parse_JAN(self) -> Optional[str]:
        return self._parser.parse_JAN()

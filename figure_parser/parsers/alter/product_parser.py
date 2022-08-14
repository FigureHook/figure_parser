import re
from datetime import date, datetime
from typing import Dict, List, Mapping, Optional, Tuple, Union
from urllib.parse import ParseResult, urlparse, urlunparse

from bs4 import BeautifulSoup, Tag
from figure_parser.core.entity import OrderPeriod
from figure_parser.parsers.base import AbstractBs4ProductParser

from ..utils import price_parse, scale_parse, size_parse


def _parse_detail(source: BeautifulSoup):
    detail = source.select_one("#contents")
    assert detail
    return detail


def _parse_spec(source: BeautifulSoup):
    tables = [*source.select("table")]
    heads = []
    values = []

    # FIXME: This is too magic...
    for table in tables:
        for th, td in zip(table.select("th"), table.select("td")):
            key = "".join(th.text.split())
            heads.append(key)
            value = td.text
            if key in ["原型", "彩色"]:
                value = [
                    content
                    for content in td.contents
                    if content.name != "br"  # type: ignore
                ]
            values.append(value)

    spec: Dict[str, str] = dict(zip(heads, values))
    return spec


class AlterProductParser(AbstractBs4ProductParser):
    spec: Mapping[str, str]
    detail: Tag
    parsed_url: ParseResult

    def __init__(self, source: BeautifulSoup, detail: Tag, spec: Mapping[str, str], parsed_url: ParseResult):
        self.detail = detail
        self.spec = spec
        self.parsed_url = parsed_url
        super().__init__(source)

    @classmethod
    def create_parser(cls, url: str, source: BeautifulSoup):
        detail = _parse_detail(source)
        spec = _parse_spec(source)
        parsed_url = urlparse(url)
        return cls(source=source, spec=spec, detail=detail, parsed_url=parsed_url)

    def parse_name(self) -> str:
        name_ele = self.source.select_one("#contents h1")
        assert name_ele
        name = name_ele.text.strip()
        return name

    def parse_category(self) -> str:
        default_category = "フィギュア"
        transform_list = ["コラボ", "アルタイル", default_category]
        category = self.source.select("#topicpath li > a")[1].text.strip()

        if category in transform_list:
            return default_category

        return category

    def parse_manufacturer(self) -> str:
        return "アルター"

    def parse_prices(self) -> List[Tuple[int, bool]]:
        price_list: List[Tuple[int, bool]] = []
        price_text = self.spec["価格"]
        is_weird_price_text = re.findall(r"税抜", price_text)
        tax_including = "税込" in price_text
        price_pattern = r"税抜\d\S+?円" if is_weird_price_text else r"\d\S+?円"
        price_text = re.findall(price_pattern, price_text)
        for p in price_text:
            price = price_parse(p)
            if price:
                price_list.append((price, tax_including))

        return price_list

    def parse_release_dates(self) -> List[date]:
        date_text = self.spec["発売月"]
        matched_date = re.findall(r"\d+年\d+月", date_text)
        date_list = [datetime.strptime(date, "%Y年%m月").date()
                     for date in matched_date]
        return date_list

    def parse_scale(self) -> Union[int, None]:
        scale = scale_parse(self.spec["サイズ"])
        return scale

    def parse_sculptors(self) -> List[str]:
        sculptor_text = self.spec["原型"]

        sculptors = []
        for s in sculptor_text:
            sculptor = parse_worker(s)
            if sculptor:
                if isinstance(sculptor, list):
                    sculptors.extend(sculptor)
                if isinstance(sculptor, str):
                    sculptors.append(sculptor)

        return sculptors

    def parse_series(self) -> Union[str, None]:
        series = self.spec["作品名"]
        return series

    def parse_size(self) -> Union[int, None]:
        size = size_parse(self.spec["サイズ"])
        return size

    def parse_paintworks(self) -> List[str]:
        paintwork_texts = self.spec["彩色"]
        paintworks: List[str] = []
        for p in paintwork_texts:
            paintwork = parse_worker(p)
            if isinstance(paintwork, list):
                paintworks.extend(paintwork)
            if paintwork and isinstance(paintwork, str):
                paintworks.append(paintwork)

        return paintworks

    def parse_releaser(self) -> Union[str, None]:
        pattern = r"：(\S.+)"

        the_other_releaser = self.detail.find(
            "span",
            text=re.compile("発売元")
        )

        if not the_other_releaser:
            return "アルター"

        assert the_other_releaser.parent
        releaser_text = the_other_releaser.parent.text
        matched_releaser = re.search(pattern, releaser_text)
        assert matched_releaser
        releaser = matched_releaser.group(1).strip()

        return releaser

    def parse_distributer(self) -> Union[str, None]:
        pattern = r"：(\S.+)"

        the_other_releaser = self.detail.find(
            "span",
            text=re.compile("販売元")
        )

        if not the_other_releaser:
            return None

        assert the_other_releaser.parent
        distributer_text = the_other_releaser.parent.text
        matched_distributer = re.search(pattern, distributer_text)
        assert matched_distributer
        distributer = matched_distributer.group(1).strip()
        return distributer

    def parse_rerelease(self) -> bool:
        is_resale = bool(self.source.find(class_='resale'))
        return is_resale

    def parse_images(self) -> List[str]:
        images_item = self.detail.select(".bxslider > li > img")
        images = []
        for img in images_item:
            image_source = img["src"]
            if not type(image_source) is str:
                image_source = image_source[0]

            assert type(image_source) is str
            url_components = (
                self.parsed_url.scheme,
                self.parsed_url.netloc,
                image_source,
                None, None, None)
            url = urlunparse(url_components)
            images.append(url)

        return images

    def parse_copyright(self) -> Union[str, None]:
        pattern = r"(©.*)※"
        copyright_ele = self.detail.select_one(".copyright")
        assert copyright_ele
        copyright_info = copyright_ele.text
        matched_copyright = re.search(
            pattern, copyright_info
        )
        assert matched_copyright
        copyright_ = matched_copyright.group(1).strip()

        return copyright_

    def parse_JAN(self) -> Optional[str]:
        return None

    def parse_adult(self) -> bool:
        return False

    def parse_order_period(self) -> OrderPeriod:
        return OrderPeriod()


def parse_worker(text) -> Union[List[str], str]:
    if text in ["―", "—"]:
        return ""

    plus_text = "＋"
    text = text.replace(" ", "")
    text = re.sub(r"／?原型協力：アルター", "", text)
    text = re.sub(r"【\S+?】", "", text)
    if "：" in text:
        text = re.search(r"(?<=：)\w+", text)
        assert text
        text = text[0]
    if plus_text in text:
        text = text.split(plus_text)

    return text

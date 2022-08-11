import re
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse, urlunparse

from bs4 import BeautifulSoup
from figure_parser.core.entity import OrderPeriod
from figure_parser.parsers.base import AbstractBs4ProductParser

from ..utils import price_parse, scale_parse, size_parse


def _parse_detail(source: BeautifulSoup):
    detail= source.select_one("#contents")
    return detail


def _parse_spec(source: BeautifulSoup):
    tables = [*source.select("table")]
    heads = []
    values = []

    for table in tables:
        for th, td in zip(table.select("th"), table.select("td")):
            key = "".join(th.text.split())
            heads.append(key)
            value = td.text
            if key in ["原型", "彩色"]:
                value = [
                    content
                    for content in td.contents
                    # if content.name != "br"
                ]
            values.append(value)

    spec: Dict[str, str] = dict(zip(heads, values))
    return spec


class AlterProductParser(AbstractBs4ProductParser):
    def __init__(self, detail, spec, parsed_url):
        self.detail = detail
        self.spec = spec
        self.parsed_url = parsed_url

    @classmethod
    def create_parser(cls, url: str, source: BeautifulSoup):
        detail = _parse_detail(source)
        spec = _parse_spec(source)
        parsed_url = urlparse(url)
        return cls(spec=spec, detail=detail, parsed_url=parsed_url)

    def parse_name(self, source: BeautifulSoup) -> str:
        name_ele = source.select_one("#contents h1")
        assert name_ele
        name = name_ele.text.strip()
        return name

    def parse_category(self, source: BeautifulSoup) -> str:
        default_category = "フィギュア"
        transform_list = ["コラボ", "アルタイル", default_category]
        category = source.select("#topicpath li > a")[1].text.strip()

        if category in transform_list:
            return default_category

        return category

    def parse_manufacturer(self, source: BeautifulSoup) -> str:
        return "アルター"

    def parse_prices(self, source: BeautifulSoup) -> List[Tuple[int, bool]]:
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

    def parse_release_dates(self, source: BeautifulSoup) -> List[date]:
        date_text = self.spec["発売月"]
        matched_date = re.findall(r"\d+年\d+月", date_text)
        date_list = [datetime.strptime(date, "%Y年%m月").date()
                     for date in matched_date]
        return date_list

    def parse_scale(self, source: BeautifulSoup) -> Union[int, None]:
        scale = scale_parse(self.spec["サイズ"])
        return scale

    def parse_sculptors(self, source: BeautifulSoup) -> List[str]:
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

    def parse_series(self, source: BeautifulSoup) -> Union[str, None]:
        series = self.spec["作品名"]
        return series

    def parse_size(self, source: BeautifulSoup) -> Union[int, None]:
        size = size_parse(self.spec["サイズ"])
        return size

    def parse_paintworks(self, source: BeautifulSoup) -> List[str]:
        paintwork_texts = self.spec["彩色"]
        paintworks: List[str] = []
        for p in paintwork_texts:
            paintwork = parse_worker(p)
            if isinstance(paintwork, list):
                paintworks.extend(paintwork)
            if paintwork and isinstance(paintwork, str):
                paintworks.append(paintwork)

        return paintworks

    def parse_releaser(self, source: BeautifulSoup) -> Union[str, None]:
        pattern = r"：(\S.+)"

        the_other_releaser = self.detail.find(
            "span",
            text=re.compile("発売元")
        )

        if not the_other_releaser:
            return "アルター"

        releaser_text = the_other_releaser.parent.text
        matched_releaser = re.search(pattern, releaser_text)
        assert matched_releaser
        releaser = matched_releaser.group(1).strip()

        return releaser

    def parse_distributer(self, source: BeautifulSoup) -> Union[str, None]:
        pattern = r"：(\S.+)"

        the_other_releaser = self.detail.find(
            "span",
            text=re.compile("販売元")
        )

        if not the_other_releaser:
            return None

        distributer_text = the_other_releaser.parent.text
        matched_distributer = re.search(pattern, distributer_text)
        assert matched_distributer
        distributer = matched_distributer.group(1).strip()
        return distributer

    def parse_rerelease(self, source: BeautifulSoup) -> bool:
        is_resale = bool(source.find(class_='resale'))
        return is_resale

    def parse_images(self, source: BeautifulSoup) -> List[str]:
        images_item = self.detail.select(".bxslider > li > img")
        images = []
        for img in images_item:
            url_components = (self.parsed_url.scheme, self.parsed_url.netloc,
                              img["src"], None, None, None)
            url = urlunparse(url_components)
            images.append(url)

        return images

    def parse_copyright(self, source: BeautifulSoup) -> Union[str, None]:
        pattern = r"(©.*)※"
        copyright_info = self.detail.select_one(".copyright").text
        matched_copyright = re.search(
            pattern, copyright_info
        )
        assert matched_copyright
        copyright_ = matched_copyright.group(1).strip()

        return copyright_

    def parse_JAN(self, source: BeautifulSoup) -> Optional[str]:
        return None

    def parse_adult(self, source: BeautifulSoup) -> bool:
        return False

    def parse_order_period(self, source: BeautifulSoup) -> OrderPeriod:
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

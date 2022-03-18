import re
from datetime import date, datetime
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse, urlunparse

from bs4 import BeautifulSoup
from bs4.element import Tag
from figure_parser.extension_class import Price

from ..abcs import ProductParser
from ..constants import BrandHost
from ..utils import price_parse, scale_parse, size_parse


class AlterProductParser(ProductParser):
    __allow_domain__ = BrandHost.ALTER

    def __init__(self, url: str, page: Optional[BeautifulSoup] = None):
        super().__init__(url, page)
        self.detail = self._parse_detail()
        self.spec = self._parse_spec()

    def _parse_detail(self):
        detail: Union[Tag, None] = self.page.select_one("#contents")
        return detail

    def _parse_spec(self):
        tables = [*self.page.select("table")]
        heads = []
        values = []

        for table in tables:
            for th, td in zip(table.select("th"), table.select("td")):
                key = "".join(th.text.split())
                heads.append(key)
                value = td.text
                if key in ["原型", "彩色"]:
                    value = [
                        content for content in td.contents if content.name != "br"]
                values.append(value)

        spec: Dict[str, str] = dict(zip(heads, values))
        return spec

    def parse_maker_id(self) -> str:
        return re.findall(r"\d+", self.url)[0]

    def parse_name(self) -> str:
        name = self.page.select_one("#contents h1").text.strip()
        return name

    def parse_category(self) -> str:
        default_category = "フィギュア"
        transform_list = ["コラボ", "アルタイル", default_category]
        category = self.page.select("#topicpath li > a")[1].text.strip()

        if category in transform_list:
            return default_category

        return category

    def parse_manufacturer(self) -> str:
        return "アルター"

    def parse_prices(self) -> List[int]:
        price_list: List[int] = []
        price_text = self.spec["価格"]
        is_weird_price_text = re.findall(r"税抜", price_text)
        tax_including = "税込" in price_text
        price_pattern = r"税抜\d\S+?円" if is_weird_price_text else r"\d\S+?円"
        price_text = re.findall(price_pattern, price_text)
        for p in price_text:
            price = price_parse(p)
            price = Price(price, tax_including)
            if price:
                price_list.append(price)

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

        releaser_text = the_other_releaser.parent.text
        releaser = re.search(pattern, releaser_text).group(1).strip()

        return releaser

    def parse_distributer(self) -> Union[str, None]:
        pattern = r"：(\S.+)"

        the_other_releaser = self.detail.find(
            "span",
            text=re.compile("販売元")
        )

        if not the_other_releaser:
            return None

        distributer_text = the_other_releaser.parent.text
        distributer = re.search(pattern, distributer_text).group(1).strip()
        return distributer

    def parse_rerelease(self) -> bool:
        is_resale = bool(self.page.find(class_='resale'))
        return is_resale

    def parse_images(self) -> List[str]:
        host = urlparse(self.url)
        images_item = self.detail.select(".bxslider > li > img")
        images = []
        for img in images_item:
            url_components = (host.scheme, host.netloc,
                              img["src"], None, None, None)
            url = urlunparse(url_components)
            images.append(url)

        return images

    def parse_copyright(self) -> Union[str, None]:
        pattern = r"(©.*)※"
        copyright_info = self.detail.select_one(".copyright").text
        copyright_ = re.search(
            pattern, copyright_info
        ).group(1).strip()

        return copyright_


def parse_worker(text) -> Union[List[str], str]:
    if text in ["―", "—"]:
        return ""

    plus_text = "＋"
    text = text.replace(" ", "")
    text = re.sub(r"／?原型協力：アルター", "", text)
    text = re.sub(r"【\S+?】", "", text)
    if "：" in text:
        text = re.search(r"(?<=：)\w+", text)[0]
    if plus_text in text:
        text = text.split(plus_text)

    return text

import re
from datetime import date, datetime
from typing import Dict, List, Optional, Union

from bs4 import BeautifulSoup

from ..abcs import ProductParser
from ..constants import BrandHost
from ..extension_class import OrderPeriod, Price
from ..utils import price_parse, scale_parse, size_parse


class NativeProductParser(ProductParser):
    __allow_domain__ = BrandHost.NATIVE

    def __init__(self, url: str, page: Optional[BeautifulSoup] = None):
        super().__init__(url, page=page)

        self._detail = parse_details(self.page)

    @property
    def detail(self):
        return self._detail

    def parse_name(self) -> str:
        name = self.page.select_one('article > header > h1').text.strip()
        return name

    def parse_adult(self) -> bool:
        return True

    def parse_manufacturer(self) -> str:
        logo_image = self.page.select_one('.entryitem_detail .logo > img')
        maker_name = logo_image['alt']
        return maker_name

    def parse_category(self) -> str:
        return "フィギュア"

    def parse_prices(self) -> List[Price]:
        prices = []
        price_text = self.detail.get('価格')
        if price_text:
            tax_including = "税込" in price_text
            price_text = price_text.split("\n")[0]
            price = price_parse(price_text)
            price = Price(price, tax_including)
            prices.append(price)

        return prices

    def parse_release_dates(self) -> List[date]:
        """FIXME: This would be problem in future.
        """
        release_date_text = self.detail.get('発売')
        pattern = r"(?P<year>\d+)[\/|年](?P<month>\d+)月?"
        release_dates = []
        if release_date_text:
            result = re.search(pattern, release_date_text)
            if result:
                year = result.groupdict().get('year', 0)
                month = result.groupdict().get('month', 0)
                release_date = datetime(int(year), int(month), 1).date()

                release_dates.append(release_date)

        return release_dates

    def parse_series(self) -> Union[str, None]:
        series = self.detail.get('作品名')
        return series

    def parse_paintworks(self) -> List[str]:
        paintworks_text = self.detail.get('彩色制作')
        if not paintworks_text:
            return []

        paintworks = paintworks_text.split("\n")
        return paintworks

    def parse_sculptors(self) -> List[str]:
        sculptors_text = self.detail.get('原型制作')
        if not sculptors_text:
            return []

        sculptors = []
        raw_sculptors = sculptors_text.split("\n")
        for raw_sculptor in raw_sculptors:
            pattern = r"\s?\(?.[原型形製制作]+協力[:：].+[\）\)]?"
            sculptor = re.sub(pattern, "", raw_sculptor)
            sculptor = sculptor.strip()
            if sculptor:
                sculptors.append(sculptor)

        return sculptors

    def parse_scale(self) -> Union[int, None]:
        spec_text = self.detail.get('サイズ')
        scale_text = spec_text.split("\n")[0]
        return scale_parse(scale_text)

    def parse_size(self) -> Union[int, None]:
        spec_text = self.detail.get('サイズ')
        if spec_text:
            return size_parse(spec_text)
        return None

    def parse_copyright(self) -> Union[str, None]:
        copyright_ele = self.page.select_one('.copyright')
        return copyright_ele.text.strip() if copyright_ele else None

    def parse_releaser(self) -> Union[str, None]:
        releaser = self.detail.get('発売元')
        return releaser

    def parse_distributer(self) -> Union[str, None]:
        distributer = self.detail.get('販売元')
        return distributer

    def parse_resale(self) -> bool:
        return False

    def parse_images(self) -> List[str]:
        slide_images = self.page.select('.swiper-slide > .img > img')

        images = []
        for image in slide_images:
            images.append(image['src'])

        return images

    def parse_thumbnail(self) -> Union[str, None]:
        slide_image = self.page.select_one('.swiper-slide > .img > img')

        thumbnail = re.sub(r"\d+(?=[.jpg])", "m", slide_image['src'])
        return thumbnail

    def parse_maker_id(self) -> Union[str, None]:
        return re.findall(r"\d+", self.url)[0]

    def parse_order_period(self) -> OrderPeriod:
        order_period_text = self.detail.get('予約受付期間')
        pattern = r"\d+年\d+月\d+日\d+時"
        if order_period_text:
            order_period_text = re.sub(r"\(\w\)", "", order_period_text)
            r = re.findall(pattern, order_period_text)
            if r:
                datetime_format = r"%Y年%m月%d日%H時"
                start_text, *remaining = r
                start = datetime.strptime(start_text, datetime_format)
                end = None
                if len(r) >= 2:
                    end_text, *_ = remaining
                    end = datetime.strptime(end_text, datetime_format)

                order_period = OrderPeriod(start, end)

                return order_period

        return super().parse_order_period()


def parse_details(page: BeautifulSoup) -> Dict[str, str]:
    details = {}

    dts = page.select('dt')
    dds = page.select('dd')

    assert len(dts) == len(dds)

    for dt, dd in zip(dts, dds):
        key = dt.text.strip()
        value = dd.text.strip()
        value = value.replace("\r", "")
        value = value.replace(u"\u3000", "\n")
        details.setdefault(key, value)

    return details

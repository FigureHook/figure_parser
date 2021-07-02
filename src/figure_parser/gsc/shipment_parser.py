import re
from datetime import date
from typing import Mapping

from bs4 import BeautifulSoup

from ..abcs import ShipmentParser
from ..utils import RelativeUrl


class GSCShipment(ShipmentParser):
    source_url = "https://www.goodsmile.info/ja/releaseinfo"

    def _parse_shipment(self, page: BeautifulSoup) -> dict[date, list[Mapping[str, str]]]:
        shipment_by_date = {}

        dates = _parse_release_dates(page)
        products = _parse_release_products(page)

        for d, ps in zip(dates, products):
            shipment_by_date.setdefault(d, ps)

        return shipment_by_date


def _parse_release_products(page):
    products_by_date = []
    ul_eles = page.select(".arrowlisting > ul")
    for ul in ul_eles:
        products = parse_products(ul)
        products_by_date.append(products)

    return products_by_date


def _parse_release_dates(page):
    release_group = page.select(".arrowlisting")

    dates = []

    for group in release_group:
        year, month = parse_year_and_month(group)

        release_dates = group.select("#syukkagreen")
        for release_date in release_dates:
            day = parse_day(release_date)

            dates.append(date(year, month, day))

    return dates


def parse_year_and_month(group):
    year, month = (
        int(x)
        for x in group.select_one("#largedate").text.split(".")
    )

    return year, month


def parse_day(day_ele):
    day_pattern = r"(?P<month>\d+)月(?P<day>\d+)日"

    day = re.match(day_pattern, day_ele.text.strip()).group('day')
    return int(day)


def parse_products(ul_ele):
    products = []

    for li in ul_ele.select("li"):
        anchor = li.select_one("a")
        if anchor:
            product = {
                "url": RelativeUrl.gsc(anchor["href"]),
                "jan": make_jan(li)
            }
            products.append(product)

    return products


def make_jan(li_ele):
    jan_text = li_ele.select_one("small")

    if not jan_text:
        return ""

    jan_pattern = r"JAN： (\d+)"
    return re.match(jan_pattern, jan_text.text.strip()).group(1)

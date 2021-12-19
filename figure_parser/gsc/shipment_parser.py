import re
from datetime import date
from typing import Callable, Dict, List, Mapping

from bs4 import BeautifulSoup

from ..abcs import ShipmentParser
from ..exceptions import UnreliableParserError
from ..utils import RelativeUrl


def is_critical(func: Callable):
    def wrap(*args, **kwargs):
        try:
            ret_val = func(*args, **kwargs)
        except AssertionError as err:
            raise UnreliableParserError(
                f"{func.__name__} part of {GSCShipment} can't be executed normally.\n"
                f"Please contact with maintainers."
                f"(reasons: {str(err)})"
                f"(params: {args}, {kwargs})"
            )

        return ret_val
    return wrap


class GSCShipment(ShipmentParser):
    source_url = "https://www.goodsmile.info/ja/releaseinfo"

    def _parse_shipment(self, page: BeautifulSoup) -> Dict[date, List[Mapping[str, str]]]:
        shipment_by_date = {}

        dates = parse_release_dates(page)
        products = parse_release_products(page)

        if len(dates) != len(products):
            raise UnreliableParserError(f"Can't align dates and products amount in {self.source_url}.")

        for d, ps in zip(dates, products):
            shipment_by_date.setdefault(d, ps)

        return shipment_by_date


def parse_release_products(page):
    products_by_date = []
    product_batches = page.select(".arrowlisting > ul")
    for batch in product_batches:
        products = parse_products(batch)
        products_by_date.append(products)

    return products_by_date


def parse_products(batch):
    products = []

    for product in batch.select("li"):
        product_link = product.select_one("a")
        jan_ele = fetch_jan_element(product)
        if product_link:
            product = {
                "url": RelativeUrl.gsc(product_link["href"]),
                "jan": parse_jan(jan_ele)
            }
            products.append(product)

    return products


@is_critical
def parse_release_dates(page):
    release_group = page.select(".arrowlisting")

    dates = []

    for group in release_group:
        year, month = parse_year_and_month(group)

        release_dates = group.select("#syukkagreen")
        for release_date in release_dates:
            day = parse_day(release_date)

            dates.append(date(year, month, day))

    return dates


def parse_year_and_month(day_month_ele):
    year, month = (
        int(x)
        for x in day_month_ele.select_one("#largedate").text.split(".")
    )

    assert all((year, month)), "Failed to parse the year and the month."

    return year, month


def parse_day(day_ele) -> int:
    day_pattern = r"(?P<month>\d+)月(?P<day>\d+)日"

    day_match = re.match(day_pattern, day_ele.text.strip())

    assert day_match, "Failed to parse the day."

    day = day_match.group('day')
    return int(day)


def parse_jan(jan_ele):
    if not jan_ele:
        return ""

    jan_pattern = r"JAN： (\d+)"
    jan_match = re.match(jan_pattern, jan_ele.text.strip())
    return jan_match.group(1) if jan_match else ""


def fetch_jan_element(product_li_ele):
    return product_li_ele.select_one("small")

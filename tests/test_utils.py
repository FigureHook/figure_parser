import pytest
from faker import Faker
from figure_parser.constants import BrandHost
from figure_parser.exceptions import UnsupportedDomainError
from figure_parser.utils import (check_domain, price_parse, scale_parse,
                                 size_parse)

fake = Faker()

brand_host_test_data = [
    (BrandHost.GSC, "https://www.goodsmile.info/ja/product/8978"),
    (BrandHost.ALTER, "http://www.alter-web.jp/products/261/")
]


@pytest.mark.parametrize("domain, url", brand_host_test_data)
def test_domain_checker(domain, url):
    class MockBaseParser:
        @check_domain
        def __init__(self, item_url, parser=None):
            pass

    class MockParser(MockBaseParser):
        __allow_domain__ = domain

    class MockFailParser(MockBaseParser):
        __allow_domain__ = 'no.xyz'

    MockParser(url)

    with pytest.raises(UnsupportedDomainError):
        MockFailParser(url)


def test_price_parser():
    for _ in range(10):
        ran_num = fake.random_int(max=99999)
        price_text = f"{ran_num:n}"
        price = price_parse(price_text)

        assert price == ran_num

        with pytest.raises(ValueError):
            price_parse('')


def test_size_parser():
    cm_units = ('cm' '㎝', 'ｃｍ')
    mm_units = ('㎜', 'mm', 'ｍｍ')
    for _ in range(1000):
        units = fake.random_element(elements=(cm_units, mm_units))
        ran_num = fake.random_int()
        unit = fake.random_element(elements=units)
        size_text = f"{ran_num:n}{unit}"

        assert unit in units

        if units == cm_units:
            ran_num = ran_num * 10

        assert size_parse(size_text) == ran_num


def test_scale_parser():
    for _ in range(100):
        denominator = fake.random_digit_not_null()
        scale_text = f"1/{denominator}"

        assert scale_parse(scale_text) == denominator

import pytest
from figure_parser.constants import BrandHost
from figure_parser.errors import UnsupportedDomainError
from figure_parser.utils import check_domain, price_parse

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
    price_text = "1,100,000,000"
    price = price_parse(price_text)

    assert price == 1100000000

    with pytest.raises(ValueError):
        price_parse('')

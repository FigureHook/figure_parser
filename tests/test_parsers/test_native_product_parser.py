import pytest

from figure_parser.parsers import NativeProductParser

from .test_product_parser import (
    TEST_CASE_DIR,
    BaseTestCase,
    ParserTestTarget,
    get_html,
    load_yaml,
)


class TestNativeParser(BaseTestCase):
    products = load_yaml(TEST_CASE_DIR.joinpath("native.yml"))

    @pytest.fixture(scope="class", params=products)
    def target(self, request) -> ParserTestTarget:
        page = get_html(request.param["url"])
        return ParserTestTarget(
            parser=NativeProductParser.create_parser(request.param["url"], source=page),
            expected=request.param,
        )

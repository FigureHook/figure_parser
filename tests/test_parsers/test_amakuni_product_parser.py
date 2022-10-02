import pytest

from figure_parser.parsers import AmakuniProductParser

from .test_product_parser import (
    TEST_CASE_DIR,
    BaseTestCase,
    ParserTestTarget,
    get_html,
    load_yaml,
)


class TestAmakuniParser(BaseTestCase):
    products = load_yaml(TEST_CASE_DIR.joinpath("amakuni.yml"))

    @pytest.fixture(scope="class", params=products)
    def target(self, request) -> ParserTestTarget:
        page = get_html(request.param["url"])
        return ParserTestTarget(
            parser=AmakuniProductParser.create_parser(
                request.param["url"], source=page
            ),
            expected=request.param,
        )

import pytest

from .test_product_parser import (
    TEST_CASE_DIR,
    BaseTestCase,
    ParserTestTarget,
    get_html,
    load_yaml,
)

from figure_parser.parsers import ${name}ProductParser


class Test${name}Parser(BaseTestCase):
    products = load_yaml(TEST_CASE_DIR.joinpath("${test_case_name}.yml"))

    @pytest.fixture(scope="class", params=products)
    def target(self, request) -> ParserTestTarget:
        page = get_html(
            url=request.param["url"],
            headers={},
            cookies={},
        )
        return ParserTestTarget(
            parser= ${name}ProductParser.create_parser(
                url=request.param["url"], source=page
            ),
            expected=request.param,
        )

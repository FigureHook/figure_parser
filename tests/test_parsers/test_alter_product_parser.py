import pytest

from figure_parser.parsers import AlterProductParser

from .test_product_parser import (
    TEST_CASE_DIR,
    BaseTestCase,
    ParserTestTarget,
    get_html,
    load_yaml,
)


class TestAlterParser(BaseTestCase):
    products = load_yaml(TEST_CASE_DIR.joinpath("alter.yml"))

    @pytest.fixture(scope="class", params=products)
    def target(self, request) -> ParserTestTarget:
        page = get_html(request.param["url"])
        return ParserTestTarget(
            parser=AlterProductParser.create_parser(request.param["url"], source=page),
            expected=request.param,
        )

    @pytest.mark.skip(reason="Alter doesn't provide order_period.")
    def test_order_period(self, *args):
        ...

    def test_thumbnail(self, target: ParserTestTarget):
        thumbnail = target.parser.parse_thumbnail()
        if thumbnail:
            assert isinstance(thumbnail, str)
            if "pagespeed" in thumbnail:
                pytest.skip()
        assert thumbnail == target.expected.get("thumbnail")

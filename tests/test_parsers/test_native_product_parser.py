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

    def test_images(self, target: ParserTestTarget):
        images = target.parser.parse_images()
        assert type(images) is list
        if "pagespeed" in images:
            pytest.skip("The url is cache url.")
        else:
            assert target.expected.get("images") in images

    def test_thumbnail(self, target: ParserTestTarget):
        thumbnail = target.parser.parse_thumbnail()
        if thumbnail:
            if "pagespeed" in thumbnail:
                pytest.skip("The url is cache url.")
        else:
            super().test_thumbnail(target)

    def test_og_image(self, target: ParserTestTarget):
        og_image = target.parser.parse_og_image()
        if og_image:
            if "pagespeed" in og_image:
                pytest.skip("The url is cache url.")
        else:
            super().test_og_image(target)

import pytest

from figure_parser.parsers import GSCProductParser

from .test_product_parser import (
    TEST_CASE_DIR,
    BaseTestCase,
    ParserTestTarget,
    get_html,
    load_yaml,
)


class TestGSCParser(BaseTestCase):
    products = load_yaml(TEST_CASE_DIR.joinpath("gsc.yml"))

    @pytest.fixture(scope="class", params=products)
    def target(self, request) -> ParserTestTarget:
        page = get_html(
            url=request.param["url"],
            headers={},
            cookies={"age_verification_ok": "true"},
        )
        return ParserTestTarget(
            parser=GSCProductParser.create_parser(
                url=request.param["url"], source=page
            ),
            expected=request.param,
        )

    def test_worker_parser(self):
        from figure_parser.parsers.gsc.product_parser import parse_people

        worker1 = "横田健(原型協力 DRAGON Toy)"
        worker2 = "乙山法純(制作協力:アルター)"
        worker3 = "川崎和史 (製作協力:ねんどろん)"
        worker4 = "KADOKAWA(協力:レイアップ)"
        worker5 = "ナナシ(製作協力:ねんどろん)"
        worker6 = "ナナシ 制作協力:ねんどろん"
        worker7 = "セイバー:市橋卓也"
        worker8 = "鈴乃木凜彩色：eriko、GSX400S カタナ彩色：雷電"

        assert parse_people(worker1) == ["横田健"]
        assert parse_people(worker2) == ["乙山法純"]
        assert parse_people(worker3) == ["川崎和史"]
        assert parse_people(worker4) == ["KADOKAWA"]
        assert parse_people(worker5) == ["ナナシ"]
        assert parse_people(worker6) == ["ナナシ"]
        assert parse_people(worker7) == ["市橋卓也"]
        assert parse_people(worker8) == ["eriko", "雷電"]

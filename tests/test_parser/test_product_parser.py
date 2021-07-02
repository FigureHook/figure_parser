import os
from datetime import datetime
from pathlib import Path

import pytest
import yaml
from _pytest.assertion.util import isiterable
from figure_parser.alter import (AlterAnnouncementLinkExtractor,
                                 AlterProductParser, AlterYearlyAnnouncement)
from figure_parser.constants import AlterCategory, GSCCategory, GSCLang
from figure_parser.extension_class import HistoricalReleases, Release
from figure_parser.gsc import (GSCAnnouncementLinkExtractor, GSCProductParser,
                               GSCYearlyAnnouncement)
from figure_parser.native import NativeProductParser
from figure_parser.utils import get_page

THIS_DIR = Path(os.path.dirname(__file__)).resolve()


def load_yaml(path):
    with open(path, "r") as stream:
        sth = yaml.safe_load(stream)

    return sth


class BaseTestCase:
    def test_name(self, item):
        name = item["test"].parse_name()
        assert name == item["expected"]["name"]

    def test_series(self, item):
        series = item["test"].parse_series()
        assert series == item["expected"]["series"]

    def test_category(self, item):
        category = item["test"].parse_category()
        assert category == item["expected"]["category"]

    def test_manufacturer(self, item):
        manufacturer = item["test"].parse_manufacturer()
        assert manufacturer == item["expected"]["manufacturer"]

    def test_order_period(self, item):
        order_period = item["test"].parse_order_period()
        expected_order_period = item["expected"]["order_period"]

        if not expected_order_period['start'] and not expected_order_period['end']:
            pytest.xfail("Some maker didn't announce the period.")

        start = order_period.start
        end = order_period.end

        if start and not end:
            pytest.xfail("Some products could be ordered until sold out.")

        if expected_order_period['start']:
            assert type(start) is datetime
            assert start == item["expected"]["order_period"]["start"]
        if expected_order_period['end']:
            assert type(end) is datetime
            assert end == item["expected"]["order_period"]["end"]

    def test_sculptor(self, item):
        sculptor = item["test"].parse_sculptors()
        assert sorted(sculptor) == sorted(item["expected"]["sculptor"])

    def test_release_infos(self, item):
        release_infos: HistoricalReleases = item["test"].parse_release_infos()
        expected_release_infos: list = item["expected"]["release_infos"]
        assert len(release_infos) == len(expected_release_infos)

        release_infos.sort()
        expected_release_infos.sort(
            key=lambda r: r["release_date"].timestamp() if r["release_date"] else 0)

        for r, e_r in zip(release_infos, expected_release_infos):
            r: Release
            assert r.price == e_r["price"]
            expected_date = e_r["release_date"].date(
            ) if e_r["release_date"] else e_r["release_date"]
            assert r.release_date == expected_date
            assert r.price.tax_including is e_r['tax_including']

    def test_maker_id(self, item):
        id_ = item["test"].parse_maker_id()
        assert id_ == item["expected"]["maker_id"]

    def test_scale(self, item):
        scale = item["test"].parse_scale()
        assert scale == item["expected"]["scale"]

    def test_size(self, item):
        size = item["test"].parse_size()
        assert size == item["expected"]["size"]

    def test_resale(self, item):
        resale = item["test"].parse_resale()
        assert resale is item["expected"]["resale"]

    def test_adult(self, item):
        adult = item["test"].parse_adult()
        assert adult is item["expected"]["adult"]

    def test_copyright(self, item):
        _copyright = item["test"].parse_copyright()
        assert _copyright == item["expected"]["copyright"]

    def test_paintwork(self, item):
        paintwork = item["test"].parse_paintworks()
        assert sorted(paintwork) == sorted(item["expected"]["paintwork"])

    def test_releaser(self, item):
        releaser = item["test"].parse_releaser()
        assert releaser == item["expected"]["releaser"]

    def test_distributer(self, item):
        distributer = item["test"].parse_distributer()
        assert distributer == item["expected"]["distributer"]

    def test_images(self, item):
        images = item["test"].parse_images()
        assert type(images) is list
        assert item["expected"]["images"] in images

    def test_thumbnail(self, item):
        thumbnail = item["test"].parse_thumbnail()
        if thumbnail:
            assert isinstance(thumbnail, str)
        assert thumbnail == item["expected"]["thumbnail"]

    def test_og_image(self, item):
        og_image = item["test"].parse_og_image()
        if og_image:
            assert isinstance(og_image, str)
        assert og_image == item["expected"]["og_image"]

    def test_jan(self, item):
        jan = item['test'].parse_JAN()
        expected_jan = item["expected"]["JAN"]

        assert jan == expected_jan


class TestGSCParser(BaseTestCase):
    products = load_yaml(
        THIS_DIR.joinpath("test_case", "gsc_products.yml")
    )

    @pytest.fixture(scope="class", params=products)
    def item(self, request):
        return {
            "test": GSCProductParser(request.param["url"]),
            "expected": request.param
        }

    def test_announcement(self):
        gsc_yearly = GSCYearlyAnnouncement(
            GSCCategory.SCALE,
            start=2020,
            lang=GSCLang.JAPANESE
        )

        assert isiterable(gsc_yearly)
        for items in gsc_yearly:
            assert items
            assert isinstance(items, list)

    def test_worker_parser(self):
        from figure_parser.gsc.product_parser import parse_people
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

    def test_announcement_link_extractor(self):
        src = "https://www.goodsmile.info/ja/products/category/scale/announced/2020"
        page = get_page(src)
        links = GSCAnnouncementLinkExtractor.extract(page)
        assert isinstance(links, list)
        assert links


class TestAlterParser(BaseTestCase):
    products = load_yaml(
        THIS_DIR.joinpath("test_case", "alter_products.yml")
    )

    @pytest.fixture(scope="class", params=products)
    def item(self, request):
        return {
            "test": AlterProductParser(request.param["url"]),
            "expected": request.param
        }

    def test_order_period(self, item):
        pytest.skip("Alter doesn't provide order_period.")

    def test_announcement(self):
        alter_yearly = AlterYearlyAnnouncement(
            AlterCategory.FIGURE,
            start=2020
        )

        assert isiterable(alter_yearly)
        for items in alter_yearly:
            assert items
            assert isinstance(items, list)

    def test_announcement_link_extractor(self):
        src = "http://www.alter-web.jp/figure/?yy=2014&mm="
        page = get_page(src)
        links = AlterAnnouncementLinkExtractor.extract(page)
        assert links
        assert isinstance(links, list)


class TestNativeParser(BaseTestCase):
    products = load_yaml(
        f"{THIS_DIR}/test_case/native_products.yml"
    )

    @pytest.fixture(scope="class", params=products)
    def item(self, request):
        return {
            "test": NativeProductParser(request.param["url"]),
            "expected": request.param
        }


class TestParserUtils:
    def test_gsc_locale_parser(self):
        en = "https://www.goodsmile.info/en/product/4364"
        ja = "https://www.goodsmile.info/ja/product/4364"
        zh = "https://www.goodsmile.info/zh/product/4364"
        assert GSCProductParser(en).locale == "en"
        assert GSCProductParser(ja).locale == "ja"
        assert GSCProductParser(zh).locale == "zh"

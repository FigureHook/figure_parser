import os
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from hashlib import md5
from pathlib import Path
from typing import Any, Mapping

import pytest
import yaml
from bs4 import BeautifulSoup
from figure_parser.core.entity import Release
from figure_parser.core.pipe.sorting import _sort_release
from figure_parser.parsers import (AlterProductParser, GSCProductParser,
                                   NativeProductParser)
from figure_parser.parsers.base import AbstractBs4ProductParser

THIS_DIR = Path(os.path.dirname(__file__)).resolve()
TEST_CASE_DIR = THIS_DIR.joinpath("product_case")


@dataclass
class ParserTestTarget:
    parser: AbstractBs4ProductParser
    page: BeautifulSoup
    expected: Mapping


def load_yaml(path):
    with open(path, "r", encoding='utf-8') as stream:
        sth = yaml.safe_load(stream)

    return sth


def get_html(url: str, headers={}, cookies={}) -> BeautifulSoup:
    m = md5()
    m.update(url.encode('utf-8'))
    hash_name = m.hexdigest()

    html_dir = THIS_DIR.joinpath("product_case", "html")
    html_dir.mkdir(exist_ok=True)

    html_path = html_dir.joinpath(f"{hash_name}.html")
    if html_path.exists():
        with open(html_path, 'r', encoding='utf-8') as html:
            page = BeautifulSoup(html, "lxml")

    else:
        with open(html_path, 'w', encoding='utf-8') as html:
            cookies_value = ','.join([f"{k}={v}" for k, v in cookies.items()])
            req = urllib.request.Request(url=url, headers=headers)
            req.add_header("Cookie", cookies_value)
            content = urllib.request.urlopen(req).read()
            page = BeautifulSoup(content, "lxml")
            html.write(str(page))

    return page


class BaseTestCase:
    def test_name(self, target: ParserTestTarget):
        name = target.parser.parse_name(target.page)
        assert name == target.expected.get("name")

    def test_series(self, target: ParserTestTarget):
        series = target.parser.parse_series(target.page)
        assert series == target.expected.get("series")

    def test_category(self, target: ParserTestTarget):
        category = target.parser.parse_category(target.page)
        assert category == target.expected.get("category")

    def test_manufacturer(self, target: ParserTestTarget):
        manufacturer = target.parser.parse_manufacturer(target.page)
        assert manufacturer == target.expected.get("manufacturer")

    def test_order_period(self, target: ParserTestTarget):
        order_period = target.parser.parse_order_period(target.page)
        expected_order_period = target.expected.get("order_period")
        assert expected_order_period
        if not expected_order_period.get('start') and not expected_order_period.get('end'):
            pytest.xfail("Some maker didn't announce the period.")

        start = order_period.start
        end = order_period.end

        if start and not end:
            pytest.xfail("Some products could be ordered until sold out.")

        if expected_order_period['start']:
            assert type(start) is datetime
            assert start == target.expected["order_period"]["start"]
        if expected_order_period['end']:
            assert type(end) is datetime
            assert end == target.expected["order_period"]["end"]

    def test_sculptor(self, target: ParserTestTarget):
        sculptor = target.parser.parse_sculptors(target.page)
        assert sorted(sculptor) == sorted(target.expected["sculptor"])

    def test_release_infos(self, target: ParserTestTarget):
        release_infos: list[Release] = target.parser.parse_releases(target.page)
        expected_release_infos: list[dict[str, Any]] = target.expected["release_infos"]
        assert len(release_infos) == len(expected_release_infos)

        release_infos.sort(key=_sort_release)
        expected_release_infos.sort(
            key=lambda r: r["release_date"].timestamp() if r["release_date"] else 0
        )

        for r, e_r in zip(release_infos, expected_release_infos):
            assert r.price == e_r["price"], "The price didn't match."
            expected_date = e_r["release_date"].date(
            ) if e_r["release_date"] else e_r["release_date"]
            assert r.release_date == expected_date, "The release date didn't match."
            assert r.tax_including is e_r['tax_including'], "Tax-including information didn't match."

    def test_scale(self, target: ParserTestTarget):
        scale = target.parser.parse_scale(target.page)
        assert scale == target.expected.get("scale")

    def test_size(self, target: ParserTestTarget):
        size = target.parser.parse_size(target.page)
        assert size == target.expected.get("size")

    def test_rerelease(self, target: ParserTestTarget):
        rerelease = target.parser.parse_rerelease(target.page)
        assert rerelease is target.expected.get("rerelease")

    def test_adult(self, target: ParserTestTarget):
        adult = target.parser.parse_adult(target.page)
        assert adult is target.expected.get("adult")

    def test_copyright(self, target: ParserTestTarget):
        _copyright = target.parser.parse_copyright(target.page)
        assert _copyright == target.expected.get("copyright")

    def test_paintwork(self, target: ParserTestTarget):
        paintwork = target.parser.parse_paintworks(target.page)
        assert sorted(paintwork) == sorted(target.expected["paintwork"])

    def test_releaser(self, target: ParserTestTarget):
        releaser = target.parser.parse_releaser(target.page)
        assert releaser == target.expected.get("releaser")

    def test_distributer(self, target: ParserTestTarget):
        distributer = target.parser.parse_distributer(target.page)
        assert distributer == target.expected.get("distributer")

    def test_images(self, target: ParserTestTarget):
        images = target.parser.parse_images(target.page)
        assert type(images) is list
        assert target.expected.get("images") in images

    def test_thumbnail(self, target: ParserTestTarget):
        thumbnail = target.parser.parse_thumbnail(target.page)
        if thumbnail:
            assert isinstance(thumbnail, str)
        assert thumbnail == target.expected.get("thumbnail")

    def test_og_image(self, target: ParserTestTarget):
        og_image = target.parser.parse_og_image(target.page)
        if og_image:
            assert isinstance(og_image, str)
        assert og_image == target.expected.get("og_image")

    def test_jan(self, target: ParserTestTarget):
        jan = target.parser.parse_JAN(target.page)
        expected_jan = target.expected.get("JAN")

        assert jan == expected_jan


class TestGSCParser(BaseTestCase):
    products = load_yaml(
        TEST_CASE_DIR.joinpath("gsc_products.yml")
    )

    @pytest.fixture(scope="class", params=products)
    def target(self, request) -> ParserTestTarget:
        page = get_html(url=request.param["url"], headers={}, cookies={
            "age_verification_ok": "true"
        })
        return ParserTestTarget(
            parser=GSCProductParser.create_parser(url=request.param["url"], source=page),
            page=page,
            expected=request.param
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


class TestAlterParser(BaseTestCase):
    products = load_yaml(
        TEST_CASE_DIR.joinpath("alter_products.yml")
    )

    @pytest.fixture(scope="class", params=products)
    def target(self, request) -> ParserTestTarget:
        page = get_html(request.param["url"])
        return ParserTestTarget(
            parser=AlterProductParser.create_parser(request.param["url"], source=page),
            page=page,
            expected=request.param
        )

    def test_order_period(self, *args):
        pytest.skip("Alter doesn't provide order_period.")


class TestNativeParser(BaseTestCase):
    products = load_yaml(
        TEST_CASE_DIR.joinpath("native_products.yml")
    )

    @pytest.fixture(scope="class", params=products)
    def target(self, request) -> ParserTestTarget:
        page = get_html(request.param["url"])
        return ParserTestTarget(
            parser=NativeProductParser.create_parser(request.param["url"], source=page),
            page=page,
            expected=request.param
        )
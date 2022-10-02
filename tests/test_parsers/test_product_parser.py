import os
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime
from hashlib import md5
from pathlib import Path
from typing import Any, Mapping

import pytest
import yaml
from bs4 import BeautifulSoup
from pytest_mock import MockerFixture

from figure_parser.entities import PriceTag, Release
from figure_parser.parsers.base import AbstractBs4ProductParser
from figure_parser.pipes.sorting import _sort_release

THIS_DIR = Path(os.path.dirname(__file__)).resolve()
TEST_CASE_DIR = THIS_DIR.joinpath("product_case")


@dataclass
class ParserTestTarget:
    parser: AbstractBs4ProductParser
    expected: Mapping


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as stream:
        sth = yaml.safe_load(stream)

    return sth


def get_html(url: str, headers={}, cookies={}) -> BeautifulSoup:
    m = md5()
    m.update(url.encode("utf-8"))
    hash_name = m.hexdigest()

    html_dir = THIS_DIR.joinpath("product_case", "html")
    html_dir.mkdir(exist_ok=True)

    html_path = html_dir.joinpath(f"{hash_name}.html")
    if html_path.exists():
        with open(html_path, "r", encoding="utf-8") as html:
            page = BeautifulSoup(html, "lxml")

    else:
        with open(html_path, "w", encoding="utf-8") as html:
            cookies_value = ",".join([f"{k}={v}" for k, v in cookies.items()])
            req = urllib.request.Request(url=url, headers=headers)
            req.add_header("Cookie", cookies_value)
            content = urllib.request.urlopen(req).read()
            page = BeautifulSoup(content, "lxml")
            html.write(str(page))

    return page


class BaseTestCase:
    def test_name(self, target: ParserTestTarget):
        name = target.parser.parse_name()
        assert name == target.expected.get("name")

    def test_series(self, target: ParserTestTarget):
        series = target.parser.parse_series()
        assert series == target.expected.get("series")

    def test_category(self, target: ParserTestTarget):
        category = target.parser.parse_category()
        assert category == target.expected.get("category")

    def test_manufacturer(self, target: ParserTestTarget):
        manufacturer = target.parser.parse_manufacturer()
        assert manufacturer == target.expected.get("manufacturer")

    def test_order_period(self, target: ParserTestTarget):
        order_period = target.parser.parse_order_period()
        expected_order_period = target.expected.get("order_period")
        assert expected_order_period
        if not expected_order_period.get("start") and not expected_order_period.get(
            "end"
        ):
            pytest.xfail("Some maker didn't announce the period.")

        start = order_period.start
        end = order_period.end

        if start and not end:
            pytest.xfail("Some products could be ordered until sold out.")

        if expected_order_period["start"]:
            assert type(start) is datetime
            assert start == target.expected["order_period"]["start"]
        if expected_order_period["end"]:
            assert type(end) is datetime
            assert end == target.expected["order_period"]["end"]

    def test_sculptor(self, target: ParserTestTarget):
        sculptor = target.parser.parse_sculptors()
        assert sorted(sculptor) == sorted(target.expected["sculptor"])

    def test_release_infos(self, target: ParserTestTarget):
        release_infos: list[Release] = target.parser.parse_releases()
        expected_release_infos: list[dict[str, Any]] = target.expected["release_infos"]
        assert len(release_infos) == len(expected_release_infos)

        release_infos.sort(key=_sort_release)
        expected_release_infos.sort(
            key=lambda r: r["release_date"].timestamp() if r["release_date"] else 0
        )

        for r, e_r in zip(release_infos, expected_release_infos):
            assert r.price == e_r["price"], "The price didn't match."
            expected_date = (
                e_r["release_date"].date()
                if e_r["release_date"]
                else e_r["release_date"]
            )
            assert r.release_date == expected_date, "The release date didn't match."
            assert (
                r.tax_including is e_r["tax_including"]
            ), "Tax-including information didn't match."

    def test_scale(self, target: ParserTestTarget):
        scale = target.parser.parse_scale()
        assert scale == target.expected.get("scale")

    def test_size(self, target: ParserTestTarget):
        size = target.parser.parse_size()
        assert size == target.expected.get("size")

    def test_rerelease(self, target: ParserTestTarget):
        rerelease = target.parser.parse_rerelease()
        assert rerelease is target.expected.get("rerelease")

    def test_adult(self, target: ParserTestTarget):
        adult = target.parser.parse_adult()
        assert adult is target.expected.get("adult")

    def test_copyright(self, target: ParserTestTarget):
        _copyright = target.parser.parse_copyright()
        assert _copyright == target.expected.get("copyright")

    def test_paintwork(self, target: ParserTestTarget):
        paintwork = target.parser.parse_paintworks()
        assert sorted(paintwork) == sorted(target.expected["paintwork"])

    def test_releaser(self, target: ParserTestTarget):
        releaser = target.parser.parse_releaser()
        assert releaser == target.expected.get("releaser")

    def test_distributer(self, target: ParserTestTarget):
        distributer = target.parser.parse_distributer()
        assert distributer == target.expected.get("distributer")

    def test_images(self, target: ParserTestTarget):
        images = target.parser.parse_images()
        assert type(images) is list
        assert target.expected.get("images") in images

    def test_thumbnail(self, target: ParserTestTarget):
        thumbnail = target.parser.parse_thumbnail()
        if thumbnail:
            assert isinstance(thumbnail, str)
        assert thumbnail == target.expected.get("thumbnail")

    def test_og_image(self, target: ParserTestTarget):
        og_image = target.parser.parse_og_image()
        if og_image:
            assert isinstance(og_image, str)
        assert og_image == target.expected.get("og_image")

    def test_jan(self, target: ParserTestTarget):
        jan = target.parser.parse_JAN()
        expected_jan = target.expected.get("JAN")

        assert jan == expected_jan


class MockStrProductParser(AbstractBs4ProductParser):
    ...


def test_releases_base_parsing(mocker: MockerFixture):
    mocker.patch.object(MockStrProductParser, "__abstractmethods__", new_callable=set)
    parser = MockStrProductParser(source="kappa")  # type: ignore

    # dates is empty.
    # fill the dates with None to fit the prices.
    parser.parse_prices = mocker.MagicMock(return_value=[PriceTag(100)])  # type: ignore
    parser.parse_release_dates = mocker.MagicMock(return_value=[])  # type: ignore
    releases = parser.parse_releases()
    assert len(releases) == 1
    assert releases[0].release_date is None
    assert releases[0].price == 100

    # prices is empty.
    # fill the dates with None to fit the prices.
    parser.parse_prices = mocker.MagicMock(return_value=[])  # type: ignore
    parser.parse_release_dates = mocker.MagicMock(return_value=[date(2023, 2, 2)])  # type: ignore
    releases = parser.parse_releases()
    assert len(releases) == 1
    assert releases[0].release_date == date(2023, 2, 2)
    assert releases[0].price is None

    # dates and prices are not empty.
    # dates is more than prices.
    # fill the prices with last price to fit the dates.
    dates = [date(2020, 2, 2), date(2023, 2, 2)]
    parser.parse_prices = mocker.MagicMock(return_value=[PriceTag(100)])  # type: ignore
    parser.parse_release_dates = mocker.MagicMock(return_value=dates)  # type: ignore
    releases = parser.parse_releases()
    assert len(releases) == 2
    for i, r in enumerate(releases):
        assert r.release_date == dates[i]
        assert r.price == 100

    # dates and prices are not empty.
    # prices is more than dates.
    # discard the part of prices that more than dates to fit the dates.
    dates = [date(2020, 2, 2)]
    parser.parse_prices = mocker.MagicMock(return_value=[PriceTag(100), PriceTag(200)])  # type: ignore
    parser.parse_release_dates = mocker.MagicMock(return_value=dates)  # type: ignore
    releases = parser.parse_releases()
    assert len(releases) == 1
    for i, r in enumerate(releases):
        assert r.release_date == date(2020, 2, 2)
        assert r.price == 100


def test_base_parser_head_parsing(mocker: MockerFixture):
    html_text = """
    <meta content="https://foobar.com/image1.jpg" content="https://foobar.com/image2.jpg" property="og:image"/>
    <meta content="https://foobar.com/image1.jpg" content="https://foobar.com/image2.jpg" name="thumbnail"/>
    """
    source = BeautifulSoup(html_text, "lxml")
    mocker.patch.object(MockStrProductParser, "__abstractmethods__", new_callable=set)
    parser = MockStrProductParser(source)  # type: ignore

    assert parser.parse_og_image() == "https://foobar.com/image1.jpg"
    assert parser.parse_thumbnail() == "https://foobar.com/image1.jpg"

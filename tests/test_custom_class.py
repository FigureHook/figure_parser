from datetime import date, datetime

import pytest
from figure_parser.errors import OrderPeriodError
from figure_parser.extension_class import (HistoricalReleases, OrderPeriod,
                                           Price, Release)
from pytest_mock import MockerFixture


class TestRelease:
    def test_release_class(self, mocker: MockerFixture):
        mocker.patch('figure_parser.extension_class.Price', int)
        r1 = Release(release_date=date(2020, 1, 1), price=Price(10000))

        assert hasattr(r1, "release_date")
        assert hasattr(r1, "price")
        assert hasattr(r1, "announced_at")


def test_release_info_class(mocker: MockerFixture):
    mocker.patch('figure_parser.extension_class.Price', int)
    first_release = Release(release_date=date(2020, 1, 1), price=Price(10000))
    second_release = Release(release_date=date(2020, 2, 1), price=Price(12000))
    third_release = Release(release_date=None, price=Price(12000))
    date_price_combos = [first_release, second_release, third_release]
    sorted_combos = [third_release, first_release, second_release]

    hr = HistoricalReleases()
    hr.append(first_release)
    hr.append(second_release)
    hr.append(third_release)

    assert hr == date_price_combos

    hr.sort()
    assert hr == sorted_combos

    last_release = hr.last()
    assert last_release.release_date == date(2020, 2, 1)
    assert last_release.price == 12000

    hr2 = HistoricalReleases()
    assert not hr2.last()


class TestOrderPeriod:
    def test_is_available(self):
        start = datetime(1990, 1, 1)
        end = datetime(2000, 1, 1)

        order_period = OrderPeriod(start, end)
        assert not order_period.is_available

    def test_is_available_at_specific_time(self):
        start = datetime(2020, 2, 2, 9, 0)
        end = datetime(2020, 3, 2, 23, 0)

        now = datetime(2020, 2, 22, 5, 34)

        order_period = OrderPeriod(start, end)
        assert order_period.is_available_at(now)
        assert now in order_period

    def test_default_value(self):
        order_period = OrderPeriod()
        assert not order_period.start
        assert not order_period.end

    def test_checker(self):
        with pytest.raises(OrderPeriodError):
            OrderPeriod(datetime(2000, 1, 1), datetime(1999, 1, 1))

    def test_none_of_one(self):
        OrderPeriod(None, datetime(2000, 1, 1))
        OrderPeriod(datetime(2020, 1, 1), None)

    def test_bool(self):
        assert not bool(OrderPeriod(None, None))
        assert OrderPeriod(None, datetime(2000, 1, 1))
        assert OrderPeriod(datetime(2020, 1, 1), None)
        assert OrderPeriod(datetime(2020, 1, 1), datetime(2022, 1, 1))


class TestPrice:
    def test_is_int(self):
        price = Price(300)
        assert isinstance(price, int)

    def test_price_always_be_postive(self):
        price = Price(-21323)
        assert price == 21323

    def test_price_has_tax_including_attribute(self):
        price = Price(500)
        assert hasattr(price, 'tax_including')

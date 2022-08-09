from datetime import datetime

import pytest
from figure_parser.core.entity import OrderPeriod
from pydantic import ValidationError


class TestOrderPeriod:
    def test_is_available(self):
        start = datetime(1990, 1, 1)
        end = datetime(2000, 1, 1)

        order_period = OrderPeriod(start=start, end=end)
        assert not order_period.is_available

    def test_is_available_at_specific_time(self):
        start = datetime(2020, 2, 2, 9, 0)
        end = datetime(2020, 3, 2, 23, 0)

        now = datetime(2020, 2, 22, 5, 34)

        order_period = OrderPeriod(start=start, end=end)
        assert order_period.is_available_at(now)
        assert now in order_period

    def test_default_value(self):
        order_period = OrderPeriod()
        assert not order_period.start
        assert not order_period.end

    def test_validator(self):
        with pytest.raises(ValidationError):
            OrderPeriod(start=datetime(2000, 1, 1), end=datetime(1999, 1, 1))

    def test_none_of_one(self):
        OrderPeriod(start=None, end=datetime(2000, 1, 1))
        OrderPeriod(start=datetime(2020, 1, 1), end=None)

    def test_bool(self):
        assert not bool(OrderPeriod(start=None, end=None))
        assert OrderPeriod(start=None, end=datetime(2000, 1, 1))
        assert OrderPeriod(start=datetime(2020, 1, 1), end=None)
        assert OrderPeriod(start=datetime(2020, 1, 1), end=datetime(2022, 1, 1))

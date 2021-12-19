from datetime import date
from pytest_mock import MockerFixture
from figure_parser.gsc.shipment_parser import GSCShipment, is_critical
from figure_parser.exceptions import TargetConstructureChangeError
import pytest


class TestGSCShipment:
    def test_shipment(self):
        s = GSCShipment()

        for d in s.dates:
            assert type(d) is date

    def test_parsing_year_and_month_failed(self, mocker: MockerFixture):
        mocker.patch(
            "figure_parser.gsc.shipment_parser._parse_release_dates",
            side_effect=TargetConstructureChangeError("Damn")
        )

        with pytest.raises(TargetConstructureChangeError):
            GSCShipment()

    def test_critical_decorator(self):
        def mock_func():
            raise TargetConstructureChangeError("Damn")

        from figure_parser.gsc.shipment_parser import is_critical

        damn = is_critical(mock_func)
        with pytest.raises(TargetConstructureChangeError, match="Please contact with"):
            damn()

from datetime import date

import pytest
from figure_parser.exceptions import UnreliableParserError
from figure_parser.gsc.shipment_parser import GSCShipment, is_critical, GSCShipmentTag
from pytest_mock import MockerFixture


class TestGSCShipment:
    def test_shipment_tag(self):
        tag = GSCShipmentTag(url='https://www.example.com', jan="8188499954723")
        assert tag

    def test_shipment(self):
        s = GSCShipment.create()

        for d in s.dates:
            assert type(d) is date

    def test_parsing_year_and_month_failed(self, mocker: MockerFixture):
        mocker.patch("figure_parser.gsc.shipment_parser.parse_year_and_month", side_effect=AssertionError("Damn"))

        with pytest.raises(UnreliableParserError):
            GSCShipment.create()

    def test_parsing_day_failed(self, mocker: MockerFixture):
        mocker.patch("figure_parser.gsc.shipment_parser.parse_day", side_effect=AssertionError("Damn"))

        with pytest.raises(UnreliableParserError):
            GSCShipment.create()

    def test_critical_decorator(self):
        def mock_func():
            assert None, "Damn"

        damn = is_critical(mock_func)
        with pytest.raises(UnreliableParserError, match="Please contact with"):
            damn()

    def test_dates_and_products_are_misaligned(self, mocker: MockerFixture):
        mocker.patch("figure_parser.gsc.shipment_parser.parse_release_dates", return_value=[1, 2])
        mocker.patch("figure_parser.gsc.shipment_parser.parse_release_products", return_value=[1, 2, 3])

        with pytest.raises(UnreliableParserError):
            GSCShipment.create()

    def test_get_today_shipment(self):
        shipments = GSCShipment.create()
        shipments.today()

    def test_get_dedicated_date_shipment(self):
        shipments = GSCShipment.create()
        shipments.shipped_out_on(date(2022, 2, 11))

import pytest
from figure_parser.errors import (FigureParserException, OrderPeriodError,
                                  UnsupportedDomainError)


def test_order_period_error():
    with pytest.raises(FigureParserException):
        raise OrderPeriodError('Nope')


def test_unsupported_host_error():
    with pytest.raises(FigureParserException):
        raise UnsupportedDomainError('Nope')

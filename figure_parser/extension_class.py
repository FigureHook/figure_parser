from collections import UserList
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional, TypeVar, Union

from .exceptions import OrderPeriodError
from .utils import AsDictable

__all__ = [
    "OrderPeriod",
    "Release",
    "Price",
    "HistoricalReleases",
]


@dataclass
class OrderPeriod(AsDictable):
    """
    A dataclass object allowS user to check the product is available for per-ordering or not.

    :param start: The starting time of pre-order.
    :type start: datetime.datetime
    :param end: The ending time of pre-order.
    :type end: datetime.datetime

    :raises OrderPeriodError: If :attr:`start` is later than :attr:`end` when initialization.
    """

    start: Optional[datetime] = None
    """The starting time of pre-order."""
    end: Optional[datetime] = None
    """The ending time of pre-order."""

    def __post_init__(self):
        start = self.start
        end = self.end
        if start and end:
            if end < start:
                raise OrderPeriodError(
                    f"start_datetime {start} shouldn't later than end_datetime {end}."
                )

    @property
    def is_available(self):
        """
        Is available for pre-ordering for current time.

        :returns: Is available for pre-ordering for current time.
        :rtype: bool
        """
        return self._is_available(datetime.now())

    def is_available_at(self, the_time: datetime) -> bool:
        """
        Convenient method for checking availability of pre-ordering for assigned time.

        :param the_time: The time that is used to check availability of pre-ordering.
        :type datetime:
        """
        return self._is_available(the_time)

    def __contains__(self, the_time: datetime) -> bool:
        return self._is_available(the_time)

    def _is_available(self, the_time: datetime) -> bool:
        is_available = True
        if not self.start and self.end:
            is_available = the_time < self.end

        elif not self.end and self.start:
            is_available = the_time > self.start

        elif self.start and self.end:
            is_available = self.start < the_time < self.end

        return is_available

    def __bool__(self):
        return any((self.start, self.end))


class Price(int):
    """
    Used to record the price is tax-including or not.

    :param value: Only positive value allowed.
    :type value: int
    :param tax_including: Tax is including or not.
    :type tax_including: bool
    """
    def __new__(cls, value: int, *args, **kwargs):
        if value < 0:
            value = abs(value)

        return super().__new__(cls, value)

    def __init__(self, value: int, tax_including: bool = False):
        super().__init__()
        self._tax_including = tax_including

    @property
    def tax_including(self):
        """
        Tax is including or not.

        :return:  Tax is including or not.
        :rtype: bool
        """
        return self._tax_including


@dataclass
class Release(AsDictable):
    """
    :param release_date: The product release date.
    :type release_date: datetime.date
    :param price: The product price for the release.
    :type price: Price
    :param announced_at: The announcing date of the release.
    :type announced_at: datetime.date
    """
    release_date: Optional[date]
    """The product release date."""
    price: Optional[Price]
    """The product price for the release."""
    announced_at: Optional[date] = None
    """The announcing date of the release."""


T = TypeVar('T')


class HistoricalReleases(UserList[T]):
    """
    A list-like container for :class:`Release`

    :param initlist: Initial data for container.
    :type initlist: list[Release]
    """

    def sort(self, *args: Any, **kwargs: Any) -> None:
        """
        This method would follow ``None-release-date-first-with-asc`` rule **when sorting**.

        Example:

        .. highlight:: python
        .. code-block:: python

            HistoricalReleases([
                Release(release_date=None, price=Price(12000)),
                Release(release_date=date(2020, 1, 1), price=Price(10000)),
                Release(release_date=date(2020, 2, 1), price=Price(12000))
            ])


        :param args: Additional arguments for :meth:`list.sort`.
        :type args: list
        :param kwargs: Additional key-word arguments for :meth:`list.sort`.
        :type kwargs: dict
        """

        def sort_release(release: Union[T, Release, None]):
            if isinstance(release, Release):
                if isinstance(release.release_date, date):
                    return release.release_date
            return date.fromtimestamp(0)

        super().sort(key=sort_release, *args, **kwargs)

    def last(self) -> Optional[T]:
        """
        If the container is not empty, return last element.

        :return: The last element.
        :rtype: Optional[Release]
        """
        if not len(self):
            return None

        self.sort()

        return self.data[-1]

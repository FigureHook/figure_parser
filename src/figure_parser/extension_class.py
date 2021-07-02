from collections import UserList
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional, TypeVar

from .errors import OrderPeriodError
from .utils import AsDictable

__all__ = [
    "OrderPeriod",
    "Release",
    "HistoricalReleases"
]


@dataclass
class OrderPeriod(AsDictable):
    start: Optional[datetime] = None
    end: Optional[datetime] = None

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
        return self._is_available(datetime.now())

    def is_available_at(self, the_time: datetime):
        return self._is_available(the_time)

    def __contains__(self, the_time: datetime):
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
    def __new__(cls, value: int, *args, **kwargs):
        if value < 0:
            value = abs(value)

        return super().__new__(cls, value)

    def __init__(self, value: int, tax_including: bool = False):
        super().__init__()
        self._tax_including = tax_including

    @property
    def tax_including(self):
        return self._tax_including


@dataclass
class Release(AsDictable):
    release_date: Optional[date]
    price: Optional[Price]
    announced_at: Optional[date] = None


T = TypeVar('T')


class HistoricalReleases(UserList[T]):
    """
    List[Release]

    This would follow None-release-date-first-with-asc rule **when sorted**.

    e.g.
    ```py
    HistoricalReleases[
        Release(release_date=None, price=12000),
        Release(release_date=date(2020, 1, 1), price=10000),
        Release(release_date=date(2020, 2, 1), price=12000)
    ]
    ```
    """

    def sort(self, *args: Any, **kwds: Any) -> None:
        def sort_release(release: Release):
            if isinstance(release.release_date, date):
                return release.release_date
            return date.fromtimestamp(0)

        super().sort(key=sort_release)

    def last(self):
        if not len(self):
            return None

        self.sort()

        return self.data[-1]

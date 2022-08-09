from collections import UserList
from datetime import date
from typing import Optional, TypeVar

from pydantic import BaseModel, NonNegativeInt

__all__ = (
    'Release',
    'HistoricalReleases'
)


class Release(BaseModel):
    """
    :param release_date: The product release date.
    :type release_date: datetime.date
    :param price: The product price for the release.
    :type price: Price
    :param announced_at: The announcing date of the release.
    :type announced_at: datetime.date
    """
    release_date: Optional[date] = None
    """The product release date."""
    price: Optional[NonNegativeInt] = None
    """The product price for the release."""
    tax_including: bool = False
    """Annotate the price is including tax or not."""
    announced_at: Optional[date] = None
    """The announcing date of the release."""


T = TypeVar('T', bound=Release)


class HistoricalReleases(UserList[T]):
    """
    A list-like container for :class:`Release`

    :param initlist: Initial data for container.
    :type initlist: list[Release]
    """

    def sort(self) -> None:
        """
        This method would follow ``None-release-date-first-with-asc`` rule **when sorting**.

        Example:

        .. highlight:: python
        .. code-block:: python

            HistoricalReleases([
                Release(release_date=None, price=12000),
                Release(release_date=date(2020, 1, 1), price=10000),
                Release(release_date=date(2020, 2, 1), price=12000)
            ])


        :param args: Additional arguments for :meth:`list.sort`.
        :type args: list
        :param kwargs: Additional key-word arguments for :meth:`list.sort`.
        :type kwargs: dict
        """

        def sort_release(release: T):
            if isinstance(release, Release):
                if isinstance(release.release_date, date):
                    return release.release_date
            return date.fromtimestamp(0)

        super().sort(key=sort_release)

    def last(self) -> Optional[T]:
        """
        If the container is not empty, return last element.

        :return: The last element.
        :rtype: Optional[Release]
        """
        if not self.data:
            return None

        self.sort()
        return self.data[-1]

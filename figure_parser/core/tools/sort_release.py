from datetime import date
from typing import List, TypeVar

from figure_parser.core.entity import Release, ProductBase

Release_T = TypeVar('Release_T', bound=Release)


def _sort_release(release: Release):
    if release.release_date:
        return release.release_date
    return date.fromtimestamp(0)


class ReleaseSorting:
    @staticmethod
    def sort(releases: List[Release_T]) -> List[Release_T]:
        """
        This method would follow ``None-release-date-first-with-asc`` rule **when sorting**.
        """
        releases.sort(key=_sort_release)
        return releases

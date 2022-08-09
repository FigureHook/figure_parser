from datetime import date
from typing import List, TypeVar

from figure_parser.core.entity import Release

Release_T = TypeVar('Release_T', bound=Release)


class ReleaseSorting:
    @staticmethod
    def sort(releases: List[Release_T]) -> List[Release_T]:
        def sort_release(release: Release_T):
            if release.release_date:
                return release.release_date
            return date.fromtimestamp(0)
        releases.sort(key=sort_release)
        return releases

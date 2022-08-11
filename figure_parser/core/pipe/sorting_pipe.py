from datetime import date
from typing import TypeVar

from figure_parser.core.entity import ProductBase, Release

from .interface import PipeInterface

Release_T = TypeVar('Release_T', bound=Release)


def _sort_release(release: Release):
    if release.release_date:
        return release.release_date
    return date.fromtimestamp(0)


class ReleaseSorting(PipeInterface[ProductBase]):
    @classmethod
    def process(cls, product_item: ProductBase) -> ProductBase:
        product_item.releases.sort(key=_sort_release)
        return product_item

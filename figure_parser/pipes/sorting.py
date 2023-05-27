from datetime import date
from typing import TypeVar

from figure_parser.core.models import ProductBase, Release

Release_T = TypeVar("Release_T", bound=Release)


def _sort_release(release: Release):
    return release.release_date or date.fromtimestamp(0)


def sort_releases(product_item: ProductBase) -> ProductBase:
    product_item.releases.sort(key=_sort_release)
    return product_item

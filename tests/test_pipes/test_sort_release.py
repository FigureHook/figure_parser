import random
from datetime import date

from figure_parser.core.entity import ProductBase, Release
from figure_parser.core.pipe.sorting import sort_releases


def test_release_sorting(product: ProductBase):
    release_1 = Release(
        release_date=None
    )
    release_2 = Release(
        release_date=date(2020, 2, 2)
    )
    release_3 = Release(
        release_date=date(2022, 2, 2)
    )

    expected_releases = [release_1, release_2, release_3]

    shuffled_releases = expected_releases.copy()
    random.shuffle(shuffled_releases)
    product.releases = shuffled_releases
    sort_releases(product)

    assert product.releases == expected_releases

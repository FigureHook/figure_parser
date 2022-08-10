import random
from datetime import date

from faker import Faker
from figure_parser.core.entity import Release
from figure_parser.core.tools.sort_release import ReleaseSorting


def test_release_sorting(faker: Faker):
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
    ReleaseSorting.sort(shuffled_releases)

    assert shuffled_releases == expected_releases

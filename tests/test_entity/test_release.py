import random

from faker import Faker
from figure_parser.core.entity import Release


def test_release_initialize(faker: Faker):
    release_date = faker.date_object()
    Release(
        release_date=release_date if faker.boolean(chance_of_getting_true=90) else None,
        price=random.randint(0, 1000000000) if faker.boolean(chance_of_getting_true=90) else None,
        tax_including=faker.boolean(chance_of_getting_true=25),
        announced_at=faker.date_between(end_date=release_date) if faker.boolean(chance_of_getting_true=60) else None
    )

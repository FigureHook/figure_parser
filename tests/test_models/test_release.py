import random

from faker import Faker

from figure_parser import PriceTag, Release


def test_release_initialize(faker: Faker):
    release_date = faker.date_object()
    Release(
        release_date=release_date if faker.boolean(chance_of_getting_true=90) else None,
        price=random.randint(0, 1000000000)
        if faker.boolean(chance_of_getting_true=90)
        else None,
        tax_including=faker.boolean(chance_of_getting_true=25),
        announced_at=faker.date_between(end_date=release_date)
        if faker.boolean(chance_of_getting_true=60)
        else None,
    )


def test_release_set_price_with_price_tag(faker: Faker):
    release_date = faker.date_object()
    price_tag = PriceTag(
        price=random.randint(0, 1000000000)
        if faker.boolean(chance_of_getting_true=90)
        else None,
        tax_including=faker.boolean(chance_of_getting_true=25),
    )
    release = Release(
        release_date=release_date if faker.boolean(chance_of_getting_true=90) else None,
        announced_at=faker.date_between(end_date=release_date)
        if faker.boolean(chance_of_getting_true=60)
        else None,
    ).set_price(price_tag)

    assert release.price == price_tag.price
    assert release.tax_including == price_tag.tax_including

import random
from typing import List

from faker import Faker

from figure_parser.entities import OrderPeriod, ProductBase, Release


def test_product_base(product: ProductBase, faker: Faker):
    release_infos: List[Release] = []
    for _ in range(random.randint(1, 4)):
        release_infos.append(
            Release(
                release_date=faker.date_object(),
                price=random.randint(1000, 1000000),
                tax_including=faker.boolean(chance_of_getting_true=25),
            )
        )

    p = ProductBase(
        url=faker.url(),
        name=faker.name(),
        series=faker.name(),
        manufacturer=faker.company(),
        category=faker.name(),
        releases=release_infos,
        order_period=OrderPeriod(start=faker.date_time()),
        size=random.randint(1, 1000),
        scale=random.randint(1, 30),
        sculptors=[faker.name() for _ in range(2)],
        paintworks=[faker.name() for _ in range(2)],
        rerelease=faker.boolean(chance_of_getting_true=25),
        adult=faker.boolean(chance_of_getting_true=30),
        copyright=faker.text(max_nb_chars=20),
        releaser=faker.company(),
        distributer=faker.company(),
        jan=faker.jan13(),
        images=[faker.uri() for _ in range(5)],
        thumbnail=faker.uri(),
        og_image=faker.uri(),
    )

    return p

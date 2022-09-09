import pytest
from faker import Faker
from figure_parser.parsers.utils import (
    make_last_element_filler,
    price_parse,
    scale_parse,
    size_parse,
)


def test_price_parser(faker: Faker):
    for _ in range(10):
        ran_num = faker.random_int(max=99999)
        price_text = f"{ran_num:n}"
        price = price_parse(price_text)

        assert price == ran_num

        with pytest.raises(ValueError):
            price_parse("")


def test_size_parser(faker: Faker):
    cm_units = ("cm" "㎝", "ｃｍ")
    mm_units = ("㎜", "mm", "ｍｍ")
    for _ in range(1000):
        units = faker.random_element(elements=(cm_units, mm_units))
        ran_num = faker.random_int()
        unit = faker.random_element(elements=units)
        size_text = f"{ran_num:n}{unit}"

        assert unit in units

        if units == cm_units:
            ran_num = ran_num * 10

        assert size_parse(size_text) == ran_num

    assert not size_parse("100dd")


def test_scale_parser(faker: Faker):
    for _ in range(100):
        denominator = faker.random_digit_not_null()
        assert scale_parse(f"1/{denominator}") == denominator
        assert scale_parse(f"1:{denominator}") == denominator


def test_last_element_filler():
    list_to_fill = [1, 2, 3]
    list_to_fill.extend(make_last_element_filler(list_to_fill, 5))
    assert list_to_fill == [1, 2, 3, 3, 3]

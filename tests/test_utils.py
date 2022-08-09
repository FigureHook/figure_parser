import pytest
from faker import Faker
from figure_parser.utils import price_parse, scale_parse, size_parse


def test_price_parser(faker: Faker):
    for _ in range(10):
        ran_num = faker.random_int(max=99999)
        price_text = f"{ran_num:n}"
        price = price_parse(price_text)

        assert price == ran_num

        with pytest.raises(ValueError):
            price_parse('')


def test_size_parser(faker: Faker):
    cm_units = ('cm' '㎝', 'ｃｍ')
    mm_units = ('㎜', 'mm', 'ｍｍ')
    for _ in range(1000):
        units = faker.random_element(elements=(cm_units, mm_units))
        ran_num = faker.random_int()
        unit = faker.random_element(elements=units)
        size_text = f"{ran_num:n}{unit}"

        assert unit in units

        if units == cm_units:
            ran_num = ran_num * 10

        assert size_parse(size_text) == ran_num


def test_scale_parser(faker: Faker):
    for _ in range(100):
        denominator = faker.random_digit_not_null()
        scale_text = f"1/{denominator}"

        assert scale_parse(scale_text) == denominator

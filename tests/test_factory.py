import pytest
from figure_parser.core.entity import ProductBase
from figure_parser.core.factory.base import GenericProductFactory
from figure_parser.core.parser.base import AbstractProductParser
from figure_parser.exceptions import (DomainInvalid,
                                      DuplicatedDomainRegistration,
                                      UnregisteredDomain)
from pytest_mock import MockerFixture


class MockStrProductFactory(GenericProductFactory[str]):
    pass


class MockStrProductParser(AbstractProductParser[str]):
    @classmethod
    def create_parser(cls, url: str, source: str) -> 'MockStrProductParser':
        return cls()
    pass


def test_factory_initialization(mocker: MockerFixture):
    MockStrProductFactory(
        parser_registrations={
            'foo.net': MockStrProductParser,
            'bar.com': MockStrProductParser
        },
        pipes=[
            (lambda x: x, 10)
        ]
    )


def test_factory_register_parser():
    factory = MockStrProductFactory()
    factory.register_parser(
        'foo.bar', MockStrProductParser
    )

    with pytest.raises(DomainInvalid):
        factory.register_parser(
            'foobar', MockStrProductParser
        )

    with pytest.raises(DuplicatedDomainRegistration):
        factory.register_parser(
            'foo.bar', MockStrProductParser
        )


def test_factory_add_pipe():
    factory = MockStrProductFactory()
    factory.add_pipe(lambda p: p, 1)
    factory.add_pipes(
        (lambda p: p, 1),
        (lambda p: p, 3),
        (lambda p: p, 5)
    )


def test_factory_registration_property():
    factory = MockStrProductFactory()
    factory.register_parser(
        'foo.bar', MockStrProductParser
    )
    assert 'foo.bar' in factory.parser_registration


def test_factory_pipes_properety():
    factory = MockStrProductFactory()
    def func(p): return p
    expected_pipe_order = [
        (func, 1),
        (func, 2)
    ]

    factory.add_pipe(func, 2)
    factory.add_pipe(func, 1)
    assert (func, 1) in factory.pipes
    assert factory.pipes == expected_pipe_order


def test_factory_url_validation():
    factory = MockStrProductFactory()
    factory.register_parser(
        'foo.bar', MockStrProductParser
    )
    domain = factory.validate_url("http://foo.bar/9527")
    assert domain
    assert not factory.validate_url("http://bar.net/114514")


def test_factory_get_parser_by_url():
    factory = MockStrProductFactory()
    factory.register_parser(
        'foo.bar', MockStrProductParser
    )

    assert factory.get_parser_by_url("https://foo.bar/114514") is MockStrProductParser


def test_factory_get_parser_by_domain():
    factory = MockStrProductFactory()
    factory.register_parser(
        'foo.bar', MockStrProductParser
    )

    assert factory.get_parser_by_domain("foo.bar") is MockStrProductParser


def test_factory_product_creation(mocker: MockerFixture, product: ProductBase):
    mocker.patch.object(MockStrProductParser, "__abstractmethods__", new_callable=set)
    mocker.patch.object(MockStrProductParser, "parse_name", new=lambda *a: product.name)
    mocker.patch.object(MockStrProductParser, "parse_series", new=lambda *a: product.series)
    mocker.patch.object(MockStrProductParser, "parse_manufacturer", new=lambda *a: product.manufacturer)
    mocker.patch.object(MockStrProductParser, "parse_category", new=lambda *a: product.category)
    mocker.patch.object(MockStrProductParser, "parse_releases", new=lambda *a: product.releases)
    mocker.patch.object(MockStrProductParser, "parse_order_period", new=lambda *a: product.order_period)
    mocker.patch.object(MockStrProductParser, "parse_size", new=lambda *a: product.size)
    mocker.patch.object(MockStrProductParser, "parse_scale", new=lambda *a: product.scale)
    mocker.patch.object(MockStrProductParser, "parse_sculptors", new=lambda *a: product.sculptors)
    mocker.patch.object(MockStrProductParser, "parse_paintworks", new=lambda *a: product.paintworks)
    mocker.patch.object(MockStrProductParser, "parse_rerelease", new=lambda *a: product.rerelease)
    mocker.patch.object(MockStrProductParser, "parse_adult", new=lambda *a: product.adult)
    mocker.patch.object(MockStrProductParser, "parse_copyright", new=lambda *a: product.copyright)
    mocker.patch.object(MockStrProductParser, "parse_releaser", new=lambda *a: product.releaser)
    mocker.patch.object(MockStrProductParser, "parse_distributer", new=lambda *a: product.distributer)
    mocker.patch.object(MockStrProductParser, "parse_JAN", new=lambda *a: product.jan)
    mocker.patch.object(MockStrProductParser, "parse_images", new=lambda *a: product.images)
    mocker.patch.object(MockStrProductParser, "parse_thumbnail", new=lambda *a: product.thumbnail)
    mocker.patch.object(MockStrProductParser, "parse_og_image", new=lambda *a: product.og_image)

    factory = MockStrProductFactory()
    with pytest.raises(UnregisteredDomain):
        factory.create_product(url="https://foo.bar/114514", source="114514")

    factory.register_parser('foo.bar', MockStrProductParser)
    factory.add_pipe(lambda p: p, 1)
    p = factory.create_product(url="https://foo.bar/114514", source="114514")
    assert type(p) is ProductBase
import pytest
from pytest_mock import MockerFixture

from figure_parser.core.entities import ProductBase
from figure_parser.core.factory_base import GenericProductFactory
from figure_parser.core.parser_base import AbstractProductParser
from figure_parser.exceptions import (
    DomainInvalid,
    DuplicatedDomainRegistration,
    FailedToCreateProduct,
    FailedToProcessProduct,
    UnregisteredDomain,
)


class MockStrProductFactory(GenericProductFactory[str]):
    pass


class MockStrProductParser(AbstractProductParser[str]):
    @classmethod
    def create_parser(cls, url: str, source: str) -> "MockStrProductParser":
        return cls(source=source)

    pass


def test_factory_initialization(mocker: MockerFixture):
    MockStrProductFactory(
        parser_registrations={
            "foo.net": MockStrProductParser,
            "bar.com": MockStrProductParser,
        },
        pipes=[(lambda x: x, 10)],
    )


def test_factory_register_parser():
    factory = MockStrProductFactory()
    factory.register_parser("foo.bar", MockStrProductParser)

    with pytest.raises(DomainInvalid):
        factory.register_parser("foobar", MockStrProductParser)

    with pytest.raises(DuplicatedDomainRegistration):
        factory.register_parser("foo.bar", MockStrProductParser)


def test_factory_add_pipe():
    factory = MockStrProductFactory()
    factory.add_pipe(lambda p: p, 1)
    factory.add_pipes((lambda p: p, 1), (lambda p: p, 3), (lambda p: p, 5))


def test_factory_registration_property():
    factory = MockStrProductFactory()
    factory.register_parser("foo.bar", MockStrProductParser)
    assert "foo.bar" in factory.parser_registration


def test_factory_pipes_properety():
    factory = MockStrProductFactory()

    def func(p):
        return p

    expected_pipe_order = [(func, 1), (func, 2)]

    factory.add_pipe(func, 2)
    factory.add_pipe(func, 1)
    assert (func, 1) in factory.pipes
    assert factory.pipes == expected_pipe_order


def test_factory_url_validation():
    factory = MockStrProductFactory()
    factory.register_parser("foo.bar", MockStrProductParser)
    domain = factory.validate_url("http://foo.bar/9527")
    assert domain
    assert not factory.validate_url("http://bar.net/114514")


def test_factory_get_parser_by_url():
    factory = MockStrProductFactory()
    factory.register_parser("foo.bar", MockStrProductParser)

    assert factory.get_parser_by_url("https://foo.bar/114514") is MockStrProductParser


def test_factory_get_parser_by_domain():
    factory = MockStrProductFactory()
    factory.register_parser("foo.bar", MockStrProductParser)

    assert factory.get_parser_by_domain("foo.bar") is MockStrProductParser


def test_factory_product_creation(mocker: MockerFixture, product: ProductBase):
    mocker.patch.object(MockStrProductParser, "__abstractmethods__", new_callable=set)
    factory = MockStrProductFactory()
    mock_product_create = mocker.MagicMock(return_value=product)
    factory._create_product_by_parser = mock_product_create  # type: ignore

    with pytest.raises(UnregisteredDomain):
        factory.create_product(url="https://foo.bar/114514", source="114514")

    factory.register_parser("foo.bar", MockStrProductParser)  # type: ignore
    factory.add_pipe(lambda p: p, 1)
    p = factory.create_product(url="https://foo.bar/114514", source="114514")
    assert mock_product_create.called
    assert type(p) is ProductBase


def test_factory_product_creation_failed(mocker: MockerFixture, product: ProductBase):
    mocker.patch.object(MockStrProductParser, "__abstractmethods__", new_callable=set)
    factory = MockStrProductFactory()

    factory.register_parser("foo.bar", MockStrProductParser)  # type: ignore
    with pytest.raises(FailedToCreateProduct):
        factory.create_product(url="https://foo.bar/114514", source="114514")


def test_factory__failed_to_process_product_with_pipe(
    mocker: MockerFixture, product: ProductBase
):
    mocker.patch.object(MockStrProductParser, "__abstractmethods__", new_callable=set)
    factory = MockStrProductFactory()
    mock_product_create = mocker.MagicMock(return_value=product)
    factory._create_product_by_parser = mock_product_create  # type: ignore

    factory.register_parser("foo.bar", MockStrProductParser)  # type: ignore

    def bad_process(p: ProductBase) -> ProductBase:
        assert None
        return p

    factory.add_pipe(bad_process, 1)
    with pytest.raises(FailedToProcessProduct):
        factory.create_product(url="https://foo.bar/114514", source="114514")

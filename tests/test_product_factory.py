from dataclasses import is_dataclass

import pytest
from figure_parser.abcs import ProductFactory
from figure_parser.exceptions import UnsupportedDomainError
from figure_parser.factory import (AlterFactory, GSCFactory, NativeFactory,
                                   UniversalFactory)
from figure_parser.product import Product
from pytest_mock import MockerFixture


class TestABCFactory:
    def test_abs_factory(self):
        with pytest.raises(NotImplementedError):
            ProductFactory.create_product("https://example.com")


class FactoryTestBase:
    factory: ProductFactory
    product_url: str

    def test_product_creation(self):
        p = self.factory.create_product(self.product_url)
        assert is_dataclass(p)
        assert isinstance(p, Product)

    def test_product_creation_with_normalize_attrs(self, mocker: MockerFixture):
        nomalization = mocker.patch.object(Product, "normalize_attrs")
        self.factory.create_product(self.product_url, is_normalized=True)
        nomalization.assert_called()

    def test_product_creation_with_speculate_announce_date(self, mocker: MockerFixture):
        speculating = mocker.patch.object(Product, 'speculate_announce_date')
        self.factory.create_product(
            self.product_url, speculate_announce_date=True
        )
        speculating.assert_called()


class TestBrandFactory:
    class TestGSCFactory(FactoryTestBase):
        factory = GSCFactory
        product_url = "https://www.goodsmile.info/ja/product/10753/"

    class TestAlterFactory(FactoryTestBase):
        factory = AlterFactory
        product_url = "https://www.alter-web.jp/products/261/"

    class TestNativeFactory(FactoryTestBase):
        factory = NativeFactory
        product_url = "https://www.native-web.jp/creators/806/"


class TestUniversalFactory:
    def test_factory_detection(self):
        with pytest.raises(ValueError):
            UniversalFactory.detect_factory("htpa:.afdsj")
        google = UniversalFactory.detect_factory("https://www.google.com/")
        assert not google
        g_f = UniversalFactory.detect_factory(
            "https://www.goodsmile.info/ja/product/10753/"
        )
        assert g_f is GSCFactory
        a_f = UniversalFactory.detect_factory(
            "https://www.alter-web.jp/products/261/"
        )
        assert a_f is AlterFactory

    def test_product_creation(self, mocker: MockerFixture):
        mocker.patch.object(ProductFactory, "create_product", return_value=True)
        assert UniversalFactory.create_product(
            "https://www.goodsmile.info/ja/product/10753/"
        )

    def test_provide_unsupported_url(self, mocker: MockerFixture):
        mocker.patch.object(
            UniversalFactory, "detect_factory", return_value=None)
        with pytest.raises(UnsupportedDomainError):
            assert UniversalFactory.create_product(
                "https://sshop.com/product/AVC222/"
            )

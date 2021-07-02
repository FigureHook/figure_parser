from dataclasses import is_dataclass

import pytest
from figure_parser.abcs import ProductFactory
from figure_parser.errors import UnsupportedDomainError
from figure_parser.factory import (AlterFactory, GeneralFactory, GSCFactory,
                                   NativeFactory)
from figure_parser.product import Product
from pytest_mock import MockerFixture


class TestABCFactory:
    def test_abs_factory(self):
        with pytest.raises(NotImplementedError):
            ProductFactory.createProduct("https://example.com")


class FactoryTestBase:
    factory: ProductFactory
    product_url: str

    def test_product_creation(self):
        p = self.factory.createProduct(self.product_url)
        assert is_dataclass(p)
        assert isinstance(p, Product)

    def test_product_creation_with_normalize_attrs(self, mocker: MockerFixture):
        nomalization = mocker.patch.object(Product, "normalize_attrs")
        self.factory.createProduct(self.product_url, is_normalized=True)
        nomalization.assert_called()

    def test_product_creation_with_speculate_announce_date(self, mocker: MockerFixture):
        speculating = mocker.patch.object(Product, 'speculate_announce_date')
        self.factory.createProduct(
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


class TestGeneralFactory:
    def test_factory_detection(self):
        with pytest.raises(ValueError):
            GeneralFactory.detect_factory("htpa:.afdsj")
        google = GeneralFactory.detect_factory("https://www.google.com/")
        assert not google
        g_f = GeneralFactory.detect_factory(
            "https://www.goodsmile.info/ja/product/10753/"
        )
        assert g_f is GSCFactory
        a_f = GeneralFactory.detect_factory(
            "https://www.alter-web.jp/products/261/"
        )
        assert a_f is AlterFactory

    def test_product_creation(self, mocker: MockerFixture):
        mocker.patch.object(ProductFactory, "createProduct", return_value=True)
        assert GeneralFactory.createProduct(
            "https://www.goodsmile.info/ja/product/10753/"
        )

    def test_provide_unsupported_url(self, mocker: MockerFixture):
        mocker.patch.object(
            GeneralFactory, "detect_factory", return_value=None)
        with pytest.raises(UnsupportedDomainError):
            assert GeneralFactory.createProduct(
                "https://sshop.com/product/AVC222/"
            )

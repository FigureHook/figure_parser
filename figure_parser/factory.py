import re
from pprint import pformat
from typing import Dict, Optional, Type
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .abcs import ProductFactory
from .alter import AlterProductParser
from .constants import BrandHost
from .exceptions import UnsupportedDomainError
from .gsc import GSCProductParser
from .native import NativeProductParser
from .product import Product

__all__ = [
    "UniversalFactory",
    "AlterFactory",
    "GSCFactory",
    "NativeFactory",
]


class GSCFactory(ProductFactory):
    """Good smile company product factory"""
    __product_parser__ = GSCProductParser


class AlterFactory(ProductFactory):
    """Alter product factory"""
    __product_parser__ = AlterProductParser


class NativeFactory(ProductFactory):
    """Native product factory"""
    __product_parser__ = NativeProductParser


class UniversalFactory(ProductFactory):
    """Universal Factory

    This factory could detect the factory fit for the given url.
    """
    __supporting_factories__: Dict[BrandHost, Type[ProductFactory]] = {
        BrandHost.ALTER: AlterFactory,
        BrandHost.GSC: GSCFactory,
        BrandHost.NATIVE: NativeFactory,
    }

    @classmethod
    def supporting_factories(cls) -> Dict[BrandHost, Type[ProductFactory]]:
        return cls.__supporting_factories__

    @classmethod
    def create_product(
            cls,
            url: str,
            page: Optional[BeautifulSoup] = None,
            is_normalized: bool = False,
            speculate_announce_date: bool = False
    ) -> Product:
        """
        The method will return the product created by factory based on the hostname of given url.

        :param url: Product url
        :type url: str
        :param page: Product page, defaults to None
        :type page: Optional[BeautifulSoup]
        :param is_normalized: Flag of exectuion of
            :meth:`figure_parser.product.ProductDataProcessMixin.normalize_attrs`,
            defaults to False
        :type is_normalized: bool, optional
        :param speculate_announce_date: Flag of exectuion of
            :meth:`figure_parser.product.ProductDataProcessMixin.speculate_announce_date`,
            defaults to False
        :type speculate_announce_date: bool, optional
        :raises UnsupportedDomainError: If the given url is from unsupported hostname.
        :return: :class:`figure_parser.product.Product` object.
        :rtype: figure_parser.product.Product
        """

        factory = cls.detect_factory(url)
        if not factory:
            supported_hosts = [host.value for host in BrandHost]
            raise UnsupportedDomainError(
                f"Couldn't detect any factory for provided url({url})\nCurrent supported hostnames: {pformat(supported_hosts)}"
            )
        return factory.create_product(url, page, is_normalized, speculate_announce_date)

    @classmethod
    def detect_factory(cls, url: str) -> Optional[Type[ProductFactory]]:
        """
        The method will return a factory based on hostname of given url.

        :param url: Product url given.
        :type url: str
        :raises ValueError: Throw exception when failed to parse hostname from given url.
        :return: Factory fit for given url.
        :rtype: Optional[Type[ProductFactory]]
        """
        netloc = urlparse(url).netloc

        if not netloc:
            raise ValueError(
                f"Failed to parse hostname from provided url({url})"
            )
        if netloc:
            for supporting_hostname, supporting_factory in cls.supporting_factories().items():
                if is_from_this_host(netloc, supporting_hostname):
                    return supporting_factory
        return None


def is_from_this_host(netloc: str, host: str):
    result = re.search(host, netloc)
    return bool(result)

import re
from collections import namedtuple
from pprint import pformat
from typing import Iterable, Optional, Type, Union
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
    "GSCFactory",
    "AlterFactory",
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


SupportingFactory = namedtuple(
    'SupportingFactory',
    ["hostname", "factory"]
)
"""Supporting Factory

Attributes
----------
hostname: str
factory: ProductFactory

"""


class UniversalFactory:
    """Universal Factory

    This factory could detect what the factory fit for the given url.
    """
    __supporting_factories__: Iterable[SupportingFactory] = [
        SupportingFactory(BrandHost.GSC, GSCFactory),
        SupportingFactory(BrandHost.ALTER, AlterFactory),
        SupportingFactory(BrandHost.NATIVE, NativeFactory)
    ]

    @classmethod
    def supporting_factories(cls) -> Iterable[SupportingFactory]:
        return cls.__supporting_factories__

    @classmethod
    def create_product(
            cls,
            url: str,
            page: Optional[BeautifulSoup] = None,
            is_normalized: bool = False,
    ) -> Product:
        """
        The method will return the product created by factory based on the hostname of given url.
        """
        factory = cls.detect_factory(url)
        if not factory:
            supported_hosts = [host.value for host in BrandHost]
            raise UnsupportedDomainError(
                f"Couldn't detect any factory for provided url({url})\nCurrent supported hostnames: {pformat(supported_hosts)}"
            )
        return factory.create_product(url, page, is_normalized)

    @classmethod
    def detect_factory(cls, url: str) -> Union[Type[ProductFactory], None]:
        """
        The method will return a factory based on hostname of giver url.
        """
        netloc = urlparse(url).netloc

        if not netloc:
            raise ValueError(
                f"Failed to parse hostname from provided url({url})"
            )
        if netloc:
            for supporting_factory in cls.supporting_factories():
                if is_from_this_host(netloc, supporting_factory.hostname):
                    return supporting_factory.factory
        return None


def is_from_this_host(netloc: str, host: str):
    result = re.search(host, netloc)
    return bool(result)

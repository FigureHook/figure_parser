import re
from collections import namedtuple
from pprint import pformat
from typing import Optional, Type, Union
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .abcs import ProductFactory
from .alter import AlterProductParser
from .constants import BrandHost
from .errors import UnsupportedDomainError
from .gsc import GSCProductParser
from .native import NativeProductParser

__all__ = [
    "GeneralFactory",
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


class GeneralFactory:
    """General Factory"""
    supporting_factories = (
        SupportingFactory(BrandHost.GSC, GSCFactory),
        SupportingFactory(BrandHost.ALTER, AlterFactory),
        SupportingFactory(BrandHost.NATIVE, NativeFactory)
    )

    @classmethod
    def createProduct(
            cls,
            url: str,
            page: Optional[BeautifulSoup] = None,
            is_normalized: bool = False,
    ):
        """
        The method will return the product created by factory based on the hostname of given url.
        """
        factory = cls.detect_factory(url)
        if not factory:
            supported_hosts = [host.value for host in BrandHost]
            raise UnsupportedDomainError(
                f"Couldn't detect any factory for provided url({url})\nCurrent supported hostnames: {pformat(supported_hosts)}"
            )
        return factory.createProduct(url, page, is_normalized)

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
            for supporting_factory in cls.supporting_factories:
                if is_from_this_host(netloc, supporting_factory.hostname):
                    return supporting_factory.factory
        return None


def is_from_this_host(netloc: str, host: str):
    result = re.search(host, netloc)
    return bool(result)

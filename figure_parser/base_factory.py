from typing import MutableMapping, Optional, Sequence, Tuple, Type
from urllib.parse import urlparse

import validators
from bs4 import BeautifulSoup

from figure_parser.core.entity.product import ProductBase
from figure_parser.core.factory.exceptions import (
    DomainInvalid, DuplicatedDomainRegistration, UnregisteredDomain)
from figure_parser.core.factory.interface import ProductFactoryInterface
from figure_parser.core.parser.interface import ProductParserInterface
from figure_parser.core.usecase.normalize_product import (
    ProductGeneralFieldstNormalizer, ProductWorkerFieldstNormalizer)


def _extract_domain_from_url(url: str) -> str:
    return urlparse(url).netloc


class BaseProductFactory(ProductFactoryInterface[BeautifulSoup, ProductBase]):
    """Base product factory"""
    __parser_registration__: MutableMapping[str, Type[ProductParserInterface[BeautifulSoup]]]

    def __init__(
        self,
        parser_registrations: Optional[Sequence[Tuple[str, Type[ProductParserInterface[BeautifulSoup]]]]] = None
    ) -> None:
        self.__parser_registration__ = {}
        if parser_registrations:
            for domain, parser in parser_registrations:
                self.register_parser(domain=domain, parser=parser)

        super().__init__()

    def create_product(
        self,
        url: str,
        source: BeautifulSoup,
        normalize_general_field: bool = False,
        normalize_workers_filed: bool = False,
        speculate_announce_date: bool = False
    ) -> ProductBase:
        parser_cls = self.get_parser_by_url(url)
        if not parser_cls:
            raise UnregisteredDomain(f"The domain of url is unregistered. (url: '{url}')")

        parser = parser_cls.create_parser(url=url, source=source)
        product = ProductBase(
            url=url,
            name=parser.parse_name(source),
            series=parser.parse_series(source),
            manufacturer=parser.parse_manufacturer(source),
            category=parser.parse_category(source),
            releases=parser.parse_releases(source),
            order_period=parser.parse_order_period(source),
            size=parser.parse_size(source),
            scale=parser.parse_scale(source),
            sculptors=parser.parse_sculptors(source),
            paintworks=parser.parse_paintworks(source),
            rerelease=parser.parse_rerelease(source),
            adult=parser.parse_adult(source),
            copyright=parser.parse_copyright(source),
            releaser=parser.parse_releaser(source),
            distributer=parser.parse_distributer(source),
            jan=parser.parse_JAN(source),
            images=parser.parse_images(source),
            thumbnail=parser.parse_thumbnail(source),
            og_image=parser.parse_og_image(source),
        )

        if normalize_general_field:
            product = ProductGeneralFieldstNormalizer.normalize(product)

        if normalize_workers_filed:
            product = ProductWorkerFieldstNormalizer.normalize(product)

        return product

    def validate_url(self, url: str) -> str:
        """
        If the url is valid, return the matched domain or ''.
        """
        the_domain = _extract_domain_from_url(url)
        for domain in self.__parser_registration__:
            if domain in the_domain:
                return domain
        return ''

    def register_parser(self, domain: str, parser: Type[ProductParserInterface[BeautifulSoup]]):
        domain = domain.strip()
        if domain in self.__parser_registration__:
            raise DuplicatedDomainRegistration(f"{domain} was registered.")

        if not validators.domain(domain):  # type: ignore
            raise DomainInvalid(f"{domain} is invalid.")

        self.__parser_registration__.setdefault(domain, parser)

    def get_parser_by_domain(self, domain: str) -> Optional[Type[ProductParserInterface[BeautifulSoup]]]:
        return self.__parser_registration__.get(domain)

    def get_parser_by_url(self, url: str) -> Optional[Type[ProductParserInterface[BeautifulSoup]]]:
        domain = self.validate_url(url)
        return self.__parser_registration__.get(domain)

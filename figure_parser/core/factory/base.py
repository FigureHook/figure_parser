from abc import ABC
from typing import (Callable, Generic, List, Mapping, MutableMapping, Optional,
                    Tuple, Type, TypeVar)
from urllib.parse import urlparse

import validators
from figure_parser.core.entity import ProductBase
from figure_parser.core.parser.base import AbstractProductParser

from .exceptions import (DomainInvalid, DuplicatedDomainRegistration,
                         FailedToCreateProduct, FailedToProcessProduct,
                         UnregisteredDomain)

__all__ = (
    'GenericProductFactory',
)


Source_T = TypeVar('Source_T')


class GenericProductFactory(Generic[Source_T], ABC):
    _is_pipes_sorted: bool
    _parser_registration: MutableMapping[str, Type[AbstractProductParser[Source_T]]]
    _pipes: List[Tuple[Callable[[ProductBase], ProductBase], int]]

    def __init__(
        self,
        *,
        parser_registrations: Optional[Mapping[str, Type[AbstractProductParser[Source_T]]]] = None,
        pipes: Optional[List[Tuple[Callable[[ProductBase], ProductBase], int]]] = None
    ) -> None:
        self._is_pipes_sorted = False
        self._parser_registration = {}
        self._pipes = pipes if pipes else []

        if parser_registrations:
            for domain, parser in parser_registrations.items():
                self.register_parser(domain=domain, parser=parser)

        self._sort_pipes()

    @property
    def parser_registration(self):
        return self._parser_registration

    @property
    def pipes(self):
        self._sort_pipes()
        return self._pipes

    def _create_product_by_parser(self, url: str, parser: AbstractProductParser[Source_T]) -> ProductBase:
        try:
            return ProductBase(
                url=url,
                name=parser.parse_name(),
                series=parser.parse_series(),
                manufacturer=parser.parse_manufacturer(),
                category=parser.parse_category(),
                releases=parser.parse_releases(),
                order_period=parser.parse_order_period(),
                size=parser.parse_size(),
                scale=parser.parse_scale(),
                sculptors=parser.parse_sculptors(),
                paintworks=parser.parse_paintworks(),
                rerelease=parser.parse_rerelease(),
                adult=parser.parse_adult(),
                copyright=parser.parse_copyright(),
                releaser=parser.parse_releaser(),
                distributer=parser.parse_distributer(),
                jan=parser.parse_JAN(),
                images=parser.parse_images(),
                thumbnail=parser.parse_thumbnail(),
                og_image=parser.parse_og_image(),
            )
        except Exception:
            raise FailedToCreateProduct(f"{parser.__class__} failed to parse the product. (url: {url})")

    def create_product(
        self,
        url: str,
        source: Source_T
    ) -> ProductBase:
        parser_cls = self.get_parser_by_url(url)
        if not parser_cls:
            raise UnregisteredDomain(f"The domain of url is unregistered. (url: '{url}')")

        parser = parser_cls.create_parser(url=url, source=source)
        product = self._create_product_by_parser(url=url, parser=parser)
        product = self.process_product_with_pipes(product)
        return product

    def process_product_with_pipes(self, product: ProductBase) -> ProductBase:
        self._sort_pipes()
        for process, _ in self._pipes:
            try:
                product = process(product)
            except Exception:
                raise FailedToProcessProduct(
                    f"Error occured when {process.__qualname__} is processing the product. (product_url: {product.url})")

        return product

    def validate_url(self, url: str) -> str:
        """
        If the url is valid, return the matched domain or ''.
        """
        the_domain = _extract_domain_from_url(url)
        for domain in self._parser_registration:
            if domain in the_domain:
                return domain
        return ''

    def add_pipe(self, pipe: Callable[[ProductBase], ProductBase], order: int):
        self._pipes.append((pipe, order))
        self._is_pipes_sorted = False

    def add_pipes(self, *pipes: Tuple[Callable[[ProductBase], ProductBase], int]):
        self._pipes.extend(pipes)
        self._is_pipes_sorted = False

    def register_parser(self, domain: str, parser: Type[AbstractProductParser[Source_T]]):
        domain = domain.strip()
        if not validators.domain(domain):  # type: ignore
            raise DomainInvalid(f"{domain} is invalid.")

        if domain in self._parser_registration:
            raise DuplicatedDomainRegistration(f"{domain} was registered.")

        self._parser_registration.setdefault(domain, parser)

    def get_parser_by_domain(self, domain: str) -> Optional[Type[AbstractProductParser[Source_T]]]:
        return self._parser_registration.get(domain)

    def get_parser_by_url(self, url: str) -> Optional[Type[AbstractProductParser[Source_T]]]:
        domain = self.validate_url(url)
        return self._parser_registration.get(domain)

    def _sort_pipes(self):
        if not self._is_pipes_sorted:
            self._pipes.sort(key=lambda p: p[1])
            self._is_pipes_sorted = True


def _extract_domain_from_url(url: str) -> str:
    return urlparse(url).netloc

from abc import ABC, abstractmethod
from typing import Generic, Optional, Type, TypeVar

from figure_parser.core.parser.interface import AbstractProductParser

Source_T = TypeVar('Source_T')
Product_T = TypeVar('Product_T')


class AbstractProductFactory(ABC, Generic[Source_T, Product_T]):
    """Abstract product factory class"""
    @abstractmethod
    def create_product(
        self,
        url: str,
        source: Source_T,
        normalize_general_field: bool = False,
        normalize_workers_filed: bool = False,
        speculate_announce_date: bool = False
    ) -> Product_T:
        raise NotImplementedError

    @abstractmethod
    def validate_url(self, url: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def register_parser(self, domain: str, parser: Type[AbstractProductParser[Source_T]]):
        raise NotImplementedError

    @abstractmethod
    def get_parser_by_domain(self, domain: str) -> Optional[Type[AbstractProductParser[Source_T]]]:
        raise NotImplementedError

    @abstractmethod
    def get_parser_by_url(self, url: str) -> Optional[Type[AbstractProductParser[Source_T]]]:
        raise NotImplementedError

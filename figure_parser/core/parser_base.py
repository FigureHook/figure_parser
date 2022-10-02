from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Type, TypeVar

from .entity import OrderPeriod, Release

Source_T = TypeVar("Source_T")
Parser_T = TypeVar("Parser_T")


__all__ = ("AbstractProductParser",)


class AbstractProductParser(ABC, Generic[Source_T]):
    """Abstract product parser class"""

    _source: Source_T

    def __init__(self, source: Source_T) -> None:
        self._source = source
        super().__init__()

    @property
    def source(self):
        return self._source

    @classmethod
    @abstractmethod
    def create_parser(cls: Type[Parser_T], url: str, source: Source_T) -> Parser_T:
        raise NotImplementedError

    @abstractmethod
    def parse_name(self) -> str:
        """Parse the product name"""
        raise NotImplementedError

    @abstractmethod
    def parse_series(self) -> Optional[str]:
        """Parse the series of product"""
        raise NotImplementedError

    @abstractmethod
    def parse_manufacturer(self) -> str:
        """Parse the manufacturer"""
        raise NotImplementedError

    @abstractmethod
    def parse_category(self) -> str:
        """Parse the category"""
        raise NotImplementedError

    @abstractmethod
    def parse_sculptors(self) -> List[str]:
        """
        This project respect sculptors,
        please try your best to parse all scultpors.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_scale(self) -> Optional[int]:
        """
        The result should be the denominator of scale:

        + 1/8 -> 8
        + 1/7 -> 7
        + Others -> None
        + Non-scale -> None
        """
        raise NotImplementedError

    @abstractmethod
    def parse_size(self) -> Optional[int]:
        """The unit is `mm`"""
        raise NotImplementedError

    @abstractmethod
    def parse_copyright(self) -> Optional[str]:
        """Copyright would be something like this
        `© YYYY foo/bar All Rights Reserved.`
        """
        raise NotImplementedError

    @abstractmethod
    def parse_releaser(self) -> Optional[str]:
        """
        Parse the releaser
        Releaser is `発売元` in Japanese.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_rerelease(self) -> bool:
        """Parse the product is rerelease or not."""
        raise NotImplementedError

    @abstractmethod
    def parse_images(self) -> List[str]:
        """Parse the images of the product."""
        raise NotImplementedError

    @abstractmethod
    def parse_releases(self) -> List[Release]:
        """
        Parse the releases.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_distributer(self) -> Optional[str]:
        """
        Parse the distributer.
        Distributer is `販売元` in Japanese.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_adult(self) -> bool:
        """Is the product adult-only? ( ͡° ͜ʖ ͡°)"""
        raise NotImplementedError

    @abstractmethod
    def parse_order_period(self) -> OrderPeriod:
        """Parse order period"""
        raise NotImplementedError

    @abstractmethod
    def parse_paintworks(self) -> List[str]:
        """
        This project respect paintworks,
        please try your best to parse all of paintworks.

        Because there would be serveral formats used to present paintworks.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_JAN(self) -> Optional[str]:
        """Parse the JAN code of the product."""
        raise NotImplementedError

    @abstractmethod
    def parse_thumbnail(self) -> Optional[str]:
        """
        Parse the thumbnail
        Most of them could be parsed from meta tag.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_og_image(self) -> Optional[str]:
        """Parse open graph image from meta tag."""
        raise NotImplementedError

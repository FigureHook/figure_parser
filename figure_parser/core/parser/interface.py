from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Type, TypeVar

from figure_parser.core.entity import OrderPeriod, Release

Source_T = TypeVar('Source_T')
Parser_T = TypeVar('Parser_T')


__all__ = (
    'ProductParserInterface',
)


class ProductParserInterface(ABC, Generic[Source_T]):
    """Abstract product parser class"""
    @classmethod
    @abstractmethod
    def create_parser(cls: Type[Parser_T], url: str, source: Source_T) -> Parser_T:
        raise NotImplementedError

    @abstractmethod
    def parse_name(self, source: Source_T) -> str:
        """Parse the product name"""
        raise NotImplementedError

    @abstractmethod
    def parse_series(self, source: Source_T) -> Optional[str]:
        """Parse the series of product"""
        raise NotImplementedError

    @abstractmethod
    def parse_manufacturer(self, source: Source_T) -> str:
        """Parse the manufacturer"""
        raise NotImplementedError

    @abstractmethod
    def parse_category(self, source: Source_T) -> str:
        """Parse the category"""
        raise NotImplementedError

    @abstractmethod
    def parse_sculptors(self, source: Source_T) -> List[str]:
        """
        This project respect sculptors,
        please try your best to parse all scultpors.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_scale(self, source: Source_T) -> Optional[int]:
        """
        The result should be the denominator of scale:

        + 1/8 -> 8
        + 1/7 -> 7
        + Others -> None
        + Non-scale -> None
        """
        raise NotImplementedError

    @abstractmethod
    def parse_size(self, source: Source_T) -> Optional[int]:
        """The unit is `mm`"""
        raise NotImplementedError

    @abstractmethod
    def parse_copyright(self, source: Source_T) -> Optional[str]:
        """Copyright would be something like this
        `© YYYY foo/bar All Rights Reserved.`
        """
        raise NotImplementedError

    @abstractmethod
    def parse_releaser(self, source: Source_T) -> Optional[str]:
        """
        Parse the releaser
        Releaser is `発売元` in Japanese.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_rerelease(self, source: Source_T) -> bool:
        """Parse the product is rerelease or not."""
        raise NotImplementedError

    @abstractmethod
    def parse_images(self, source: Source_T) -> List[str]:
        """Parse the images of the product."""
        raise NotImplementedError

    @abstractmethod
    def parse_releases(self, source: Source_T) -> List[Release]:
        """
        Focus on release dates.
        if prices is longer than dates, discard remaining data.

        The method will use `dates` from :meth:`.parse_release_dates`
        and `prices` from :meth:`.parse_prices`.

        If one of them is empty list,
        the empty one would be filled by `None` to fit the other's length.

        If boths are not empty but one of them is shorter,
        the shorter would use last element to fit the other's length.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_distributer(self, source: Source_T) -> Optional[str]:
        """
        Parse the distributer.
        Distributer is `販売元` in Japanese.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_adult(self, source: Source_T) -> bool:
        """Is the product is adult-only? ( ͡° ͜ʖ ͡°)
        """
        raise NotImplementedError

    @abstractmethod
    def parse_order_period(self, source: Source_T) -> OrderPeriod:
        """Parse order period"""
        raise NotImplementedError

    @abstractmethod
    def parse_paintworks(self, source: Source_T) -> List[str]:
        """
        This project respect paintworks,
        please try your best to parse all of paintworks.

        Because there would be serveral formats used to present paintworks.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_JAN(self, source: Source_T) -> Optional[str]:
        """Parse the JAN code of the product."""
        raise NotImplementedError

    @abstractmethod
    def parse_thumbnail(self, source: Source_T) -> Optional[str]:
        """
        Parse the thumbnail
        Most of them could be parsed from meta tag.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_og_image(self, source: Source_T) -> Optional[str]:
        """Parse open graph image from meta tag."""
        raise NotImplementedError

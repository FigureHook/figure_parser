from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

from figure_parser.core.entity import OrderPeriod, Release

Source_T = TypeVar('Source_T')


class AbstractProductParser(ABC, Generic[Source_T]):
    """Abstract product parser class"""
    @staticmethod
    @abstractmethod
    def parse_name(source: Source_T) -> str:
        """Parse the product name"""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse_series(source: Source_T) -> Optional[str]:
        """Parse the series of product"""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse_manufacturer(source: Source_T) -> str:
        """Parse the manufacturer"""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse_category(source: Source_T) -> str:
        """Parse the category"""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse_sculptors(source: Source_T) -> List[str]:
        """
        This project respect sculptors,
        please try your best to parse all scultpors.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse_scale(source: Source_T) -> Optional[int]:
        """
        The result should be the denominator of scale:

        + 1/8 -> 8
        + 1/7 -> 7
        + Others -> None
        + Non-scale -> None
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse_size(source: Source_T) -> Optional[int]:
        """The unit is `mm`"""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse_copyright(source: Source_T) -> Optional[str]:
        """Copyright would be something like this
        `© YYYY foo/bar All Rights Reserved.`
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse_releaser(source: Source_T) -> Optional[str]:
        """
        Parse the releaser
        Releaser is `発売元` in Japanese.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse_rerelease(source: Source_T) -> bool:
        """Parse the product is rerelease or not."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse_images(source: Source_T) -> List[str]:
        """Parse the images of the product."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse_releases(source: Source_T) -> List[Release]:
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

    @staticmethod
    @abstractmethod
    def parse_distributer(source: Source_T) -> Optional[str]:
        """
        Parse the distributer.
        Distributer is `販売元` in Japanese.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse_adult(source: Source_T) -> bool:
        """Is the product is adult-only? ( ͡° ͜ʖ ͡°)
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse_order_period(source: Source_T) -> OrderPeriod:
        """Parse order period"""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse_paintworks(source: Source_T) -> List[str]:
        """
        This project respect paintworks,
        please try your best to parse all of paintworks.

        Because there would be serveral formats used to present paintworks.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse_JAN(source: Source_T) -> Optional[str]:
        """Parse the JAN code of the product."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse_thumbnail(source: Source_T) -> Optional[str]:
        """
        Parse the thumbnail
        Most of them could be parsed from meta tag.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse_og_image(source: Source_T) -> Optional[str]:
        """Parse open graph image from meta tag."""
        raise NotImplementedError

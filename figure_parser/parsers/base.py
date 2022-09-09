from abc import abstractmethod
from datetime import date
from typing import List, Optional

from bs4 import BeautifulSoup
from figure_parser.core.entity import PriceTag, Release
from figure_parser.core.parser.base import AbstractProductParser
from .utils import make_last_element_filler


class AbstractBs4ProductParser(AbstractProductParser[BeautifulSoup]):
    @abstractmethod
    def parse_release_dates(self) -> List[date]:
        raise NotImplementedError

    @abstractmethod
    def parse_prices(self) -> List[PriceTag]:
        raise NotImplementedError

    def parse_releases(self) -> List[Release]:
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
        dates = self.parse_release_dates()
        prices = self.parse_prices()

        dates_len = len(dates)
        prices_len = len(prices)

        if not prices:
            prices = [PriceTag()] * dates_len

        elif not dates:
            dates = [None] * prices_len  # type: ignore

        elif dates_len > prices_len:
            filler = make_last_element_filler(prices, len(dates))
            prices.extend(filler)
        # elif prices_len > dates_len:
        #     filler = make_last_element_filler(dates, len(prices))
        #     dates.extend(filler)

        assert len(dates) <= len(prices)

        return [
            Release(release_date=d, price=p.price, tax_including=p.tax_including)
            for d, p in zip(dates, prices)
        ]

    def parse_thumbnail(self) -> Optional[str]:
        """Parse thumbnail from meta tag."""
        meta_thumbnail = self.source.select_one("meta[name='thumbnail']")
        thumbnail = (
            meta_thumbnail.get_attribute_list("content") if meta_thumbnail else None
        )

        return thumbnail[0] if thumbnail else None

    def parse_og_image(self) -> Optional[str]:
        """Parse open graph image from meta tag."""
        meta_og_image = self.source.select_one("meta[property='og:image']")
        og_image = (
            meta_og_image.get_attribute_list("content") if meta_og_image else None
        )

        return og_image[0] if og_image else None

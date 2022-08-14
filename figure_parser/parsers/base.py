from abc import abstractmethod
from datetime import date
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup
from figure_parser.core.entity import Release
from figure_parser.core.parser.base import AbstractProductParser

from .utils import make_last_element_filler


class AbstractBs4ProductParser(AbstractProductParser[BeautifulSoup]):
    @abstractmethod
    def parse_release_dates(self) -> List[date]:
        raise NotImplementedError

    @abstractmethod
    def parse_prices(self) -> List[Tuple[int, bool]]:
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
            prices = [(None, False)] * dates_len

        elif not dates:
            dates = [None] * prices_len

        elif dates_len > prices_len:
            filler = make_last_element_filler(prices, len(dates))
            prices.extend(filler)
        # elif prices_len > dates_len:
        #     filler = make_last_element_filler(dates, len(prices))
        #     dates.extend(filler)

        assert len(dates) <= len(prices)

        releases: List[Release] = [
            Release(release_date=d, price=p[0], tax_including=p[1])
            for d, p in zip(dates, prices)
        ]

        return releases

    def parse_thumbnail(self) -> Optional[str]:
        """Parse thumbnail from meta tag.
        """
        meta_thumbnail = self.source.select_one("meta[name='thumbnail']")
        thumbnail = meta_thumbnail["content"] if meta_thumbnail else None

        if type(thumbnail) is list:
            if len(thumbnail):
                return thumbnail[0]
        if type(thumbnail) is str:
            return thumbnail

        return None

    def parse_og_image(self) -> Optional[str]:
        """Parse open graph image from meta tag.
        """
        meta_og_image = self.source.select_one("meta[property='og:image']")
        og_image = meta_og_image["content"] if meta_og_image else None

        if type(og_image) is list:
            if len(og_image):
                return og_image[0]
        if type(og_image) is str:
            return og_image

        return None

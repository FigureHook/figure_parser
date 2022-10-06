from datetime import date
from typing import List, Optional

from bs4 import BeautifulSoup

from figure_parser import OrderPeriod, PriceTag
from figure_parser.parsers.base import AbstractBs4ProductParser
from figure_parser.parsers.utils import price_parse, scale_parse, size_parse


class ${name}ProductParser(AbstractBs4ProductParser):
    def __init__(self, source: BeautifulSoup) -> None:
        super().__init__(source)

    @classmethod
    def create_parser(cls, url: str, source: BeautifulSoup):
        raise NotImplementedError

    def parse_name(self) -> str:
        raise NotImplementedError

    def parse_adult(self) -> bool:
        raise NotImplementedError

    def parse_manufacturer(self) -> str:
        raise NotImplementedError

    def parse_category(self) -> str:
        raise NotImplementedError

    def parse_prices(self) -> List[PriceTag]:
        raise NotImplementedError

    def parse_release_dates(self) -> List[date]:
        raise NotImplementedError

    def parse_series(self) -> Optional[str]:
        raise NotImplementedError

    def parse_paintworks(self) -> List[str]:
        raise NotImplementedError

    def parse_sculptors(self) -> List[str]:
        raise NotImplementedError

    def parse_scale(self) -> Optional[int]:
        raise NotImplementedError

    def parse_size(self) -> Optional[int]:
        raise NotImplementedError

    def parse_copyright(self) -> Optional[str]:
        raise NotImplementedError

    def parse_releaser(self) -> Optional[str]:
        raise NotImplementedError

    def parse_distributer(self) -> Optional[str]:
        raise NotImplementedError

    def parse_rerelease(self) -> bool:
        raise NotImplementedError

    def parse_images(self) -> List[str]:
        raise NotImplementedError

    def parse_thumbnail(self) -> Optional[str]:
        raise NotImplementedError

    def parse_order_period(self) -> OrderPeriod:
        raise NotImplementedError

    def parse_JAN(self) -> Optional[str]:
        raise NotImplementedError

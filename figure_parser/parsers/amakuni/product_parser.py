from datetime import date
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup
from figure_parser.entities import OrderPeriod
from figure_parser.parsers.base import AbstractBs4ProductParser
from figure_parser.parsers.utils import price_parse, scale_parse, size_parse


class AmakuniLegacyProductParser(AbstractBs4ProductParser):
    def __init__(self, source: BeautifulSoup):
        super().__init__(source)

    @classmethod
    def create_parser(cls, url: str, source: BeautifulSoup):
        return cls(source=source)

    def parse_name(self) -> str: ...

    def parse_adult(self) -> bool: ...

    def parse_manufacturer(self) -> str: ...

    def parse_category(self) -> str: ...

    def parse_prices(self) -> List[Tuple[int, bool]]: ...

    def parse_release_dates(self) -> List[date]: ...

    def parse_series(self) -> Optional[str]: ...

    def parse_paintworks(self) -> List[str]: ...

    def parse_sculptors(self) -> List[str]: ...

    def parse_scale(self) -> Optional[int]: ...

    def parse_size(self) -> Optional[int]: ...

    def parse_copyright(self) -> Optional[str]: ...

    def parse_releaser(self) -> Optional[str]: ...

    def parse_distributer(self) -> Optional[str]: ...

    def parse_rerelease(self) -> bool: ...

    def parse_images(self) -> List[str]: ...

    def parse_thumbnail(self) -> Optional[str]: ...

    def parse_order_period(self) -> OrderPeriod: ...

    def parse_JAN(self) -> Optional[str]: ...


class AmakuniFormalProductParser(AbstractBs4ProductParser):
    def __init__(self, source: BeautifulSoup):
        super().__init__(source)

    @classmethod
    def create_parser(cls, url: str, source: BeautifulSoup):
        return cls(source=source)

    def parse_name(self) -> str: ...

    def parse_adult(self) -> bool: ...

    def parse_manufacturer(self) -> str: ...

    def parse_category(self) -> str: ...

    def parse_prices(self) -> List[Tuple[int, bool]]: ...

    def parse_release_dates(self) -> List[date]: ...

    def parse_series(self) -> Optional[str]: ...

    def parse_paintworks(self) -> List[str]: ...

    def parse_sculptors(self) -> List[str]: ...

    def parse_scale(self) -> Optional[int]: ...

    def parse_size(self) -> Optional[int]: ...

    def parse_copyright(self) -> Optional[str]: ...

    def parse_releaser(self) -> Optional[str]: ...

    def parse_distributer(self) -> Optional[str]: ...

    def parse_rerelease(self) -> bool: ...

    def parse_images(self) -> List[str]: ...

    def parse_thumbnail(self) -> Optional[str]: ...

    def parse_order_period(self) -> OrderPeriod: ...

    def parse_JAN(self) -> Optional[str]: ...


class AmakuniProductParser(AbstractBs4ProductParser):
    _parser: AbstractBs4ProductParser

    def __init__(self, source: BeautifulSoup, parser: AbstractBs4ProductParser) -> None:
        self._parser = parser
        super().__init__(source)

    @classmethod
    def create_parser(cls, url: str, source: BeautifulSoup):
        if source.select_one(".name_waku"):
            parser = AmakuniFormalProductParser.create_parser(url=url, source=source)
        else:
            parser = AmakuniLegacyProductParser.create_parser(url=url, source=source)
        return cls(source=source, parser=parser)

    def parse_name(self) -> str:
        return self._parser.parse_name()

    def parse_adult(self) -> bool:
        return self._parser.parse_adult()

    def parse_manufacturer(self) -> str:
        return self._parser.parse_manufacturer()

    def parse_category(self) -> str:
        return self._parser.parse_category()

    def parse_prices(self) -> List[Tuple[int, bool]]:
        return self._parser.parse_prices()

    def parse_release_dates(self) -> List[date]:
        return self._parser.parse_release_dates()

    def parse_series(self) -> Optional[str]:
        return self._parser.parse_series()

    def parse_paintworks(self) -> List[str]:
        return self._parser.parse_paintworks()

    def parse_sculptors(self) -> List[str]:
        return self._parser.parse_sculptors()

    def parse_scale(self) -> Optional[int]:
        return self._parser.parse_scale()

    def parse_size(self) -> Optional[int]:
        return self._parser.parse_size()

    def parse_copyright(self) -> Optional[str]:
        return self._parser.parse_copyright()

    def parse_releaser(self) -> Optional[str]:
        return self._parser.parse_releaser()

    def parse_distributer(self) -> Optional[str]:
        return self._parser.parse_distributer()

    def parse_rerelease(self) -> bool:
        return self._parser.parse_rerelease()

    def parse_images(self) -> List[str]:
        return self._parser.parse_images()

    def parse_thumbnail(self) -> Optional[str]:
        return self._parser.parse_thumbnail()

    def parse_order_period(self) -> OrderPeriod:
        return self._parser.parse_order_period()

    def parse_JAN(self) -> Optional[str]:
        return self._parser.parse_JAN()

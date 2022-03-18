import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from hashlib import md5
from typing import Callable, List, Optional, Protocol, Union, overload

from .extension_class import HistoricalReleases, OrderPeriod, Price, Release
from .utils import AsDictable

__all__ = [
    "ProductBase",
    "ProductDataProcessMixin",
    "ProductUtils"
]


@dataclass
class ProductBase(AsDictable):
    __slots__ = (
        "url",
        "name",
        "series",
        "manufacturer",
        "category",
        "price",
        "release_date",
        "release_infos",
        "order_period",
        "size",
        "scale",
        "sculptors",
        "paintworks",
        "rerelease",
        "adult",
        "copyright",
        "releaser",
        "distributer",
        "jan",
        "maker_id",
        "images",
        "thumbnail",
        "og_image"
    )

    url: str
    name: str
    manufacturer: str
    category: str
    rerelease: bool
    adult: bool
    images: List[str]
    sculptors: List[str]
    paintworks: List[str]
    order_period: OrderPeriod
    release_infos: HistoricalReleases[Release]
    release_date: Optional[date]
    price: Optional[Price]
    size: Optional[int]
    scale: Optional[int]
    series: Optional[str]
    copyright: Optional[str]
    releaser: Optional[str]
    distributer: Optional[str]
    jan: Optional[str]
    maker_id: Optional[str]
    thumbnail: Optional[str]
    og_image: Optional[str]

    @property
    def checksum(self):
        """md5 checksum.

        This value could be used to check the data was changed or not.
        """
        checksum_slot = (
            self.name,
            self.manufacturer,
            self.category,
            self.copyright,
            self.price,
            self.size,
            self.rerelease,
            self.adult,
            self.images,
            self.sculptors,
            self.paintworks,
            self.release_date,
            self.order_period,
            self.series,
            self.scale,
            self.releaser,
            self.distributer,
            self.jan,
            self.release_infos,
            self.thumbnail,
            self.og_image
        )

        m = md5()
        for s in checksum_slot:
            m.update(str(s).encode("utf-8"))

        return m.hexdigest()

    def __str__(self):
        return f"[{self.manufacturer}] {self.name} {self.category}"


class ProductProtocol(Protocol):
    order_period: OrderPeriod
    release_infos: HistoricalReleases[Release]


class ProductDataProcessMixin(ProductProtocol):
    __slots__ = ()
    __worker_attrs__ = [
        "paintworks",
        "sculptors"
    ]
    __attrs_to_be_normalized__: List[str] = [
        "name",
        "series",
        "manufacturer",
        "releaser",
        "distributer",
        "paintworks",
        "sculptors"
    ]

    def normalize_attrs(self) -> None:
        """
        normalize string value listed in :attr:`__attrs_to_be_normalized__` from :class:`ProductBase`

        +  full-width (alphabet, notation) to half-width.

        +  remove duplicate spaces.

        +  remove some weird notations.


        normalize attributes :attr:`.paintworks` and :attr:`.sculptors`

        +  replace all brackets to round bracket

        """
        for attr in self.__attrs_to_be_normalized__:
            attr_value = getattr(self, attr)
            if attr_value is not None:
                normalized_attr_value = ProductUtils.normalize_product_attr(
                    attr_value)
                if attr in self.__worker_attrs__:
                    normalized_attr_value = ProductUtils.normalize_worker_attr(
                        normalized_attr_value)
                setattr(self, attr, normalized_attr_value)

    def speculate_announce_date(self) -> None:
        """Speculate announce date from :attr:`~ProductBase.order_period`
        """
        last_release = self.release_infos.last()
        if last_release:
            if last_release.announced_at is None:
                if self.order_period.start:
                    last_release.announced_at = self.order_period.start.date()


class Product(ProductBase, ProductDataProcessMixin):
    __slots__ = ()


class ProductUtils:
    @staticmethod
    def normalize_product_attr(attr_value: Union[str, list[str]]):
        return _normalize(attr_value, _general_normalize)

    @staticmethod
    def normalize_worker_attr(attr_value: Union[str, list[str]]):
        return _normalize(attr_value, _worker_normalize)


NormalizeFunc = Callable[[str], str]


@overload
def _normalize(attr_value: str, normalize_func: NormalizeFunc) -> str: ...
@overload
def _normalize(attr_value: list[str], normalize_func: NormalizeFunc) -> list[str]: ...


def _normalize(attr_value: Union[str, list[str]], normalize_func: NormalizeFunc) -> Union[str, list[str]]:
    if not attr_value:
        return attr_value
    if isinstance(attr_value, str):
        return normalize_func(attr_value)
    if isinstance(attr_value, list):
        return [normalize_func(v) for v in attr_value]

    raise TypeError(
        f"attr_value can't be {type(attr_value)} should be `{str}` or `{list[str]}`. (value: {attr_value}"
    )


def _general_normalize(value: str) -> str:
    # full-width to half-width
    value = unicodedata.normalize("NFKC", value)
    # remove weird spaces
    value = re.sub(r"\s{1,}", " ", value, 0, re.MULTILINE)
    # replace weird quotation
    value = re.sub(r"’", "'", value, 0)

    return value.strip()


def _worker_normalize(value: str) -> str:
    # add space before bracket
    value = value.replace("[", "(")
    value = value.replace("]", ")")
    value = value.replace("{", "(")
    value = value.replace("]", ")")
    value = re.sub(r"(?<![\s])\(", " (", value, 0)

    return value.strip()

from typing import ClassVar, List, Optional

from pydantic import BaseModel

from .order_period import OrderPeriod
from .release import Release

__all__ = ("ProductBase",)


class ProductBase(BaseModel):
    __general_str_fields__: ClassVar[List[str]] = [
        "name",
        "series",
        "manufacturer",
        "releaser",
        "distributer",
        "paintworks",
        "sculptors",
    ]
    __worker_fields__: ClassVar[List[str]] = ["paintworks", "sculptors"]

    url: str
    name: str
    manufacturer: str
    category: str
    rerelease: bool
    adult: bool

    images: List[str]
    sculptors: List[str]
    paintworks: List[str]
    releases: List[Release]

    size: Optional[int]
    scale: Optional[int]
    series: Optional[str]
    copyright: Optional[str]
    releaser: Optional[str]
    distributer: Optional[str]
    jan: Optional[str]
    thumbnail: Optional[str]
    og_image: Optional[str]

    order_period: OrderPeriod

    @classmethod
    def general_str_fields(cls):
        return cls.__general_str_fields__

    @classmethod
    def worker_fields(cls):
        return cls.__worker_fields__

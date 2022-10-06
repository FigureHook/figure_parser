import re
import unicodedata
from typing import Any, Callable, TypeVar, overload

from figure_parser.core.entities import ProductBase

T = TypeVar("T")
NormalizeFunc = Callable[[T], T]


def normalize_general_fields(product_item: ProductBase) -> ProductBase:
    for field in product_item.general_str_fields():
        processed_value = _normalize(getattr(product_item, field), general_normalize)
        setattr(product_item, field, processed_value)
    return product_item


def normalize_worker_fields(product_item: ProductBase) -> ProductBase:
    for field in product_item.worker_fields():
        processed_value = _normalize(getattr(product_item, field), worker_normalize)
        setattr(product_item, field, processed_value)
    return product_item


@overload
def _normalize(value: str, normalize_func: NormalizeFunc) -> str:
    ...


@overload
def _normalize(value: list[str], normalize_func: NormalizeFunc) -> list[str]:
    ...


def _normalize(value: Any, normalize_func: NormalizeFunc[Any]) -> Any:
    if isinstance(value, str):
        return normalize_func(value)
    if isinstance(value, list):
        if all([type(v) is str for v in value]):
            return [normalize_func(v) for v in value]
    return value


def general_normalize(value: str) -> str:
    # full-width to half-width
    value = unicodedata.normalize("NFKC", value)
    # remove weird spaces
    value = re.sub(r"\s{1,}", " ", value, 0, re.MULTILINE)
    # replace weird quotation
    value = re.sub(r"’", "'", value, 0)

    return value.strip()


def worker_normalize(value: str) -> str:
    # add space before bracket
    value = value.replace("[", "(")
    value = value.replace("]", ")")
    value = value.replace("{", "(")
    value = value.replace("]", ")")
    value = re.sub(r"(?<![\s])\(", " (", value, 0)

    return value.strip()

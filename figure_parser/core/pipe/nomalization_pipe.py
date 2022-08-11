import re
import unicodedata
from functools import wraps
from typing import Callable, Union, overload

from figure_parser.core.entity import ProductBase

from .interface import PipeInterface

NormalizeFunc = Callable[[str], str]


class ProductGeneralFieldstNormalizer(PipeInterface[ProductBase]):
    @staticmethod
    def process(product_item: ProductBase) -> ProductBase:
        for field in product_item.general_str_fields():
            value = getattr(product_item, field)
            processed_value = _normalize(getattr(product_item, field), general_normalize)
            setattr(product_item, field, processed_value)
        return product_item


class ProductWorkerFieldstNormalizer(PipeInterface[ProductBase]):
    @staticmethod
    def process(product_item: ProductBase) -> ProductBase:
        for field in product_item.worker_fields():
            value = getattr(product_item, field)
            processed_value = _normalize(getattr(product_item, field), worker_normalize)
            setattr(product_item, field, processed_value)
        return product_item


def _validate_field_value(func):
    @wraps(func)
    def wrapper(value, normalize_func: Callable):
        if type(value) is str:
            return func(value, normalize_func)
        elif type(value) is list:
            if all([type(v) is str for v in value]):
                return func(value, normalize_func)
        elif value is None:
            return None
        else:
            raise TypeError(
                f"value can't be {type(value)} should be `{str}` or `{list[str]}`. (value: {value})"
            )
    return wrapper


@overload
def _normalize(value: str, normalize_func: NormalizeFunc) -> str: ...
@overload
def _normalize(value: list[str], normalize_func: NormalizeFunc) -> list[str]: ...


@_validate_field_value
def _normalize(value: Union[str, list[str], None], normalize_func: NormalizeFunc) -> Union[str, list[str], None]:
    if not value:
        return value
    if isinstance(value, str):
        return normalize_func(value)
    if isinstance(value, list):
        if all([type(v) is str for v in value]):
            return [normalize_func(v) for v in value]


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

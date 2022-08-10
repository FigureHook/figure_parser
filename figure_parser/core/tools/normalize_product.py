import re
import unicodedata
from abc import ABC, abstractmethod
from typing import Any, Callable, Union, overload

from figure_parser.core.entity import ProductBase


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


NormalizeFunc = Callable[[str], str]


@overload
def _normalize(value: str, normalize_func: NormalizeFunc) -> str: ...
@overload
def _normalize(value: list[str], normalize_func: NormalizeFunc) -> list[str]: ...


def _normalize(value: Union[str, list[str]], normalize_func: NormalizeFunc) -> Union[str, list[str]]:
    if not value:
        return value
    if isinstance(value, str):
        return normalize_func(value)
    if isinstance(value, list):
        return [normalize_func(v) for v in value]


def _validate_field_value(value: Any):
    if any((type(value) is str, all(type(v) is str for v in value))):
        return
    raise TypeError(
        f"value can't be {type(value)} should be `{str}` or `{list[str]}`. (value: {value})"
    )


class NormalizerInterface(ABC):
    @staticmethod
    @abstractmethod
    def normalize(product: ProductBase):
        raise NotImplementedError


class ProductGeneralFieldstNormalizer(NormalizerInterface):
    @staticmethod
    def normalize(product: ProductBase):
        for field in product.general_str_fields():
            value = getattr(product, field)
            _validate_field_value(value)
            processed_value = _normalize(getattr(product, field), general_normalize)
            setattr(product, field, processed_value)
        return product


class ProductWorkerFieldstNormalizer(NormalizerInterface):
    @staticmethod
    def normalize(product: ProductBase):
        for field in product.general_str_fields():
            value = getattr(product, field)
            _validate_field_value(value)
            processed_value = _normalize(getattr(product, field), worker_normalize)
            setattr(product, field, processed_value)
        return product

import re
from itertools import repeat
from typing import Iterable, List, TypeVar, Union


T = TypeVar('T')


def make_last_element_filler(target_list: List[T], desired_length: int) -> Iterable[T]:
    original_len = len(target_list)
    last_element = target_list[-1]
    repeat_times = desired_length - original_len
    filler = repeat(last_element, repeat_times)

    return filler


def price_parse(text: str) -> int:
    pattern = r"\d+"
    price_text = ""

    for n in re.findall(pattern, text):
        price_text += n

    if price_text.isdigit():
        price = int(price_text)
    else:
        raise ValueError(f"Can't parse price from `{text}`.")

    return price


def scale_parse(text: str) -> Union[int, None]:
    pattern = r"\d(\/|:)(\d+)"
    scale_text = re.search(pattern, text)
    scale = int(scale_text.group(2)) if scale_text else None
    return scale


def size_parse(text: str) -> Union[int, None]:
    text = text.replace(",", "")
    pattern = r"([\d\.?]+)\s?[㎜|mm|ｍｍ|cm|㎝|ｃｍ]"
    is_cm = any(("cm" in text, "㎝" in text, "ｃｍ" in text))
    size_text = re.search(pattern, text)

    if not size_text:
        return None

    size = size_text.group(1)

    if is_cm:
        return int(float(size) * 10)

    return int(float(size))

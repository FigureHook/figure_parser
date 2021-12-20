import re
from dataclasses import asdict
from functools import wraps
from itertools import repeat
from typing import Iterable, List, TypeVar, Union
from urllib.parse import urlparse

import requests as rq
from bs4 import BeautifulSoup

from .constants import BrandHost
from .exceptions import UnsupportedDomainError

T = TypeVar('T')


class AsDictable:
    def as_dict(self):
        return asdict(self)


def make_last_element_filler(target_list: List[T], desired_length: int) -> Iterable[T]:
    original_len = len(target_list)
    last_element = target_list[-1]
    repeat_times = desired_length - original_len
    filler = repeat(last_element, repeat_times)

    return filler


def get_page(url, headers={}, cookies={}):
    response = rq.get(url, headers=headers, cookies=cookies)
    response.raise_for_status()
    page = BeautifulSoup(response.text, "lxml")
    return page


class RelativeUrl:
    @staticmethod
    def gsc(path):
        return f"https://{BrandHost.GSC}{path}"

    @staticmethod
    def alter(path):
        return f"https://{BrandHost.ALTER}{path}"

    @staticmethod
    def native(path):
        return f"https://{BrandHost.NATIVE}{path}"


def check_domain(init_func):
    @wraps(init_func)
    def checker(parser, url, *args, **kwargs):
        netloc = urlparse(url).netloc

        valid_domain = re.search(parser.__allow_domain__, netloc)
        if netloc and not valid_domain:
            raise UnsupportedDomainError("Invalid domain.")

        elif netloc and valid_domain:
            init_func(parser, url, *args, **kwargs)

    return checker


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
    pattern = r"\d/(\d+)"
    scale_text = re.search(pattern, text)
    scale = int(scale_text.group(1)) if scale_text else None
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

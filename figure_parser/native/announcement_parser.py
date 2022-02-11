import re
from typing import List

from bs4 import BeautifulSoup

from ..constants import NativeCategory
from ..utils import RelativeUrl, get_page

# FIXME: lack of test


def get_max_page_count(category_page: BeautifulSoup):
    pattern = r"\d\ / (?P<total>\d)"
    count_ele = category_page.select_one('.pages')
    assert count_ele, "Can't get native page counting element."
    count_text = count_ele.text.strip()
    result = re.search(pattern, count_text)
    assert result, "Can't get native announcement page counting."
    total = result.groupdict().get('total')
    if total:
        if total.isdigit():
            return int(total)

    raise ValueError


class NativeAnnouncementParser:
    def __init__(self, category: NativeCategory) -> None:
        self.category = category
        self.pages_count = self._get_category_pages_count()

    def _get_category_pages_count(self):
        url = RelativeUrl.native(
            f"/{self.category}/"
        )
        page = get_page(url)
        return get_max_page_count(page)

    def _get_page_items(self, page_num):
        announcement_url = RelativeUrl.native(
            f"/{self.category}/page/{page_num}/"
        )
        page = get_page(announcement_url)
        return NativeAnnouncementLinkExtractor.extract(page)

    def __iter__(self):
        for page in range(1, self.pages_count + 1):
            items = self._get_page_items(page)
            yield items


class NativeAnnouncementLinkExtractor:
    @staticmethod
    def extract(page: BeautifulSoup) -> List[str]:
        item_selector = 'section > a'
        items = page.select(item_selector)
        return [item['href'] for item in items]

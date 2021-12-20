from typing import List, Optional

from bs4 import BeautifulSoup

from ..abcs import YearlyAnnouncement
from ..utils import RelativeUrl, get_page


class GSCYearlyAnnouncement(YearlyAnnouncement):
    def __init__(
        self,
        category: str,
        start: int = 2006,
        end: Optional[int] = None,
        lang: str = "ja"
    ) -> None:
        super().__init__(start, end)
        self.category = category
        self.lang = lang

    def get_yearly_items(self, year: int) -> List[str]:
        url = RelativeUrl.gsc(f"/{self.lang}/products/category/{self.category}/announced/{year}")
        page = get_page(url)
        return GSCAnnouncementLinkExtractor.extract(page)


class GSCAnnouncementLinkExtractor:
    @staticmethod
    def extract(page: BeautifulSoup) -> List[str]:
        item_urls = []
        item_selector = ".hitItem:not(.shimeproduct) > .hitBox > a"
        items = page.select(item_selector)

        for item in items:
            if 'href' in item.attrs:
                item_urls.append([item.get('href')])

        return item_urls

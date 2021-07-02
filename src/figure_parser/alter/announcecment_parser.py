from datetime import datetime
from typing import Optional, Union

from bs4 import BeautifulSoup

from ..abcs import YearlyAnnouncement
from ..constants import AlterCategory
from ..utils import RelativeUrl, get_page


class AlterYearlyAnnouncement(YearlyAnnouncement):
    def __init__(
        self,
        category: AlterCategory = AlterCategory.ALL,
        start: int = 2005,
        end: Optional[int] = None
    ):
        if not end:
            newest_year = fetch_alter_newest_year()
            end = newest_year or datetime.now().year

        super().__init__(start, end)
        self._category = category

    def get_yearly_items(self, year: int):
        url = RelativeUrl.alter(f"/{self._category}/?yy={year}")
        page = get_page(url)
        return AlterAnnouncementLinkExtractor.extract(page)


class AlterAnnouncementLinkExtractor:
    @staticmethod
    def extract(page: BeautifulSoup):
        item_selector = "figure > a"
        items = page.select(item_selector)
        return [RelativeUrl.alter(item["href"]) for item in items]


def fetch_alter_newest_year() -> Union[int, None]:
    page = get_page("http://www.alter-web.jp/products/")
    year_selection = page.select_one("#changeY")
    year_options = year_selection.select("option")
    years = []
    for option in year_options:
        year: str = option["value"]
        if year.isdigit():
            years.append(int(year))

    if years:
        return max(years)
    return None

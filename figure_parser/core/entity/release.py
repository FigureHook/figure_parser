from datetime import date
from typing import NamedTuple, Optional

from pydantic import BaseModel, NonNegativeInt

__all__ = (
    'Release',
    'PriceTag'
)


class PriceTag(NamedTuple):
    price: Optional[int] = None
    tax_including: bool = False


class Release(BaseModel):
    """
    :param release_date: The product release date.
    :type release_date: datetime.date
    :param price: The product price for the release.
    :type price: Price
    :param announced_at: The announcing date of the release.
    :type announced_at: datetime.date
    """
    release_date: Optional[date] = None
    """The product release date."""
    price: Optional[NonNegativeInt] = None
    """The product price for the release."""
    tax_including: bool = False
    """Annotate the price is including tax or not."""
    announced_at: Optional[date] = None
    """The announcing date of the release."""

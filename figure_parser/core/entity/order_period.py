from datetime import datetime
from typing import Optional

from pydantic import BaseModel, root_validator

__all__ = (
    'OrderPeriod',
)


class OrderPeriod(BaseModel):
    """
    A dataclass object allowS user to check the product is available for per-ordering or not.

    :param start: The starting time of pre-order.
    :type start: datetime.datetime
    :param end: The ending time of pre-order.
    :type end: datetime.datetime

    :raises OrderPeriodError: If :attr:`start` is later than :attr:`end` when initialization.
    """

    start: Optional[datetime] = None
    """The start-time of pre-order."""
    end: Optional[datetime] = None
    """The end-time of pre-order."""

    @root_validator(pre=True)
    def valid_order_period(cls, values: dict):
        start, end = values.get('start'), values.get('end')
        if start and end:
            assert start < end, f"start_datetime {start} shouldn't later than end_datetime {end}."
        return values

    @property
    def is_available(self):
        """
        Is available for pre-ordering for current time.

        :returns: Is available for pre-ordering for current time.
        :rtype: bool
        """
        return self._is_available(datetime.now())

    def is_available_at(self, the_time: datetime) -> bool:
        """
        Convenient method for checking availability of pre-ordering for assigned time.

        :param the_time: The time that is used to check availability of pre-ordering.
        :type datetime:
        """
        return self._is_available(the_time)

    def __contains__(self, the_time: datetime) -> bool:
        return self._is_available(the_time)

    def _is_available(self, the_time: datetime) -> bool:
        if self.start and self.end:
            return self.start < the_time < self.end

        if self.start and not self.end:
            return self.start < the_time

        if not self.start and self.end:
            return the_time < self.end

        return False

    def __bool__(self):
        return any((self.start, self.end))

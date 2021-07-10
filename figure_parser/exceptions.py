class FigureParserException(Exception):
    """Base exception for figure_parser
    """
    pass


class OrderPeriodError(FigureParserException):
    """Exception which is thrown when :class:`OrderPeriod` :attr:`.start` is smaller than :attr:`.end`
    """
    pass


class UnsupportedDomainError(FigureParserException):
    """Exception which is thrown when the given url is from a unsupported domain.
    """
    pass

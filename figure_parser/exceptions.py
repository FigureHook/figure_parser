class FigureParserException(Exception):
    """
    Base exception for figure_parser
    """
    pass


class OrderPeriodError(FigureParserException):
    """
    Exception which is thrown by :class:`figure_parser.extension_class.OrderPeriod`
    """
    pass


class UnsupportedDomainError(FigureParserException):
    """
    Exception which is thrown when the given url is from a unsupported domain.
    """
    pass


class UnreliableParserError(FigureParserException):
    """
    Thrown when the parser might be unreliable.
    """

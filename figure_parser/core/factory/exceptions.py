from figure_parser.core.entity.exceptions import FigureParserException


class DomainException(FigureParserException):
    pass


class DuplicatedDomainRegistration(DomainException):
    """
    Exception which is thrown when register duplicated domain in :class:`figure_parser.core.factory.base_factory.BaseProductFactory.
    """
    pass


class DomainInvalid(DomainException):
    """
    Exception which is thrown when the domain is invalid.
    """


class UnregisteredDomain(DomainException):
    """
    Exception which is thrown when the given url is from a unsupported domain.
    """
    pass


class FailedToCreateProduct(FigureParserException):
    """
    Exception thrown when faild to create product.
    """


class FailedToProcessProduct(FigureParserException):
    """
    Exception thrown when faild to process product with pipe.
    """

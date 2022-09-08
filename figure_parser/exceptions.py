# flake8: noqa
from .core.entity.exceptions import FigureParserException
from .core.factory.exceptions import (DomainException, DomainInvalid,
                                      DuplicatedDomainRegistration,
                                      FailedToCreateProduct,
                                      FailedToProcessProduct,
                                      UnregisteredDomain)
from .core.parser.exceptions import ParserInitializationFailed

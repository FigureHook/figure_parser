from bs4 import BeautifulSoup

from figure_parser.core.factory.base import GenericProductFactory

from .parsers import AlterProductParser, GSCProductParser, NativeProductParser
from .pipes import (normalize_general_fields, normalize_worker_fields,
                    sort_releases)


class Bs4ProductFactory(GenericProductFactory[BeautifulSoup]):
    pass


class GeneralBs4ProductFactory(Bs4ProductFactory):
    @classmethod
    def create_factory(cls):
        factory = cls()
        factory.register_parser('goodsmile.info', GSCProductParser)
        factory.register_parser('alter-web.jp', AlterProductParser)
        factory.register_parser('native-web.jp', NativeProductParser)
        factory.add_pipes(
            (normalize_general_fields, 1),
            (normalize_worker_fields, 2),
            (sort_releases, 3)
        )
        return factory

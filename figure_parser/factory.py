from bs4 import BeautifulSoup

from figure_parser.core.factory.base import GenericProductFactory


class Bs4ProductFactory(GenericProductFactory[BeautifulSoup]):
    pass

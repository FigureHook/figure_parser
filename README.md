[![Pypi](https://img.shields.io/pypi/pyversions/figure_parser.svg?style=flat-square)](https://pypi.org/project/figure_parser/)
[![Pypi](https://img.shields.io/pypi/v/figure_parser.svg?style=flat-square)](https://pypi.org/project/figure_parser/)
[![CI](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2FFigureHook%2Ffigure_parser%2Fbadge%3Fref%3Dmain&style=flat-square)](https://actions-badge.atrox.dev/FigureHook/figure_parser/goto?ref=main)
[![Coverage](https://img.shields.io/coveralls/github/FigureHook/figure_parser?style=flat-square)](https://coveralls.io/github/FigureHook/figure_parser)

# Figure Parser
A web parser focus on parsing product information on Japan ACG figure sites.

[Supporting site list](SUPPORT_SITES.md)

## Install
```bash
pip install figure_parser
```

## Usage
```py
from pprint import pprint

import requests as rq
from bs4 import BeautifulSoup

from figure_parser.exceptions import FigureParserException
from figure_parser.factories import GeneralBs4ProductFactory


factory = GeneralBs4ProductFactory.create_factory()

resp = rq.get(url)
try:
    product = factory.create_product(resp.url, BeautifulSoup(resp.content, 'lxml'))
    pprint(product.dict())
except FigureParserException as e:
    print(e)
```
```sh
{'adult': False,
 'category': 'フィギュア',
 'copyright': '© SUNBORN Network Technology Co., Ltd. © SUNBORN Japan Co., '
              'Ltd.',
 'distributer': 'グッドスマイルカンパニー',
 'images': ['https://images.goodsmile.info/cgm/images/product/20210521/11246/85011/large/346a0402da0a835b6969105e77c7bf7f.jpg',
            'https://images.goodsmile.info/cgm/images/product/20210521/11246/85012/large/e1fb5ad64d58498477611082c7219759.jpg',
            'https://images.goodsmile.info/cgm/images/product/20210521/11246/85013/large/cad59d379e0ac60b8d386eee93253502.jpg',
            'https://images.goodsmile.info/cgm/images/product/20210521/11246/85014/large/4e4957b4783cc9b8cc6e6101aaf346b3.jpg',
            'https://images.goodsmile.info/cgm/images/product/20210521/11246/85015/large/9bf879603be71259f2d673a84d1b3b2a.jpg',
            'https://images.goodsmile.info/cgm/images/product/20210521/11246/85016/large/f464915a47d744441a0574e97016e8d0.jpg',
            'https://images.goodsmile.info/cgm/images/product/20210521/11246/85017/large/f8ae4c2ebfb05d3b3c2c9a427d9dd9af.jpg',
            'https://images.goodsmile.info/cgm/images/product/20210521/11246/85018/large/d03ebd90e1fd832e5909deba3c78432c.jpg',
            'https://images.goodsmile.info/cgm/images/product/20210521/11246/85019/large/1a4421435c14c53857d5125c0f3da4aa.jpg',
            'https://images.goodsmile.info/cgm/images/product/20210521/11246/85020/large/eede36da01b9ab86ba35a3e5f30a8394.jpg',
            'https://images.goodsmile.info/cgm/images/product/20210521/11246/85021/large/8afccdd56243497830857ec612374266.jpg'],
 'jan': None,
 'manufacturer': 'Phat!',
 'name': 'PA-15 高校胸キュン物語',
 'og_image': 'http://images.goodsmile.info/cgm/images/product/20210521/11246/85023/medium/b1a1a49e9bb72ebd95670ca757e22735.jpg',
 'order_period': {'end': datetime.datetime(2021, 7, 7, 21, 0),
                  'start': datetime.datetime(2021, 5, 27, 12, 0)},
 'paintworks': ['緋色 (scarlet)'],
 'releaser': 'ファット・カンパニー',
 'releases': [{'announced_at': None,
               'price': 19800,
               'release_date': datetime.date(2022, 12, 1),
               'tax_including': True}],
 'rerelease': False,
 'scale': 7,
 'sculptors': ['Phat!'],
 'series': 'ドールズフロントライン',
 'size': 280,
 'thumbnail': 'http://images.goodsmile.info/cgm/images/product/20210521/11246/85023/medium/b1a1a49e9bb72ebd95670ca757e22735.jpg',
 'url': 'https://www.goodsmile.info/ja/product/11246/PA+15+%E9%AB%98%E6%A0%A1%E8%83%B8%E3%82%AD%E3%83%A5%E3%83%B3%E7%89%A9%E8%AA%9E.html'}
```

# Development

This project is using [poetry](https://python-poetry.org/) as package manager.

Install dependencies
```sh
poetry install
```

Use virtualenv
```sh
poetry shell
```

Install pre-commit
```
pre-commit install
```

Generate new parser (the name should be in snake case)
```sh
python cli.py generate new_site
```
After generating the new site, the test data can be found [here].(tests/test_pasers/product_case)

Run the test and coverage
```sh
tox
coverage combine
coverage report -m
```

Type check
```sh
mypy
```

Lint the code
```sh
isort -e .
black .
```

If you add or update dependencies
```sh
poetry export --without-hashes --dev -f requirements.txt --output requirements.txt
```

If you use `Makefile`, it provides several useful command.
```
clean-test-cache     Clean cache of test.
cov-report           Show the coverage of tests.
format               Format the code.
freeze               Export the requirements.txt file.
help                 Show this help message.
install              Install requirements of project.
lint                 Lint the code.
test                 Run the tests.
type-check           Type check with mypy.
```

from setuptools import find_packages, setup

setup(
    name="figure_parser",
    version="0.0.1",
    author="Elton H.Y. Chou",
    author_email="plscd748@gmail.com",
    description="Parser for figure",
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.6",
    include_package_data=True,
    package_data={
        "": ["**/*.yml"]
    },
    install_requires=[
        "beautifulsoup4>=4.9.3",
        "lxml>=4.6.3",
        "requests>=2.25.1",
        "PyYAML>=5.4.1",
        "feedparser>=6.0.2",
        "aiohttp",
    ]
)

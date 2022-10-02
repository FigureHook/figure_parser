import os
from pathlib import Path
from shutil import rmtree

import click
import inflection
from mako.template import Template

Here = Path(os.path.dirname(__file__)).resolve()
Parser_Test_Dir = Here.joinpath("tests", "test_parsers")
Parser_Test_Case_Dir = Parser_Test_Dir.joinpath("product_case")
Parser_Dir = Here.joinpath("figure_parser", "parsers")
Template_Dir = Here.joinpath("templates")

parser_template = Template(filename=str(Template_Dir.joinpath("product_parser.mako")))
parser_test_template = Template(
    filename=str(Template_Dir.joinpath("product_parser_test.mako"))
)
test_case_template = Template(filename=str(Template_Dir.joinpath("test_case.mako")))


class Target:
    def __init__(self, name: str) -> None:
        self.snake_name = inflection.underscore(name)
        self.camel_name = inflection.camelize(name)

    @property
    def parser_dir(self):
        return Parser_Dir.joinpath(self.snake_name)

    @property
    def parser_file(self):
        return self.parser_dir.joinpath("product_parser.py")

    @property
    def test_case_file(self):
        return Parser_Test_Case_Dir.joinpath(f"{self.snake_name}.yml")

    @property
    def parser_test_file(self):
        return Parser_Test_Dir.joinpath(f"test_{self.snake_name}_product_parser.py")

    @staticmethod
    def _rm(path: Path):
        if not path.exists():
            return
        click.echo(f"Remove ({str(path)})")
        if os.path.isdir(path):
            rmtree(path)
        else:
            os.remove(path)

    @staticmethod
    def generate_file(
        path: Path, template: Template, overwrite: bool = False, **kwargs
    ):
        if path.exists() and not overwrite:
            click.echo(f"File existed. Skip generating. ({str(path)})")
        else:
            click.echo(f"{'Overwriting' if overwrite else 'Generating'} ({str(path)})")
            with open(path, "w", encoding="utf-8") as f:
                f.write(str(template.render(**kwargs)))

    def generate(self):
        self.parser_dir.mkdir(exist_ok=True)
        self.generate_file(
            self.parser_file,
            parser_template,
            name=self.camel_name,
        )
        self.generate_file(
            self.parser_test_file,
            parser_test_template,
            name=self.camel_name,
            test_case_name=self.snake_name,
        )
        self.generate_file(
            self.test_case_file,
            test_case_template,
            name=self.camel_name,
        )
        self.post_process()

    def remove(self):
        self._rm(self.parser_dir)
        self._rm(self.parser_test_file)
        self._rm(self.test_case_file)
        self.post_process()

    def post_process(self):
        site_parsers = []
        for site_name, _ in get_existing_sites():
            site_parsers.append(
                (site_name, inflection.camelize(site_name) + "ProductParser")
            )
        self.generate_file(
            Parser_Dir.joinpath("__init__.py"),
            template=Template(filename=str(Template_Dir.joinpath("parsers_init.mako"))),
            overwrite=True,
            site_parsers=site_parsers,
        )


def get_existing_sites():
    return sorted(
        [
            (dir, Parser_Dir.joinpath(dir))
            for dir in os.listdir(Parser_Dir)
            if os.path.isdir(Parser_Dir.joinpath(dir))
            and not dir.startswith("_")
            and not dir.startswith(".")
        ]
    )


@click.group()
def main():
    pass


@main.command("list")
def _list():
    """List existing sites."""
    sites = get_existing_sites()
    for site, path in sites:
        click.echo(f"{site}\t({path})")


@main.command()
@click.argument("name")
def generate(name):
    "Generate new parser files with NAME (snakecase)"
    target = Target(name=name)
    target.generate()


@main.command()
@click.argument("name")
def remove(name):
    "Remove parser files with NAME (snakecase)"
    target = Target(name=name)
    target.remove()


if __name__ == "__main__":
    main()

import os
from pathlib import Path

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


def generate_file(name: str, path: Path, template: Template, **kwargs):
    click.echo(f"Generating '{str(path)}' ...")
    with open(path, "w", encoding="utf-8") as f:
        f.write(str(template.render(name=name, **kwargs)))


@click.group()
def main():
    pass


@main.command()
@click.argument("name")
def generate(name):
    "Generate new parser files with NAME (camelcase)"
    snake_case_name = inflection.underscore(name)
    new_parser_dir = Parser_Dir.joinpath(snake_case_name)
    new_parser_file = new_parser_dir.joinpath("product_parser.py")
    new_parser_test_file = Parser_Test_Dir.joinpath(
        f"test_{snake_case_name}_product_parser.py"
    )
    new_test_case_file = Parser_Test_Case_Dir.joinpath(f"{snake_case_name}.yml")

    paths = (new_parser_dir, new_parser_file, new_parser_test_file, new_test_case_file)
    exists: list[bool] = []
    for path in paths:
        is_exist = path.exists()
        if is_exist:
            click.echo(f"'{str(path)}' is existed.")
        exists.append(is_exist)

    if not all(exists):
        new_parser_dir.mkdir()
        generate_file(name, new_parser_file, parser_template)
        generate_file(
            name,
            new_parser_test_file,
            parser_test_template,
            test_case_name=snake_case_name,
        )
        generate_file(name, new_test_case_file, test_case_template)


if __name__ == "__main__":
    main()

.PHONY: help
.SILENT:

help: # Show this help message.
	@grep -E '^[a-zA-Z_-]+:.*?# .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?# "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: # Install requirements of project.
	poetry install

lint: # Lint the code.
	flake8

type-check: # Type check with mypy.
	mypy

format: # Format the code.
	isort -e .; \
	black .

test: # Run the tests.
	coverage run -m pytest

cov-report: test # Show the coverage of tests.
	coverage combine; \
	coverage report -m

freeze: # Export the requirements.txt file.
	poetry export --without-hashes --dev -f requirements.txt --output requirements.txt

clean-test-cache: # Clean cache of test.
	rm tests/test_parsers/product_case/html/*.html && rm -r .pytest_cache

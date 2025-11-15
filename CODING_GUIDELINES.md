# Coding Guidelines

This document outlines the coding guidelines for the Reviewcheck project. Please follow these guidelines when contributing to the project.

## Code Formatting

This project uses [Black](https://github.com/psf/black) for code formatting. All code should be formatted with Black before committing.

We also use [isort](https://pycqa.github.io/isort/) to sort our imports. Please ensure your imports are sorted correctly. The isort profile is configured in `pyproject.toml` to be compatible with Black.

## Linting

We use [flake8](https://flake8.pycqa.org/en/latest/) for linting. Please ensure your code passes all flake8 checks before submitting a pull request.

## Type Hinting

We use [mypy](http://mypy-lang.org/) for static type checking. All new code should include type hints.

## Docstrings

Docstrings should follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#3.8-comments-and-docstrings).

## Testing

All new features should be accompanied by tests. Tests are written using the [pytest](https://docs.pytest.org/en/stable/) framework.

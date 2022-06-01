RUN := poetry run
BUILD := poetry build
TARGET := reviewcheck

BLACK := ${RUN} black
FLAKE8 := ${RUN} flake8
ISORT := ${RUN} isort
MYPY := ${RUN} mypy
PYTEST := ${RUN} pytest
PYTHON := ${RUN} python3

all: run

build:
	${BUILD}

run:
	${PYTHON} -m ${TARGET}

lint:
	${BLACK} --check --diff --color .
	${FLAKE8}
	${ISORT} --color --check-only --diff .
	${MYPY} --strict .

format:
	${ISORT} .
	${BLACK} .

test:
	${PYTEST} tests/

.PHONY: all lint format run test

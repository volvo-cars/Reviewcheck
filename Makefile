RUN := poetry run
TARGET := reviewcheck

BLACK := ${RUN} black
FLAKE8 := ${RUN} flake8
ISORT := ${RUN} isort
PYTEST := ${RUN} pytest
PYTHON := ${RUN} python3

all: run

run:
	${PYTHON} -m ${TARGET}

lint:
	${FLAKE8}
	${ISORT} --color --check-only --diff .
	${BLACK} --check --diff --color .

format:
	${ISORT} .
	${BLACK} .

test:
	${PYTEST} tests/

.PHONY: all lint format run test

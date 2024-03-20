include .env
SHELL := /bin/bash
SOURCE_FOLDERS=proceedings_curation tests
BLACK_ARGS=--line-length 120 --target-version py311 --skip-string-normalization -q
MYPY_ARGS=--show-column-numbers --no-error-summary --python-version 3.11
ISORT_ARGS=--profile black --float-to-top --line-length 120 --py auto

black:
	@poetry run black $(BLACK_ARGS) $(SOURCE_FOLDERS)
.PHONY: black

isort:
	@poetry run isort $(ISORT_ARGS) $(SOURCE_FOLDERS)
.PHONY: isort

tidy: isort black
.PHONY: tidy

pylint:
	@poetry run pylint $(SOURCE_FOLDERS)
.PHONY: pylint

notes:
	@poetry run pylint --notes=FIXME,XXX,TODO --disable=all --enable=W0511 -f colorized $(SOURCE_FOLDERS)
.PHONY: notes

mypy:
	@poetry run mypy $(MYPY_ARGS) $(SOURCE_FOLDERS) || true
.PHONY: mypy

lint: tidy pylint
.PHONY: lint

typing: lint mypy
.PHONY: typing

create_metadata:
	@poetry run python proceedings_curation/scripts/create_metadata_index.py $(PROCEEDINGS_INDEX) $(PROCEEDINGS_METADATA) $(METADATA_INDEX)
.PHONY: create_metadata

create_metadata_csv:
	@poetry run python proceedings_curation/scripts/create_metadata_index.py $(PROCEEDINGS_INDEX) $(PROCEEDINGS_METADATA) $(METADATA_INDEX_CSV)
.PHONY: create_metadata_csv

extract_meetings: export PYTHONPATH=.
extract_meetings:
	@poetry run python proceedings_curation/scripts/extract_meetings.py $(METADATA_INDEX) $(PROCEEDINGS_PDF_CORPUS_PATH) $(PROCEEDINGS_MEETINGS_CORPUS_PATH)
.PHONY: extract_meetings

create_dataset: export PYTHONPATH=.
create_dataset:
	@poetry run python proceedings_curation/scripts/create_jsonl_dataset.py $(METADATA_INDEX_CSV) $(PROCEEDINGS_MEETINGS_CORPUS_PATH) $(PROCEEDINGS_DATASET_PATH)
.PHONY: create_dataset

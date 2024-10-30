include .env
SHELL := /bin/bash
SOURCE_FOLDERS=proceedings_curation tests
PACKAGE_FOLDER=proceedings_curation
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

mypy-strict:
	@poetry run mypy $(MYPY_ARGS) --strict $(SOURCE_FOLDERS) || true
.PHONY: mypy-strict

lint: tidy pylint
.PHONY: lint

typing: lint mypy
.PHONY: typing

typing-strict: lint mypy-strict
.PHONY: typing-strict

data: nltk_data
.PHONY: data

test:
	@poetry run pytest tests/
.PHONY: test

retest:
	@poetry run pytest --last-failed tests/
.PHONY: retest

coverage:
	@poetry run pytest --cov=$(PACKAGE_FOLDER) --cov-report=html tests/

clean:
	@rm -rf .coverage htmlcov
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '*pytest_cache*' -exec rm -rf {} +
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@rm -rf tests/output
.PHONY: clean

nltk_data:
	@mkdir -p $(NLTK_DATA)
	@poetry run python -c "import nltk; nltk.download('punkt', download_dir='$(NLTK_DATA)'); nltk.download('punkt_tab', download_dir='$(NLTK_DATA)')"
.PHONY: nltk_data

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
	@poetry run python proceedings_curation/scripts/create_jsonl_dataset.py $(METADATA_INDEX_CSV) $(PROCEEDINGS_MEETINGS_CORPUS_PATH) $(PROCEEDINGS_DATASET_PATH) dataset
.PHONY: create_dataset

create_dataset_sample: export PYTHONPATH=.
create_dataset_sample: nltk_data
	@poetry run python proceedings_curation/scripts/create_jsonl_dataset.py $(METADATA_INDEX_CSV) $(PROCEEDINGS_MEETINGS_CORPUS_PATH) $(PROCEEDINGS_DATASET_PATH) dataset_sample 100 10 --seed 42
.PHONY: create_dataset_sample


extract_english_corpus: export PYTHONPATH=.
extract_english_corpus:
	@poetry run python proceedings_curation/scripts/extract_language_subset.py $(PROCEEDINGS_MEETINGS_CORPUS_PATH) $(ENGLISH_CORPUS_PATH) --tokenizer simple --filter-languages en 
.PHONY: extract_english_corpus

extract_french_corpus: export PYTHONPATH=.
extract_french_corpus:
	@poetry run python proceedings_curation/scripts/extract_language_subset.py $(PROCEEDINGS_MEETINGS_CORPUS_PATH) $(FRENCH_CORPUS_PATH) --tokenizer simple --filter-languages fr
.PHONY: extract_french_corpus
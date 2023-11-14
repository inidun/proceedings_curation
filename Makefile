include .env
SHELL := /bin/bash

create_metadata:
	@poetry run python proceedings_curation/scripts/create_metadata_index.py $(PROCEEDINGS_INDEX) $(PROCEEDINGS_METADATA) $(METADATA_INDEX)
.PHONY: create_metadata
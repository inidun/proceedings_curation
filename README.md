This repository is designed to handle the extraction, processing, and curation of text data from UNESCO’s Proceedings, 1945-2017. It provides a set of tools and scripts to facilitate the extraction of text from various formats, language detection, filtering, and metadata indexing.

## Modules 

### extractors

This module contains functions and classes for extracting text from various formats, such as PDF, ALTO XML and HOCR files.

### language_detectors

Classes and functions related to language detection.

### language_filters

This subdirectory contains classes and functions related to filtering text data based on language.

### tokenizers

The tokenizers module contains classes and functions for tokenizing text data. Tokenization is the process of breaking down text into smaller units, such as words or sentences, which can then be processed and analyzed individually. This module can be expanded to provide more tokenization methods to suit different text processing needs. 

## Scripts

Contains standalone scripts for various tasks related to proceedings curation.

#### `compare_excel.py`

The `compare_excel.py` script compares two Excel files and highlights the differences between them. This script is useful for identifying changes, discrepancies, or updates between two versions of an Excel file, making it easier to track modifications and ensure data consistency.

#### `create_jsonl_dataset.py`

The `create_jsonl_dataset.py` script converts a metadata index into a JSON Lines (JSONL) dataset. This script is useful for transforming structured metadata into a format that is easy to process and analyze with various data processing tools.

#### `create_metadata_index.py`

The `create_metadata_index.py` script creates a metadata index by merging and updating `proceedings_index` and `proceedings_metadata`. This script is used for consolidating and organizing metadata from two different sources into a single, unified index.

#### `extract_language_subset.py`

The `extract_language_subset.py` script processes text files in a specified input folder by tokenizing paragraphs, detecting languages, and filtering paragraphs based on the specified languages. The filtered paragraphs are then saved to a specified output folder.

#### `extract_meetings.py`

The `extract_meetings.py` script uses a metadata index to extract text from a folder of text files and saves the extracted data into a structured format.


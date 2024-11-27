# Scripts

## `compare_excel.py`

The `compare_excel.py` script compares two Excel files and highlights the differences between them. This script is useful for identifying changes, discrepancies, or updates between two versions of an Excel file, making it easier to track modifications and ensure data consistency.

### Usage

```sh
compare_excel.py FILE1 FILE2 OUTPUT_FILE
```

### Arguments

- `FILE1`: The path to the first Excel file to compare.
- `FILE2`: The path to the second Excel file to compare.
- `OUTPUT_FILE`: The path to the output Excel file where the differences will be highlighted and saved.

### Example

```sh
python compare_excel.py old_version.xlsx new_version.xlsx differences.xlsx
```

This example command compares `old_version.xlsx` and `new_version.xlsx`, and saves the highlighted differences to `differences.xlsx`.


## `create_jsonl_dataset.py`

The `create_jsonl_dataset.py` script converts a metadata index into a JSON Lines (JSONL) dataset. This script is useful for transforming structured metadata into a format that is easy to process and analyze with various data processing tools.

### Usage

```sh
create_jsonl_dataset.py INPUT_METADATA_INDEX OUTPUT_JSONL_FILE
```

### Arguments

- `INPUT_METADATA_INDEX`: The path to the file containing the input metadata index.
- `OUTPUT_JSONL_FILE`: The path to the output JSONL file where the transformed dataset will be saved.

### Example

```sh
python create_jsonl_dataset.py metadata_index.csv dataset.jsonl
```

This example command converts the metadata from `metadata_index.csv` into a JSON Lines format and saves the resulting dataset to `dataset.jsonl`.


## `create_metadata_index.py`

The `create_metadata_index.py` script creates a metadata index by merging and updating `proceedings_index` and `proceedings_metadata`. This script is used for consolidating and organizing metadata from two different sources into a single, unified index.

### Usage

```sh
create_metadata_index.py PROCEEDINGS_INDEX PROCEEDINGS_METADATA FILENAME
```

### Arguments

- `PROCEEDINGS_INDEX`: The path to the file containing the proceedings index.
- `PROCEEDINGS_METADATA`: The path to the file containing the proceedings metadata.
- `FILENAME`: The name of the output file where the merged and updated metadata index will be saved.

### Example

```sh
python create_metadata_index.py proceedings_index.csv proceedings_metadata.csv merged_metadata_index.csv
```

This example command merges the metadata from `proceedings_index.csv` and `proceedings_metadata.csv`, and saves the resulting metadata index to `merged_metadata_index.csv`.


## `extract_language_subset.py`

The `extract_language_subset.py` script processes text files in a specified input folder by tokenizing paragraphs, detecting languages, and filtering paragraphs based on the specified languages. The filtered paragraphs are then saved to a specified output folder.

### Usage

```sh
extract_language_subset.py [OPTIONS] INPUT_FOLDER OUTPUT_FOLDER
```

### Arguments

- `INPUT_FOLDER`: The path to the folder containing the input text files.
- `OUTPUT_FOLDER`: The path to the folder where the filtered text files will be saved.

### Options

- `--tokenizer TEXT`: The tokenizer to use for processing the text files. (e.g., `nltk`, `spacy`)
- `--possible_languages LIST`: A list of possible languages to consider during language detection. (e.g., `['en', 'fr', 'de']`)
- `--filter_languages TEXT`: The languages to keep in the filtered output. This can be a single language code or a list of language codes. (e.g., `'en'` or `['en', 'fr']`)
- `--language_detector TEXT`: The language detector to use. Defaults to `"langdetect"`.
- `--keep_undetected`: A flag to keep paragraphs with undetected languages. Defaults to `False`.
- `--force_overwrite`: A flag to overwrite existing files in the output folder. Defaults to `False`.

### Example

```sh
python extract_language_subset.py --tokenizer nltk --possible_languages '["en", "fr", "de"]' --filter_languages '["en", "fr"]' --language_detector langdetect --keep_undetected --force_overwrite input_folder output_folder
```

This example command processes text files in the `input_folder`, tokenizes paragraphs using the `nltk` tokenizer, considers English, French, and German as possible languages, keeps only English and French paragraphs, uses the `langdetect` language detector, keeps paragraphs with undetected languages, and overwrites existing files in the `output_folder`.


## `extract_meetings.py`

The `extract_meetings.py` script uses a metadata index to extract text from a folder of text files and saves the extracted data into a structured format.

### Usage

```sh
extract_meetings.py [OPTIONS] METADATA_INDEX INPUT_PATH OUTPUT_PATH
```

### Arguments

- `METADATA_INDEX`: The path to the metadata index file containing information about the text files to be processed.
- `INPUT_PATH`: The path to the folder containing the input text files.
- `OUTPUT_PATH`: The path to the folder where the extracted meeting information will be saved.

### Options

- `-e, --extractor [pdfbox|tesseract]`: The extractor to use for processing the text files. Defaults to `pdfbox`.
- `--page_numbers`: A flag to include page numbers in the extracted output. Defaults to `False`.
- `--page_sep TEXT`: The separator to use between pages in the extracted output. Defaults to an empty string.
- `--force`: A flag to overwrite existing files in the output folder. Defaults to `False`.

### Example

```sh
python extract_meetings.py --extractor tesseract --page_numbers --page_sep '\n' --force metadata_index.csv input_texts/ output_folder/
```

This example command processes the text files in the `input_texts/` folder using the `tesseract` extractor, includes page numbers in the extracted output, uses a newline character as the page separator, forces overwriting of existing files, and saves the extracted meeting information to the `output_folder/`.

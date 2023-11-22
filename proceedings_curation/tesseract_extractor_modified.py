import os
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

import pdf2image
import pytesseract
from loguru import logger
from pdf2image import convert_from_path
from pdf_extract.tesseract_extractor import TesseractExtractor


# TODO: Add language as argument
@dataclass
class TesseractExtractorMod(TesseractExtractor):
    """Extract text from PDF files using Tesseract OCR

    Args:
        dpi (int, optional): Resolution. Defaults to 350.
        fmt (str, optional): Format. Defaults to 'tiff'.
        grayscale (bool, optional): Grayscale. Defaults to True.
        use_pdftocairo (bool, optional): Use pdftocairo. Defaults to True.
        language (str, optional): Language. Defaults to "eng+ara+chi_sim+fra+rus+spa".
        tesseract_config (str, optional): Tesseract config. Defaults to '--oem 1 --psm 1'.
        tessdata (str | None, optional): Path to tessdata. Defaults to os.getenv('TESSDATA_PREFIX').
    """

    dpi: int = 350
    fmt: str = 'tiff'
    grayscale: bool = True
    use_pdftocairo: bool = True
    language: str = "eng+ara+chi_sim+fra+rus+spa"

    tesseract_config: str = '--oem 1 --psm 1'
    tessdata: str | None = os.getenv('TESSDATA_PREFIX')

    def __post_init__(self) -> None:
        if self.tessdata:
            self.tesseract_config += f' --tessdata-dir {self.tessdata}'

    def pdf_to_txt(
        self,
        filename: str | os.PathLike,
        output_folder: str | os.PathLike,
        first_page: int = 1,
        last_page: int | None = None,
        language: str | None = None,
    ) -> None:
        """Extracts text from PDF-file and saves result as TXT-file

        Args:
            filename (str | os.PathLike): Path to PDF file
            output_folder (str | os.PathLike): Path to save extracted text
            first_page (int, optional): First page to extract. Defaults to 1.
            last_page (int | None, optional): Last page to extract. Defaults to None.
            language (str | None, optional): Language. Defaults to None.

        Raises:
            ValueError: If last_page is less than first_page
        """

        lang = language or self.language
        basename = Path(filename).stem
        images = convert_from_path(
            str(filename),
            first_page=first_page,
            last_page=last_page,  # type: ignore
            dpi=self.dpi,
            fmt=self.fmt,
            grayscale=self.grayscale,
            use_pdftocairo=self.use_pdftocairo,
        )

        i = 0
        for i, image in enumerate(images):
            text_filename = Path(output_folder) / f'{basename}_{i+first_page:04}.txt'
            with open(text_filename, 'w', encoding='utf-8') as fp:
                fp.write(pytesseract.image_to_string(image, lang=lang, config=self.tesseract_config))

        logger.success(
            f'Extracted: {basename}, pages: {first_page}-{last_page}, dpi: {self.dpi}, fmt: {self.fmt}, lang: {lang}'
        )

    def pdf_to_alto(
        self,
        filename: str | os.PathLike,
        output_folder: str | os.PathLike,
        first_page: int = 1,
        last_page: int | None = None,
        language: str | None = None,
    ) -> None:
        """Extracts text from PDF-file and saves result as ALTO-XML

        Args:
            filename (str | os.PathLike): Path to PDF file
            output_folder (str | os.PathLike): Path to save extracted text
            first_page (int, optional): First page to extract. Defaults to 1.
            last_page (int | None, optional): Last page to extract. Defaults to None.
            language (str | None, optional): Language. Defaults to None.

        Raises:
            ValueError: If last_page is less than first_page
        """

        lang = language or self.language
        basename = Path(filename).stem
        images = convert_from_path(
            str(filename),
            first_page=first_page,
            last_page=last_page,  # type: ignore
            dpi=self.dpi,
            fmt=self.fmt,
            grayscale=self.grayscale,
            use_pdftocairo=self.use_pdftocairo,
        )

        i = 0
        for i, image in enumerate(images):
            text_filename = Path(output_folder) / f'{basename}_{i+first_page:04}.alto'
            with open(text_filename, 'wb') as fp:
                fp.write(pytesseract.image_to_alto_xml(image, lang=lang, config=self.tesseract_config))

        logger.success(
            f'Extracted: {basename}, pages: {first_page}-{last_page}, dpi: {self.dpi}, fmt: {self.fmt}, lang: {lang}'
        )

    def pdf_to_hocr(
        self,
        filename: str | os.PathLike,
        output_folder: str | os.PathLike,
        first_page: int = 1,
        last_page: int | None = None,
        language: str | None = None,
    ) -> None:
        """Extracts text from PDF-file and saves result as hOCR

        Args:
            filename (str | os.PathLike): Path to PDF file
            output_folder (str | os.PathLike): Path to save extracted text
            first_page (int, optional): First page to extract. Defaults to 1.
            last_page (int | None, optional): Last page to extract. Defaults to None.
            language (str | None, optional): Language. Defaults to None.

        Raises:
            ValueError: If last_page is less than first_page
        """

        lang = language or self.language
        basename = Path(filename).stem
        images = convert_from_path(
            str(filename),
            first_page=first_page,
            last_page=last_page,  # type: ignore
            dpi=self.dpi,
            fmt=self.fmt,
            grayscale=self.grayscale,
            use_pdftocairo=self.use_pdftocairo,
        )

        i = 0
        for i, image in enumerate(images):
            text_filename = Path(output_folder) / f'{basename}_{i+first_page:04}.hocr'
            with open(text_filename, 'wb') as fp:
                hocr = pytesseract.image_to_pdf_or_hocr(
                    image, extension='hocr', lang=lang, config=self.tesseract_config
                )
                fp.write(hocr)

        logger.success(f'Extracted: {basename}, pages: {i+1}, dpi: {self.dpi}, fmt: {self.fmt}, lang: {lang}')

    def extract_text(  # pylint: disable=too-many-arguments
        self,
        filename: str | os.PathLike,
        output_folder: str | os.PathLike,
        first_page: int | None = 1,
        last_page: int | None = None,
        page_numbers: bool = False,
        language: str | None = None,
        page_sep: str = '',
        output_filename: str | None = None,
        force: bool = False,
    ) -> None:
        """Extracts text from PDF-file and saves result as text

        Args:
            filename (str | os.PathLike): Path to PDF file
            output_folder (str | os.PathLike): Path to save extracted text
            first_page (int | None, optional): First page to extract. Defaults to 1.
            last_page (int | None, optional): Last page to extract. Defaults to None.
            page_numbers (bool, optional): Add page numbers to output. Defaults to False.
            language (str | None, optional): Language. Defaults to None.
            page_sep (str, optional): Page separator. Defaults to ''.
            output_filename (str | None, optional): Output filename. Defaults to None.
            force (bool, optional): Overwrite existing files. Defaults to False.

        Raises:
            ValueError: If last_page is less than first_page
        """

        lang = language or self.language
        first_page: int = first_page or 1
        if page_numbers:
            page_sep = ''
        basename = Path(filename).stem

        num_pages = pdf2image.pdfinfo_from_path(str(filename))['Pages']
        if last_page is None or last_page > num_pages:
            last_page = int(num_pages)

        ouput_filename: str = (
            output_filename
            if output_filename
            else (
                f'{basename}_{first_page}-{last_page}.txt'
                if last_page < num_pages or first_page > 1
                else f'{basename}.txt'
            )
        )
        output_filepath: Path = Path(output_folder) / ouput_filename

        if output_filepath.exists():
            if not force:
                logger.info(f'Skipping {ouput_filename}: Already extracted')
                return
            logger.info(f'Overwriting {ouput_filename}')

        logger.info(f'Processing {ouput_filename} ({basename}.pdf:{first_page}-{last_page})')

        images = convert_from_path(
            str(filename),
            first_page=first_page,
            last_page=last_page,  # type: ignore
            dpi=self.dpi,
            fmt=self.fmt,
            grayscale=self.grayscale,
            use_pdftocairo=self.use_pdftocairo,
        )

        with TemporaryDirectory() as temp_dir:
            for i, image in enumerate(images):
                text_filename = Path(temp_dir) / f'{basename}_{i+first_page:04}.txt'
                with open(text_filename, 'w', encoding='utf-8') as fp:
                    fp.write(pytesseract.image_to_string(image, lang=lang, config=self.tesseract_config))

            with open(Path(output_folder) / ouput_filename, 'w', encoding='utf-8') as outfile:
                if page_numbers:
                    outfile.write(f'# {basename}\n\n')

                for file in sorted(Path(temp_dir).glob('*.txt')):
                    with open(file, 'r', encoding='utf-8') as infile:
                        if page_numbers:
                            page_number: int = int(file.stem.rsplit('_', 1)[-1])
                            outfile.write(f'\n## Page {page_number}\n\n')

                        contents = infile.read()
                        outfile.write(contents)
                        outfile.write(f'\n{page_sep}\n')

        logger.success(
            f'Extracted: {ouput_filename}, pages: {first_page}-{last_page}, dpi: {self.dpi}, fmt: {self.fmt}, lang: {lang}'
        )


if __name__ == '__main__':
    pass

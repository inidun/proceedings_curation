import os
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

import pdf2image
import pdfbox
from loguru import logger
from pdf_extract.pdfbox_extractor import PDFBoxExtractor
from tqdm import tqdm


@dataclass
class PDFBoxExtractorMod(PDFBoxExtractor):  # type: ignore[misc]
    """Extract text from PDF files using Apache PDFBox"""
    def extract_text(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        filename: str | os.PathLike[str],
        output_folder: str | os.PathLike[str],
        first_page: int | None = 1,
        last_page: int | None = None,
        page_numbers: bool = False,
        page_sep: str = '',
        output_filename: str | None = None,
        force: bool = False,
    ) -> None:
        """Extract text from PDF files. Uses Apache PDFBox to extract text from PDF files. The extracted text is saved to a text file.

        Args:
            filename (str | os.PathLike): Path to PDF file
            output_folder (str | os.PathLike): Path to save extracted text
            first_page (int | None, optional): First page to extract. Defaults to 1.
            last_page (int | None, optional): Last page to extract. Defaults to None.
            page_numbers (bool, optional): Extract page numbers. Defaults to False.
            page_sep (str, optional): Page separator. Defaults to ''.
            output_filename (str | None, optional): Output filename. Defaults to None.
            force (bool, optional): Force overwrite existing files. Defaults to False.
        """

        first_page: int = first_page or 1
        if page_numbers:
            page_sep = ''

        basename = Path(filename).stem
        p = pdfbox.PDFBox()

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

        with TemporaryDirectory() as temp_dir:
            for page in tqdm(range(first_page, last_page + 1), desc='Extracting pages'):
                output_path = Path(temp_dir) / f'{basename}_{page:04}.txt'
                p.extract_text(
                    filename,
                    output_path=output_path,
                    encoding=self.encoding,
                    html=self.html,
                    sort=self.sort,
                    ignore_beads=self.ignore_beads,
                    start_page=page,
                    end_page=page,
                    console=self.console,
                )

            with open(Path(output_folder) / ouput_filename, 'w', encoding='utf-8') as outfile:
                if page_numbers:
                    outfile.write(f'# {basename}\n\n')

                for file in sorted(Path(temp_dir).glob('*.txt')):
                    with open(file, 'r', encoding='utf-8') as infile:
                        if page_numbers:
                            page_number: int = int(file.stem.rsplit('_', 1)[-1])
                            outfile.write(f'## Page {page_number}\n\n')
                        contents = infile.read()
                        outfile.write(contents)
                        outfile.write(f'\n{page_sep}\n')

        logger.success(f'Extracted {ouput_filename} ({basename}.pdf:{first_page}-{last_page})')


if __name__ == '__main__':  # pragma: no cover
    pass

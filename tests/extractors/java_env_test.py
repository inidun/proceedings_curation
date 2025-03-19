import os

from pdf_extract.java_extractor import get_pdfbox_path


class TestJavaEnvionment:
    def test_java_home_is_set(self):
        assert os.environ.get('JAVA_HOME') is not None

    def test_get_pdfbox_path_returns_valid_path(self):
        assert get_pdfbox_path().exists()

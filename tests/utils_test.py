import pytest

from proceedings_curation.utils import extract_text_from_alto, extract_text_from_hocr

# Sample ALTO XML content for testing
alto_xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<alto xmlns="http://www.loc.gov/standards/alto/ns-v3#">
    <Layout>
        <Page>
            <PrintSpace>
                <ComposedBlock>
                    <TextBlock>
                        <TextLine>
                            <String CONTENT="Lorem"/>
                            <String CONTENT="ipsum"/>
                            <String CONTENT="dolor"/>
                            <String CONTENT="sit"/>
                            <String CONTENT="amet"/>
                        </TextLine>
                    </TextBlock>
                </ComposedBlock>
            </PrintSpace>
        </Page>
    </Layout>
</alto>"""

# Sample HOCR content for testing
hocr_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
 <body>
  <div class='ocr_page'>
   <div class='ocr_carea'>
    <p class='ocr_par'>
     <span class='ocr_line'>
      <span class='ocrx_word'>Lorem</span>
      <span class='ocrx_word'>ipsum</span>
      <span class='ocrx_word'>dolor</span>
      <span class='ocrx_word'>sit</span>
      <span class='ocrx_word'>amet</span>
     </span>
    </p>
   </div>
  </div>
 </body>
</html>"""


@pytest.fixture(name='alto_xml_file')
def fixture_alto_xml_file(tmp_path):
    file_path = tmp_path / "test_alto.xml"
    file_path.write_text(alto_xml_content)
    return file_path


@pytest.fixture(name='hocr_file')
def fixture_hocr_file(tmp_path):
    file_path = tmp_path / "test_hocr.hocr"
    file_path.write_text(hocr_content)
    return file_path


def test_extract_text_from_alto(alto_xml_file):
    text = extract_text_from_alto(alto_xml_file)
    assert text == "Lorem ipsum dolor sit amet"


def test_extract_text_from_hocr(hocr_file):
    text = extract_text_from_hocr(hocr_file)
    assert text == "Lorem ipsum dolor sit amet"


if __name__ == "__main__":
    pytest.main()

import os
import xml.etree.ElementTree as ET


def extract_text_from_alto(file_path: os.PathLike | str) -> str:
    """Extract text content from an ALTO XML file.

    Args:
        file_path (os.PathLike | str): Path to the ALTO XML file.

    Returns:
        str: Text content extracted from the ALTO XML file.
    """
    # Convert the file path to a string
    file_path = os.fspath(file_path)

    # Define the namespace
    namespaces = {'alto': 'http://www.loc.gov/standards/alto/ns-v3#'}

    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Find all String elements
    strings = root.findall('.//alto:String', namespaces)

    # Extract the CONTENT attribute from each String element
    content = ' '.join(string.get('CONTENT', '') for string in strings)

    return content


def extract_text_from_hocr(file_path: os.PathLike | str) -> str:
    """Extract text content from an HOCR file.

    Args:
        file_path (os.PathLike | str): Path to the HOCR file.

    Returns:
        str: Text content extracted from the HOCR file.
    """
    # Convert the file path to a string
    file_path = os.fspath(file_path)

    # Parse the HOCR file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Define the namespace (if any)
    namespaces = {'xhtml': 'http://www.w3.org/1999/xhtml'}

    # Find all ocrx_word elements
    words = root.findall('.//xhtml:span[@class="ocrx_word"]', namespaces)

    # Extract the text content
    text_content = ' '.join(word.text for word in words if word.text)

    return text_content


if __name__ == "__main__":
    pass

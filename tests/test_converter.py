import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from converter import FB2Converter
from ebooklib import epub


@pytest.fixture
def mock_fb2_file(tmp_path):
    fb2_content = """<?xml version="1.0" encoding="UTF-8"?>
    <FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:l="http://www.w3.org/1999/xlink">
        <description>
            <title-info>
                <genre>science_fiction</genre>
                <author>
                    <first-name>Test</first-name>
                    <last-name>Author</last-name>
                </author>
                <book-title>Test Title</book-title>
                <lang>en</lang>
            </title-info>
        </description>
        <body>
        <section>
            <title><p>Chapter 1</p></title>
            <p>Content 1</p>
        </section>
    </body>
    </FictionBook>
    """
    fb2_file = tmp_path / "test.fb2"
    fb2_file.write_text(fb2_content, encoding="utf-8")
    return fb2_file


def test_converter_init(tmp_path):
    input_path = tmp_path / "input.fb2"
    output_path = tmp_path / "output.epub"
    converter = FB2Converter(input_path, output_path)
    assert converter.input_path == input_path
    assert converter.output_path == output_path


def test_process_metadata(mock_fb2_file, tmp_path):
    output_path = tmp_path / "output.epub"
    converter = FB2Converter(mock_fb2_file, output_path)

    # We need to parse the tree first to test _process_metadata directly
    # Or we can test the whole convert process and check the book object
    # But since convert() writes to file, let's mock epub.write_epub

    with patch("ebooklib.epub.write_epub") as mock_write:
        converter.convert()

        # Get the book object passed to write_epub
        args, _ = mock_write.call_args
        book = args[1]

        assert book.title == "Test Title"
        # ebooklib stores authors as a list of tuples or strings depending on version/usage
        # but add_author adds to metadata
        assert "Test Author" in [a[0] for a in book.get_metadata("DC", "creator")]
        assert book.language == "en"


def test_process_body(mock_fb2_file, tmp_path):
    output_path = tmp_path / "output.epub"
    converter = FB2Converter(mock_fb2_file, output_path)

    with patch("ebooklib.epub.write_epub") as mock_write:
        converter.convert()
        args, _ = mock_write.call_args
        book = args[1]

        # Check items
        items = book.get_items()
        # EpubNav inherits from EpubHtml, so we need to exclude it
        chapters = [
            item
            for item in items
            if isinstance(item, epub.EpubHtml) and not isinstance(item, epub.EpubNav)
        ]
        assert len(chapters) == 1
        assert "Chapter 1" in chapters[0].content
        assert "Content 1" in chapters[0].content


def test_convert_success(mock_fb2_file, tmp_path):
    output_path = tmp_path / "output.epub"
    converter = FB2Converter(mock_fb2_file, output_path)
    assert converter.convert() is True
    assert output_path.exists()


def test_convert_failure(tmp_path):
    # Non-existent file
    input_path = tmp_path / "nonexistent.fb2"
    output_path = tmp_path / "output.epub"
    converter = FB2Converter(input_path, output_path)
    assert converter.convert() is False

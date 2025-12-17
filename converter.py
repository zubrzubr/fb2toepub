import os
import base64
from pathlib import Path
from lxml import etree
from ebooklib import epub


class FB2Converter:
    def __init__(self, input_path: Path, output_path: Path):
        self.input_path = input_path
        self.output_path = output_path
        self.namespaces = {
            "fb": "http://www.gribuser.ru/xml/fictionbook/2.0",
            "l": "http://www.w3.org/1999/xlink",
        }

    def convert(self):
        try:
            tree = etree.parse(str(self.input_path))
            root = tree.getroot()

            book = epub.EpubBook()

            # Metadata
            self._process_metadata(root, book)

            # Chapters
            chapters = self._process_body(root, book)

            # Images
            self._process_images(root, book)

            # Navigation
            book.toc = chapters
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())

            # CSS
            style = "body { font-family: Times, Times New Roman, serif; }"
            nav_css = epub.EpubItem(
                uid="style_nav",
                file_name="style/nav.css",
                media_type="text/css",
                content=style,
            )
            book.add_item(nav_css)

            # Spine
            book.spine = ["nav"] + chapters

            # Write
            epub.write_epub(str(self.output_path), book, {})
            print(f"Successfully converted {self.input_path} to {self.output_path}")
            return True

        except Exception as e:
            print(f"Error converting {self.input_path}: {e}")
            return False

    def _process_metadata(self, root, book):
        desc = root.find("fb:description", self.namespaces)
        if desc is None:
            return

        title_info = desc.find("fb:title-info", self.namespaces)
        if title_info is not None:
            book_title = title_info.find("fb:book-title", self.namespaces)
            if book_title is not None and book_title.text:
                book.set_title(book_title.text)

            author = title_info.find("fb:author", self.namespaces)
            if author is not None:
                first = author.find("fb:first-name", self.namespaces)
                last = author.find("fb:last-name", self.namespaces)
                name_parts = []
                if first is not None and first.text:
                    name_parts.append(first.text)
                if last is not None and last.text:
                    name_parts.append(last.text)
                if name_parts:
                    book.add_author(" ".join(name_parts))

            lang = title_info.find("fb:lang", self.namespaces)
            if lang is not None and lang.text:
                book.set_language(lang.text)

    def _process_body(self, root, book):
        body = root.find("fb:body", self.namespaces)
        if body is None:
            return []

        chapters = []
        for i, section in enumerate(body.findall("fb:section", self.namespaces)):
            title_elem = section.find("fb:title", self.namespaces)
            title_text = "Chapter"
            if title_elem is not None:
                p = title_elem.find("fb:p", self.namespaces)
                if p is not None and p.text:
                    title_text = p.text

            # Simple content extraction (can be improved)
            content = f"<h1>{title_text}</h1>"
            for p in section.findall("fb:p", self.namespaces):
                if p.text:
                    content += f"<p>{p.text}</p>"

            chapter = epub.EpubHtml(
                title=title_text, file_name=f"chap_{i+1}.xhtml", lang="en"
            )
            chapter.content = content
            book.add_item(chapter)
            chapters.append(chapter)

        return chapters

    def _process_images(self, root, book):
        for binary in root.findall("fb:binary", self.namespaces):
            content_type = binary.get("content-type")
            image_id = binary.get("id")
            if image_id and binary.text:
                try:
                    image_data = base64.b64decode(binary.text)
                    img = epub.EpubItem(
                        uid=image_id,
                        file_name=f"images/{image_id}",
                        media_type=content_type,
                        content=image_data,
                    )
                    book.add_item(img)
                except Exception as e:
                    print(f"Failed to process image {image_id}: {e}")

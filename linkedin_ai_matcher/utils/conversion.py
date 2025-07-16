"""
Functionality for converting documents to text.
"""

from pathlib import Path

import html_to_markdown
import pymupdf4llm

from linkedin_ai_matcher.models import Document


def load_file(path: Path) -> Document:
    """
    Load the file as a string, converting it if necessary.
    """
    name = path.stem
    extension = path.suffix.lower()[1:]

    match extension:
        case "txt" | "md":
            content = path.read_text(encoding="utf-8")
        case "html":
            content = html_to_markdown.convert_to_markdown(
                path.read_text(encoding="utf-8")
            )
        case "pdf":
            content = pymupdf4llm.to_markdown(path)
        case _:
            raise ValueError(f"Unsupported file format: {extension}")

    return Document(name=name, content=content, format=extension)

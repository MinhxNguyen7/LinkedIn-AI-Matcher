"""
Document-related models
"""

from pathlib import Path

import html_to_markdown
import pymupdf4llm
from pydantic import Field

from .base import Model


class Document(Model):
    name: str = Field(
        description="Name of the document",
    )
    format: str = Field(
        description="Format of the document, e.g., 'pdf', 'docx', 'txt'",
    )
    content: str = Field(
        description="Stringified content of the document",
    )

    @staticmethod
    def from_file(path: Path) -> "Document":
        """
        Load the file as a string, converting it if necessary.

        Args:
            path (Path): Path to the file to load.

        Returns:
            Document: A Document instance representing the file.
        """
        name = path.name
        format = path.suffix.lower().lstrip(".")

        if format == "pdf":
            # Use pymupdf4llm to extract text from PDF
            content = pymupdf4llm.to_markdown(path)
        elif format == "html":
            # Use html_to_markdown to convert HTML to markdown
            content = html_to_markdown.convert(path.read_text())
        elif format in ("txt", "md"):
            # Read text files directly
            content = path.read_text()
        else:
            raise ValueError(f"Unsupported file format: {format}")

        return Document(name=name, format=format, content=content)
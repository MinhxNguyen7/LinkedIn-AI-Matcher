"""
Data models
"""

from enum import Enum
from pathlib import Path
from typing import TypeVar, Type, Any

import html_to_markdown
import pymupdf4llm
from pydantic import BaseModel, Field

from .text_manipulation import normalize_markup


class Model(BaseModel):
    def __str__(self) -> str:
        """
        Convert the data to an HTML-like markup format.
        """
        return normalize_markup(
            "\n".join(
                f"<{key}>{value}</{key}>" for key, value in self.model_dump().items()
            )
        )


class BetterEnum(Enum):
    FactoryReturnT = TypeVar("FactoryReturnT", bound="BetterEnum")

    @classmethod
    def from_value(cls: Type[FactoryReturnT], value: Any) -> FactoryReturnT:
        if value is None:
            raise ValueError(f"None cannot be converted to {cls.__name__}")

        # Try exact match first
        for member in cls:
            if member.value == value:
                return member

        # If it's a string, try case-insensitive matching
        if isinstance(value, str):
            # Try case-insensitive match
            value_lower = value.lower()
            for member in cls:
                if (
                    isinstance(member.value, str)
                    and member.value.lower() == value_lower
                ):
                    return member

            # Try matching against member names
            value_upper = value.upper()
            for member in cls:
                if member.name == value_upper:
                    return member

        raise ValueError(f"'{value}' is not a valid {cls.__name__} value")


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


class ApplicantSummary(Model):
    education: str = Field(
        description="Applicant's education background",
    )
    skills: str = Field(
        description="Summary of applicant's skills",
    )
    character: str = Field(
        description="What kind of person the applicant is",
    )
    additional_notes: str = Field(
        description="Additional notes about the applicant",
    )


class JobLevel(Enum):
    ENTRY = "Entry"
    MID = "Mid"
    SENIOR = "Senior"
    LEAD = "Lead"
    MANAGER = "Manager"
    DIRECTOR = "Director"
    VP = "VP"
    C_LEVEL = "C-Level"


class ApplicantInfo(Model):
    """
    Information about the applicant, including their summary and preferences,
    used to compare against job postings.
    """

    applicant_summary: ApplicantSummary = Field(
        description="Generated and possibly user-modified summary of the applicant",
    )
    additional_preferences: str = Field(
        description="Additional preferences for the job match provided by the user",
    )


class JobContent(Model):
    title: str = Field(
        description="Title of the job",
    )
    company: str = Field(
        description="Company offering the job",
    )
    description: str = Field(
        description="Description of the job",
    )


class JobInfo(Model):
    id: str = Field(
        description="Unique identifier for the job posting",
    )
    content: JobContent = Field(
        description="Content of the job posting",
    )


class JobFit(BetterEnum):  # type: ignore[misc]
    EXCELLENT = "Excellent"
    GOOD = "Good"
    FAIR = "Fair"
    POOR = "Poor"


class JobMatchResult(Model):
    job_info: JobInfo = Field(
        description="Information about the job",
    )
    fit: JobFit = Field(
        description="How well the job matches the applicant",
    )
    reasons: str = Field(
        description="Reasons for the match score",
    )

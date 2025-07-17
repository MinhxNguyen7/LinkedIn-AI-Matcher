"""
Data models
"""

from enum import Enum

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


class JobPreference(Model):
    titles: list[str] = Field(
        description="Preferred job titles",
    )
    levels: list[JobLevel] = Field(
        description="Preferred job levels",
    )
    additional_notes: str = Field(
        description="Additional notes about job preferences",
    )

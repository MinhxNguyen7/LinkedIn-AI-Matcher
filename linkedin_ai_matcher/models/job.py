"""
Job-related models
"""

from enum import Enum

from pydantic import Field

from .base import Model


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


class JobFit(Enum):
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

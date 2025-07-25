"""
Applicant-related models
"""

from enum import Enum

from pydantic import Field

from .base import Model


class JobLevel(Enum):
    ENTRY = "Entry"
    JUNIOR = "Junior"
    MID = "Mid"
    SENIOR = "Senior"
    LEAD = "Lead"
    MANAGER = "Manager"
    DIRECTOR = "Director"
    VP = "VP"
    C_LEVEL = "C-Level"


class ApplicantSummary(Model):
    """
    Summary of the applicant's profile based on their documents.
    """

    education: str = Field(
        description="Education background of the applicant",
    )
    skills: str = Field(
        description="Skills and competencies of the applicant",
    )
    character: str = Field(
        description="Character traits and interpersonal skills",
    )
    additional_notes: str = Field(
        description="Additional notes about the applicant",
    )


class JobPreference(Model):
    """
    Job preferences for the applicant.
    """

    job_titles: list[str] = Field(
        description="Preferred job titles",
    )
    job_levels: list[JobLevel] = Field(
        description="Preferred job levels",
    )
    notes: str = Field(
        description="Additional notes about job preferences",
    )


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

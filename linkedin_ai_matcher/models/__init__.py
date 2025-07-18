"""
Models module - centralized data models for the LinkedIn AI Matcher
"""

# Base classes
from .base import Model as Model

# Document models
from .document import Document as Document

# Applicant models
from .applicant import (
    JobLevel as JobLevel,
    ApplicantSummary as ApplicantSummary,
    JobPreference as JobPreference,
    ApplicantInfo as ApplicantInfo,
)

# Job models
from .job import (
    JobContent as JobContent,
    JobInfo as JobInfo,
    JobFit as JobFit,
    JobMatchResult as JobMatchResult,
)
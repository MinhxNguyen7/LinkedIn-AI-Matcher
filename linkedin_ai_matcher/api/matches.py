from collections import defaultdict
import json
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from linkedin_ai_matcher.db import Job, Match, get_engine
from linkedin_ai_matcher.models import JobContent, JobInfo, JobMatchResult, JobFit
from linkedin_ai_matcher.utils import enum_from_value


def get_matches_from_db():
    with Session(get_engine()) as session:
        statement = select(
            Job.id,
            Job.title,
            Job.company,
            Job.description,
            Match.fit,
            Match.reasons,
        ).join(Job, Match.job_id == Job.id)

        result = session.execute(statement).all()

        return [
            JobMatchResult(
                job_info=JobInfo(
                    id=id,
                    content=JobContent(
                        title=title,
                        company=company,
                        description=description,
                    ),
                ),
                fit=enum_from_value(JobFit, fit),
                reasons=reasons,
            )
            for id, title, company, description, fit, reasons in result
        ]


def group_matches_by_fit(
    matches: Iterable[JobMatchResult],
) -> dict[str, list[JobMatchResult]]:
    """
    Group an Iterable of JobMatchResult's by their fit value.
    """
    matches_by_fit: defaultdict[str, list[JobMatchResult]] = defaultdict(list)

    for match in matches:
        matches_by_fit[match.fit.value].append(match)

    return matches_by_fit

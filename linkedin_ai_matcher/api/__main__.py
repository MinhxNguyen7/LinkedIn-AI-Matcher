from collections import defaultdict
import json

from flask import Flask, Response, jsonify
from sqlalchemy import select
from sqlalchemy.orm import Session

from linkedin_ai_matcher.db import Job, Match, get_engine
from linkedin_ai_matcher.models import JobContent, JobInfo, JobMatchResult, JobFit
from linkedin_ai_matcher.utils import enum_from_value


app = Flask(__name__)


@app.route("/matches", methods=["GET"])
def get_matches():
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
        matches = [
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

        # Group by fit
        matches_by_fit: defaultdict[str, list[JobMatchResult]] = defaultdict(list)
        for match in matches:
            matches_by_fit[match.fit.value].append(match)

        body = json.dumps(
            {
                fit: [
                    {
                        "job_info": match.job_info.toJSON(),
                        "fit": match.fit.value,
                        "reasons": match.reasons,
                    }
                    for match in matches
                ]
                for fit, matches in matches_by_fit.items()
            }
        )

        return Response(
            body,
            status=200,
            mimetype="application/json",
        )


if __name__ == "__main__":
    get_matches()
    app.run()

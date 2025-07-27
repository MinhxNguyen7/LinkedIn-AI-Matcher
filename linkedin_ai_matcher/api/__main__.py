from flask import Flask, jsonify

from .matches import get_matches_from_db, group_matches_by_fit


app = Flask(__name__)


@app.route("/grouped-matches", methods=["GET"])
def get_matches_grouped():
    raw_matches = get_matches_from_db()
    grouped_matches = group_matches_by_fit(raw_matches)
    return jsonify(
        {
            fit: [
                {
                    "job_info": match.job_info.toJSON(),
                    "fit": match.fit.value,
                    "reasons": match.reasons,
                }
                for match in matches
            ]
            for fit, matches in grouped_matches.items()
        }
    )


@app.route("/matches", methods=["GET"])
def get_matches():
    """
    Endpoint to get all job matches.
    """
    matches = get_matches_from_db()
    return jsonify(
        [
            {
                "job_info": match.job_info.toJSON(),
                "fit": match.fit.value,
                "reasons": match.reasons,
            }
            for match in matches
        ]
    )


if __name__ == "__main__":
    get_matches_from_db()
    app.run()

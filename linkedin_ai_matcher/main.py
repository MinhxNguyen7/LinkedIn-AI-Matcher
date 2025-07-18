from pathlib import Path
from typing import Iterable

from linkedin_ai_matcher.linkedin import RecommendedIdsScraper, JobPageClient
from linkedin_ai_matcher.llm import ApplicantSummarizer, AnthropicLLM

from linkedin_ai_matcher.utils import sleep_normal
from linkedin_ai_matcher.models import ApplicantSummary


def scrape_jobs(n: int = 5):
    ids_scraper = RecommendedIdsScraper(log_in=True)
    job_client = JobPageClient(log_in=True)

    for job_id in ids_scraper.scrape_job_ids(n):
        print(f"Found job ID: {job_id}")
        job_client.open_job_page(job_id)

        sleep_normal(1)  # Slow down to be less bot-like

        description = job_client.extract_job_description()
        if description:
            print(f"Job Description for {job_id}:\n{description}\n")
        else:
            print(f"No job description found for {job_id}.\n")


def summarize(document_paths: Iterable[Path]) -> ApplicantSummary:
    """
    Summarize applicant documents into an ApplicantSummary object.

    Args:
        document_paths (Iterable[Path]): Paths to the documents to summarize.

    Returns:
        ApplicantSummary: A structured summary of the applicant.
    """
    summarizer = ApplicantSummarizer(AnthropicLLM(messages_log_dir=Path("./.logs/llm")))
    summary = summarizer.summary_from_paths(document_paths)

    print(f"Applicant Summary:\n{summary}\n")
    return summary


if __name__ == "__main__":
    # scrape_jobs()
    summary = summarize([Path("./.data/resume1.pdf"), Path("./.data/resume2.pdf")])

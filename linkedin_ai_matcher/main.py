from pathlib import Path
from typing import Iterable
import csv


from linkedin_ai_matcher.linkedin import RecommendedIdsScraper, JobPageClient
from linkedin_ai_matcher.llm import ApplicantSummarizer, AnthropicLLM, JobMatchChecker
from linkedin_ai_matcher.utils import sleep_normal
from linkedin_ai_matcher.models import ApplicantSummary, ApplicantInfo, JobInfo
from linkedin_ai_matcher.integration import JobMatchManager


def scrape_job_ids(n: int = 5) -> Iterable[str]:
    """
    Scrape job IDs from LinkedIn's recommended jobs page.

    Args:
        n (int): Number of job IDs to scrape.

    Returns:
        Iterable[str]: A generator yielding job IDs.
    """
    ids_scraper = RecommendedIdsScraper()
    return ids_scraper.scrape_job_ids(n)


def scrape_jobs(n: int = 5):
    ids_scraper = RecommendedIdsScraper()
    job_client = JobPageClient(log_in=True)

    for job_id in ids_scraper.scrape_job_ids(n):
        print(f"Found job ID: {job_id}")
        job_client.open_job_page(job_id)

        sleep_normal(1)  # Slow down to be less bot-like

        description = job_client._extract_job_description()
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


def end_to_end(
    document_paths: Iterable[Path],
    additional_preferences: str = "",
    n_jobs: int = 5,
):
    ids_scraper = RecommendedIdsScraper()
    job_client = JobPageClient(log_in=True)

    applicant_summary = summarize(document_paths)

    matcher = JobMatchChecker(AnthropicLLM(messages_log_dir=Path("./.logs/llm")))
    applicant_info = ApplicantInfo(
        applicant_summary=applicant_summary,
        additional_preferences=additional_preferences,
    )

    writer = csv.writer(open("job_matches.csv", "w", newline=""))
    writer.writerow(["ID", "Fit", "Reasons"])

    for job_id in ids_scraper.scrape_job_ids(n_jobs):
        print(f"Found job ID: {job_id}")
        job_client.open_job_page(job_id)

        job_content = job_client.extract_job_content()
        if not job_content:
            print(f"No job content found for {job_id}. Skipping.")
            continue

        job_info = JobInfo(
            id=job_id,
            content=job_content,
        )

        result = matcher.check_job_match(applicant_info, job_info)

        print(
            f"{job_content.title} @ {job_content.company}: {result.fit.value} - {result.reasons}"
        )
        writer.writerow([job_id, result.fit.value, result.reasons])


def full_test(
    document_paths: Iterable[Path], additional_preferences: str = "", n_jobs: int = 100
):
    ids_scraper = RecommendedIdsScraper()
    job_client = JobPageClient(log_in=True)

    applicant_summary = summarize(document_paths)

    matcher = JobMatchChecker(AnthropicLLM(messages_log_dir=Path("./.logs/llm")))
    applicant_info = ApplicantInfo(
        applicant_summary=applicant_summary,
        additional_preferences=additional_preferences,
    )

    job_match_manager = JobMatchManager(
        applicant=applicant_info,
        ids_scraper=ids_scraper,
        job_page_client=job_client,
        job_match_checker=matcher,
    )

    job_match_manager.run(n_jobs)


if __name__ == "__main__":
    DOCS_DIR = Path(".data/documents")
    document_paths = list(DOCS_DIR.rglob("*.pdf"))
    full_test(
        document_paths=document_paths,
        additional_preferences="I'm a US citizen looking for full time positions (not internships)",
    )

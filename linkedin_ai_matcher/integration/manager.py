from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy import select

from linkedin_ai_matcher.linkedin import JobPageClient, RecommendedIdsScraper
from linkedin_ai_matcher.llm import JobMatchChecker
from linkedin_ai_matcher.models import ApplicantInfo
from linkedin_ai_matcher.models import JobInfo, JobMatchResult, JobContent
from linkedin_ai_matcher.utils import create_logger
from linkedin_ai_matcher.db import get_engine, Job, Match


class JobMatchManager:
    """
    Manages concurrent scraping and processing of job matches.
    """

    DEFAULT_NUM_JOBS = 32

    def __init__(
        self,
        applicant: ApplicantInfo,
        ids_scraper: RecommendedIdsScraper,
        job_page_client: JobPageClient,
        job_match_checker: JobMatchChecker,
    ):
        self._applicant = applicant
        self._ids_scraper = ids_scraper
        self._job_page_client = job_page_client
        self._job_match_checker = job_match_checker

        self._logger = create_logger(__class__.__name__)

        # ID into JobsPageClient
        self._ids_queue: Queue[str | None] = Queue(4)
        # JobInfo into JobMatchChecker
        self._jobs_queue: Queue[JobInfo | None] = Queue(4)

    def _load_unmatched_jobs(self) -> None:
        """
        Retrieves all jobs for which a match has not been checked yet
        and adds them to the jobs queue.
        """
        with Session(get_engine()) as session:
            statement = (
                select(Job)
                .join(Match, Job.id == Match.job_id)
                .where(Match.job_id.is_(None))
            )

            result = session.execute(statement).scalars().fetchall()

            for job in result:
                job_info = JobInfo(
                    id=job.id,
                    content=JobContent(
                        title=job.title,
                        company=job.company,
                        description=job.description,
                    ),
                )
                self._jobs_queue.put(job_info)
                self._logger.info(f"Loaded unmatched job: {job_info.id}")

        self._logger.info(f"Finished loading {len(result)} unmatched jobs.")

    def _scrape_job_ids(self, n: int = DEFAULT_NUM_JOBS) -> None:
        """
        Scrape job IDs from LinkedIn's recommended jobs page and put them into the queue.

        Args:
            n (int): Number of job IDs to scrape.
        """
        self._logger.info("Starting to scrape job IDs.")
        for job_id in self._ids_scraper.scrape_job_ids(n):
            self._ids_queue.put(job_id)
            self._logger.info(f"Scraped job ID: {job_id}")

        self._logger.info("Finished scraping job IDs.")
        # Signal that no more job IDs will be added
        self._ids_queue.put(None)

    def _process_job_ids(self) -> None:
        """
        Scrapes the content of the job pages for each job ID in the queue and puts the JobInfo into the jobs queue.

        Also adds the job information to the database.
        """
        self._logger.info("Starting to process job IDs.")
        while True:
            job_id = self._ids_queue.get()

            if job_id is None:
                self._logger.info("No more job IDs to process.")

                # Signal that no more jobs will be processed
                self._jobs_queue.put(None)
                self._ids_queue.task_done()
                return

            self._logger.info(f"Processing job ID: {job_id}")

            self._job_page_client.open_job_page(job_id)
            content = self._job_page_client.extract_job_content()

            if content:
                job_info = JobInfo(id=job_id, content=content)

                self._save_job_to_db(job_info)
                self._jobs_queue.put(job_info)

                self._logger.info(
                    f"Processed job ({job_id}): {content.title} @ {content.company}"
                )
            else:
                self._logger.warning(f"No content found for job ID: {job_id}")

            self._ids_queue.task_done()

    def _save_job_to_db(self, job_info: JobInfo) -> bool:
        """
        Saves the scraped job information to the database.
        """
        self._logger.info(f"Saving job info to database: {job_info.id}")

        with Session(get_engine()) as session:
            statement = (
                insert(Job)
                .values(
                    id=job_info.id,
                    title=job_info.content.title,
                    company=job_info.content.company,
                    description=job_info.content.description,
                )
                .on_conflict_do_nothing()
            )

        self._logger.info(f"Job info upserted into database: {job_info.id}")
        return True

    def _save_match_to_db(self, match_result: JobMatchResult) -> None:
        """
        Saves the job match result to the database.
        """
        self._logger.info(
            f"Saving match result to database for job ID: {match_result.job_info.id}"
        )

        with Session(get_engine()) as session:
            match = Match(
                job_id=match_result.job_info.id,
                fit=match_result.fit.value,
                reasons=match_result.reasons,
            )
            session.add(match)

    def _check_job_matches(self) -> None:
        """
        Checks job matches for each JobInfo in the jobs queue and puts the results into the database.
        """
        self._logger.info("Starting to check job matches.")

        while not self._jobs_queue.empty():
            job_info = self._jobs_queue.get()

            if job_info is None:
                self._logger.info("No more jobs to process.")

                # Signal to the other threads that no more jobs will be processed
                self._jobs_queue.put(None)
                self._jobs_queue.task_done()
                return

            self._logger.info(f"Checking match for job ID: {job_info.id}")

            match_result = self._job_match_checker.check_job_match(
                self._applicant, job_info
            )

            self._save_match_to_db(match_result)

            self._jobs_queue.task_done()

    def run(self, num_jobs: int = DEFAULT_NUM_JOBS, num_llm_threads: int = 4) -> None:
        """
        Concurrently scrapes job IDs, processes them, and checks job matches.

        NOTE: This method blocks and can only be called once.
        """
        self._logger.info("Starting job match manager.")

        loader_thread = Thread(
            target=self._load_unmatched_jobs, name="UnmatchedJobsLoaderThread"
        )
        loader_thread.start()

        ids_thread = Thread(
            target=self._scrape_job_ids, args=(num_jobs,), name="JobIDScraperThread"
        )
        ids_thread.start()

        process_thread = Thread(
            target=self._process_job_ids, name="JobIDProcessorThread"
        )
        process_thread.start()

        match_executor = ThreadPoolExecutor(max_workers=num_llm_threads)
        for _ in range(num_llm_threads):
            match_executor.submit(self._check_job_matches)

        # Wait for all threads to finish
        loader_thread.join()
        ids_thread.join()
        process_thread.join()
        match_executor.shutdown(wait=True)

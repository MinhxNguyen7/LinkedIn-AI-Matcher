from typing import Generator
from urllib.parse import urljoin

from selenium.webdriver.common.by import By

from linkedin_ai_matcher.utils import sleep_normal

from .linkedin_client import LinkedinClient, NoJobsFound


class RecommendedIdsScraper(LinkedinClient):
    RECOMMENDED_JOBS_URL = urljoin(LinkedinClient.LINKEDIN_URL, "/jobs/recommended/")

    JOB_CARD_CLASS = "job-card-container--clickable"

    def _scrape_recommended_page(self) -> Generator[str, None, None]:
        """
        Scrapes the recommended jobs page and yields job IDs.
        """
        self.driver.get(self.RECOMMENDED_JOBS_URL)
        self.wait_for_element(self.JOB_CARD_CLASS)

        sleep_normal(self.MEAN_DELAY)

        job_cards = self.driver.find_elements(By.CLASS_NAME, self.JOB_CARD_CLASS)
        if not job_cards:
            self.logger.warning("No job cards found on the recommended jobs page.")
            raise NoJobsFound("No recommended jobs found.")

        for job_card in job_cards:
            job_id = job_card.get_attribute("data-job-id")
            if job_id:
                yield job_id

    def scrape_job_ids(self, num_jobs: int) -> Generator[str, None, None]:
        """
        Scrapes IDs of recommended jobs from the LinkedIn jobs page.
        """
        self.driver.get(self.RECOMMENDED_JOBS_URL)

        num_scraped = 0

        while True:
            sleep_normal(self.MEAN_DELAY)
            try:
                for job_id in self._scrape_recommended_page():
                    yield job_id

                    num_scraped += 1
                    if num_scraped >= num_jobs:
                        return

            except NoJobsFound:
                self.logger.info("No more jobs found on the recommended page.")
                break

        self.logger.info(
            f"Scraped {num_scraped} job IDs from the recommended jobs page."
        )

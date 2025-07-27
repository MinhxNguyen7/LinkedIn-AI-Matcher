from typing import Generator
import re
from urllib.parse import urljoin

import numpy as np

from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions

from linkedin_ai_matcher.utils import sleep_normal

from .linkedin_client import LinkedinClient, NoJobsFound


class RecommendedIdsScraper(LinkedinClient):
    RECOMMENDED_JOBS_URL = urljoin(LinkedinClient.LINKEDIN_URL, "/jobs/recommended/")

    JOB_ID_PATTERN = re.compile(r"data-job-id=\"([0-9]+)\"")

    JOB_CARD_CLASS = "job-card-container--clickable"
    NEXT_PAGE_BUTTON_CLASS = "jobs-search-pagination__button--next"

    def __init__(self):
        super().__init__(log_in=True)

    def _scrape_recommended_page(self) -> list[str]:
        """
        Scrapes the recommended jobs page and yields job IDs.
        """
        self.wait_for_element(self.JOB_CARD_CLASS)

        job_list = self.driver.find_element(
            By.CLASS_NAME, "scaffold-layout__list"
        ).find_element(By.TAG_NAME, "ul")

        list_html = job_list.get_attribute("innerHTML")
        if not list_html:
            self.logger.warning("Job list HTML is empty.")
            raise NoJobsFound("No jobs found on the recommended page.")

        job_ids = self._job_ids_from_html(list_html)
        return job_ids

    def _job_ids_from_html(self, html: str) -> list[str]:
        return [match.group(1) for match in self.JOB_ID_PATTERN.finditer(html)]

    def _make_mobile_screen(self) -> None:
        self.driver.set_window_size(412, 915)  # Galaxy S20 Ultra

    def _scroll_to_bottom(self) -> None:
        """
        Slowly scroll down to the bottom of the page to load all job cards.
        """
        target_scroll = self.driver.execute_script("return document.body.scrollHeight")
        target_height = 0

        while True:
            target_height += np.random.rand() * 100 + 250
            self.driver.execute_script(f"window.scrollTo(0, {target_height});")

            new_scroll_height = self.driver.execute_script(
                "return window.pageYOffset + window.innerHeight"
            )
            if np.allclose(new_scroll_height, target_scroll, atol=250):
                break

            sleep_normal(self.MEAN_DELAY)

    def _open_next_page(self) -> None:
        self.driver.find_element(By.CLASS_NAME, self.NEXT_PAGE_BUTTON_CLASS).click()

    def scrape_job_ids(self, num_jobs: int) -> Generator[str, None, None]:
        """
        Scrapes IDs of recommended jobs from the LinkedIn jobs page.
        """
        self.driver.get(self.RECOMMENDED_JOBS_URL)

        num_scraped = 0

        while True:
            self._make_mobile_screen()
            self._scroll_to_bottom()

            try:
                for job_id in self._scrape_recommended_page():
                    yield job_id

                    num_scraped += 1
                    if num_scraped >= num_jobs:
                        return
                    
                    sleep_normal(self.MEAN_DELAY)

            except NoJobsFound:
                self.logger.info("No more jobs found on the recommended page.")
                break

            self._open_next_page()

        self.logger.info(
            f"Scraped {num_scraped} job IDs from the recommended jobs page."
        )

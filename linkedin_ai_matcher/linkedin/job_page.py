from selenium.webdriver.common.by import By
from html_to_markdown import convert_to_markdown

from linkedin_ai_matcher.utils import sleep_normal

from .linkedin_client import LinkedinClient


class JobPageClient(LinkedinClient):
    JOB_DETAILS_ID = "job-details"
    SEE_MORE_BUTTON = "jobs-description__footer-button"

    def _click_see_more_optional(self) -> None:
        """
        Clicks the "See more" button if it exists to expand the job description.

        This is actually not necessary because the description is already in the DOM,
        just hidden. However, this *might* help with anti-bot measures.
        """
        try:
            see_more_button = self.driver.find_element(
                By.CLASS_NAME, self.SEE_MORE_BUTTON
            )
            see_more_button.click()
        except Exception as e:
            self.logger.warning(f"Could not click 'See more' button: {e}")

    def _description_to_markdown(self, description_html: str) -> str:
        """
        Converts the job description HTML to Markdown format,
        cleaning it up in the process by removing empty lines and trailing whitespace.
        """
        markdown = convert_to_markdown(description_html)

        # Remove empty lines and trailing whitespace
        return "\n".join(
            filter(lambda line: line.rstrip() != "", markdown.splitlines())
        )

    def open_job_page(self, job_id: str) -> None:
        """
        Opens the job page for the given job ID.
        """
        job_page_url = self.job_page_from_id(job_id)
        self.driver.get(job_page_url)

        try:
            self.wait_for_element(self.JOB_DETAILS_ID, by=By.ID)
        except Exception as e:
            self.logger.error(f"Failed to open job page for ID {job_id}: {e}")
            raise

        sleep_normal(self.MEAN_DELAY)
        self._click_see_more_optional()

        self.logger.info(f"Opened job page for ID {job_id}: {job_page_url}")

    def extract_job_description(self) -> str | None:
        """
        Extracts the job description from the job page.
        """
        try:
            job_details_element = self.driver.find_element(By.ID, self.JOB_DETAILS_ID)
        except Exception as e:
            self.logger.error(f"Failed to extract job description: {e}")
            return None

        job_details_html = job_details_element.get_attribute("innerHTML")
        if not job_details_html:
            self.logger.warning("Job details HTML is empty.")
            return None

        return self._description_to_markdown(job_details_html)

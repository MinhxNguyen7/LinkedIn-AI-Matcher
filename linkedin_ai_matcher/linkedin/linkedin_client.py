import logging
import os
from urllib.parse import urljoin

import dotenv

from linkedin_ai_matcher.utils import create_logger, sleep_normal

from selenium import webdriver
from selenium.webdriver.common.by import By, ByType
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class ParseError(Exception): ...


class NoJobsFound(Exception): ...


class LinkedinClient:
    MEAN_DELAY = 1
    TIMEOUT = 10

    LINKEDIN_URL = "https://www.linkedin.com/"
    LOGIN_URL = urljoin(LINKEDIN_URL, "login")

    def __init__(
        self,
        driver: webdriver.Chrome | None = None,
        log_in: bool = False,
        chrome_options: webdriver.ChromeOptions | None = None,
        logger: logging.Logger | None = None,
    ):
        self.driver = driver or webdriver.Chrome(options=chrome_options)
        if log_in:
            if not self.login_with_cookie():
                self.logger.info("Cookie login failed, trying email/password login.")
                self.login_with_email_password()

        self.logger = logger or create_logger("linkedin_ai_matcher")

        self.logger.info(f"Initialized {self.__class__.__name__}")

    def wait_for_element(self, value: str, by: ByType = By.CLASS_NAME) -> None:
        """
        Waits for an element to be present in the DOM.
        """
        WebDriverWait(self.driver, self.TIMEOUT).until(
            EC.presence_of_element_located((by, value))
        )

    def job_page_from_id(self, job_id: str) -> str:
        """
        Constructs the job page URL from the job ID.
        """
        return urljoin(self.LINKEDIN_URL, f"/jobs/view/{job_id}/")

    def get_email_password(self) -> tuple[str, str]:
        """
        Retrieves the LinkedIn email and password from environment variables.
        """
        email = os.getenv("LINKEDIN_EMAIL")
        password = os.getenv("LINKEDIN_PASSWORD")

        if not email or not password:
            raise ValueError(
                "LinkedIn email or password not found in environment variables."
            )

        return email, password

    def login_with_cookie(self) -> bool:
        """
        Logs in using cookie (`li_at`) provided in the environment variable.

        Returns:
            bool: True if login was successful, False otherwise.
        """
        cookie = os.getenv("LINKEDIN_COOKIE")
        if not (cookie and cookie.startswith("AQEDAT")):
            return False

        self.driver.get(self.LINKEDIN_URL)
        self.driver.add_cookie({"name": "li_at", "value": cookie})
        self.driver.refresh()

        # Check if login was successful
        try:
            self.wait_for_element("global-nav", By.ID)
            return True
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False

    def login_with_email_password(self) -> None:
        email, password = self.get_email_password()

        self.driver.get(self.LOGIN_URL)
        self.wait_for_element("session_key", By.NAME)

        sleep_normal(self.MEAN_DELAY)
        self.driver.find_element(By.NAME, "session_key").send_keys(email)

        sleep_normal(self.MEAN_DELAY)
        self.driver.find_element(By.NAME, "session_password").send_keys(password)

        sleep_normal(self.MEAN_DELAY)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

    def __del__(self):
        self.driver.quit()

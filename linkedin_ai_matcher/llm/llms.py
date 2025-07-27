from abc import ABC, abstractmethod
import os
from time import time
from typing import Any

from anthropic import Anthropic
from pathlib import Path
from dotenv import load_dotenv

from linkedin_ai_matcher.utils import create_logger

load_dotenv()


class LLM(ABC):
    """
    Abstract base class for Language Model (LLM) implementations.
    """

    def __init__(self, model_name: str, messages_log_dir: Path | None = None):
        """
        Initialize the LLM with a model name.

        :param model_name: The name of the language model.
        """
        self.model_name = model_name
        self.messages_log_dir = messages_log_dir

        if self.messages_log_dir is not None:
            self.messages_log_dir.mkdir(parents=True, exist_ok=True)

        self.logger = create_logger(__class__.__name__, console_output=False)

    def __call__(self, prompt: str) -> str:
        """
        Call the LLM with a prompt to generate text.

        :param prompt: The input text to generate a response for.
        :return: Generated text as a string.
        """
        start = time()
        self.logger.info("Generating text with model '%s'", self.model_name)

        response = None
        try:
            response = self.generate(prompt)

            self.logger.info(
                "Generated text with model '%s': %s. Took %s",
                self.model_name,
                response,
                round(time() - start, 2),
            )

            return response
        except Exception as e:
            self.logger.error(
                "Error generating text with model '%s': %s", self.model_name, str(e)
            )
            raise
        finally:
            self._log(prompt, response, start)

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Abstract method to generate text based on the provided prompt.
        This should not be called directly. Call the instance itself instead.
        """
        return NotImplemented

    def _log(self, prompt: str, response: str | None, timestamp: float):
        """
        Log the prompt and response to files in the messages log directory.
        """
        if self.messages_log_dir is None:
            return
        
        try:
            with open(self.messages_log_dir / f"{int(timestamp)}_prompt.log", "x") as f:
                f.write(prompt)

            if response is not None:
                with open(
                    self.messages_log_dir / f"{int(timestamp)}_response.log", "x"
                ) as f:
                    f.write(response)
        except FileExistsError:
            self.logger.error(
                "Log files already exist for timestamp %s. Skipping logging.",
                int(timestamp),
            )

class AnthropicLLM(LLM):
    """
    Implementation of LLM using Anthropic's language model.
    """

    # Lazy initialization
    _client: Anthropic | None = None

    def __init__(
        self,
        model_name: str = "claude-sonnet-4-20250514",
        messages_log_dir: Path | None = None,
        create_message_kwargs: dict[str, Any] | None = None,
    ):
        """
        Initialize the AnthropicLLM with a model name.

        :param model_name: The name of the Anthropic model to use.
        """
        super().__init__(model_name, messages_log_dir=messages_log_dir)
        self.create_message_kwargs = create_message_kwargs or {}

    @classmethod
    def _get_client(cls) -> Anthropic:
        """
        Get the Anthropic client, initializing it lazily if needed.

        :return: The Anthropic client instance.
        :raises ValueError: If ANTHROPIC_API_KEY environment variable is not set.
        """
        if cls._client is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is required")
            cls._client = Anthropic(api_key=api_key)
        return cls._client

    def generate(self, prompt: str, **create_message_kwargs: dict[str, Any]) -> str:
        """
        Generate text based on the provided prompt using Anthropic's API.

        :param prompt: The input text to generate a response for.
        :return: Generated text as a string.
        :raises Exception: If the API call fails.
        """
        client = self._get_client()

        try:
            kwargs = self.create_message_kwargs.copy()
            kwargs.update(create_message_kwargs)

            response = client.messages.create(
                model=self.model_name,
                max_tokens=2048,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
            return response.content[0].text  # type: ignore
        except Exception as e:
            raise Exception(f"Failed to generate response from Anthropic API: {str(e)}")

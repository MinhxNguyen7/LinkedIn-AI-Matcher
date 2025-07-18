"""
Base classes for models
"""

from pydantic import BaseModel

from linkedin_ai_matcher.utils.text_manipulation import normalize_markup


class Model(BaseModel):
    def __str__(self) -> str:
        """
        Convert the data to an HTML-like markup format.
        """
        return normalize_markup(
            "\n".join(
                f"<{key}>{value}</{key}>" for key, value in self.model_dump().items()
            )
        )

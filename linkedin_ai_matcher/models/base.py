"""
Base classes for models
"""

from pathlib import Path
from typing import Type, TypeVar

from pydantic import BaseModel

from linkedin_ai_matcher.utils.text_manipulation import normalize_markup

ModelSubclass = TypeVar("ModelSubclass", bound="Model")


class Model(BaseModel):
    def save(self, path: Path | str):
        if isinstance(path, str):
            path = Path(path)
        # Save the model data to the specified path
        with open(path, "w") as f:
            f.write(self.model_dump_json())

    @classmethod
    def load(cls: Type[ModelSubclass], path: Path | str) -> ModelSubclass:
        """Load a Model subclass from a JSON file with type validation."""
        if isinstance(path, str):
            path = Path(path)

        with open(path, "r") as f:
            json_data = f.read()

        return cls.model_validate_json(json_data)

    def __str__(self) -> str:
        """
        Convert the data to an HTML-like markup format.
        """
        return normalize_markup(
            "\n".join(
                f"<{key}>{value}</{key}>" for key, value in self.model_dump().items()
            )
        )

    def toJSON(self) -> str:
        """
        Convert the model to a JSON string.
        """
        return self.model_dump_json()

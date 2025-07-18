"""Base model classes for the Personal Assistant application."""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class BaseModel(ABC):
    """Abstract base class for all models in the application."""

    def __init__(self):
        """Initialize the base model with a unique ID and timestamps."""
        self.id: str = str(uuid.uuid4())
        self.created_at: datetime = datetime.now()
        self.modified_at: datetime = datetime.now()

    def update_modified_time(self) -> None:
        """Update the modified timestamp."""
        self.modified_at = datetime.now()

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Convert the model to a dictionary representation."""
        pass

    @abstractmethod
    def from_dict(self, data: dict[str, Any]) -> None:
        """Load the model from a dictionary representation."""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate the model's data."""
        pass

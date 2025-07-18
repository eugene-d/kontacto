"""Note model for the Personal Assistant application."""

from datetime import datetime
from typing import Any, Optional, Set

from ..models.base import BaseModel
from ..utils.validators import ValidationError


class Note(BaseModel):
    """Model representing a note with tags."""

    def __init__(self, content: str, tags: Optional[list[str]] = None):
        """
        Initialize a note.

        Args:
            content: Note content (required)
            tags: List of tags for the note
        """
        super().__init__()
        if not content or not content.strip():
            raise ValidationError("Note content cannot be empty")
        self._content = content.strip()
        self._tags: Set[str] = set()

        if tags:
            for tag in tags:
                self.add_tag(tag)

    @property
    def content(self) -> str:
        """Get note content."""
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        """Set note content with validation."""
        if not value or not value.strip():
            raise ValidationError("Note content cannot be empty")
        self._content = value.strip()
        self.update_modified_time()

    @property
    def tags(self) -> list[str]:
        """Get list of tags."""
        return sorted(list(self._tags))

    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the note.

        Args:
            tag: Tag to add

        Raises:
            ValidationError: If tag is invalid
        """
        tag = self._normalize_tag(tag)
        if not tag:
            raise ValidationError("Tag cannot be empty")
        self._tags.add(tag)
        self.update_modified_time()

    def remove_tag(self, tag: str) -> None:
        """
        Remove a tag from the note.

        Args:
            tag: Tag to remove

        Raises:
            ValidationError: If tag doesn't exist
        """
        tag = self._normalize_tag(tag)
        if tag not in self._tags:
            raise ValidationError(f"Tag '{tag}' not found")
        self._tags.remove(tag)
        self.update_modified_time()

    def has_tag(self, tag: str) -> bool:
        """
        Check if note has a specific tag.

        Args:
            tag: Tag to check

        Returns:
            True if note has the tag
        """
        tag = self._normalize_tag(tag)
        return tag in self._tags

    def matches_search(self, query: str) -> bool:
        """
        Check if note matches search query.

        Args:
            query: Search query string

        Returns:
            True if note matches query
        """
        query_lower = query.lower()

        # Search in content
        if query_lower in self._content.lower():
            return True

        # Search in tags
        for tag in self._tags:
            if query_lower in tag.lower():
                return True

        return False

    def _normalize_tag(self, tag: str) -> str:
        """
        Normalize tag format.

        Args:
            tag: Tag to normalize

        Returns:
            Normalized tag
        """
        # Remove leading/trailing whitespace and convert to lowercase
        normalized = tag.strip().lower()
        # Replace spaces with hyphens
        normalized = normalized.replace(" ", "-")
        # Remove special characters except hyphen and underscore
        normalized = "".join(c for c in normalized if c.isalnum() or c in "-_")
        return normalized

    def to_dict(self) -> dict[str, Any]:
        """Convert note to dictionary representation."""
        return {
            "id": self.id,
            "content": self._content,
            "tags": list(self._tags),
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
        }

    def from_dict(self, data: dict[str, Any]) -> None:
        """Load note from dictionary representation."""
        self.id = data["id"]
        self._content = data["content"]
        self._tags = set(data.get("tags", []))
        self.created_at = datetime.fromisoformat(data["created_at"])
        self.modified_at = datetime.fromisoformat(data["modified_at"])

    def validate(self) -> bool:
        """Validate the note's data."""
        if not self._content or not self._content.strip():
            return False

        # Validate all tags
        for tag in self._tags:
            if not tag or not tag.strip():
                return False

        return True

    def __str__(self) -> str:
        """String representation of the note."""
        content_preview = self._content[:50] + "..." if len(self._content) > 50 else self._content
        return f"Note(content='{content_preview}', tags={len(self._tags)})"

    def __repr__(self) -> str:
        """Developer representation of the note."""
        return f"Note(id='{self.id}', tags={self.tags})"

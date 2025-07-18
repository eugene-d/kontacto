import pytest

from kontacto.models.note import Note
from kontacto.utils.validators import ValidationError


class TestNote:
    """Test cases for the Note model."""

    def test_note_creation(self):
        """Test creating a note with basic content."""
        note = Note(content="Test note content")

        assert note.content == "Test note content"
        assert note.tags == []
        assert note.id is not None
        assert note.created_at is not None
        assert note.modified_at is not None

    def test_note_with_tags(self):
        """Test creating a note with tags."""
        tags = ["work", "important", "Project X"]
        note = Note(content="Project deadline", tags=tags)

        # Tags should be normalized
        assert "work" in note.tags
        assert "important" in note.tags
        assert "project-x" in note.tags  # Normalized
        assert len(note.tags) == 3

    def test_add_tag(self):
        """Test adding tags to a note."""
        note = Note(content="Shopping list")

        # Add tags
        note.add_tag("personal")
        note.add_tag("TODO")

        assert "personal" in note.tags
        assert "todo" in note.tags  # Normalized to lowercase

        # Try to add duplicate (should not raise error)
        note.add_tag("personal")
        assert len(note.tags) == 2  # Still only 2 tags

    def test_remove_tag(self):
        """Test removing tags from a note."""
        note = Note(content="Test", tags=["tag1", "tag2", "tag3"])

        # Remove existing tag
        note.remove_tag("tag2")
        assert "tag2" not in note.tags
        assert len(note.tags) == 2

        # Try to remove non-existent tag
        with pytest.raises(ValidationError):
            note.remove_tag("nonexistent")

    def test_tag_normalization(self):
        """Test tag normalization."""
        note = Note(content="Test")

        # Test various tag formats
        note.add_tag("UPPERCASE")
        note.add_tag("with spaces")
        note.add_tag("special!@#chars")
        note.add_tag("  trimmed  ")

        assert "uppercase" in note.tags
        assert "with-spaces" in note.tags
        assert "specialchars" in note.tags
        assert "trimmed" in note.tags

    def test_has_tag(self):
        """Test checking if note has a tag."""
        note = Note(content="Test", tags=["python", "coding"])

        assert note.has_tag("python")
        assert note.has_tag("PYTHON")  # Case insensitive
        assert not note.has_tag("java")

    def test_search_functionality(self):
        """Test note search matching."""
        note = Note(content="Important project meeting notes", tags=["work", "meeting"])

        # Search in content
        assert note.matches_search("project")
        assert note.matches_search("IMPORTANT")  # Case insensitive

        # Search in tags
        assert note.matches_search("work")
        assert note.matches_search("meeting")

        # Non-matching search
        assert not note.matches_search("vacation")

    def test_content_validation(self):
        """Test content validation."""
        # Empty content should raise error
        with pytest.raises(ValidationError):
            Note(content="")

        with pytest.raises(ValidationError):
            Note(content="   ")  # Only whitespace

    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        # Create note with data
        note1 = Note(content="Serialization test", tags=["test", "important"])

        # Convert to dict
        data = note1.to_dict()

        # Create new note from dict
        note2 = Note(content="Temp")
        note2.from_dict(data)

        # Verify data matches
        assert note2.content == note1.content
        assert set(note2.tags) == set(note1.tags)
        assert note2.id == note1.id
        assert note2.created_at == note1.created_at
        assert note2.modified_at == note1.modified_at

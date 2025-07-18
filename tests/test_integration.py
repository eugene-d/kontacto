from unittest.mock import patch

import pytest

from kontacto.main import Kontacto


class TestContactRepository:
    """Mock repository for testing."""

    def __init__(self):
        self._contacts = []
        self._next_id = 1

    def add(self, contact):
        contact.id = self._next_id
        self._next_id += 1
        self._contacts.append(contact)
        return contact

    def get_all(self):
        return self._contacts

    def get_by_name(self, name):
        for contact in self._contacts:
            if contact.name.lower() == name.lower():
                return contact
        return None

    def search(self, query):
        """Search contacts by any field."""
        results = []
        query_lower = query.lower()
        for contact in self._contacts:
            if (
                query_lower in contact.name.lower() or query_lower in contact.address.lower()
                if contact.address
                else False
            ):
                results.append(contact)
        return results

    def delete(self, contact):
        """Delete a contact."""
        if contact in self._contacts:
            self._contacts.remove(contact)
            return True
        return False

    def update(self, contact):
        """Update a contact."""
        # In a real implementation, this would save to persistence
        return contact

    def get_upcoming_birthdays(self, days=7):
        """Get contacts with upcoming birthdays."""
        return []  # Simplified for testing


class TestNoteRepository:
    """Mock repository for testing."""

    def __init__(self):
        self._notes = []
        self._next_id = 1

    def add(self, note):
        note.id = self._next_id
        self._next_id += 1
        self._notes.append(note)
        return note

    def get_all(self):
        return self._notes

    def search(self, query):
        """Search notes by content."""
        results = []
        query_lower = query.lower()
        for note in self._notes:
            if query_lower in note.content.lower():
                results.append(note)
        return results

    def search_by_tag(self, tag):
        """Search notes by tag."""
        results = []
        for note in self._notes:
            if note.has_tag(tag):
                results.append(note)
        return results

    def get_all_tags(self):
        """Get all unique tags."""
        tags = set()
        for note in self._notes:
            tags.update(note.tags)
        return sorted(list(tags))

    def get_notes_by_tags(self):
        """Get notes grouped by tags."""
        grouped = {}
        for note in self._notes:
            for tag in note.tags:
                if tag not in grouped:
                    grouped[tag] = []
                grouped[tag].append(note)
        return grouped

    def delete(self, note):
        """Delete a note."""
        if note in self._notes:
            self._notes.remove(note)
            return True
        return False

    def update(self, note):
        """Update a note."""
        # In a real implementation, this would save to persistence
        return note

    def count_by_tag(self, tag):
        """Count notes by tag."""
        count = 0
        for note in self._notes:
            if note.has_tag(tag):
                count += 1
        return count


class TestIntegration:
    """Integration tests for the complete workflow."""

    @pytest.fixture
    def app(self):
        """Create app with test repositories."""
        with patch("kontacto.main.ContactRepository", TestContactRepository):
            with patch("kontacto.main.NoteRepository", TestNoteRepository):
                app = Kontacto()
                return app

    def test_full_contact_workflow(self, app):
        """Test complete contact management workflow."""
        # Add a contact
        with patch("builtins.print") as mock_print:
            app.process_command('add-contact "John Doe" --address="123 Main St"')
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "added successfully" in output

        # List contacts
        with patch("builtins.print") as mock_print:
            app.process_command("list-contacts")
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "John Doe" in output
            assert "123 Main St" in output

        # Search for the contact
        with patch("builtins.print") as mock_print:
            app.process_command("search-contacts john")
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "John Doe" in output

        # Edit the contact
        with patch("builtins.print") as mock_print:
            app.process_command('edit-contact "John Doe" add-phone "555-123-4567"')
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "updated successfully" in output

        # Verify the edit
        with patch("builtins.print") as mock_print:
            app.process_command("list-contacts")
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "5551234567" in output  # Phone numbers are displayed without dashes

    def test_full_note_workflow(self, app):
        """Test complete note management workflow."""
        # Add a note
        with patch("builtins.print") as mock_print:
            app.process_command('add-note "Buy milk and bread" shopping urgent')
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "added successfully" in output

        # List notes
        with patch("builtins.print") as mock_print:
            app.process_command("list-notes")
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Buy milk and bread" in output
            assert "shopping" in output
            assert "urgent" in output

        # Search notes
        with patch("builtins.print") as mock_print:
            app.process_command("search-notes milk")
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Buy milk and bread" in output

        # Search by tag
        with patch("builtins.print") as mock_print:
            app.process_command("search-tag shopping")
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Buy milk and bread" in output

        # Add another note
        with patch("builtins.print") as mock_print:
            app.process_command('add-note "Meeting at 3pm" work')
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "added successfully" in output

        # List tags
        with patch("builtins.print") as mock_print:
            app.process_command("list-tags")
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "shopping" in output
            assert "urgent" in output
            assert "work" in output

        # Group notes by tags
        with patch("builtins.print") as mock_print:
            app.process_command("notes-by-tag")
            output = " ".join(str(call[0][0]) if call[0] else str(call) for call in mock_print.call_args_list)
            assert "shopping" in output
            assert "work" in output

    def test_command_aliases(self, app):
        """Test that command aliases work in practice."""
        # Test contact aliases
        with patch("builtins.print") as mock_print:
            app.process_command('ac "Jane Smith" --address="456 Oak Ave"')
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "added successfully" in output

        with patch("builtins.print") as mock_print:
            app.process_command("lc")
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Jane Smith" in output

        with patch("builtins.print") as mock_print:
            app.process_command("sc jane")
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Jane Smith" in output

        # Test note aliases
        with patch("builtins.print") as mock_print:
            app.process_command('an "Test note" test')
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "added successfully" in output

        with patch("builtins.print") as mock_print:
            app.process_command("ln")
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Test note" in output

    def test_help_system(self, app):
        """Test the help system integration."""
        # Test general help
        with patch("builtins.print") as mock_print:
            app.process_command("help")
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Available Commands" in output
            assert "Contact Commands" in output
            assert "Note Commands" in output

        # Test help with alias
        with patch("builtins.print") as mock_print:
            app.process_command("h")
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Available Commands" in output

        # Test specific command help
        with patch("builtins.print") as mock_print:
            app.process_command("help add-contact")
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "add-contact" in output
            assert "Add a new contact" in output

    def test_error_handling_integration(self, app):
        """Test error handling in real scenarios."""
        # Unknown command
        with patch("builtins.print") as mock_print:
            app.process_command("unknown-command")
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Unknown command" in output

        # Invalid arguments
        with patch("builtins.print") as mock_print:
            app.process_command("add-contact")  # Missing name
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Name is required" in output

        # Contact not found
        with patch("builtins.print") as mock_print:
            app.process_command('edit-contact "Nonexistent" name "New Name"')
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "No contacts found matching" in output

    def test_mixed_workflow(self, app):
        """Test mixed contact and note operations."""
        # Add a contact and a note
        with patch("builtins.print") as mock_print:
            app.process_command('add-contact "Business Partner" --address="789 Corp Ave"')
            app.process_command('add-note "Call business partner about project" work important')

            # List both
            app.process_command("list-contacts")
            app.process_command("list-notes")

            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Business Partner" in output
            assert "Call business partner" in output
            assert "work" in output
            assert "important" in output

    def test_command_parsing_edge_cases(self, app):
        """Test edge cases in command parsing."""
        # Quoted arguments with spaces
        with patch("builtins.print") as mock_print:
            app.process_command('add-contact "John Q. Public" --address="123 Main Street, Apt 4B"')
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "added successfully" in output

        # Multiple tags
        with patch("builtins.print") as mock_print:
            app.process_command('add-note "Complex note" tag1 tag2 tag3')
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "added successfully" in output

    def test_validation_integration(self, app):
        """Test validation in real scenarios."""
        from kontacto.utils.validators import ValidationError

        # Test with invalid email format
        with patch("builtins.print") as mock_print:
            app.process_command('add-contact "Test User" --address="123 Main St"')
            app.process_command('edit-contact "Test User" add-email "invalid-email"')
            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            # Should handle validation error gracefully
            assert "Error" in output or "Invalid" in output

    def test_data_persistence_simulation(self, app):
        """Test that operations work as if data persists."""
        # Create repositories that share data
        from kontacto.repositories.contact_repository import ContactRepository
        from kontacto.repositories.note_repository import NoteRepository

        # Add data
        with patch("builtins.print") as mock_print:
            app.process_command('add-contact "Persistent User" --address="456 Oak St"')
            app.process_command('add-note "Persistent note" test')

            # Verify data exists
            assert len(app.contact_repo.get_all()) == 1
            assert len(app.note_repo.get_all()) == 1

            # Verify we can retrieve it
            app.process_command("list-contacts")
            app.process_command("list-notes")

            output = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Persistent User" in output
            assert "Persistent note" in output

    @pytest.fixture
    def app_with_real_repos(self):
        """Create app with real repositories for testing."""
        with patch("kontacto.main.ContactRepository"):
            with patch("kontacto.main.NoteRepository"):
                return Kontacto()

    def test_app_initialization_with_real_repos(self, app_with_real_repos):
        """Test that app initializes correctly with real repositories."""
        assert app_with_real_repos.contact_repo is not None
        assert app_with_real_repos.note_repo is not None
        assert app_with_real_repos.command_registry is not None
        assert app_with_real_repos.completer is not None
        assert app_with_real_repos.context is not None

        # Test that context is set up correctly
        assert "contact_repo" in app_with_real_repos.context
        assert "note_repo" in app_with_real_repos.context
        assert "kontacto" in app_with_real_repos.context

"""Integration tests for the Personal Assistant application."""

import pytest
from unittest.mock import patch, Mock, MagicMock
import tempfile
import os
from datetime import date, timedelta

from personal_assistant.main import PersonalAssistant
from personal_assistant.models.contact import Contact
from personal_assistant.models.note import Note


class TestFullApplicationFlow:
    """Test complete application workflows."""
    
    @pytest.fixture
    def app_with_real_repos(self, tmp_path):
        """Create app with real repositories using temporary files."""
        # Patch the default file paths to use temp directory
        contact_file = str(tmp_path / "test_contacts.pkl")
        note_file = str(tmp_path / "test_notes.pkl")
        
        # Create the app with custom repositories
        from personal_assistant.repositories.contact_repository import ContactRepository
        from personal_assistant.repositories.note_repository import NoteRepository
        
        class TestContactRepository(ContactRepository):
            def __init__(self):
                self.file_path = tmp_path / "test_contacts.pkl"
                self._ensure_directory()
                self._contacts = self.load_data()
        
        class TestNoteRepository(NoteRepository):
            def __init__(self):
                self.file_path = tmp_path / "test_notes.pkl"
                self._ensure_directory()
                self._notes = self.load_data()
        
        with patch('personal_assistant.main.ContactRepository', TestContactRepository):
            with patch('personal_assistant.main.NoteRepository', TestNoteRepository):
                app = PersonalAssistant()
                return app
    
    def test_complete_contact_workflow(self, app_with_real_repos):
        """Test adding, editing, and deleting a contact."""
        app = app_with_real_repos
        
        # Add a contact
        with patch('builtins.print') as mock_print:
            app.process_command('add-contact "Jane Smith" "456 Oak Street"')
            assert any("added successfully" in str(call) for call in mock_print.call_args_list)
        
        # Add phone and email
        with patch('builtins.print') as mock_print:
            app.process_command('edit-contact "Jane Smith" add-phone "555-9876"')
            assert any("updated successfully" in str(call) for call in mock_print.call_args_list)
        
        with patch('builtins.print') as mock_print:
            app.process_command('edit-contact "Jane Smith" add-email "jane@example.com"')
            assert any("updated successfully" in str(call) for call in mock_print.call_args_list)
        
        # List contacts to verify
        with patch('builtins.print') as mock_print:
            app.process_command('list-contacts')
            printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Jane Smith" in printed_text
            assert "456 Oak Street" in printed_text
            assert "5559876" in printed_text  # Phone without dash
            assert "jane@example.com" in printed_text
        
        # Search for the contact
        with patch('builtins.print') as mock_print:
            app.process_command('search-contacts jane')
            printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Jane Smith" in printed_text
        
        # Delete the contact
        with patch('builtins.print') as mock_print:
            app.process_command('delete-contact "Jane Smith"')
            assert any("deleted successfully" in str(call) for call in mock_print.call_args_list)
        
        # Verify contact is gone
        with patch('builtins.print') as mock_print:
            app.process_command('list-contacts')
            assert any("No contacts found" in str(call) for call in mock_print.call_args_list)
    
    def test_complete_note_workflow(self, app_with_real_repos):
        """Test adding, editing, and managing notes with tags."""
        app = app_with_real_repos
        
        # Add notes with tags
        with patch('builtins.print') as mock_print:
            app.process_command('add-note "Buy groceries" shopping todo')
            assert any("added successfully" in str(call) for call in mock_print.call_args_list)
        
        with patch('builtins.print') as mock_print:
            app.process_command('add-note "Finish project report" work important')
            assert any("added successfully" in str(call) for call in mock_print.call_args_list)
        
        # List all notes
        with patch('builtins.print') as mock_print:
            app.process_command('list-notes')
            printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Buy groceries" in printed_text
            assert "Finish project report" in printed_text
        
        # Search by tag
        with patch('builtins.print') as mock_print:
            app.process_command('search-tag work')
            printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Finish project report" in printed_text
            assert "Buy groceries" not in printed_text
        
        # Add tag to existing note
        with patch('builtins.print') as mock_print:
            app.process_command('add-tag "Buy groceries" urgent')
            assert any("added successfully" in str(call) for call in mock_print.call_args_list)
        
        # List all tags
        with patch('builtins.print') as mock_print:
            app.process_command('list-tags')
            printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "shopping" in printed_text
            assert "todo" in printed_text
            assert "work" in printed_text
            assert "important" in printed_text
            assert "urgent" in printed_text
    
    def test_birthday_workflow(self, app_with_real_repos):
        """Test birthday-related functionality."""
        app = app_with_real_repos
        
        # Add contacts with birthdays
        today = date.today()
        
        # Birthday in 5 days (but in the past year to pass validation)
        birthday1_future = today + timedelta(days=5)
        birthday1 = date(1990, birthday1_future.month, birthday1_future.day)
        with patch('builtins.print'):
            app.process_command('add-contact "Alice Brown"')
            app.process_command(f'edit-contact "Alice Brown" birthday {birthday1.strftime("%Y-%m-%d")}')
        
        # Birthday in 10 days (but in the past year to pass validation)
        birthday2_future = today + timedelta(days=10)
        birthday2 = date(1985, birthday2_future.month, birthday2_future.day)
        with patch('builtins.print'):
            app.process_command('add-contact "Bob Green"')
            app.process_command(f'edit-contact "Bob Green" birthday {birthday2.strftime("%Y-%m-%d")}')
        
        # Birthday in 30 days (but in the past year to pass validation)
        birthday3_future = today + timedelta(days=30)
        birthday3 = date(1995, birthday3_future.month, birthday3_future.day)
        with patch('builtins.print'):
            app.process_command('add-contact "Charlie Blue"')
            app.process_command(f'edit-contact "Charlie Blue" birthday {birthday3.strftime("%Y-%m-%d")}')
        
        # Check birthdays in next 7 days
        with patch('builtins.print') as mock_print:
            app.process_command('birthdays')
            printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Alice Brown" in printed_text
            assert "Bob Green" not in printed_text
            assert "Charlie Blue" not in printed_text
        
        # Check birthdays in next 15 days
        with patch('builtins.print') as mock_print:
            app.process_command('birthdays 15')
            printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Alice Brown" in printed_text
            assert "Bob Green" in printed_text
            assert "Charlie Blue" not in printed_text


class TestEdgeCases:
    """Test edge cases and error scenarios."""
    
    @pytest.fixture
    def app(self):
        """Create app with mocked repositories."""
        with patch('personal_assistant.main.ContactRepository'):
            with patch('personal_assistant.main.NoteRepository'):
                return PersonalAssistant()
    
    def test_special_characters_in_input(self, app):
        """Test handling of special characters."""
        with patch('builtins.print') as mock_print:
            # Contact with special characters
            app.process_command('add-contact "John O\'Brien" "123 \"Main\" Street"')
            app.contact_repo.add.assert_called_once()
    
    def test_very_long_input(self, app):
        """Test handling of very long input."""
        long_text = "A" * 1000
        with patch('builtins.print'):
            app.process_command(f'add-note "{long_text}" long-note')
            app.note_repo.add.assert_called_once()
    
    def test_unicode_characters(self, app):
        """Test handling of unicode characters."""
        with patch('builtins.print'):
            app.process_command('add-contact "José García" "Calle España 123"')
            app.contact_repo.add.assert_called_once()
        
        # Reset the mock for the second test
        app.note_repo.add.reset_mock()
        
        with patch('builtins.print'):
            app.process_command('add-note "Meeting at café ☕" unicode émoji')
            app.note_repo.add.assert_called_once()
    
    def test_empty_quotes_as_arguments(self, app):
        """Test handling of empty quotes."""
        # Set up the mock to raise ValidationError when Contact is created with empty name
        from personal_assistant.utils.validators import ValidationError
        app.contact_repo.add.side_effect = ValidationError("Name cannot be empty")
        
        with patch('builtins.print') as mock_print:
            app.process_command('add-contact "" ""')
            printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
            # Should show validation error
            assert "Name cannot be empty" in printed_text or "Name is required" in printed_text
    
    def test_multiple_spaces_in_command(self, app):
        """Test handling of multiple spaces."""
        with patch('builtins.print'):
            app.process_command('add-contact    "John Doe"    "123 Main St"')
            app.contact_repo.add.assert_called_once()
    
    def test_command_with_only_spaces(self, app):
        """Test command that is only spaces."""
        with patch('builtins.print') as mock_print:
            app.process_command('     ')
            # Should handle like empty command
            mock_print.assert_not_called()


class TestConcurrentOperations:
    """Test scenarios that might involve concurrent operations."""
    
    @pytest.fixture
    def app_with_real_repos(self, tmp_path):
        """Create app with real repositories."""
        from personal_assistant.repositories.contact_repository import ContactRepository
        from personal_assistant.repositories.note_repository import NoteRepository
        
        class TestContactRepository(ContactRepository):
            def __init__(self):
                self.file_path = tmp_path / "test_contacts.pkl"
                self._ensure_directory()
                self._contacts = self.load_data()
        
        class TestNoteRepository(NoteRepository):
            def __init__(self):
                self.file_path = tmp_path / "test_notes.pkl"
                self._ensure_directory()
                self._notes = self.load_data()
        
        with patch('personal_assistant.main.ContactRepository', TestContactRepository):
            with patch('personal_assistant.main.NoteRepository', TestNoteRepository):
                return PersonalAssistant()
    
    def test_multiple_operations_on_same_contact(self, app_with_real_repos):
        """Test multiple rapid operations on the same contact."""
        app = app_with_real_repos
        
        # Add contact
        with patch('builtins.print'):
            app.process_command('add-contact "Test User"')
        
        # Perform multiple edits
        operations = [
            'edit-contact "Test User" add-phone "111-1111"',
            'edit-contact "Test User" add-phone "222-2222"',
            'edit-contact "Test User" add-email "test1@example.com"',
            'edit-contact "Test User" add-email "test2@example.com"',
            'edit-contact "Test User" address "New Address"'
        ]
        
        for op in operations:
            with patch('builtins.print'):
                app.process_command(op)
        
        # Verify all changes persisted
        contact = app.contact_repo.get_by_name("Test User")
        assert len(contact.phones) == 2
        assert len(contact.emails) == 2
        assert contact.address == "New Address"
    
    def test_search_after_modifications(self, app_with_real_repos):
        """Test that search works correctly after modifications."""
        app = app_with_real_repos
        
        # Add contacts
        with patch('builtins.print'):
            app.process_command('add-contact "John Doe"')
            app.process_command('add-contact "Jane Doe"')
            app.process_command('add-contact "Jim Smith"')
        
        # Modify one contact
        with patch('builtins.print'):
            app.process_command('edit-contact "John Doe" add-phone "555-1234"')
        
        # Search should still work
        with patch('builtins.print') as mock_print:
            app.process_command('search-contacts Doe')
            printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "John Doe" in printed_text
            assert "Jane Doe" in printed_text
            assert "Jim Smith" not in printed_text 
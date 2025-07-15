"""Unit tests for the main application and command processing."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import sys

from personal_assistant.main import PersonalAssistant
from personal_assistant.repositories.contact_repository import ContactRepository
from personal_assistant.repositories.note_repository import NoteRepository
from personal_assistant.models.contact import Contact
from personal_assistant.models.note import Note


class TestPersonalAssistant:
    """Test cases for the main PersonalAssistant class."""
    
    @pytest.fixture
    def app(self, tmp_path):
        """Create a PersonalAssistant instance with test repositories."""
        # Use temporary files for testing
        with patch('personal_assistant.repositories.contact_repository.ContactRepository.__init__') as mock_contact_init:
            with patch('personal_assistant.repositories.note_repository.NoteRepository.__init__') as mock_note_init:
                # Make the __init__ methods return None
                mock_contact_init.return_value = None
                mock_note_init.return_value = None
                
                app = PersonalAssistant()
                
                # Set up test repositories with temp files
                app.contact_repo.file_path = tmp_path / "test_contacts.pkl"
                app.contact_repo._contacts = []
                app.note_repo.file_path = tmp_path / "test_notes.pkl"
                app.note_repo._notes = []
                
                return app
    
    def test_app_initialization(self, app):
        """Test that the app initializes correctly."""
        assert app is not None
        assert app.contact_repo is not None
        assert app.note_repo is not None
        assert app.command_registry is not None
        assert len(app.command_registry.get_all_commands()) > 0
    
    def test_process_empty_command(self, app):
        """Test processing empty command."""
        with patch('builtins.print') as mock_print:
            app.process_command("")
            # Should not print anything for empty command
            mock_print.assert_not_called()
    
    def test_process_help_command(self, app):
        """Test help command."""
        with patch('builtins.print') as mock_print:
            app.process_command("help")
            
            # Check that help was printed
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Available Commands" in printed_text
            assert "Contact Commands:" in printed_text
            assert "Note Commands:" in printed_text
    
    def test_process_unknown_command(self, app):
        """Test handling of unknown command."""
        with patch('builtins.print') as mock_print:
            app.process_command("unknowncommand")
            
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Unknown command" in printed_text
    
    def test_process_exit_command(self, app):
        """Test exit command."""
        with pytest.raises(SystemExit):
            app.process_command("exit")
    
    def test_command_aliases(self, app):
        """Test that command aliases work."""
        # Test 'q' alias for exit
        with pytest.raises(SystemExit):
            app.process_command("q")
        
        # Test 'h' alias for help
        with patch('builtins.print') as mock_print:
            app.process_command("h")
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Available Commands" in printed_text


class TestContactCommands:
    """Test contact-related commands."""
    
    @pytest.fixture
    def app(self, tmp_path):
        """Create app with mocked repositories."""
        with patch('personal_assistant.main.ContactRepository') as MockContactRepo:
            with patch('personal_assistant.main.NoteRepository') as MockNoteRepo:
                # Create mock instances
                mock_contact_repo = Mock(spec=ContactRepository)
                mock_note_repo = Mock(spec=NoteRepository)
                
                # Configure the mocks to return our instances
                MockContactRepo.return_value = mock_contact_repo
                MockNoteRepo.return_value = mock_note_repo
                
                # Set up default return values
                mock_contact_repo.get_all.return_value = []
                mock_contact_repo.search.return_value = []
                mock_contact_repo.get_by_name.return_value = None
                mock_contact_repo.get_upcoming_birthdays.return_value = []
                
                app = PersonalAssistant()
                return app
    
    def test_add_contact_success(self, app):
        """Test adding a contact successfully."""
        with patch('builtins.print') as mock_print:
            app.process_command('add-contact "John Doe" "123 Main St"')
            
            # Verify contact was added
            app.contact_repo.add.assert_called_once()
            
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "added successfully" in printed_text
    
    def test_add_contact_no_name(self, app):
        """Test adding contact without name."""
        with patch('builtins.print') as mock_print:
            app.process_command('add-contact')
            
            # Should not call add
            app.contact_repo.add.assert_not_called()
            
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Name is required" in printed_text
    
    def test_list_contacts_empty(self, app):
        """Test listing contacts when empty."""
        with patch('builtins.print') as mock_print:
            app.process_command('list-contacts')
            
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "No contacts found" in printed_text
    
    def test_list_contacts_with_data(self, app):
        """Test listing contacts with data."""
        # Create test contacts
        contact1 = Contact("John Doe", "123 Main St")
        contact1.add_phone("555-1234")
        contact1.add_email("john@example.com")
        
        app.contact_repo.get_all.return_value = [contact1]
        
        with patch('builtins.print') as mock_print:
            app.process_command('list-contacts')
            
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Total contacts: 1" in printed_text
            # Check if table is printed (tabulate adds grid characters)
            assert "John Doe" in printed_text
    
    def test_search_contacts_no_query(self, app):
        """Test searching contacts without query."""
        with patch('builtins.print') as mock_print:
            app.process_command('search-contacts')
            
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Search query is required" in printed_text
    
    def test_search_contacts_no_results(self, app):
        """Test searching contacts with no results."""
        with patch('builtins.print') as mock_print:
            app.process_command('search-contacts john')
            
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "No contacts found matching" in printed_text
    
    def test_edit_contact_not_found(self, app):
        """Test editing non-existent contact."""
        with patch('builtins.print') as mock_print:
            app.process_command('edit-contact "John Doe" address "New Address"')
            
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "not found" in printed_text
    
    def test_delete_contact_not_found(self, app):
        """Test deleting non-existent contact."""
        with patch('builtins.print') as mock_print:
            app.process_command('delete-contact "John Doe"')
            
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "not found" in printed_text
    
    def test_birthdays_command(self, app):
        """Test birthdays command."""
        with patch('builtins.print') as mock_print:
            app.process_command('birthdays')
            
            app.contact_repo.get_upcoming_birthdays.assert_called_once_with(7)
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "No birthdays" in printed_text


class TestNoteCommands:
    """Test note-related commands."""
    
    @pytest.fixture
    def app(self, tmp_path):
        """Create app with mocked repositories."""
        with patch('personal_assistant.main.ContactRepository') as MockContactRepo:
            with patch('personal_assistant.main.NoteRepository') as MockNoteRepo:
                # Create mock instances
                mock_contact_repo = Mock(spec=ContactRepository)
                mock_note_repo = Mock(spec=NoteRepository)
                
                # Configure the mocks
                MockContactRepo.return_value = mock_contact_repo
                MockNoteRepo.return_value = mock_note_repo
                
                # Set up default return values
                mock_note_repo.get_all.return_value = []
                mock_note_repo.search.return_value = []
                mock_note_repo.search_by_tag.return_value = []
                mock_note_repo.get_all_tags.return_value = []
                mock_note_repo.get_notes_by_tags.return_value = {}
                
                app = PersonalAssistant()
                return app
    
    def test_add_note_success(self, app):
        """Test adding a note successfully."""
        with patch('builtins.print') as mock_print:
            app.process_command('add-note "Remember to buy milk" shopping')
            
            # Verify note was added
            app.note_repo.add.assert_called_once()
            
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "added successfully" in printed_text
    
    def test_add_note_no_content(self, app):
        """Test adding note without content."""
        with patch('builtins.print') as mock_print:
            app.process_command('add-note')
            
            # Should not call add
            app.note_repo.add.assert_not_called()
            
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Note content is required" in printed_text
    
    def test_list_notes_empty(self, app):
        """Test listing notes when empty."""
        with patch('builtins.print') as mock_print:
            app.process_command('list-notes')
            
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "No notes found" in printed_text
    
    def test_search_notes_no_query(self, app):
        """Test searching notes without query."""
        with patch('builtins.print') as mock_print:
            app.process_command('search-notes')
            
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Search query is required" in printed_text
    
    def test_search_by_tag(self, app):
        """Test searching notes by tag."""
        with patch('builtins.print') as mock_print:
            app.process_command('search-tag work')
            
            app.note_repo.search_by_tag.assert_called_once_with('work')
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "No notes found with tag" in printed_text
    
    def test_list_tags_empty(self, app):
        """Test listing tags when none exist."""
        with patch('builtins.print') as mock_print:
            app.process_command('list-tags')
            
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "No tags found" in printed_text


class TestCommandSuggestions:
    """Test command suggestion functionality."""
    
    @pytest.fixture
    def app(self):
        """Create a PersonalAssistant instance."""
        with patch('personal_assistant.main.ContactRepository'):
            with patch('personal_assistant.main.NoteRepository'):
                return PersonalAssistant()
    
    def test_suggest_similar_command(self, app):
        """Test that similar commands are suggested."""
        with patch('builtins.print') as mock_print:
            # Misspell 'help' as 'hlep'
            app.process_command('hlep')
            
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Unknown command" in printed_text
            assert "Did you mean" in printed_text
            assert "help" in printed_text
    
    def test_suggest_for_partial_command(self, app):
        """Test suggestions for partial commands."""
        with patch('builtins.print') as mock_print:
            # Type partial command
            app.process_command('add-con')
            
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Unknown command" in printed_text
            assert "Did you mean" in printed_text


class TestErrorHandling:
    """Test error handling in various scenarios."""
    
    @pytest.fixture
    def app(self):
        """Create a PersonalAssistant instance."""
        with patch('personal_assistant.main.ContactRepository'):
            with patch('personal_assistant.main.NoteRepository'):
                return PersonalAssistant()
    
    def test_command_execution_error(self, app):
        """Test handling of errors during command execution."""
        # Make a command raise an exception
        with patch.object(app.command_registry.get('help'), 'execute', side_effect=Exception("Test error")):
            with patch('builtins.print') as mock_print:
                app.process_command('help')
                
                printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
                assert "Error executing command" in printed_text
                assert "Test error" in printed_text
    
    def test_invalid_command_arguments(self, app):
        """Test handling of invalid command arguments."""
        with patch('builtins.print') as mock_print:
            # Birthdays with invalid number
            app.process_command('birthdays abc')
            
            printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
            assert "Invalid number of days" in printed_text 
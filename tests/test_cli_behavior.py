"""Tests for CLI behavior and user interaction."""

import pytest
from unittest.mock import patch, Mock, MagicMock, call
import sys
from io import StringIO

from personal_assistant.main import PersonalAssistant, main
from personal_assistant.ui.console import Console


class TestCLIInteraction:
    """Test command line interface interactions."""
    
    def test_main_run_loop_with_exit(self):
        """Test the main run loop with exit command."""
        # Mock prompt to return commands then exit
        commands = ['help', 'exit']
        
        with patch('personal_assistant.main.prompt', side_effect=commands):
            with patch('personal_assistant.main.ContactRepository'):
                with patch('personal_assistant.main.NoteRepository'):
                    with patch('builtins.print') as mock_print:
                        with pytest.raises(SystemExit):
                            app = PersonalAssistant()
                            app.run()
        
        # Verify welcome message was shown
        printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
        assert "Welcome to Personal Assistant" in printed_text
    
    def test_main_run_loop_with_keyboard_interrupt(self):
        """Test handling of Ctrl+C in the main loop."""
        def prompt_side_effect(*args, **kwargs):
            raise KeyboardInterrupt()
        
        with patch('personal_assistant.main.prompt', side_effect=prompt_side_effect):
            with patch('personal_assistant.main.ContactRepository'):
                with patch('personal_assistant.main.NoteRepository'):
                    with patch('builtins.print') as mock_print:
                        app = PersonalAssistant()
                        
                        # Create a generator that will exit after showing warning
                        def exit_after_warning(*args, **kwargs):
                            printed = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
                            if "Use 'exit' command to quit" in printed:
                                raise EOFError()  # Exit the loop
                            raise KeyboardInterrupt()
                        
                        with patch('personal_assistant.main.prompt', side_effect=exit_after_warning):
                            app.run()
        
        # Verify warning message was shown
        printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
        assert "Use 'exit' command to quit" in printed_text
    
    def test_main_run_loop_with_eof(self):
        """Test handling of Ctrl+D (EOF) in the main loop."""
        with patch('personal_assistant.main.prompt', side_effect=EOFError()):
            with patch('personal_assistant.main.ContactRepository'):
                with patch('personal_assistant.main.NoteRepository'):
                    with patch('builtins.print') as mock_print:
                        app = PersonalAssistant()
                        app.run()
        
        # Verify goodbye message was shown
        printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
        assert "Goodbye!" in printed_text
    
    def test_main_function_error_handling(self):
        """Test the main() function error handling."""
        with patch('personal_assistant.main.PersonalAssistant.__init__', side_effect=Exception("Init error")):
            with patch('builtins.print') as mock_print:
                with pytest.raises(SystemExit) as exc_info:
                    main()
        
        # Verify error message was shown
        printed_text = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
        assert "Fatal error" in printed_text
        assert "Init error" in printed_text
        assert exc_info.value.code == 1


class TestConsoleOutput:
    """Test console output formatting."""
    
    def test_console_colors(self):
        """Test that console methods use correct colors."""
        with patch('builtins.print') as mock_print:
            Console.success("Success message")
            Console.error("Error message")
            Console.warning("Warning message")
            Console.info("Info message")
        
        calls = mock_print.call_args_list
        
        # Check that color codes are present
        assert any("✓" in str(call) for call in calls)  # Success
        assert any("✗" in str(call) for call in calls)  # Error
        assert any("⚠" in str(call) for call in calls)  # Warning
        assert any("ℹ" in str(call) for call in calls)  # Info
    
    def test_console_prompt(self):
        """Test console prompt functionality."""
        with patch('builtins.input', return_value="test input"):
            result = Console.prompt("Enter something:")
            assert result == "test input"
        
        with patch('builtins.input', return_value="yes"):
            result = Console.confirm("Are you sure?")
            assert result is True
        
        with patch('builtins.input', return_value="no"):
            result = Console.confirm("Are you sure?")
            assert result is False
    
    def test_console_header(self):
        """Test console header formatting."""
        with patch('builtins.print') as mock_print:
            Console.header("Test Header")
        
        calls = [str(call[0][0]) for call in mock_print.call_args_list]
        
        # Header should have separator lines
        assert any("=" * len("Test Header") in call for call in calls)
        assert any("Test Header" in call for call in calls)


class TestCommandAutocomplete:
    """Test command autocomplete functionality."""
    
    def test_command_completer_suggestions(self):
        """Test that command completer provides suggestions."""
        from personal_assistant.ui.command_completer import CommandCompleter
        from prompt_toolkit.document import Document
        
        commands = ['help', 'add-contact', 'list-contacts', 'add-note']
        completer = CommandCompleter(commands)
        
        # Test partial match
        doc = Document('add')
        mock_event = Mock()
        completions = list(completer.get_completions(doc, mock_event))
        
        # Should suggest add-contact and add-note
        suggestions = [c.text for c in completions]
        assert 'add-contact' in suggestions
        assert 'add-note' in suggestions
        assert 'help' not in suggestions
    
    def test_command_completer_no_suggestions_after_space(self):
        """Test that completer doesn't suggest after space."""
        from personal_assistant.ui.command_completer import CommandCompleter
        from prompt_toolkit.document import Document
        
        commands = ['help', 'add-contact']
        completer = CommandCompleter(commands)
        
        # Test with space (arguments position)
        doc = Document('add-contact ')
        mock_event = Mock()
        completions = list(completer.get_completions(doc, mock_event))
        
        # Should not provide suggestions after space
        assert len(completions) == 0


class TestCommandLineArguments:
    """Test parsing of command line arguments."""
    
    @pytest.fixture
    def app(self):
        """Create app with mocked repositories."""
        with patch('personal_assistant.main.ContactRepository'):
            with patch('personal_assistant.main.NoteRepository'):
                return PersonalAssistant()
    
    def test_quoted_arguments(self, app):
        """Test handling of quoted arguments."""
        # Test double quotes
        with patch('builtins.print'):
            app.process_command('add-contact "John Doe" "123 Main St"')
            
            # Verify the command was parsed correctly
            app.contact_repo.add.assert_called_once()
            call_args = app.contact_repo.add.call_args[0][0]
            assert hasattr(call_args, 'name')
            assert call_args.name == "John Doe"
    
    def test_mixed_quotes(self, app):
        """Test handling of mixed quote types."""
        # This tests the command parsing, not the actual execution
        with patch('builtins.print'):
            app.process_command("add-note 'Note with \"quotes\"' tag")
            
            # Verify note was created with correct content
            call_args = app.note_repo.add.call_args[0][0]
            assert hasattr(call_args, 'content')
    
    def test_arguments_without_quotes(self, app):
        """Test handling of arguments without quotes."""
        with patch('builtins.print'):
            app.process_command('search-contacts john')
            
            # Verify search was called with correct argument
            app.contact_repo.search.assert_called_once_with('john')
    
    def test_multiple_word_arguments(self, app):
        """Test handling of multiple word arguments."""
        with patch('builtins.print'):
            app.process_command('search-contacts john doe smith')
            
            # Should combine into single search query
            app.contact_repo.search.assert_called_once_with('john doe smith')


class TestClearCommand:
    """Test the clear screen command."""
    
    def test_clear_command_posix(self):
        """Test clear command on POSIX systems."""
        with patch('personal_assistant.main.ContactRepository'):
            with patch('personal_assistant.main.NoteRepository'):
                app = PersonalAssistant()
                
                with patch('os.name', 'posix'):
                    with patch('os.system') as mock_system:
                        app.process_command('clear')
                        mock_system.assert_called_once_with('clear')
    
    def test_clear_command_windows(self):
        """Test clear command on Windows."""
        with patch('personal_assistant.main.ContactRepository'):
            with patch('personal_assistant.main.NoteRepository'):
                app = PersonalAssistant()
                
                with patch('os.name', 'nt'):
                    with patch('os.system') as mock_system:
                        app.process_command('clear')
                        mock_system.assert_called_once_with('cls') 
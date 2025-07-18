from unittest.mock import Mock, patch

import pytest

from kontacto.main import Kontacto


class TestKontacto:
    """Test the main Kontacto class."""

    def test_kontacto_initialization(self):
        """Create a Kontacto instance with test repositories."""
        with patch("kontacto.repositories.contact_repository.ContactRepository.__init__") as mock_contact_init:
            with patch("kontacto.repositories.note_repository.NoteRepository.__init__") as mock_note_init:
                mock_contact_init.return_value = None
                mock_note_init.return_value = None

                app = Kontacto()

                # Verify repositories were initialized
                mock_contact_init.assert_called_once()
                mock_note_init.assert_called_once()

                # Verify commands were registered
                assert app.command_registry is not None
                assert len(app.command_registry.get_all_commands()) > 0

                # Verify context was set up
                assert "contact_repo" in app.context
                assert "note_repo" in app.context
                assert "kontacto" in app.context

    def test_command_registry_has_basic_commands(self):
        """Test that basic commands are registered."""
        with patch("kontacto.main.ContactRepository") as MockContactRepo:
            with patch("kontacto.main.NoteRepository") as MockNoteRepo:
                MockContactRepo.return_value = Mock()
                MockNoteRepo.return_value = Mock()

                app = Kontacto()

                # Check that basic commands are registered
                commands = app.command_registry.get_command_names()
                assert "help" in commands
                assert "exit" in commands
                assert "clear" in commands
                assert "add-contact" in commands
                assert "list-contacts" in commands
                assert "add-note" in commands
                assert "list-notes" in commands

    def test_command_execution_success(self):
        """Test successful command execution."""
        with patch("kontacto.main.ContactRepository") as MockContactRepo:
            with patch("kontacto.main.NoteRepository") as MockNoteRepo:
                MockContactRepo.return_value = Mock()
                MockNoteRepo.return_value = Mock()

                app = Kontacto()

                # Mock the command execution
                with patch("builtins.print") as mock_print:
                    app.process_command("help")

                # Verify that help was executed (no exception raised)
                mock_print.assert_called()

    def test_command_execution_with_invalid_command(self):
        """Test command execution with invalid command."""
        with patch("kontacto.main.ContactRepository") as MockContactRepo:
            with patch("kontacto.main.NoteRepository") as MockNoteRepo:
                MockContactRepo.return_value = Mock()
                MockNoteRepo.return_value = Mock()

                app = Kontacto()

                with patch("builtins.print") as mock_print:
                    app.process_command("invalid-command")

                # Verify error message was printed
                print_calls = [str(call) for call in mock_print.call_args_list]
                assert any("Unknown command" in call for call in print_calls)

    def test_command_execution_with_empty_input(self):
        """Test command execution with empty input."""
        with patch("kontacto.main.ContactRepository") as MockContactRepo:
            with patch("kontacto.main.NoteRepository") as MockNoteRepo:
                MockContactRepo.return_value = Mock()
                MockNoteRepo.return_value = Mock()

                app = Kontacto()

                # Empty input should not raise an exception
                app.process_command("")
                app.process_command("   ")
                app.process_command("\t")

    def test_command_execution_with_exception(self):
        """Test command execution when command raises exception."""
        with patch("kontacto.main.ContactRepository") as MockContactRepo:
            with patch("kontacto.main.NoteRepository") as MockNoteRepo:
                MockContactRepo.return_value = Mock()
                MockNoteRepo.return_value = Mock()

                app = Kontacto()

                # Mock a command that raises an exception
                mock_command = Mock()
                mock_command.name = "test-command"
                mock_command.aliases = []
                mock_command.execute.side_effect = Exception("Test error")
                mock_command.validate_args.return_value = True
                app.command_registry.register(mock_command)

                with patch("builtins.print") as mock_print:
                    app.process_command("test-command")

                # Verify error message was printed
                print_calls = [str(call) for call in mock_print.call_args_list]
                assert any("Error executing command" in call for call in print_calls)

    def test_command_aliases(self):
        """Test that command aliases work correctly."""
        with patch("kontacto.main.ContactRepository") as MockContactRepo:
            with patch("kontacto.main.NoteRepository") as MockNoteRepo:
                MockContactRepo.return_value = Mock()
                MockNoteRepo.return_value = Mock()

                app = Kontacto()

                # Test that aliases are properly set up
                help_command = app.command_registry.get("help")
                assert help_command is not None
                assert "h" in help_command.aliases
                assert "?" in help_command.aliases

                exit_command = app.command_registry.get("exit")
                assert exit_command is not None
                assert "quit" in exit_command.aliases
                assert "q" in exit_command.aliases

    def test_kontacto_context_setup(self):
        """Test that the kontacto context is set up correctly."""
        with patch("kontacto.main.ContactRepository") as MockContactRepo:
            with patch("kontacto.main.NoteRepository") as MockNoteRepo:
                MockContactRepo.return_value = Mock()
                MockNoteRepo.return_value = Mock()

                app = Kontacto()

                # Verify context contains the expected objects
                assert "contact_repo" in app.context
                assert "note_repo" in app.context
                assert "kontacto" in app.context
                assert app.context["kontacto"] is app

    def test_command_completer_setup(self):
        """Test that command completer is set up correctly."""
        with patch("kontacto.main.ContactRepository") as MockContactRepo:
            with patch("kontacto.main.NoteRepository") as MockNoteRepo:
                MockContactRepo.return_value = Mock()
                MockNoteRepo.return_value = Mock()

                app = Kontacto()

                # Verify completer is set up
                assert app.completer is not None
                assert hasattr(app.completer, "get_completions")

    @pytest.fixture
    def app(self):
        """Create a Kontacto instance."""
        with patch("kontacto.main.ContactRepository"):
            with patch("kontacto.main.NoteRepository"):
                return Kontacto()

    def test_add_contact_command_registration(self, app):
        """Test that add-contact command is registered."""
        command = app.command_registry.get("add-contact")
        assert command is not None
        assert command.name == "add-contact"
        assert "ac" in command.aliases

    def test_help_command_execution(self, app):
        """Test help command execution."""
        with patch("builtins.print") as mock_print:
            app.process_command("help")

        # Verify help output was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Available Commands" in call for call in print_calls)

    @pytest.fixture
    def app_with_mocked_run(self):
        """Create a Kontacto instance."""
        with patch("kontacto.main.ContactRepository"):
            with patch("kontacto.main.NoteRepository"):
                return Kontacto()

    def test_run_method_setup(self, app_with_mocked_run):
        """Test that run method is available."""
        assert hasattr(app_with_mocked_run, "run")
        assert callable(app_with_mocked_run.run)

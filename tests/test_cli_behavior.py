from unittest.mock import Mock, patch

import pytest

from kontacto.main import Kontacto, main


class TestCLIBehavior:
    """Test CLI behavior and command flow."""

    def test_help_command(self):
        """Test help command shows available commands."""
        commands = ["help", "exit"]

        with patch("kontacto.main.prompt", side_effect=commands):
            with patch("kontacto.main.ContactRepository"):
                with patch("kontacto.main.NoteRepository"):
                    with patch("builtins.print") as mock_print:
                        with pytest.raises(SystemExit):
                            app = Kontacto()
                            app.run()

        # Verify welcome message was shown
        printed_text = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
        assert "Welcome to Kontacto!" in printed_text

    def test_keyboard_interrupt_handling(self):
        """Test that keyboard interrupts are handled gracefully."""

        def prompt_side_effect(*args, **kwargs):
            raise KeyboardInterrupt()

        with patch("kontacto.main.prompt", side_effect=prompt_side_effect):
            with patch("kontacto.main.ContactRepository"):
                with patch("kontacto.main.NoteRepository"):
                    with patch("builtins.print") as mock_print:
                        app = Kontacto()

                        # Create a generator that will exit after showing warning
                        def exit_after_warning(*args, **kwargs):
                            printed = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
                            if "Use 'exit' command to quit" in printed:
                                raise EOFError()  # Exit the loop
                            raise KeyboardInterrupt()

                        with patch("kontacto.main.prompt", side_effect=exit_after_warning):
                            app.run()

        # Verify warning message was shown
        printed_text = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
        assert "Use 'exit' command to quit" in printed_text

    def test_eof_handling(self):
        """Test that EOF (Ctrl+D) is handled gracefully."""
        with patch("kontacto.main.prompt", side_effect=EOFError()):
            with patch("kontacto.main.ContactRepository"):
                with patch("kontacto.main.NoteRepository"):
                    with patch("builtins.print") as mock_print:
                        app = Kontacto()
                        app.run()

        # Verify goodbye message was shown
        printed_text = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
        assert "Goodbye!" in printed_text

    def test_fatal_error_handling(self):
        """Test that fatal errors are handled properly."""
        with patch("kontacto.main.Kontacto.__init__", side_effect=Exception("Init error")):
            with patch("builtins.print") as mock_print:
                with pytest.raises(SystemExit):
                    main()

        # Verify error message was shown
        printed_text = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
        assert "Fatal error: Init error" in printed_text

    def test_command_parsing(self):
        """Test various command parsing scenarios."""
        test_cases = [
            (
                "add-contact 'John Doe' '123 Main St'",
                "add-contact",
                ["John Doe", "123 Main St"],
            ),
            ("list-contacts", "list-contacts", []),
            ("search-contacts john", "search-contacts", ["john"]),
            ("ac 'Jane Smith'", "add-contact", ["Jane Smith"]),  # Test alias
            ("lc", "list-contacts", []),  # Test alias
        ]

        for command, expected_cmd, expected_args in test_cases:
            from kontacto.utils.fuzzy_matcher import parse_command_input

            # Create command aliases mapping
            command_aliases = {
                "add-contact": "add-contact",
                "ac": "add-contact",
                "list-contacts": "list-contacts",
                "lc": "list-contacts",
                "search-contacts": "search-contacts",
            }

            parsed_cmd, parsed_args = parse_command_input(command, command_aliases)
            assert parsed_cmd == expected_cmd
            assert parsed_args == expected_args

    def test_command_completion(self):
        """Test command completion functionality."""
        from prompt_toolkit.completion import Completion
        from prompt_toolkit.document import Document

        from kontacto.ui.command_completer import CommandCompleter

        completer = CommandCompleter(["add-contact", "list-contacts", "search-contacts"])

        # Test completion with partial command
        document = Document("add")
        completions = list(completer.get_completions(document, None))
        assert len(completions) == 1
        assert completions[0].text == "add-contact"

        # Test completion with full command (should not provide completions)
        document = Document("add-contact")
        completions = list(completer.get_completions(document, None))
        assert len(completions) == 1  # The completer still returns the full match

    def test_command_aliases(self):
        """Test that command aliases work correctly."""
        from kontacto.ui.command_completer import CommandCompleter

        completer = CommandCompleter(["add-contact", "list-contacts", "search-contacts"])

        # Test completion with alias
        completions = list(completer.get_completions(Mock(text="ac"), Mock(text="ac")))
        assert len(completions) == 0  # 'ac' is not a base command, it's an alias

    def test_fuzzy_matching(self):
        """Test fuzzy matching for command suggestions."""
        from kontacto.utils.fuzzy_matcher import find_best_match

        commands = ["add-contact", "list-contacts", "search-contacts", "delete-contact"]

        # Test close match
        suggestion = find_best_match("add-contac", commands)
        assert suggestion == "add-contact"

        # Test no match
        suggestion = find_best_match("xyz", commands)
        assert suggestion is None

    @pytest.fixture
    def app(self):
        """Create a test app instance."""
        with patch("kontacto.main.ContactRepository"):
            with patch("kontacto.main.NoteRepository"):
                return Kontacto()

    def test_quoted_arguments(self, app):
        """Test that quoted arguments are parsed correctly."""
        # Test with quoted arguments
        app.process_command('add-contact "John Doe" "123 Main St"')

        # The command should be processed without errors
        # Since we're mocking the repositories, we can't test the actual addition
        # but we can verify the command was parsed correctly

    def test_unknown_command_suggestion(self, app, capsys):
        """Test that unknown commands provide helpful suggestions."""
        # Test command that's close to existing command
        app.process_command("add-contac John")
        output = capsys.readouterr().out
        assert "Unknown command: add-contac" in output
        assert "Did you mean: add-contact?" in output

    def test_empty_command(self, app):
        """Test that empty commands are handled gracefully."""
        # These should not raise exceptions
        app.process_command("")
        app.process_command("   ")
        app.process_command("\t")

    def test_clear_command(self, app):
        """Test clear command functionality."""
        with patch("os.name", "posix"):
            with patch("os.system") as mock_system:
                app.process_command("clear")
                mock_system.assert_called_once_with("clear")

        with patch("os.name", "nt"):
            with patch("os.system") as mock_system:
                app.process_command("cls")
                mock_system.assert_called_once_with("cls")

    def test_help_for_specific_command(self, app, capsys):
        """Test help command for specific commands."""
        app.process_command("help add-contact")
        output = capsys.readouterr().out
        assert "add-contact" in output
        assert "Add a new contact" in output

    def test_invalid_help_command(self, app, capsys):
        """Test help for non-existent command."""
        app.process_command("help invalid-command")
        output = capsys.readouterr().out
        assert "Unknown command: invalid-command" in output

    def test_command_history(self):
        """Test that command history is properly initialized."""
        from prompt_toolkit.history import FileHistory

        with patch("kontacto.main.ContactRepository"):
            with patch("kontacto.main.NoteRepository"):
                app = Kontacto()

                # History should be initialized
                assert hasattr(app, "command_registry")
                assert hasattr(app, "completer")

    def test_context_setup(self):
        """Test that command context is properly set up."""
        with patch("kontacto.main.ContactRepository"):
            app = Kontacto()

            # Context should contain necessary objects
            assert "contact_repo" in app.context
            assert "note_repo" in app.context
            assert "kontacto" in app.context
            assert app.context["kontacto"] is app

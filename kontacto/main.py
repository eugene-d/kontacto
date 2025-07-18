import sys
from typing import Any

from colorama import init as init_colorama
from prompt_toolkit import prompt
from prompt_toolkit.filters import completion_is_selected, has_completions
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import CompleteStyle

from .commands.builtin_commands import ClearCommand, ExitCommand, HelpCommand
from .commands.command_registry import CommandRegistry
from .commands.contact_commands import (
    AddContactCommand,
    CleanContactsCommand,
    DeleteContactCommand,
    EditContactCommand,
    GenerateContactsCommand,
    ListContactsCommand,
    SearchContactsCommand,
    UpcomingBirthdaysCommand,
)
from .commands.note_commands import (
    AddNoteCommand,
    CleanNotesCommand,
    DeleteNoteCommand,
    EditNoteCommand,
    GenerateNotesCommand,
    ListNotesCommand,
    SearchByTagCommand,
    SearchNotesCommand,
)
from .commands.tag_commands import AddTagCommand, CleanTagsCommand, ListTagsCommand, NotesByTagCommand, RemoveTagCommand
from .repositories.contact_repository import ContactRepository
from .repositories.note_repository import NoteRepository
from .ui.command_completer import CommandCompleter
from .ui.console import Console
from .utils.fuzzy_matcher import find_best_match, parse_command_input


class Kontacto:
    """Main application class"""

    def __init__(self):
        # Initialize colorama for Windows support
        init_colorama()

        # Initialize repositories
        self.contact_repo = ContactRepository()
        self.note_repo = NoteRepository()

        self.command_registry = CommandRegistry()
        self._register_commands()

        self.completer = CommandCompleter(self.command_registry.get_command_names())

        self.context: dict[str, Any] = {
            "contact_repo": self.contact_repo,
            "note_repo": self.note_repo,
            "kontacto": self,
        }

        # Set up key bindings for better Tab completion
        self.key_bindings = self._setup_key_bindings()

    def _setup_key_bindings(self) -> KeyBindings:
        """Set up custom key bindings for enhanced completion."""
        bindings = KeyBindings()

        @bindings.add("tab", filter=has_completions)
        def _(event):
            """Handle Tab key for completion cycling."""
            event.app.current_buffer.complete_next()

        @bindings.add("s-tab", filter=has_completions)  # Shift+Tab
        def _(event):
            """Handle Shift+Tab for reverse completion cycling."""
            event.app.current_buffer.complete_previous()

        @bindings.add("enter", filter=completion_is_selected)
        def _(event):
            """Handle Enter key when completion is selected."""
            # Just complete the text without executing
            event.app.current_buffer.complete_state = None
            # Add a space after completion so user can continue typing arguments
            event.app.current_buffer.insert_text(" ")

        @bindings.add("escape", filter=has_completions)
        def _(event):
            """Handle Escape key to cancel completion."""
            event.app.current_buffer.complete_state = None

        return bindings

    def _register_commands(self) -> None:
        # Contact commands
        self.command_registry.register(AddContactCommand())
        self.command_registry.register(ListContactsCommand())
        self.command_registry.register(SearchContactsCommand())
        self.command_registry.register(EditContactCommand())
        self.command_registry.register(DeleteContactCommand())
        self.command_registry.register(UpcomingBirthdaysCommand())
        self.command_registry.register(GenerateContactsCommand())
        self.command_registry.register(CleanContactsCommand())

        # Note commands
        self.command_registry.register(AddNoteCommand())
        self.command_registry.register(ListNotesCommand())
        self.command_registry.register(SearchNotesCommand())
        self.command_registry.register(SearchByTagCommand())
        self.command_registry.register(EditNoteCommand())
        self.command_registry.register(DeleteNoteCommand())
        self.command_registry.register(GenerateNotesCommand())
        self.command_registry.register(CleanNotesCommand())

        # Tag commands
        self.command_registry.register(AddTagCommand())
        self.command_registry.register(RemoveTagCommand())
        self.command_registry.register(ListTagsCommand())
        self.command_registry.register(NotesByTagCommand())
        self.command_registry.register(CleanTagsCommand())

        # Add built-in commands
        self._add_builtin_commands()

    def _add_builtin_commands(self) -> None:
        """Add built-in commands like help and exit."""
        self.command_registry.register(HelpCommand())
        self.command_registry.register(ExitCommand())
        self.command_registry.register(ClearCommand())

    def process_command(self, input_text: str) -> None:
        """
        Process a command input.

        Args:
            input_text: User input text
        """
        if not input_text.strip():
            return

        # Parse command and arguments
        command_aliases = {}
        for cmd_name in self.command_registry.get_command_names():
            cmd = self.command_registry.get(cmd_name)
            if cmd:
                command_aliases[cmd_name] = cmd_name
                for alias in cmd.aliases:
                    command_aliases[alias] = cmd_name

        command_name, args = parse_command_input(input_text, command_aliases)

        if not command_name:
            return

        command = self.command_registry.get(command_name)

        if not command:
            Console.error(f"Unknown command: {command_name}")

            # Suggest similar commands
            suggestions = find_best_match(command_name, self.command_registry.get_command_names())
            if suggestions:
                Console.info(f"Did you mean: {suggestions}?")
            else:
                Console.info("Type 'help' to see available commands.")
            return

        # Validate arguments
        if not command.validate_args(args):
            Console.error("Invalid arguments")
            Console.info(command.usage)
            return

        # Execute command
        try:
            command.execute(args, self.context)
        except Exception as e:
            Console.error(f"Error executing command: {str(e)}")

    def run(self) -> None:
        """Run the main application loop."""
        Console.header("Welcome to Kontacto!")
        Console.info("Type 'help' to see available commands.")
        Console.info("Use Tab to cycle through completions, Shift+Tab to go back, arrow keys for history.\n")

        # Command history
        history = FileHistory(".kontacto_history")

        while True:
            try:
                # Get user input with completion
                user_input = prompt(
                    "kontacto> ",
                    completer=self.completer,
                    complete_style=CompleteStyle.MULTI_COLUMN,
                    complete_while_typing=False,  # Only show completions when Tab is pressed
                    history=history,
                    key_bindings=self.key_bindings,
                )

                self.process_command(user_input)

            except KeyboardInterrupt:
                Console.warning("\nUse 'exit' command to quit.")
            except EOFError:
                # Handle Ctrl+D
                Console.info("\nGoodbye!")
                break


def main():
    """Main entry point."""
    try:
        app = Kontacto()
        app.run()
    except Exception as e:
        Console.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

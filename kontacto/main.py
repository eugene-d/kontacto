import sys
from typing import Any
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import CompleteStyle
from colorama import init as init_colorama

from .commands.base_command import CommandRegistry
from .commands.contact_commands import (
    AddContactCommand, ListContactsCommand, SearchContactsCommand,
    EditContactCommand, DeleteContactCommand, UpcomingBirthdaysCommand,
    GenerateContactsCommand, CleanContactsCommand
)
from .commands.note_commands import (
    AddNoteCommand, ListNotesCommand, SearchNotesCommand,
    SearchByTagCommand, EditNoteCommand, AddTagCommand,
    RemoveTagCommand, DeleteNoteCommand, ListTagsCommand,
    NotesByTagCommand, GenerateNotesCommand, CleanNotesCommand, CleanTagsCommand
)
from .repositories.contact_repository import ContactRepository
from .repositories.note_repository import NoteRepository
from .ui.console import Console
from .ui.command_completer import CommandCompleter
from .utils.fuzzy_matcher import parse_command_input, find_best_match


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
            'contact_repo': self.contact_repo,
            'note_repo': self.note_repo,
            'kontacto': self
        }

    def _register_commands(self) -> None:
        """Register all available commands."""
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
        self.command_registry.register(AddTagCommand())
        self.command_registry.register(RemoveTagCommand())
        self.command_registry.register(DeleteNoteCommand())
        self.command_registry.register(ListTagsCommand())
        self.command_registry.register(NotesByTagCommand())
        self.command_registry.register(GenerateNotesCommand())
        self.command_registry.register(CleanNotesCommand())
        self.command_registry.register(CleanTagsCommand())

        # Add built-in commands
        self._add_builtin_commands()

    def _add_builtin_commands(self) -> None:
        """Add built-in commands like help and exit."""
        from .commands.base_command import BaseCommand

        class HelpCommand(BaseCommand):
            def __init__(self):
                super().__init__()
                self.name = "help"
                self.aliases = ["h", "?"]
                self.description = "Show available commands or help for a specific command"
                self.usage = "help [command]"
                self.examples = ["help", "help add-contact", "? search-notes"]

            def execute(self, args, context):
                kontacto = context['kontacto']

                if args:
                    # Show help for specific command
                    command_name = args[0]
                    command = kontacto.command_registry.get(command_name)

                    if command:
                        print(command.get_help())
                    else:
                        Console.error(f"Unknown command: {command_name}")
                        suggestions = find_best_match(
                            command_name,
                            kontacto.command_registry.get_command_names()
                        )
                        if suggestions:
                            Console.info(f"Did you mean: {suggestions}?")
                else:
                    # Show all commands
                    Console.header("Kontacto - Available Commands")

                    commands = kontacto.command_registry.get_all_commands()

                    # Group commands by category
                    contact_commands = []
                    note_commands = []
                    other_commands = []

                    for cmd in commands:
                        if 'contact' in cmd.name:
                            contact_commands.append(cmd)
                        elif 'note' in cmd.name or 'tag' in cmd.name:
                            note_commands.append(cmd)
                        else:
                            other_commands.append(cmd)

                    # Display commands by category
                    if contact_commands:
                        print("\nContact Commands:")
                        for cmd in sorted(contact_commands, key=lambda x: x.name):
                            aliases = f" ({', '.join(cmd.aliases)})" if cmd.aliases else ""
                            print(f"  {cmd.name:<20} {cmd.description}{aliases}")

                    if note_commands:
                        print("\nNote Commands:")
                        for cmd in sorted(note_commands, key=lambda x: x.name):
                            aliases = f" ({', '.join(cmd.aliases)})" if cmd.aliases else ""
                            print(f"  {cmd.name:<20} {cmd.description}{aliases}")

                    if other_commands:
                        print("\nOther Commands:")
                        for cmd in sorted(other_commands, key=lambda x: x.name):
                            aliases = f" ({', '.join(cmd.aliases)})" if cmd.aliases else ""
                            print(f"  {cmd.name:<20} {cmd.description}{aliases}")

                    print("\nType 'help <command>' for detailed help on a specific command.")

        class ExitCommand(BaseCommand):
            def __init__(self):
                super().__init__()
                self.name = "exit"
                self.aliases = ["quit", "q", "bye"]
                self.description = "Exit the application"
                self.usage = "exit"
                self.examples = ["exit", "quit", "q"]

            def execute(self, args, context):
                Console.info("Goodbye! Thank you for using Kontacto.")
                sys.exit(0)

        class ClearCommand(BaseCommand):
            def __init__(self):
                super().__init__()
                self.name = "clear"
                self.aliases = ["cls"]
                self.description = "Clear the screen"
                self.usage = "clear"
                self.examples = ["clear", "cls"]

            def execute(self, args, context):
                import os
                os.system('clear' if os.name == 'posix' else 'cls')

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
        Console.info("Use Tab for command completion, arrow keys for history.\n")

        # Command history
        history = FileHistory('.kontacto_history')

        while True:
            try:
                # Get user input with completion
                user_input = prompt(
                    "kontacto> ",
                    completer=self.completer,
                    complete_style=CompleteStyle.READLINE_LIKE,
                    history=history
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

"""Command completer for interactive command-line interface."""

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document

from ..utils.fuzzy_matcher import get_command_suggestions


class CommandCompleter(Completer):
    """Completer for command suggestions."""

    def __init__(self, command_names: list[str]):
        """
        Initialize the command completer.

        Args:
            command_names: List of available command names
        """
        self.command_names = command_names

    def get_completions(self, document: Document, complete_event):
        """
        Get completions for the current input.

        Args:
            document: Current document
            complete_event: Completion event

        Yields:
            Completion suggestions
        """
        text = document.text

        # Only complete if we're at the beginning (command position)
        if " " in text:
            return

        text = text.strip()

        if not text:
            return

        suggestions = get_command_suggestions(text, self.command_names)

        if suggestions:
            for suggestion in suggestions:
                yield Completion(
                    suggestion,
                    start_position=-len(text),
                    display=suggestion,
                    display_meta="",
                )
        else:
            yield Completion(
                "help",
                start_position=-len(text),
                display="help",
                display_meta="💡 Type 'help' to see all available commands",
            )

            popular_commands = ["add-contact", "add-note", "list-contacts", "list-notes", "search-contacts"]
            available_popular = [cmd for cmd in popular_commands if cmd in self.command_names]

            for cmd in available_popular[:3]:
                yield Completion(
                    cmd,
                    start_position=-len(text),
                    display=cmd,
                    display_meta="📝 Popular command",
                )

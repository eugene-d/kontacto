"""Base command class for the Command Pattern."""

from abc import ABC, abstractmethod
from typing import Any


class BaseCommand(ABC):
    """Abstract base class for all commands."""

    def __init__(self):
        """Initialize the command."""
        self.name: str = ""
        self.aliases: list[str] = []
        self.description: str = ""
        self.usage: str = ""
        self.examples: list[str] = []

    @abstractmethod
    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        """
        Execute the command.

        Args:
            args: Command arguments
            context: Execution context containing repositories and utilities
        """
        pass

    def validate_args(self, args: list[str]) -> bool:
        """
        Validate command arguments.

        Args:
            args: Command arguments

        Returns:
            True if arguments are valid
        """
        return True

    def get_help(self) -> str:
        """
        Get help text for the command.

        Returns:
            Formatted help text
        """
        help_text = f"\n{self.name}"
        if self.aliases:
            help_text += f" (aliases: {', '.join(self.aliases)})"
        help_text += f"\n{'-' * len(self.name)}\n"
        help_text += f"{self.description}\n\n"
        help_text += f"Usage: {self.usage}\n"

        if self.examples:
            help_text += "\nExamples:\n"
            for example in self.examples:
                help_text += f"  {example}\n"

        return help_text

    def matches(self, command_name: str) -> bool:
        """
        Check if command name matches this command.

        Args:
            command_name: Name to check

        Returns:
            True if name matches command or aliases
        """
        return command_name == self.name or command_name in self.aliases

"""Base command class for the Command Pattern."""

from abc import ABC, abstractmethod
from typing import Any, Optional


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


class CommandRegistry:
    """Registry for managing commands."""

    def __init__(self):
        """Initialize the command registry."""
        self._commands: dict[str, BaseCommand] = {}
        self._aliases: dict[str, str] = {}

    def register(self, command: BaseCommand) -> None:
        """
        Register a command.

        Args:
            command: Command to register

        Raises:
            ValueError: If command name or alias already exists
        """
        if command.name in self._commands:
            raise ValueError(f"Command '{command.name}' already registered")

        self._commands[command.name] = command

        # Register aliases
        for alias in command.aliases:
            if alias in self._aliases:
                raise ValueError(f"Alias '{alias}' already registered")
            self._aliases[alias] = command.name

    def get(self, command_name: str) -> Optional[BaseCommand]:
        """
        Get a command by name or alias.

        Args:
            command_name: Command name or alias

        Returns:
            Command if found, None otherwise
        """
        # Check if it's an alias
        if command_name in self._aliases:
            command_name = self._aliases[command_name]

        return self._commands.get(command_name)

    def get_all_commands(self) -> list[BaseCommand]:
        """
        Get all registered commands.

        Returns:
            List of all commands
        """
        return list(self._commands.values())

    def get_command_names(self) -> list[str]:
        """
        Get all command names and aliases.

        Returns:
            List of command names and aliases
        """
        names = list(self._commands.keys())
        names.extend(self._aliases.keys())
        return sorted(names)

"""Command registry for managing commands."""

from typing import Optional

from .base_command import BaseCommand


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

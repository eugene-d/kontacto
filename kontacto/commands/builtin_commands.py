import os
import sys

from ..ui.console import Console
from ..utils.fuzzy_matcher import find_best_match
from .base_command import BaseCommand


class HelpCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self.name = "help"
        self.aliases = ["h", "?"]
        self.description = "Show available commands or help for a specific command"
        self.usage = "help [command]"
        self.examples = ["help", "help add-contact", "? search-notes"]

    def execute(self, args, context):
        kontacto = context["kontacto"]

        if args:
            # Show help for specific command
            command_name = args[0]
            command = kontacto.command_registry.get(command_name)

            if command:
                print(command.get_help())
            else:
                Console.error(f"Unknown command: {command_name}")
                suggestions = find_best_match(command_name, kontacto.command_registry.get_command_names())
                if suggestions:
                    Console.info(f"Did you mean: {suggestions}?")
        else:
            # Show all commands
            Console.header("Kontacto - Available Commands")

            commands = kontacto.command_registry.get_all_commands()

            # Group commands by category
            contact_commands = []
            note_commands = []
            tag_commands = []
            other_commands = []

            for cmd in commands:
                if "contact" in cmd.name:
                    contact_commands.append(cmd)
                elif cmd.name in ["add-tag", "remove-tag", "list-tags", "notes-by-tag", "clean-tags"]:
                    tag_commands.append(cmd)
                elif "note" in cmd.name or "tag" in cmd.name:
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

            if tag_commands:
                print("\nTag Commands:")
                for cmd in sorted(tag_commands, key=lambda x: x.name):
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
        os.system("clear" if os.name == "posix" else "cls")

from typing import Any

from tabulate import tabulate

from ..commands.base_command import BaseCommand
from ..repositories.note_repository import NoteRepository
from ..ui.console import Console


class AddTagCommand(BaseCommand):
    """Command to add tag to a note."""

    def __init__(self):
        super().__init__()
        self.name = "add-tag"
        self.aliases = ["at"]
        self.description = "Add tag to a note"
        self.usage = "add-tag <search-query> <tag>"
        self.examples = ["add-tag 'buy milk' urgent", "at 'project' important"]

    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        if len(args) < 2:
            Console.error("Search query and tag are required")
            Console.info(self.usage)
            return
        search_query = args[0]
        tag = args[1]
        repo: NoteRepository = context["note_repo"]
        notes = repo.search(search_query)
        if not notes:
            Console.error(f"No notes found matching '{search_query}'")
            return
        if len(notes) > 1:
            Console.warning(f"Found {len(notes)} notes. Adding tag to first match.")
        note = notes[0]
        try:
            note.add_tag(tag)
            repo.update(note)
            Console.success(f"Tag '{tag}' added successfully!")
        except Exception as e:
            Console.error(f"Failed to add tag: {str(e)}")


class RemoveTagCommand(BaseCommand):
    """Command to remove tag from a note."""

    def __init__(self):
        super().__init__()
        self.name = "remove-tag"
        self.aliases = ["rt"]
        self.description = "Remove tag from a note"
        self.usage = "remove-tag '<note>' <tag>"
        self.examples = ["remove-tag 'buy milk' urgent", "rt 'project' old"]

    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        if len(args) < 2:
            Console.error("Search query and tag are required")
            Console.info(self.usage)
            return
        search_query = args[0]
        tag = args[1]
        repo: NoteRepository = context["note_repo"]
        notes = repo.search(search_query)
        if not notes:
            Console.error(f"No notes found matching '{search_query}'")
            return
        if len(notes) > 1:
            Console.warning(f"Found {len(notes)} notes. Removing tag from first match.")
        note = notes[0]
        try:
            note.remove_tag(tag)
            repo.update(note)
            Console.success(f"Tag '{tag}' removed successfully!")
        except Exception as e:
            Console.error(f"Failed to remove tag: {str(e)}")


class ListTagsCommand(BaseCommand):
    """Command to list all tags."""

    def __init__(self):
        super().__init__()
        self.name = "list-tags"
        self.aliases = ["lt"]
        self.description = "List all tags used in notes"
        self.usage = "list-tags"
        self.examples = ["list-tags", "lt"]

    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        repo: NoteRepository = context["note_repo"]
        tags = repo.get_all_tags()
        if not tags:
            Console.info("No tags found")
            return
        table_data = []
        for tag in tags:
            count = repo.count_by_tag(tag)
            table_data.append([tag, count])
        headers = ["Tag", "Note Count"]
        table = tabulate(table_data, headers=headers, tablefmt="grid")
        Console.info(f"\nTotal tags: {len(tags)}")
        print(table)


class NotesByTagCommand(BaseCommand):
    """Command to show notes grouped by tags."""

    def __init__(self):
        super().__init__()
        self.name = "notes-by-tag"
        self.aliases = ["nbt", "grouped"]
        self.description = "Show notes grouped by tags"
        self.usage = "notes-by-tag"
        self.examples = ["notes-by-tag", "nbt"]

    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        repo: NoteRepository = context["note_repo"]
        grouped = repo.get_notes_by_tags()
        if not grouped:
            Console.info("No tagged notes found")
            return
        for tag, notes in grouped.items():
            Console.header(f"Tag: {tag} ({len(notes)} notes)")
            for note in notes:
                content_preview = note.content[:80] + "..." if len(note.content) > 80 else note.content
                created = note.created_at.strftime("%Y-%m-%d %H:%M")
                print(f"  • {content_preview}")
                print(f"    Created: {created}")
                print()


class CleanTagsCommand(BaseCommand):
    """Command to remove all tags from every note, keeping the notes themselves."""

    def __init__(self):
        super().__init__()
        self.name = "clean-tags"
        self.aliases = ["ct", "clear-tags"]
        self.description = "Remove all tags from every note"
        self.usage = "clean-tags"
        self.examples = ["clean-tags", "ct"]

    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        repo: NoteRepository = context["note_repo"]
        notes = repo.get_all()
        if not notes:
            Console.info("No notes found.")
            return
        if not Console.confirm("Are you sure you want to remove ALL tags from every note?"):
            Console.info("Operation cancelled.")
            return
        try:
            for note in notes:
                note._tags.clear() if hasattr(note, "_tags") else None
                repo.update(note)
            Console.success("All tags removed from all notes!")
        except Exception as e:
            Console.error(f"Failed to remove all tags: {str(e)}")

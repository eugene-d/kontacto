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
        self.description = "Add tag to a note (interactive)"
        self.usage = "add-tag"
        self.examples = ["add-tag", "at"]

    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        repo: NoteRepository = context["note_repo"]

        # Get all notes
        all_notes = repo.get_all()

        if not all_notes:
            Console.info("No notes found")
            return

        # Show all notes for selection
        Console.info(f"Found {len(all_notes)} notes:")
        for i, note in enumerate(all_notes):
            content_preview = note.content[:60] + "..." if len(note.content) > 60 else note.content
            tags_str = ", ".join(sorted(note.tags)) if note.tags else "no tags"
            print(f"{i+1}. {content_preview}")
            print(f"   Tags: {tags_str}")

        # Ask user to select a note
        try:
            choice = int(Console.prompt("Select note number (0 to cancel)"))
            if choice == 0:
                return
            if choice < 1 or choice > len(all_notes):
                Console.error("Invalid selection")
                return
            selected_note = all_notes[choice - 1]
        except ValueError:
            Console.error("Invalid input")
            return

        # Ask for tag name
        tag_name = Console.prompt("Enter tag name to add").strip()
        if not tag_name:
            Console.error("Tag name cannot be empty")
            return

        # Add the tag
        try:
            selected_note.add_tag(tag_name)
            repo.update(selected_note)
            Console.success(f"Tag '{tag_name}' added successfully!")
        except Exception as e:
            Console.error(f"Failed to add tag: {str(e)}")


class RemoveTagCommand(BaseCommand):
    """Command to remove tag from a note."""

    def __init__(self):
        super().__init__()
        self.name = "remove-tag"
        self.aliases = ["rt"]
        self.description = "Remove tag from a note (interactive)"
        self.usage = "remove-tag"
        self.examples = ["remove-tag", "rt"]

    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        repo: NoteRepository = context["note_repo"]

        # Get all notes that have tags
        all_notes = repo.get_all()
        notes_with_tags = [note for note in all_notes if note.tags]

        if not notes_with_tags:
            Console.info("No notes with tags found")
            return

        # Show notes with tags for selection
        Console.info(f"Found {len(notes_with_tags)} notes with tags:")
        for i, note in enumerate(notes_with_tags):
            content_preview = note.content[:60] + "..." if len(note.content) > 60 else note.content
            tags_str = ", ".join(sorted(note.tags))
            print(f"{i+1}. {content_preview}")
            print(f"   Tags: {tags_str}")

        # Ask user to select a note
        try:
            choice = int(Console.prompt("Select note number (0 to cancel)"))
            if choice == 0:
                return
            if choice < 1 or choice > len(notes_with_tags):
                Console.error("Invalid selection")
                return
            selected_note = notes_with_tags[choice - 1]
        except ValueError:
            Console.error("Invalid input")
            return

        # Show tags on the selected note
        tags = sorted(selected_note.tags)
        Console.info("\nTags on selected note:")
        for i, tag in enumerate(tags):
            print(f"{i+1}. {tag}")

        # Ask user to select a tag to remove
        try:
            tag_choice = int(Console.prompt("Select tag number to remove (0 to cancel)"))
            if tag_choice == 0:
                return
            if tag_choice < 1 or tag_choice > len(tags):
                Console.error("Invalid selection")
                return
            tag_to_remove = tags[tag_choice - 1]
        except ValueError:
            Console.error("Invalid input")
            return

        # Remove the tag
        try:
            selected_note.remove_tag(tag_to_remove)
            repo.update(selected_note)
            Console.success(f"Tag '{tag_to_remove}' removed successfully!")
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
                print(f"  • {content_preview}")


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

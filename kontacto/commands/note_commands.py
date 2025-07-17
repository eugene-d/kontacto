"""Note-related commands for the Personal Assistant."""

from typing import Any
from tabulate import tabulate
from ..commands.base_command import BaseCommand
from ..models.note import Note
from ..repositories.note_repository import NoteRepository
from ..ui.console import Console
from faker import Faker


class AddNoteCommand(BaseCommand):
    """Command to add a new note."""
    
    def __init__(self):
        super().__init__()
        self.name = "add-note"
        self.aliases = ["an", "new-note"]
        self.description = "Add a new note"
        self.usage = "add-note <content> [tag1] [tag2] ..."
        self.examples = [
            "add-note 'Remember to buy milk' shopping",
            "an 'Project deadline next week' work important"
        ]
    
    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        if len(args) < 1:
            Console.error("Note content is required")
            Console.info(self.usage)
            return
        
        content = args[0]
        tags = args[1:] if len(args) > 1 else []
        
        note = Note(content=content, tags=tags)
        repo: NoteRepository = context['note_repo']
        
        try:
            repo.add(note)
            Console.success(f"Note added successfully with {len(tags)} tag(s)!")
        except Exception as e:
            Console.error(f"Failed to add note: {str(e)}")


class ListNotesCommand(BaseCommand):
    """Command to list all notes."""
    
    def __init__(self):
        super().__init__()
        self.name = "list-notes"
        self.aliases = ["ln", "notes"]
        self.description = "List all notes"
        self.usage = "list-notes"
        self.examples = ["list-notes", "ln"]
    
    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        repo: NoteRepository = context['note_repo']
        notes = repo.get_all()
        
        if not notes:
            Console.info("No notes found")
            return
        
        # Prepare data for table
        table_data = []
        for note in notes:
            content_preview = note.content[:60] + "..." if len(note.content) > 60 else note.content
            tags = ", ".join(note.tags) if note.tags else "N/A"
            created = note.created_at.strftime("%Y-%m-%d %H:%M")
            
            table_data.append([
                content_preview,
                tags,
                created
            ])
        
        headers = ["Content", "Tags", "Created"]
        table = tabulate(table_data, headers=headers, tablefmt="grid")
        
        Console.info(f"\nTotal notes: {len(notes)}")
        print(table)


class SearchNotesCommand(BaseCommand):
    """Command to search notes."""
    
    def __init__(self):
        super().__init__()
        self.name = "search-notes"
        self.aliases = ["sn", "find-notes"]
        self.description = "Search notes by content or tags"
        self.usage = "search-notes <query>"
        self.examples = ["search-notes shopping", "sn important"]
    
    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        if not args:
            Console.error("Search query is required")
            Console.info(self.usage)
            return
        
        query = " ".join(args)
        repo: NoteRepository = context['note_repo']
        notes = repo.search(query)
        
        if not notes:
            Console.info(f"No notes found matching '{query}'")
            return
        
        # Display results
        table_data = []
        for note in notes:
            content_preview = note.content[:60] + "..." if len(note.content) > 60 else note.content
            tags = ", ".join(note.tags) if note.tags else "N/A"
            
            table_data.append([
                content_preview,
                tags
            ])
        
        headers = ["Content", "Tags"]
        table = tabulate(table_data, headers=headers, tablefmt="grid")
        
        Console.info(f"\nFound {len(notes)} note(s) matching '{query}':")
        print(table)


class SearchByTagCommand(BaseCommand):
    """Command to search notes by tag."""
    
    def __init__(self):
        super().__init__()
        self.name = "search-tag"
        self.aliases = ["st", "tag"]
        self.description = "Search notes by tag"
        self.usage = "search-tag <tag>"
        self.examples = ["search-tag work", "st important"]
    
    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        if not args:
            Console.error("Tag is required")
            Console.info(self.usage)
            return
        
        tag = args[0]
        repo: NoteRepository = context['note_repo']
        notes = repo.search_by_tag(tag)
        
        if not notes:
            Console.info(f"No notes found with tag '{tag}'")
            return
        
        # Display results
        table_data = []
        for note in notes:
            content_preview = note.content[:60] + "..." if len(note.content) > 60 else note.content
            all_tags = ", ".join(note.tags)
            
            table_data.append([
                content_preview,
                all_tags
            ])
        
        headers = ["Content", "All Tags"]
        table = tabulate(table_data, headers=headers, tablefmt="grid")
        
        Console.info(f"\nFound {len(notes)} note(s) with tag '{tag}':")
        print(table)


class EditNoteCommand(BaseCommand):
    """Command to edit a note."""
    
    def __init__(self):
        super().__init__()
        self.name = "edit-note"
        self.aliases = ["en", "update-note"]
        self.description = "Edit an existing note (search by content)"
        self.usage = "edit-note <search-query> <new-content>"
        self.examples = [
            "edit-note 'buy milk' 'Buy milk and bread'",
            "en 'project deadline' 'Project deadline moved to Friday'"
        ]
    
    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        if len(args) < 2:
            Console.error("Search query and new content are required")
            Console.info(self.usage)
            return
        
        search_query = args[0]
        new_content = " ".join(args[1:])
        
        repo: NoteRepository = context['note_repo']
        notes = repo.search(search_query)
        
        if not notes:
            Console.error(f"No notes found matching '{search_query}'")
            return
        
        if len(notes) > 1:
            Console.warning(f"Found {len(notes)} notes matching '{search_query}'")
            Console.info("Showing first 5 matches:")
            
            # Show matches
            for i, note in enumerate(notes[:5]):
                content_preview = note.content[:60] + "..." if len(note.content) > 60 else note.content
                print(f"{i+1}. {content_preview}")
            
            # Ask user to select
            try:
                choice = int(Console.prompt("Select note number to edit (0 to cancel)"))
                if choice == 0:
                    return
                if choice < 1 or choice > min(len(notes), 5):
                    Console.error("Invalid selection")
                    return
                note = notes[choice - 1]
            except ValueError:
                Console.error("Invalid input")
                return
        else:
            note = notes[0]
        
        try:
            note.content = new_content
            repo.update(note)
            Console.success("Note updated successfully!")
        except Exception as e:
            Console.error(f"Failed to update note: {str(e)}")


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
        
        repo: NoteRepository = context['note_repo']
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
        self.usage = "remove-tag <search-query> <tag>"
        self.examples = ["remove-tag 'buy milk' urgent", "rt 'project' old"]
    
    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        if len(args) < 2:
            Console.error("Search query and tag are required")
            Console.info(self.usage)
            return
        
        search_query = args[0]
        tag = args[1]
        
        repo: NoteRepository = context['note_repo']
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


class DeleteNoteCommand(BaseCommand):
    """Command to delete a note."""
    
    def __init__(self):
        super().__init__()
        self.name = "delete-note"
        self.aliases = ["dn", "remove-note"]
        self.description = "Delete a note"
        self.usage = "delete-note <search-query>"
        self.examples = ["delete-note 'old reminder'", "dn 'temporary note'"]
    
    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        if not args:
            Console.error("Search query is required")
            Console.info(self.usage)
            return
        
        search_query = " ".join(args)
        repo: NoteRepository = context['note_repo']
        notes = repo.search(search_query)
        
        if not notes:
            Console.error(f"No notes found matching '{search_query}'")
            return
        
        if len(notes) > 1:
            Console.warning(f"Found {len(notes)} notes matching '{search_query}'")
            Console.info("Showing first 5 matches:")
            
            # Show matches
            for i, note in enumerate(notes[:5]):
                content_preview = note.content[:60] + "..." if len(note.content) > 60 else note.content
                print(f"{i+1}. {content_preview}")
            
            # Ask user to select
            try:
                choice = int(Console.prompt("Select note number to delete (0 to cancel)"))
                if choice == 0:
                    return
                if choice < 1 or choice > min(len(notes), 5):
                    Console.error("Invalid selection")
                    return
                note = notes[choice - 1]
            except ValueError:
                Console.error("Invalid input")
                return
        else:
            note = notes[0]
            
        # Confirm deletion
        content_preview = note.content[:60] + "..." if len(note.content) > 60 else note.content
        if not Console.confirm(f"Delete note: '{content_preview}'?"):
            Console.info("Deletion cancelled")
            return
        
        try:
            repo.delete(note.id)
            Console.success("Note deleted successfully!")
        except Exception as e:
            Console.error(f"Failed to delete note: {str(e)}")


class ListTagsCommand(BaseCommand):
    """Command to list all tags."""
    
    def __init__(self):
        super().__init__()
        self.name = "list-tags"
        self.aliases = ["lt", "tags"]
        self.description = "List all tags used in notes"
        self.usage = "list-tags"
        self.examples = ["list-tags", "lt"]
    
    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        repo: NoteRepository = context['note_repo']
        tags = repo.get_all_tags()
        
        if not tags:
            Console.info("No tags found")
            return
        
        # Get count for each tag
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
        repo: NoteRepository = context['note_repo']
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


class GenerateNotesCommand(BaseCommand):
    """Command to generate random test notes."""

    def __init__(self):
        super().__init__()
        self.name = "generate-notes"
        self.aliases = ["gn", "random-notes"]
        self.description = "Generate random test notes"
        self.usage = "generate-notes [count]"
        self.examples = ["generate-notes", "generate-notes 50", "gn 100"]

    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        count = 100
        if args:
            try:
                count = int(args[0])
                if count < 1:
                    Console.error("Count must be a positive number")
                    return
            except ValueError:
                Console.error("Invalid count")
                return

        repo: NoteRepository = context['note_repo']
        fake = Faker()
        Console.info(f"Generating {count} random notes...")

        try:
            for i in range(count):
                content = fake.sentence(nb_words=fake.random_int(5, 15))

                tags = [fake.word() for _ in range(fake.random_int(1, 3))]
                note = Note(content=content, tags=tags)
                repo.add(note)

                if (i + 1) % 10 == 0:
                    Console.info(f"Generated {i + 1}/{count} notes...")

            Console.success(f"Successfully generated {count} random notes!")
        except Exception as e:
            Console.error(f"Failed to generate notes: {str(e)}") 


class CleanNotesCommand(BaseCommand):
    """Command to delete all notes from the repository."""
    def __init__(self):
        super().__init__()
        self.name = "clean-notes"
        self.aliases = ["cn", "clear-notes"]
        self.description = "Delete all notes from the repository"
        self.usage = "clean-notes"
        self.examples = ["clean-notes", "cn"]

    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        repo: NoteRepository = context['note_repo']
        notes = repo.get_all()
        if not notes:
            Console.info("No notes to delete.")
            return
        if not Console.confirm("Are you sure you want to delete ALL notes? This cannot be undone."):
            Console.info("Operation cancelled.")
            return
        try:
            repo._notes.clear() if hasattr(repo, '_notes') else None
            if hasattr(repo, 'save_data'):
                repo.save_data([])
            Console.success("All notes deleted successfully!")
        except Exception as e:
            Console.error(f"Failed to delete all notes: {str(e)}")

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
        repo: NoteRepository = context['note_repo']
        notes = repo.get_all()
        if not notes:
            Console.info("No notes found.")
            return
        if not Console.confirm("Are you sure you want to remove ALL tags from every note?"):
            Console.info("Operation cancelled.")
            return
        try:
            for note in notes:
                note._tags.clear() if hasattr(note, '_tags') else None
                repo.update(note)
            Console.success("All tags removed from all notes!")
        except Exception as e:
            Console.error(f"Failed to remove all tags: {str(e)}") 
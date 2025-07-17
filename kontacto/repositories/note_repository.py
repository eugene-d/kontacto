"""Note repository for managing note persistence."""

from typing import Optional
from collections import defaultdict
from ..models.note import Note
from .base_repository import BaseRepository


class NoteRepository(BaseRepository[Note]):
    """Repository for managing notes."""
    
    def __init__(self, file_path: str = "notes.pkl"):
        """
        Initialize the note repository.
        
        Args:
            file_path: Path to the notes data file
        """
        super().__init__(file_path)
        self._notes: list[Note] = self.load_data()
    
    def add(self, note: Note) -> None:
        """
        Add a new note to the repository.
        
        Args:
            note: Note to add
            
        Raises:
            ValueError: If note with same ID already exists
        """
        if self.exists(note.id):
            raise ValueError(f"Note with ID {note.id} already exists")
        
        self._notes.append(note)
        self.save_data(self._notes)
    
    def get(self, note_id: str) -> Optional[Note]:
        """
        Get a note by ID.
        
        Args:
            note_id: ID of the note to retrieve
            
        Returns:
            Note if found, None otherwise
        """
        for note in self._notes:
            if note.id == note_id:
                return note
        return None
    
    def get_all(self) -> list[Note]:
        """
        Get all notes.
        
        Returns:
            List of all notes
        """
        return self._notes.copy()
    
    def update(self, note: Note) -> None:
        """
        Update an existing note.
        
        Args:
            note: Note with updated information
            
        Raises:
            ValueError: If note doesn't exist
        """
        for i, existing in enumerate(self._notes):
            if existing.id == note.id:
                self._notes[i] = note
                self.save_data(self._notes)
                return
        
        raise ValueError(f"Note with ID {note.id} not found")
    
    def delete(self, note_id: str) -> None:
        """
        Delete a note by ID.
        
        Args:
            note_id: ID of the note to delete
            
        Raises:
            ValueError: If note doesn't exist
        """
        for i, note in enumerate(self._notes):
            if note.id == note_id:
                del self._notes[i]
                self.save_data(self._notes)
                return
        
        raise ValueError(f"Note with ID {note_id} not found")
    
    def search(self, query: str) -> list[Note]:
        """
        Search for notes matching the query.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching notes
        """
        results = []
        for note in self._notes:
            if note.matches_search(query):
                results.append(note)
        return results
    
    def search_by_tag(self, tag: str) -> list[Note]:
        """
        Search for notes with a specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of notes with the tag
        """
        results = []
        for note in self._notes:
            if note.has_tag(tag):
                results.append(note)
        return results
    
    def get_all_tags(self) -> list[str]:
        """
        Get all unique tags used across all notes.
        
        Returns:
            Sorted list of unique tags
        """
        tags = set()
        for note in self._notes:
            tags.update(note.tags)
        return sorted(list(tags))
    
    def get_notes_by_tags(self) -> dict[str, list[Note]]:
        """
        Get notes grouped by tags.
        
        Returns:
            Dictionary mapping tags to lists of notes
        """
        grouped = defaultdict(list)
        for note in self._notes:
            for tag in note.tags:
                grouped[tag].append(note)
        
        # Sort notes within each tag by creation date
        for tag in grouped:
            grouped[tag].sort(key=lambda n: n.created_at)
        
        return dict(grouped)
    
    def count(self) -> int:
        """
        Get the total number of notes.
        
        Returns:
            Number of notes in repository
        """
        return len(self._notes)
    
    def count_by_tag(self, tag: str) -> int:
        """
        Count notes with a specific tag.
        
        Args:
            tag: Tag to count
            
        Returns:
            Number of notes with the tag
        """
        return len(self.search_by_tag(tag))
    
    def load_data(self) -> list[Note]:
        """
        Load notes from file.
        
        Returns:
            List of loaded notes
        """
        data = super().load_data()
        notes = []
        
        # If data is already Note objects, return as is
        if data and isinstance(data[0], Note):
            return data
        
        # Otherwise, convert from dictionaries
        for item in data:
            if isinstance(item, dict):
                note = Note("")  # Temporary content
                note.from_dict(item)
                notes.append(note)
            elif isinstance(item, Note):
                notes.append(item)
        
        return notes 
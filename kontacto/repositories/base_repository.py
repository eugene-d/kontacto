"""Base repository class for data persistence."""

from abc import ABC, abstractmethod
from typing import Optional, Generic, TypeVar
import pickle
from pathlib import Path

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Abstract base class for all repositories."""
    
    def __init__(self, file_path: str):
        """
        Initialize the repository with a file path.
        
        Args:
            file_path: Path to the data file
        """
        self.file_path = Path(file_path)
        self._ensure_directory()
    
    def _ensure_directory(self) -> None:
        """Ensure the directory for the data file exists."""
        directory = self.file_path.parent
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def add(self, item: T) -> None:
        """Add an item to the repository."""
        pass
    
    @abstractmethod
    def get(self, item_id: str) -> Optional[T]:
        """Get an item by ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> list[T]:
        """Get all items from the repository."""
        pass
    
    @abstractmethod
    def update(self, item: T) -> None:
        """Update an existing item."""
        pass
    
    @abstractmethod
    def delete(self, item_id: str) -> None:
        """Delete an item by ID."""
        pass
    
    @abstractmethod
    def search(self, query: str) -> list[T]:
        """Search for items matching the query."""
        pass
    
    def save_data(self, data: list[T]) -> None:
        """
        Save data to file using pickle.
        
        Args:
            data: List of items to save
        """
        try:
            with open(self.file_path, 'wb') as file:
                pickle.dump(data, file)
        except Exception as e:
            raise IOError(f"Failed to save data: {str(e)}")
    
    def load_data(self) -> list[T]:
        """
        Load data from file using pickle.
        
        Returns:
            List of loaded items
        """
        if not self.file_path.exists():
            return []
        
        try:
            with open(self.file_path, 'rb') as file:
                return pickle.load(file)
        except Exception as e:
            # If file is corrupted or incompatible, return empty list
            print(f"Warning: Failed to load data: {str(e)}")
            return []
    
    def clear(self) -> None:
        """Clear all data from the repository."""
        self.save_data([])
    
    def exists(self, item_id: str) -> bool:
        """
        Check if an item exists in the repository.
        
        Args:
            item_id: ID of the item to check
            
        Returns:
            True if item exists
        """
        return self.get(item_id) is not None 
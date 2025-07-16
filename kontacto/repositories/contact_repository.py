"""Contact repository for managing contact persistence."""

from typing import List, Optional
from datetime import date, timedelta
from ..models.contact import Contact
from .base_repository import BaseRepository


class ContactRepository(BaseRepository[Contact]):
    """Repository for managing contacts."""
    
    def __init__(self, file_path: str = "contacts.pkl"):
        """
        Initialize the contact repository.
        
        Args:
            file_path: Path to the contacts data file
        """
        super().__init__(file_path)
        self._contacts: List[Contact] = self.load_data()
    
    def add(self, contact: Contact) -> None:
        """
        Add a new contact to the repository.
        
        Args:
            contact: Contact to add
            
        Raises:
            ValueError: If contact with same ID already exists
        """
        if self.exists(contact.id):
            raise ValueError(f"Contact with ID {contact.id} already exists")
        
        self._contacts.append(contact)
        self.save_data(self._contacts)
    
    def get(self, contact_id: str) -> Optional[Contact]:
        """
        Get a contact by ID.
        
        Args:
            contact_id: ID of the contact to retrieve
            
        Returns:
            Contact if found, None otherwise
        """
        for contact in self._contacts:
            if contact.id == contact_id:
                return contact
        return None
    
    def get_by_name(self, name: str) -> Optional[Contact]:
        """
        Get a contact by name (case-insensitive).
        
        Args:
            name: Name of the contact to retrieve
            
        Returns:
            First matching contact if found, None otherwise
        """
        name_lower = name.lower()
        for contact in self._contacts:
            if contact.name.lower() == name_lower:
                return contact
        return None
    
    def get_all(self) -> List[Contact]:
        """
        Get all contacts.
        
        Returns:
            List of all contacts
        """
        return self._contacts.copy()
    
    def update(self, contact: Contact) -> None:
        """
        Update an existing contact.
        
        Args:
            contact: Contact with updated information
            
        Raises:
            ValueError: If contact doesn't exist
        """
        for i, existing in enumerate(self._contacts):
            if existing.id == contact.id:
                self._contacts[i] = contact
                self.save_data(self._contacts)
                return
        
        raise ValueError(f"Contact with ID {contact.id} not found")
    
    def delete(self, contact_id: str) -> None:
        """
        Delete a contact by ID.
        
        Args:
            contact_id: ID of the contact to delete
            
        Raises:
            ValueError: If contact doesn't exist
        """
        for i, contact in enumerate(self._contacts):
            if contact.id == contact_id:
                del self._contacts[i]
                self.save_data(self._contacts)
                return
        
        raise ValueError(f"Contact with ID {contact_id} not found")
    
    def search(self, query: str) -> List[Contact]:
        """
        Search for contacts matching the query.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching contacts
        """
        results = []
        for contact in self._contacts:
            if contact.matches_search(query):
                results.append(contact)
        return results
    
    def get_upcoming_birthdays(self, days: int = 7) -> List[Contact]:
        """
        Get contacts with birthdays in the next N days.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of contacts with upcoming birthdays
        """
        results = []
        
        for contact in self._contacts:
            if contact.birthday:
                days_until = contact.days_until_birthday()
                if days_until is not None and 0 <= days_until <= days:
                    results.append(contact)
        
        # Sort by days until birthday
        results.sort(key=lambda c: c.days_until_birthday() or 0)
        
        return results
    
    def count(self) -> int:
        """
        Get the total number of contacts.
        
        Returns:
            Number of contacts in repository
        """
        return len(self._contacts)
    
    def load_data(self) -> List[Contact]:
        """
        Load contacts from file.
        
        Returns:
            List of loaded contacts
        """
        data = super().load_data()
        contacts = []
        
        # If data is already Contact objects, return as is
        if data and isinstance(data[0], Contact):
            return data
        
        # Otherwise, convert from dictionaries
        for item in data:
            if isinstance(item, dict):
                contact = Contact("")  # Temporary name
                contact.from_dict(item)
                contacts.append(contact)
            elif isinstance(item, Contact):
                contacts.append(item)
        
        return contacts 
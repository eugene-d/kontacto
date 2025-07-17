"""Contact model for the Personal Assistant application."""

from datetime import date, datetime
from typing import Any, Optional
from ..models.base import BaseModel
from ..utils.validators import validate_phone, validate_email, validate_birthday, ValidationError


class Contact(BaseModel):
    """Model representing a contact with personal information."""
    
    def __init__(self, name: str, address: str = "", birthday: Optional[date] = None):
        """
        Initialize a contact.
        
        Args:
            name: Contact's name (required)
            address: Contact's address
            birthday: Contact's birthday
        """
        super().__init__()
        self._name = name
        self._address = address
        self._phones: list[str] = []
        self._emails: list[str] = []
        self._birthday: Optional[date] = None
        
        if birthday:
            self.birthday = birthday
    
    @property
    def name(self) -> str:
        """Get contact's name."""
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        """Set contact's name with validation."""
        if not value or not value.strip():
            raise ValidationError("Name cannot be empty")
        self._name = value.strip()
        self.update_modified_time()
    
    @property
    def address(self) -> str:
        """Get contact's address."""
        return self._address
    
    @address.setter
    def address(self, value: str) -> None:
        """Set contact's address."""
        self._address = value.strip()
        self.update_modified_time()
    
    @property
    def phones(self) -> list[str]:
        """Get list of phone numbers."""
        return self._phones.copy()
    
    def add_phone(self, phone: str) -> None:
        """
        Add a phone number to the contact.
        
        Args:
            phone: Phone number to add
            
        Raises:
            ValidationError: If phone is invalid or already exists
        """
        validated_phone = validate_phone(phone)
        if validated_phone in self._phones:
            raise ValidationError(f"Phone {phone} already exists")
        self._phones.append(validated_phone)
        self.update_modified_time()
    
    def remove_phone(self, phone: str) -> None:
        """
        Remove a phone number from the contact.
        
        Args:
            phone: Phone number to remove
            
        Raises:
            ValidationError: If phone doesn't exist
        """
        validated_phone = validate_phone(phone)
        if validated_phone not in self._phones:
            raise ValidationError(f"Phone {phone} not found")
        self._phones.remove(validated_phone)
        self.update_modified_time()
    
    @property
    def emails(self) -> list[str]:
        """Get list of email addresses."""
        return self._emails.copy()
    
    def add_email(self, email: str) -> None:
        """
        Add an email address to the contact.
        
        Args:
            email: Email address to add
            
        Raises:
            ValidationError: If email is invalid or already exists
        """
        validated_email = validate_email(email)
        if validated_email in self._emails:
            raise ValidationError(f"Email {email} already exists")
        self._emails.append(validated_email)
        self.update_modified_time()
    
    def remove_email(self, email: str) -> None:
        """
        Remove an email address from the contact.
        
        Args:
            email: Email address to remove
            
        Raises:
            ValidationError: If email doesn't exist
        """
        validated_email = validate_email(email)
        if validated_email not in self._emails:
            raise ValidationError(f"Email {email} not found")
        self._emails.remove(validated_email)
        self.update_modified_time()
    
    @property
    def birthday(self) -> Optional[date]:
        """Get contact's birthday."""
        return self._birthday
    
    @birthday.setter
    def birthday(self, value: Optional[date]) -> None:
        """Set contact's birthday with validation."""
        if value:
            self._birthday = validate_birthday(value)
        else:
            self._birthday = None
        self.update_modified_time()
    
    def days_until_birthday(self) -> Optional[int]:
        """
        Calculate days until next birthday.
        
        Returns:
            Number of days until birthday or None if no birthday set
        """
        if not self._birthday:
            return None
        
        today = date.today()
        this_year_birthday = date(today.year, self._birthday.month, self._birthday.day)
        
        if this_year_birthday < today:
            # Birthday passed this year, calculate for next year
            next_birthday = date(today.year + 1, self._birthday.month, self._birthday.day)
        else:
            next_birthday = this_year_birthday
        
        return (next_birthday - today).days
    
    def matches_search(self, query: str) -> bool:
        """
        Check if contact matches search query.
        
        Args:
            query: Search query string
            
        Returns:
            True if contact matches query
        """
        query_lower = query.lower()
        
        # Search in name
        if query_lower in self._name.lower():
            return True
        
        # Search in address
        if query_lower in self._address.lower():
            return True
        
        # Search in phones
        for phone in self._phones:
            if query in phone:
                return True
        
        # Search in emails
        for email in self._emails:
            if query_lower in email.lower():
                return True
        
        # Search in birthday
        if self._birthday and query in str(self._birthday):
            return True
        
        return False
    
    def to_dict(self) -> dict[str, Any]:
        """Convert contact to dictionary representation."""
        return {
            'id': self.id,
            'name': self._name,
            'address': self._address,
            'phones': self._phones,
            'emails': self._emails,
            'birthday': self._birthday.isoformat() if self._birthday else None,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat()
        }
    
    def from_dict(self, data: dict[str, Any]) -> None:
        """Load contact from dictionary representation."""
        self.id = data['id']
        self._name = data['name']
        self._address = data.get('address', '')
        self._phones = data.get('phones', [])
        self._emails = data.get('emails', [])
        
        if data.get('birthday'):
            self._birthday = date.fromisoformat(data['birthday'])
        else:
            self._birthday = None
        
        self.created_at = datetime.fromisoformat(data['created_at'])
        self.modified_at = datetime.fromisoformat(data['modified_at'])
    
    def validate(self) -> bool:
        """Validate the contact's data."""
        if not self._name or not self._name.strip():
            return False
        
        # Validate all phones
        for phone in self._phones:
            try:
                validate_phone(phone)
            except ValidationError:
                return False
        
        # Validate all emails
        for email in self._emails:
            try:
                validate_email(email)
            except ValidationError:
                return False
        
        # Validate birthday if set
        if self._birthday:
            try:
                validate_birthday(self._birthday)
            except ValidationError:
                return False
        
        return True
    
    def __str__(self) -> str:
        """String representation of the contact."""
        return f"Contact(name='{self._name}', phones={len(self._phones)}, emails={len(self._emails)})"
    
    def __repr__(self) -> str:
        """Developer representation of the contact."""
        return f"Contact(id='{self.id}', name='{self._name}')" 
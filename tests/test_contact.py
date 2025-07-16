import pytest
from datetime import date
from kontacto.models.contact import Contact
from kontacto.utils.validators import ValidationError


class TestContact:
    """Test cases for the Contact model."""

    def test_contact_creation(self):
        """Test creating a contact with basic information."""
        contact = Contact(name="John Doe", address="123 Main St")

        assert contact.name == "John Doe"
        assert contact.address == "123 Main St"
        assert contact.phones == []
        assert contact.emails == []
        assert contact.birthday is None
        assert contact.id is not None

    def test_add_phone(self):
        """Test adding phone numbers to a contact."""
        contact = Contact(name="Jane Smith")

        # Add valid phone
        contact.add_phone("555-1234")
        assert len(contact.phones) == 1

        # Try to add duplicate
        with pytest.raises(ValidationError):
            contact.add_phone("555-1234")

    def test_add_email(self):
        """Test adding email addresses to a contact."""
        contact = Contact(name="Bob Johnson")

        # Add valid email
        contact.add_email("bob@example.com")
        assert len(contact.emails) == 1
        assert contact.emails[0] == "bob@example.com"

        # Try to add invalid email
        with pytest.raises(ValidationError):
            contact.add_email("invalid-email")

    def test_birthday_validation(self):
        """Test birthday validation."""
        contact = Contact(name="Alice Brown")

        # Set valid birthday
        valid_date = date(1990, 1, 15)
        contact.birthday = valid_date
        assert contact.birthday == valid_date

        # Try to set future date
        future_date = date(2030, 1, 1)
        with pytest.raises(ValidationError):
            contact.birthday = future_date

    def test_days_until_birthday(self):
        """Test birthday calculation."""
        contact = Contact(name="Charlie Davis")

        # No birthday set
        assert contact.days_until_birthday() is None

        # Set birthday
        today = date.today()
        birthday = date(1990, today.month, today.day)
        contact.birthday = birthday

        # Birthday is today
        assert contact.days_until_birthday() == 0

    def test_search_functionality(self):
        """Test contact search matching."""
        contact = Contact(name="Test User", address="Test Address")
        contact.add_phone("123-456-7890")
        contact.add_email("test@example.com")

        # Test various search queries
        assert contact.matches_search("Test")
        assert contact.matches_search("user")
        assert contact.matches_search("Address")
        assert contact.matches_search("123")
        assert contact.matches_search("example.com")
        assert not contact.matches_search("nonexistent")

    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        # Create contact with data
        contact1 = Contact(name="Serialize Test", address="123 Test St")
        contact1.add_phone("555-0000")
        contact1.add_email("test@test.com")
        contact1.birthday = date(1985, 5, 15)

        # Convert to dict
        data = contact1.to_dict()

        # Create new contact from dict
        contact2 = Contact(name="Temp")
        contact2.from_dict(data)

        # Verify data matches
        assert contact2.name == contact1.name
        assert contact2.address == contact1.address
        assert contact2.phones == contact1.phones
        assert contact2.emails == contact1.emails
        assert contact2.birthday == contact1.birthday
        assert contact2.id == contact1.id

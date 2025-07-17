from typing import List, Dict, Any
from datetime import date
from tabulate import tabulate
from faker import Faker
from ..commands.base_command import BaseCommand
from ..models.contact import Contact
from ..repositories.contact_repository import ContactRepository
from ..utils.validators import parse_date, ValidationError
from ..ui.console import Console


class AddContactCommand(BaseCommand):
    """Command to add a new contact."""

    def __init__(self):
        super().__init__()
        self.name = "add-contact"
        self.aliases = ["ac", "new-contact"]
        self.description = "Add a new contact"
        self.usage = "add-contact <name> [address]"
        self.examples = [
            "add-contact 'John Doe' '123 Main St, City'",
            "ac 'Jane Smith'"
        ]

    def execute(self, args: List[str], context: Dict[str, Any]) -> None:
        if len(args) < 1:
            Console.error("Name is required")
            Console.info(self.usage)
            return

        name = args[0]
        address = " ".join(args[1:]) if len(args) > 1 else ""

        contact = Contact(name=name, address=address)
        repo: ContactRepository = context['contact_repo']

        try:
            repo.add(contact)
            Console.success(f"Contact '{name}' added successfully!")
        except Exception as e:
            Console.error(f"Failed to add contact: {str(e)}")


class ListContactsCommand(BaseCommand):
    """Command to list all contacts."""

    def __init__(self):
        super().__init__()
        self.name = "list-contacts"
        self.aliases = ["lc", "contacts"]
        self.description = "List all contacts"
        self.usage = "list-contacts"
        self.examples = ["list-contacts", "lc"]

    def execute(self, args: List[str], context: Dict[str, Any]) -> None:
        repo: ContactRepository = context['contact_repo']
        contacts = repo.get_all()

        if not contacts:
            Console.info("No contacts found")
            return

        # Prepare data for table
        table_data = []
        for contact in contacts:
            phones = ", ".join(contact.phones) if contact.phones else "N/A"
            emails = ", ".join(contact.emails) if contact.emails else "N/A"
            birthday = contact.birthday.strftime("%Y-%m-%d") if contact.birthday else "N/A"

            table_data.append([
                contact.name,
                contact.address or "N/A",
                phones,
                emails,
                birthday
            ])

        headers = ["Name", "Address", "Phones", "Emails", "Birthday"]
        table = tabulate(table_data, headers=headers, tablefmt="grid")

        Console.info(f"\nTotal contacts: {len(contacts)}")
        print(table)


class SearchContactsCommand(BaseCommand):
    """Command to search contacts."""

    def __init__(self):
        super().__init__()
        self.name = "search-contacts"
        self.aliases = ["sc", "find-contacts"]
        self.description = "Search contacts by any field"
        self.usage = "search-contacts <query>"
        self.examples = ["search-contacts john", "sc 555-1234"]

    def execute(self, args: List[str], context: Dict[str, Any]) -> None:
        if not args:
            Console.error("Search query is required")
            Console.info(self.usage)
            return

        query = " ".join(args)
        repo: ContactRepository = context['contact_repo']
        contacts = repo.search(query)

        if not contacts:
            Console.info(f"No contacts found matching '{query}'")
            return

        # Display results
        table_data = []
        for contact in contacts:
            phones = ", ".join(contact.phones) if contact.phones else "N/A"
            emails = ", ".join(contact.emails) if contact.emails else "N/A"

            table_data.append([
                contact.name,
                contact.address or "N/A",
                phones,
                emails
            ])

        headers = ["Name", "Address", "Phones", "Emails"]
        table = tabulate(table_data, headers=headers, tablefmt="grid")

        Console.info(f"\nFound {len(contacts)} contact(s) matching '{query}':")
        print(table)


class EditContactCommand(BaseCommand):
    """Command to edit a contact."""

    def __init__(self):
        super().__init__()
        self.name = "edit-contact"
        self.aliases = ["ec", "update-contact"]
        self.description = "Edit an existing contact"
        self.usage = "edit-contact <name> <field> <value>"
        self.examples = [
            "edit-contact 'John Doe' address '456 New St'",
            "ec 'Jane Smith' add-phone '555-1234'",
            "edit-contact 'Bob' birthday '1990-01-15'"
        ]

    def execute(self, args: List[str], context: Dict[str, Any]) -> None:
        if len(args) < 3:
            Console.error("Name, field, and value are required")
            Console.info(self.usage)
            return

        name = args[0]
        field = args[1].lower()
        value = " ".join(args[2:])

        repo: ContactRepository = context['contact_repo']
        contact = repo.get_by_name(name)

        if not contact:
            Console.error(f"Contact '{name}' not found")
            return

        try:
            if field == "name":
                contact.name = value
            elif field == "address":
                contact.address = value
            elif field == "add-phone":
                contact.add_phone(value)
            elif field == "remove-phone":
                contact.remove_phone(value)
            elif field == "add-email":
                contact.add_email(value)
            elif field == "remove-email":
                contact.remove_email(value)
            elif field == "birthday":
                birthday = parse_date(value)
                if birthday:
                    contact.birthday = birthday
                else:
                    Console.error("Invalid date format. Use YYYY-MM-DD")
                    return
            else:
                Console.error(f"Unknown field: {field}")
                Console.info("Available fields: name, address, add-phone, remove-phone, add-email, remove-email, birthday")
                return

            repo.update(contact)
            Console.success(f"Contact '{name}' updated successfully!")

        except ValidationError as e:
            Console.error(f"Validation error: {str(e)}")
        except Exception as e:
            Console.error(f"Failed to update contact: {str(e)}")


class DeleteContactCommand(BaseCommand):
    """Command to delete a contact."""

    def __init__(self):
        super().__init__()
        self.name = "delete-contact"
        self.aliases = ["dc", "remove-contact"]
        self.description = "Delete a contact"
        self.usage = "delete-contact <name>"
        self.examples = ["delete-contact 'John Doe'", "dc 'Jane Smith'"]

    def execute(self, args: List[str], context: Dict[str, Any]) -> None:
        if not args:
            Console.error("Contact name is required")
            Console.info(self.usage)
            return

        name = " ".join(args)
        repo: ContactRepository = context['contact_repo']
        contact = repo.get_by_name(name)

        if not contact:
            Console.error(f"Contact '{name}' not found")
            return

        try:
            repo.delete(contact.id)
            Console.success(f"Contact '{name}' deleted successfully!")
        except Exception as e:
            Console.error(f"Failed to delete contact: {str(e)}")


class UpcomingBirthdaysCommand(BaseCommand):
    """Command to show upcoming birthdays."""

    def __init__(self):
        super().__init__()
        self.name = "birthdays"
        self.aliases = ["bd", "upcoming-birthdays"]
        self.description = "Show upcoming birthdays"
        self.usage = "birthdays [days]"
        self.examples = ["birthdays", "birthdays 30", "bd 7"]

    def execute(self, args: List[str], context: Dict[str, Any]) -> None:
        days = 7  # Default to 7 days

        if args:
            try:
                days = int(args[0])
                if days < 0:
                    Console.error("Days must be a positive number")
                    return
            except ValueError:
                Console.error("Invalid number of days")
                return

        repo: ContactRepository = context['contact_repo']
        contacts = []

        # We iterate over all contacts and select only those whose birthday is in N days
        for contact in repo.get_all():
            days_left = contact.days_until_birthday()
            if days_left is not None and days_left == days:
                contacts.append(contact)

        if not contacts:
            Console.info(f"No contacts with birthdays in the next {days} day(s).")
            return

        # Prepare data for table
        table_data = []
        for contact in contacts:
            birthday_str = contact.birthday.strftime("%Y-%m-%d") if contact.birthday else "N/A"
            table_data.append([
                contact.name,
                birthday_str,
                f"{days} days",
            ])

        headers = ["Name", "Birthday", "Days Until"]
        table = tabulate(table_data, headers=headers, tablefmt="grid")

        Console.info(f"\nBirthdays in the next {days} days:")
        print(table)


class GenerateContactsCommand(BaseCommand):
    """Command to generate random test contacts."""

    def __init__(self):
        super().__init__()
        self.name = "generate-contacts"
        self.aliases = ["gc", "random-contacts"]
        self.description = "Generate random test contacts"
        self.usage = "generate-contacts [count]"
        self.examples = ["generate-contacts", "generate-contacts 50", "gc 100"]

    def execute(self, args: List[str], context: Dict[str, Any]) -> None:
        count = 100  # Default to 100 contacts

        if args:
            try:
                count = int(args[0])
                if count < 1:
                    Console.error("Count must be a positive number")
                    return
            except ValueError:
                Console.error("Invalid count")
                return

        repo: ContactRepository = context['contact_repo']
        fake = Faker()

        Console.info(f"Generating {count} random contacts...")

        try:
            for i in range(count):
                contact = Contact(
                    name=fake.name(),
                    address=fake.address().replace('\n', ', ')
                )

                # Add random phone numbers (1-3)
                for _ in range(fake.random_int(1, 3)):
                    try:
                        contact.add_phone(fake.phone_number())
                    except:
                        pass  # Skip invalid phone numbers

                # Add random emails (1-2)
                for _ in range(fake.random_int(1, 2)):
                    try:
                        contact.add_email(fake.email())
                    except:
                        pass

                # Add random birthday (60% chance)
                if fake.random_int(1, 10) <= 6:
                    contact.birthday = fake.date_of_birth(minimum_age=18, maximum_age=80)

                repo.add(contact)

                # Show progress
                if (i + 1) % 10 == 0:
                    Console.info(f"Generated {i + 1}/{count} contacts...")

            Console.success(f"Successfully generated {count} random contacts!")

        except Exception as e:
            Console.error(f"Failed to generate contacts: {str(e)}")

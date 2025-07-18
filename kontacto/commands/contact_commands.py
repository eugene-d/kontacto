from datetime import datetime
from typing import Any

from faker import Faker
from tabulate import tabulate

from ..commands.base_command import BaseCommand
from ..models.contact import Contact
from ..repositories.contact_repository import ContactRepository
from ..ui.console import Console
from ..utils.validators import ValidationError, parse_date


class AddContactCommand(BaseCommand):
    """Command to add a new contact."""

    def __init__(self):
        super().__init__()
        self.name = "add-contact"
        self.aliases = ["ac", "new-contact"]
        self.description = "Add a new contact"
        self.usage = "add-contact <name> [--address=<address>] [--email=<email>] [--phone=<phone>] [--birthday=<date>]"
        self.examples = [
            "add-contact John --address='123 Main St' --email=john@example.com --phone=0501234567 --birthday=15.04.1990",
            "ac 'Jane Smith' --phone=0501234567",
            "add-contact John --addr='123 Main St' --bday=15.04.1990",
        ]

    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        if len(args) < 1:
            Console.error("Name is required")
            Console.info(self.usage)
            return

        # Parse arguments: first arg is name, rest are flags
        name = args[0]
        parsed_args = self._parse_flags(args[1:])

        if parsed_args is None:
            return  # Error already displayed

        # Extract values from parsed flags
        address = parsed_args.get("address", "")
        emails = parsed_args.get("emails", [])
        phones = parsed_args.get("phones", [])
        birthday = parsed_args.get("birthday")

        contact = Contact(name=name, address=address, birthday=birthday)

        for email in emails:
            contact.add_email(email)
        for phone in phones:
            contact.add_phone(phone)

        repo: ContactRepository = context["contact_repo"]

        try:
            repo.add(contact)
            Console.success(f"Contact '{name}' added successfully!")
        except Exception as e:
            Console.error(f"Failed to add contact: {str(e)}")

    def _parse_flags(self, args: list[str]) -> dict[str, Any] | None:
        """Parse command line flags into a dictionary of values."""
        result = {"address": "", "emails": [], "phones": [], "birthday": None}

        # Flag aliases
        aliases = {"addr": "address", "bday": "birthday", "bd": "birthday"}

        i = 0
        while i < len(args):
            arg = args[i]

            if not arg.startswith("--"):
                Console.error(f"Invalid argument: {arg}")
                Console.info("All arguments after name must be flags starting with --")
                Console.info(self.usage)
                return None

            # Parse flag
            if "=" in arg:
                # Format: --flag=value
                flag_part, value = arg[2:].split("=", 1)
                i += 1
            else:
                # Format: --flag value
                flag_part = arg[2:]
                if i + 1 >= len(args):
                    Console.error(f"Flag --{flag_part} requires a value")
                    Console.info(self.usage)
                    return None
                value = args[i + 1]
                i += 2

            # Resolve aliases
            flag_name = aliases.get(flag_part, flag_part)

            # Process flag value
            if flag_name == "address":
                result["address"] = value.strip()
            elif flag_name == "email":
                result["emails"].append(value.strip())
            elif flag_name == "phone":
                result["phones"].append(value.strip())
            elif flag_name == "birthday":
                try:
                    result["birthday"] = datetime.strptime(value.strip(), "%d.%m.%Y").date()
                except ValueError:
                    Console.error(f"Invalid birthday format: {value}")
                    Console.info("Birthday must be in DD.MM.YYYY format")
                    return None
            else:
                Console.error(f"Unknown flag: --{flag_part}")
                Console.info("Supported flags: --address, --email, --phone, --birthday")
                Console.info("Short aliases: --addr, --bday, --bd")
                return None

        return result


class ListContactsCommand(BaseCommand):
    """Command to list all contacts."""

    def __init__(self):
        super().__init__()
        self.name = "list-contacts"
        self.aliases = ["lc", "contacts"]
        self.description = "List all contacts"
        self.usage = "list-contacts"
        self.examples = ["list-contacts", "lc"]

    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        repo: ContactRepository = context["contact_repo"]
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

            table_data.append([contact.name, contact.address or "N/A", phones, emails, birthday])

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

    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        if not args:
            Console.error("Search query is required")
            Console.info(self.usage)
            return

        query = " ".join(args)
        repo: ContactRepository = context["contact_repo"]
        contacts = repo.search(query)

        if not contacts:
            Console.info(f"No contacts found matching '{query}'")
            return

        # Display results
        table_data = []
        for contact in contacts:
            phones = ", ".join(contact.phones) if contact.phones else "N/A"
            emails = ", ".join(contact.emails) if contact.emails else "N/A"

            table_data.append([contact.name, contact.address or "N/A", phones, emails])

        headers = ["Name", "Address", "Phones", "Emails"]
        table = tabulate(table_data, headers=headers, tablefmt="grid")

        Console.info(f"\nFound {len(contacts)} contact(s) matching '{query}':")
        print(table)


class EditContactCommand(BaseCommand):
    def __init__(self):
        super().__init__()
        self.name = "edit-contact"
        self.aliases = ["ec", "update-contact"]
        self.description = "Edit an existing contact (interactive mode)"
        self.usage = "edit-contact <name> [field] [value]"
        self.examples = [
            "edit-contact 'John Doe'",  # Interactive mode
            "edit-contact 'John' address '456 New St'",  # Direct mode
            "ec 'Jane'",  # Interactive mode with alias
        ]

    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        if not args:
            Console.error("Contact name is required")
            Console.info(self.usage)
            Console.info("💡 Tip: Use interactive mode by just providing the name")
            return

        name = args[0]
        repo: ContactRepository = context["contact_repo"]

        # Find the contact (with fuzzy matching)
        contact = self._find_contact(name, repo)
        if not contact:
            return

        # If only name provided, use interactive mode
        if len(args) == 1:
            self._interactive_edit(contact, repo)
        else:
            # Direct mode (backward compatibility)
            self._direct_edit(contact, args[1:], repo)

    def _find_contact(self, name: str, repo: ContactRepository):
        """Find contact with fuzzy matching."""
        # Try exact match first
        contact = repo.get_by_name(name)
        if contact:
            return contact

        # Try fuzzy search
        matching_contacts = repo.search(name)
        if not matching_contacts:
            Console.error(f"No contacts found matching '{name}'")
            return None

        if len(matching_contacts) == 1:
            contact = matching_contacts[0]
            Console.info(f"Found contact: {contact.name}")
            return contact

        # Multiple matches - let user choose
        Console.info(f"Found {len(matching_contacts)} contacts matching '{name}':")
        for i, contact in enumerate(matching_contacts, 1):
            phones = ", ".join(contact.phones) if contact.phones else "No phones"
            emails = ", ".join(contact.emails) if contact.emails else "No emails"
            print(f"  {i}. {contact.name} - {phones} - {emails}")

        try:
            choice = int(Console.prompt("Select contact number (0 to cancel)"))
            if choice == 0:
                Console.info("Edit cancelled")
                return None
            if 1 <= choice <= len(matching_contacts):
                return matching_contacts[choice - 1]
            else:
                Console.error("Invalid selection")
                return None
        except ValueError:
            Console.error("Invalid input")
            return None

    def _interactive_edit(self, contact, repo: ContactRepository):
        """Interactive editing mode."""
        Console.info(f"\n📝 Editing contact: {contact.name}")
        Console.info("=" * 40)

        self._display_contact_info(contact)

        # Show edit options
        Console.info("\n🔧 What would you like to edit?")
        options = [
            ("Name", f"Current: {contact.name}"),
            ("Address", f"Current: {contact.address or 'Not set'}"),
            ("Birthday", f"Current: {contact.birthday or 'Not set'}"),
            ("Add Phone", f"Current phones: {', '.join(contact.phones) if contact.phones else 'None'}"),
            ("Remove Phone", f"Current phones: {', '.join(contact.phones) if contact.phones else 'None'}"),
            ("Add Email", f"Current emails: {', '.join(contact.emails) if contact.emails else 'None'}"),
            ("Remove Email", f"Current emails: {', '.join(contact.emails) if contact.emails else 'None'}"),
        ]

        for i, (option, current) in enumerate(options, 1):
            print(f"  {i}. {option:<12} - {current}")

        try:
            choice = int(Console.prompt("\nSelect option (0 to cancel)"))
            if choice == 0:
                Console.info("Edit cancelled")
                return
            if not (1 <= choice <= len(options)):
                Console.error("Invalid selection")
                return

            self._handle_field_edit(contact, choice, repo)

        except ValueError:
            Console.error("Invalid input")
            return

    def _display_contact_info(self, contact):
        """Display current contact information."""
        print("\n📋 Contact Information:")
        print(f"   Name: {contact.name}")
        print(f"   Address: {contact.address or 'Not set'}")
        print(f"   Birthday: {contact.birthday or 'Not set'}")
        print(f"   Phones: {', '.join(contact.phones) if contact.phones else 'None'}")
        print(f"   Emails: {', '.join(contact.emails) if contact.emails else 'None'}")

    def _handle_field_edit(self, contact, choice: int, repo: ContactRepository):
        """Handle editing a specific field."""
        original_name = contact.name

        try:
            if choice == 1:  # Name
                new_name = Console.prompt("Enter new name")
                if new_name.strip():
                    contact.name = new_name.strip()
                    Console.success(f"Name updated: {original_name} → {contact.name}")
                else:
                    Console.error("Name cannot be empty")
                    return

            elif choice == 2:  # Address
                new_address = Console.prompt("Enter new address (or leave empty to clear)")
                contact.address = new_address.strip()
                Console.success(f"Address updated to: {contact.address or 'Cleared'}")

            elif choice == 3:  # Birthday
                birthday_str = Console.prompt("Enter birthday (YYYY-MM-DD, DD/MM/YYYY, etc.)")
                if birthday_str.strip():
                    birthday = parse_date(birthday_str.strip())
                    if birthday:
                        contact.birthday = birthday
                        Console.success(f"Birthday updated to: {contact.birthday}")
                    else:
                        Console.error("Invalid date format. Please use YYYY-MM-DD, DD/MM/YYYY, etc.")
                        return
                else:
                    contact.birthday = None
                    Console.success("Birthday cleared")

            elif choice == 4:  # Add Phone
                phone = Console.prompt("Enter phone number to add")
                if phone.strip():
                    contact.add_phone(phone.strip())
                    Console.success(f"Phone added: {phone}")
                else:
                    Console.error("Phone number cannot be empty")
                    return

            elif choice == 5:  # Remove Phone
                if not contact.phones:
                    Console.error("No phones to remove")
                    return

                Console.info("Current phones:")
                for i, phone in enumerate(contact.phones, 1):
                    print(f"  {i}. {phone}")

                try:
                    phone_choice = int(Console.prompt("Select phone number to remove (0 to cancel)"))
                    if phone_choice == 0:
                        Console.info("Remove cancelled")
                        return
                    if 1 <= phone_choice <= len(contact.phones):
                        removed_phone = contact.phones[phone_choice - 1]
                        contact.remove_phone(removed_phone)
                        Console.success(f"Phone removed: {removed_phone}")
                    else:
                        Console.error("Invalid selection")
                        return
                except ValueError:
                    Console.error("Invalid input")
                    return

            elif choice == 6:  # Add Email
                email = Console.prompt("Enter email address to add")
                if email.strip():
                    contact.add_email(email.strip())
                    Console.success(f"Email added: {email}")
                else:
                    Console.error("Email address cannot be empty")
                    return

            elif choice == 7:  # Remove Email
                if not contact.emails:
                    Console.error("No emails to remove")
                    return

                Console.info("Current emails:")
                for i, email in enumerate(contact.emails, 1):
                    print(f"  {i}. {email}")

                try:
                    email_choice = int(Console.prompt("Select email to remove (0 to cancel)"))
                    if email_choice == 0:
                        Console.info("Remove cancelled")
                        return
                    if 1 <= email_choice <= len(contact.emails):
                        removed_email = contact.emails[email_choice - 1]
                        contact.remove_email(removed_email)
                        Console.success(f"Email removed: {removed_email}")
                    else:
                        Console.error("Invalid selection")
                        return
                except ValueError:
                    Console.error("Invalid input")
                    return

            # Save the changes
            repo.update(contact)
            Console.success(f"\n✅ Contact '{contact.name}' updated successfully!")

            # Ask if user wants to make more changes
            more_changes = Console.prompt("\nMake another change? (y/n)").lower()
            if more_changes in ["y", "yes"]:
                self._interactive_edit(contact, repo)

        except ValidationError as e:
            Console.error(f"Validation error: {str(e)}")
        except Exception as e:
            Console.error(f"Failed to update contact: {str(e)}")

    def _direct_edit(self, contact, args: list[str], repo: ContactRepository):
        """Direct editing mode (backward compatibility)."""
        if len(args) < 2:
            Console.error("Field and value are required for direct mode")
            Console.info("💡 Tip: Use 'edit-contact <name>' for interactive mode")
            return

        field = args[0].lower()
        value = " ".join(args[1:])
        original_name = contact.name

        try:
            if field == "name":
                contact.name = value
            elif field == "address":
                contact.address = value
            elif field == "birthday":
                birthday = parse_date(value)
                if birthday:
                    contact.birthday = birthday
                else:
                    Console.error("Invalid date format. Use YYYY-MM-DD")
                    return
            elif field == "add-phone":
                contact.add_phone(value)
            elif field == "remove-phone":
                contact.remove_phone(value)
            elif field == "replace-phone":
                old_new = value.split()
                if len(old_new) != 2:
                    Console.error("Usage: replace-phone '<old>' '<new>'")
                    return
                old_phone, new_phone = old_new
                contact.remove_phone(old_phone)
                contact.add_phone(new_phone)
            elif field == "add-email":
                contact.add_email(value)
            elif field == "remove-email":
                contact.remove_email(value)
            elif field == "replace-email":
                old_new = value.split()
                if len(old_new) != 2:
                    Console.error("Usage: replace-email '<old>' '<new>'")
                    return
                old_email, new_email = old_new
                contact.remove_email(old_email)
                contact.add_email(new_email)
            else:
                Console.error(f"Unknown field: {field}")
                Console.info(
                    "Available fields: name, address, birthday, add-phone, remove-phone, replace-phone, add-email, remove-email, replace-email"
                )
                Console.info("💡 Tip: Use 'edit-contact <name>' for interactive mode")
                return

            repo.update(contact)
            Console.success(f"Contact '{original_name}' updated successfully!")

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

    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        if not args:
            Console.error("Contact name is required")
            Console.info(self.usage)
            return

        name = " ".join(args)
        repo: ContactRepository = context["contact_repo"]
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
        self.usage = "birthdays <days>"
        self.examples = ["birthdays", "birthdays 30", "bd 7"]

    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        if not args:
            Console.error("You must provide the number of days")
            Console.info(self.usage)
            return

        try:
            days = int(args[0])
            if days < 0:
                Console.error("Days must be a positive number")
                return
        except ValueError:
            Console.error("Invalid number of days")
            return

        repo: ContactRepository = context["contact_repo"]
        contacts = []

        # We iterate over all contacts and select only those whose birthday is in N days
        for contact in repo.get_all():
            days_left = contact.days_until_birthday()
            if days_left is not None and 0 <= days_left <= days:
                contacts.append((contact, days_left))

        if not contacts:
            Console.info(f"No contacts with birthdays in the next {days} day(s).")
            return

        # Prepare data for table
        table_data = []
        for contact, days_left in contacts:
            birthday_str = contact.birthday.strftime("%Y-%m-%d") if contact.birthday else "N/A"
            table_data.append(
                [
                    contact.name,
                    birthday_str,
                    f"{days_left} days",
                ]
            )

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

    def execute(self, args: list[str], context: dict[str, Any]) -> None:
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

        repo: ContactRepository = context["contact_repo"]
        fake = Faker()

        Console.info(f"Generating {count} random contacts...")

        try:
            for i in range(count):
                contact = Contact(name=fake.name(), address=fake.address().replace("\n", ", "))

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


class CleanContactsCommand(BaseCommand):
    """Command to delete all contacts from the repository."""

    def __init__(self):
        super().__init__()
        self.name = "clean-contacts"
        self.aliases = ["cc", "clear-contacts"]
        self.description = "Delete all contacts from the repository"
        self.usage = "clean-contacts"
        self.examples = ["clean-contacts", "cc"]

    def execute(self, args: list[str], context: dict[str, Any]) -> None:
        repo: ContactRepository = context["contact_repo"]
        contacts = repo.get_all()
        if not contacts:
            Console.info("No contacts to delete.")
            return
        if not Console.confirm("Are you sure you want to delete ALL contacts? This cannot be undone."):
            Console.info("Operation cancelled.")
            return
        try:
            repo._notes.clear() if hasattr(repo, "_notes") else None
            repo._contacts.clear() if hasattr(repo, "_contacts") else None
            if hasattr(repo, "save_data"):
                repo.save_data([])
            Console.success("All contacts deleted successfully!")
        except Exception as e:
            Console.error(f"Failed to delete all contacts: {str(e)}")

# Kontacto

A command-line contact and note management application with intelligent command recognition.

## Features

- **Contact Management**: Store contacts with name, address, phones, emails, and birthdays
- **Notes Management**: Create, edit, and delete notes with tag support
- **Search**: Search contacts and notes by any field or tag
- **Interactive CLI**: Tab completion, command history, and fuzzy matching
- **Data Persistence**: Automatic data saving with pickle serialization

## Installation

### Prerequisites
- Python 3.9+
- Poetry

### Setup
```bash
git clone <repository-url>
cd kontacto
make setup
```

### Run
```bash
# Development
poetry run kontacto

# Install as CLI command
make install-cli
kontacto
```

## Usage

### Contact Commands
```bash
add-contact <name> [--address=<addr>] [--email=<email>] [--phone=<phone>] [--birthday=<date>]
list-contacts, lc                    # List all contacts
search-contacts <query>, sc          # Search contacts
edit-contact <name>                  # Interactive edit mode
delete-contact <name>                # Delete contact
birthdays <days>                     # Show upcoming birthdays
```

### Note Commands
```bash
add-note <content> [tag1] [tag2]...  # Add note with tags
list-notes, ln                       # List all notes
search-notes <query>                 # Search notes
search-tag <tag>                     # Find notes by tag
edit-note <query> <new-content>      # Edit note
delete-note <query>                  # Delete note
add-tag, at                          # Add tag to note (interactive)
remove-tag, rt                       # Remove tag from note (interactive)
list-tags, lt                        # List all tags
notes-by-tag, nbt                    # Show notes grouped by tags
clean-tags, ct                       # Remove all tags from all notes
```

### System Commands
```bash
help, h, ?                           # Show help
clear, cls                           # Clear screen
exit, quit, q                        # Exit application
```

## Examples

```bash
# Add contact
kontacto> add-contact "John Doe" --email=john@example.com --phone=555-1234

# Search contacts
kontacto> sc john

# Add note with tags
kontacto> add-note "Meeting notes" work important

# Search notes by tag
kontacto> search-tag work

# Add tag to note interactively (shows all notes, then asks for tag name)
kontacto> add-tag

# Remove tag interactively (shows all notes with tags, then their tags)
kontacto> remove-tag

# List all tags
kontacto> list-tags

# View notes grouped by tags
kontacto> notes-by-tag
```

## Development

### Commands
```bash
make setup      # Install dependencies and setup environment
make test       # Run tests
make format     # Format code
make lint       # Run linting
make clean      # Clean cache files
```

### Project Structure
```
kontacto/
├── kontacto/
│   ├── models/           # Data models
│   ├── commands/         # Command implementations
│   ├── repositories/     # Data persistence
│   ├── ui/              # CLI interface
│   └── utils/           # Utilities
├── tests/               # Test files
└── pyproject.toml       # Project configuration
```

### Data Storage
- Contacts: `contacts.pkl`
- Notes: `notes.pkl`
- History: `.kontacto_history`

## Requirements

- Python 3.9+
- Poetry for dependency management
- Unix-like system for Makefile (optional)

## License

MIT License

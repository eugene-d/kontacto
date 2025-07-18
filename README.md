# Kontacto

A command-line Kontacto application for managing contacts and notes with intelligent command recognition.

## Features

### Contact Management
- Store contacts with name, address, multiple phone numbers, multiple emails, and birthday
- Search contacts by any field
- Edit and delete contacts
- Display upcoming birthdays
- Generate random test contacts

### Notes Management
- Create, edit, and delete text notes
- Add tags to notes for categorization
- Search notes by content or tags
- Sort and group notes by tags

### Intelligent Command Analysis
- Fuzzy matching for command suggestions
- Command aliases for convenience
- Tab completion for commands
- Command history with arrow key navigation

### Data Persistence
- All data is automatically saved using pickle serialization
- Data persists between application restarts
- Files are stored in the project root directory

## Installation

### Prerequisites
- Python 3.8.1 or higher
- Poetry (dependency management)

### Installing Poetry

If you don’t have Poetry installed, follow the instructions in [Poetry's official documentation](https://python-poetry.org/docs/#installing-with-the-official-installer).
Quick install:
```bash
# On macOS/Linux/WSL
curl -sSL https://install.python-poetry.org | python3 -
```

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd kontacto
```

2. Install dependencies with Poetry:
```bash
poetry install
```

For development (includes testing tools):
```bash
poetry install --with dev
```

3. Run the application:

```bash
# Using Poetry (recommended)
poetry run kontacto

# Or activate the virtual environment first
source $(poetry env info --path)/bin/activate
kontacto

# Or run directly
poetry run python -m kontacto.main
```

## Usage

### Starting the Application
When you start the application, you'll see:
```
============================
Welcome to Personal Kontacto!
============================

ℹ Type 'help' to see available commands.
ℹ Use Tab for command completion, arrow keys for history.

kontacto>
```

### Basic Commands

#### Help
- `help` or `h` or `?` - Show all available commands
- `help <command>` - Show detailed help for a specific command

#### Contact Commands
- `add-contact <name> [address]` - Add a new contact
- `list-contacts` or `lc` - List all contacts
- `search-contacts <query>` or `sc` - Search contacts by any field
- `edit-contact <name> <field> <value>` - Edit a contact field
- `delete-contact <name>` - Delete a contact
- `birthdays <days>` - Show upcoming birthdays
- `generate-contacts [count]` - Generate random test contacts

#### Note Commands
- `add-note <content> [tag1] [tag2]...` - Add a new note with optional tags
- `list-notes` or `ln` - List all notes
- `search-notes <query>` - Search notes by content or tags
- `search-tag <tag>` - Find notes with a specific tag
- `edit-note <search-query> <new-content>` - Edit a note
- `add-tag <search-query> <tag>` - Add a tag to a note
- `remove-tag <search-query> <tag>` - Remove a tag from a note
- `delete-note <search-query>` - Delete a note
- `list-tags` - List all tags with counts
- `notes-by-tag` - Show notes grouped by tags

#### System Commands
- `clear` or `cls` - Clear the screen
- `exit` or `quit` or `q` - Exit the application

### Examples

#### Managing Contacts
```bash
# Add a contact
kontacto> add-contact "John Doe" "123 Main St, New York, NY"

# Add phone and email to contact
kontacto> edit-contact "John Doe" add-phone "555-1234"
kontacto> edit-contact "John Doe" add-email "john@example.com"

# Search for contacts
kontacto> search-contacts john
kontacto> sc 555

# Check upcoming birthdays
kontacto> birthdays 30

# Generate test data
kontacto> generate-contacts 50
```

#### Managing Notes
```bash
# Add a note with tags
kontacto> add-note "Remember to buy milk" shopping urgent

# Search notes
kontacto> search-notes milk
kontacto> search-tag urgent

# Edit a note
kontacto> edit-note "buy milk" "Buy milk and bread"

# Manage tags
kontacto> add-tag "project deadline" important
kontacto> list-tags
kontacto> notes-by-tag
```

### Command Editing Fields

When editing contacts, you can modify these fields:
- `name` - Contact's name
- `address` - Contact's address
- `add-phone` - Add a phone number
- `remove-phone` - Remove a phone number
- `add-email` - Add an email address
- `remove-email` - Remove an email address
- `birthday` - Set birthday (format: YYYY-MM-DD)
- `replace-phone` - Replace phone
- `replace-email` - Replace email

### Date Formats

The application accepts dates in multiple formats:
- YYYY-MM-DD (2024-01-15)
- DD-MM-YYYY (15-01-2024)
- DD/MM/YYYY (15/01/2024)
- MM/DD/YYYY (01/15/2024)

### Tips

1. **Use Tab Completion**: Start typing a command and press Tab to autocomplete
2. **Command History**: Use arrow keys to navigate through previous commands
3. **Aliases**: Use short aliases like `ac` instead of `add-contact` for faster input
4. **Fuzzy Matching**: Even if you misspell a command, the kontacto will suggest the closest match
5. **Multiple Values**: When searching, the query will match any field in contacts or notes

## Data Storage

- Contacts are stored in `contacts.pkl`
- Notes are stored in `notes.pkl`
- Command history is stored in `.kontacto_history`

All files are stored in the project root directory and are automatically created on first use.

## Error Handling

The application includes comprehensive error handling:
- Invalid input validation with helpful error messages
- Graceful handling of missing data files
- Clear feedback for all operations
- Suggestions for misspelled commands

## Development

### Project Structure
```
kontacto/
├── models/           # Data models (Contact, Note)
├── commands/         # Command implementations
├── repositories/     # Data persistence layer
├── ui/              # User interface utilities
├── utils/           # Helper utilities
└── main.py          # Application entry point
```

### Design Patterns Used
- **Command Pattern**: For handling user commands
- **Repository Pattern**: For data access and persistence
- **Factory Pattern**: For creating model instances
- **Observer Pattern**: For event notifications

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run with coverage report
poetry run pytest --cov=kontacto --cov-report=term-missing
```

## Troubleshooting

### Common Issues

1. **Poetry not found**
   - Install Poetry following the instructions in the Prerequisites section
   - Make sure Poetry is in your PATH: `export PATH="$HOME/.local/bin:$PATH"`

2. **Command not found: kontacto**
   - Make sure you're using `poetry run kontacto`
   - Or activate the Poetry shell first: `poetry shell`

3. **Module not found errors**
   - Make sure you're in the `kontacto` directory
   - Run `poetry install` to install all dependencies
   - Use `poetry run` to execute commands in the virtual environment

4. **Python version errors**
   - Ensure you have Python 3.8.1 or higher: `python3 --version`
   - Poetry will automatically use the correct Python version

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper tests
4. Submit a pull request

## License

This project is licensed under the MIT License.

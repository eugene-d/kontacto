# Quick Start Guide

## Fastest Way to Get Started

1. **Install Poetry (if not already installed):**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
   
   For detailed installation instructions, see [POETRY_SETUP.md](POETRY_SETUP.md)

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Run the application:**
   ```bash
   poetry run assistant
   ```

That's it! The application should now be running.

## First Steps

Once the application is running, try these commands:

1. **See all available commands:**
   ```
   help
   ```

2. **Add your first contact:**
   ```
   add-contact "John Doe" "123 Main Street"
   ```

3. **Add a phone number to the contact:**
   ```
   edit-contact "John Doe" add-phone "555-1234"
   ```

4. **Create your first note:**
   ```
   add-note "Remember to buy milk" shopping
   ```

5. **Generate test data:**
   ```
   generate-contacts 10
   ```

## Tips

- Use **Tab** for command completion
- Use **Arrow Keys** to navigate command history
- Commands have short aliases (e.g., `ac` for `add-contact`)
- Type `help <command>` for detailed help on any command

## Need Help?

- Type `help` in the application for all commands
- Check the README.md for full documentation
- See TROUBLESHOOTING section in README if you encounter issues 
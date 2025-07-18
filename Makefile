.PHONY:  help install uninstall setup status lint format check spell-check test clean pre-commit

help:
	@echo "Available commands:"
	@echo "  setup       - Complete environment setup (check Poetry, create venv, install deps)"
	@echo "  status      - Check environment status and requirements"
	@echo "  install     - Install kontacto CLI command system-wide"
	@echo "  uninstall   - Uninstall kontacto CLI command"
	@echo "  format      - Format code with black and isort"
	@echo "  lint        - Run all linting checks (including spell check)"
	@echo "  check       - Run format check without making changes"
	@echo "  spell-check - Run spell check and fix issues"
	@echo "  test        - Run tests"
	@echo "  pre-commit  - Install pre-commit hooks"
	@echo "  clean       - Clean up cache files"

setup:
	@echo "🚀 Setting up development environment..."
	@echo "📋 Checking Poetry installation..."
	@command -v poetry >/dev/null 2>&1 || { echo "❌ Poetry is not installed. Please install Poetry first:"; echo "   curl -sSL https://install.python-poetry.org | python3 -"; exit 1; }
	@echo "✅ Poetry is installed"
	@echo "📋 Checking Python version..."
	@python3 --version | grep -E "Python 3\.(9|[1-9][0-9])" >/dev/null || { echo "❌ Python 3.9+ required. Current version:"; python3 --version; exit 1; }
	@echo "✅ Python version is compatible"
	@echo "📋 Checking virtual environment..."
	@poetry env info >/dev/null 2>&1 || { echo "🔧 Creating virtual environment..."; poetry install --no-deps; }
	@echo "✅ Virtual environment ready"
	@echo "📦 Installing dependencies..."
	@poetry install
	@echo "🪝 Setting up pre-commit hooks..."
	@poetry run pre-commit install
	@echo "🎉 Setup complete! You can now run:"
	@echo "   make test     - Run tests"
	@echo "   make lint     - Check code quality"
	@echo "   poetry run kontacto - Run the application"

status:
	@echo "🔍 Environment Status Check"
	@echo "=========================="
	@command -v poetry >/dev/null 2>&1 && echo "Poetry:              ✅ Installed" || echo "Poetry:              ❌ Not installed"
	@python3 --version 2>/dev/null | grep -E "Python 3\.(9|[1-9][0-9])" >/dev/null && echo "Python:              ✅ $$(python3 --version)" || echo "Python:              ❌ Need Python 3.9+"
	@poetry env info >/dev/null 2>&1 && echo "Virtual Environment: ✅ Ready" || echo "Virtual Environment: ❌ Not created"
	@poetry run python -c "import kontacto" 2>/dev/null && echo "Dependencies:        ✅ Installed" || echo "Dependencies:        ❌ Not installed"
	@test -f .git/hooks/pre-commit && echo "Pre-commit:          ✅ Installed" || echo "Pre-commit:          ❌ Not installed"
	@echo ""
	@echo "💡 To fix any issues, run: make setup"

install:
	@echo "📦 Installing Kontacto CLI..."
	@echo "🔧 Building package..."
	@poetry build
	@echo "⚡ Installing CLI command..."
	@pip install --user --force-reinstall dist/*.whl
	@echo "🎉 Installation complete!"
	@echo ""
	@echo "✅ You can now run 'kontacto' from anywhere!"
	@echo "💡 If 'kontacto' is not found, add ~/.local/bin to your PATH:"
	@echo "   export PATH=\"$$HOME/.local/bin:$$PATH\""
	@echo "   echo 'export PATH=\"$$HOME/.local/bin:$$PATH\"' >> ~/.zshrc"

uninstall:
	@echo "🗑️  Uninstalling Kontacto CLI..."
	@pip uninstall -y kontacto 2>/dev/null || echo "⚠️  Kontacto was not installed"
	@rm -rf dist/ 2>/dev/null || true
	@echo "✅ Uninstallation complete!"

format:
	poetry run black --config black.toml kontacto/ tests/
	poetry run isort --settings-path .isort.cfg kontacto/ tests/

lint:
	poetry run flake8 kontacto/ tests/
	poetry run mypy --config-file mypy.ini kontacto/
	poetry run black --config black.toml --check kontacto/ tests/
	poetry run isort --settings-path .isort.cfg --check-only kontacto/ tests/
	poetry run codespell --config .codespellrc kontacto/ tests/

check:
	poetry run black --config black.toml --check --diff kontacto/ tests/
	poetry run isort --settings-path .isort.cfg --check-only --diff kontacto/ tests/
	poetry run flake8 kontacto/ tests/
	poetry run mypy --config-file mypy.ini kontacto/
	poetry run codespell --config .codespellrc kontacto/ tests/

spell-check:
	poetry run codespell --config .codespellrc kontacto/ tests/ --write-changes

test:
	poetry run pytest

pre-commit:
	poetry run pre-commit install
	poetry run pre-commit run --all-files

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf dist/ build/ *.egg-info/ .venv/

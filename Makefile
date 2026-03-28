.PHONY: help sync format lint test clean all

help:
	@echo "Available targets:"
	@echo "  sync       - Sync dependencies with uv"
	@echo "  format     - Format code with ruff"
	@echo "  lint       - Run linting checks (ruff, mypy)"
	@echo "  test       - Run pytest with coverage"
	@echo "  clean      - Remove build artifacts and cache files"
	@echo "  all        - Run sync, format, lint, and test"

sync:
	uv sync --dev

format:
	uv run ruff format src/ tests/ scripts/

lint:
	@echo "Running ruff format check..."
	uv run ruff format --check src/ tests/ scripts/
	@echo "Running ruff check..."
	uv run ruff check src/ tests/ scripts/
	@echo "Running mypy..."
	uv run mypy src/

test:
	uv run pytest tests/ --cov=src/ --cov-report=html --cov-report=term-missing

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name .coverage -delete
	find . -type f -name coverage.xml -delete
	rm -rf build/ dist/ *.egg-info/

all: sync format lint test

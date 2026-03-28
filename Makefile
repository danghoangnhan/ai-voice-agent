.PHONY: help install format lint test clean all

help:
	@echo "Available targets:"
	@echo "  install    - Install dependencies"
	@echo "  format     - Format code with black and isort"
	@echo "  lint       - Run linting checks (black, isort, ruff, mypy)"
	@echo "  test       - Run pytest with coverage"
	@echo "  clean      - Remove build artifacts and cache files"
	@echo "  all        - Run format, lint, and test"

install:
	pip install -r requirements.txt
	pip install -e ".[dev]"

format:
	black src/ tests/ scripts/
	isort src/ tests/ scripts/

lint:
	@echo "Running black..."
	black --check src/ tests/ scripts/
	@echo "Running isort..."
	isort --check-only src/ tests/ scripts/
	@echo "Running ruff..."
	ruff check src/ tests/ scripts/
	@echo "Running mypy..."
	mypy src/

test:
	pytest tests/ --cov=src/ --cov-report=html --cov-report=term-missing

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name .coverage -delete
	find . -type f -name coverage.xml -delete
	rm -rf build/ dist/ *.egg-info/

all: format lint test

format:
	uv run ruff format
	uv run ruff check --fix

lint:
	uv run ruff check
	uv run mypy src tests

test:
	uv run pytest

coverage:
	uv run pytest --cov=src --cov-report=term-missing:skip-covered

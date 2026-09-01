format:
	poetry run ruff format
	poetry run ruff check --fix

lint:
	poetry run ruff check
	poetry run mypy src tests

test:
	poetry run pytest

coverage:
	poetry run pytest --cov=src --cov-report=term-missing:skip-covered

format:
	poetry run ruff format
	poetry run ruff check --fix
	zizmor .github/workflows/ --fix --pedantic

lint:
	poetry check
	poetry run ruff check
	poetry run mypy src tests
	zizmor .github/workflows/ --pedantic
	hadolint Dockerfile -t style

test:
	poetry run pytest

coverage:
	poetry run pytest --cov=src --cov-report=term-missing:skip-covered


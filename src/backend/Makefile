.PHONY: dev test check

dev:
	uv run fastapi dev src/health_api/main.py --host 127.0.0.1 --port 8000

test:
	uv run pytest

check:
	uv run ruff check .
	uv run ruff format --check .
	uv run pyright
	uv run pytest

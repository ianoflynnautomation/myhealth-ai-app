FROM python:3.13-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /uvx /bin/

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --group local --no-install-project

COPY src ./src
RUN uv sync --frozen --no-dev --group local

ENV PATH="/app/.venv/bin:$PATH"

CMD ["fastapi", "run", "src/health_api/main.py", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first (layer cache)
COPY pyproject.toml .
RUN uv sync --no-dev

# Copy source
COPY . .

CMD ["uv", "run", "python", "-B", "main.py"]

# syntax=docker/dockerfile:1.4
FROM python:3.13-slim AS builder

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY app ./app

FROM python:3.13-slim AS runner
WORKDIR /app

COPY --from=builder /app /app

EXPOSE 8000

# Run the application.
CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--port", "8000", "--host", "0.0.0.0"]
#CMD ["bash", "-c", "trap 'exit 0' SIGINT SIGTERM; while true; do sleep 1; done"]

FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_SYSTEM_PYTHON=1

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv pip install --system . && uv pip install --system --group dev .

COPY src/ ./src/
COPY tests/ ./tests/
COPY data/ ./data/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000", "--reload"]

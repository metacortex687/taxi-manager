FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml README.md ./

RUN uv sync \
    --no-dev \
    --no-install-project

COPY . .

CMD ["sh", "-c", "uv run --no-sync manage.py migrate && exec uv run --no-sync manage.py start_service"]
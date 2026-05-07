# Build stage
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        make \
    && rm -rf /var/lib/apt/lists/*

    RUN make install-geo-deps

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .
RUN uv sync --frozen --no-editable

# Runtime stage
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        make \
    && rm -rf /var/lib/apt/lists/*

    RUN make install-geo-deps

WORKDIR /app

COPY --from=builder /app /app

RUN make collectstatic

# EXPOSE 8000

# CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["make", "run-gunicorn"]

# Frontend build stage
FROM node:22-slim AS frontend-builder

WORKDIR /app/taxi_manager/infrastructure/react_frontend

COPY taxi_manager/infrastructure/react_frontend/package*.json ./
RUN npm ci

COPY taxi_manager/infrastructure/react_frontend/ ./
RUN npm run build

# Python base stage with geo dependencies
FROM python:3.12-slim AS python-system-deps

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY Makefile ./
RUN make install-geo-deps


# Build stage
FROM python-system-deps AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .

RUN uv sync --frozen --no-editable

COPY --from=frontend-builder \
    /app/taxi_manager/infrastructure/react_frontend/static/react_frontend/dist \
    /app/taxi_manager/infrastructure/react_frontend/static/react_frontend/dist
    
# Runtime stage
FROM python-system-deps AS runtime

COPY --from=builder /app /app

CMD ["make", "run-gunicorn"]

# Frontend build stage
FROM node:22-slim AS frontend-builder

WORKDIR /app/taxi_manager/react_frontend

COPY taxi_manager/react_frontend/package*.json ./
RUN npm ci

COPY taxi_manager/react_frontend/ ./
RUN npm run build

# Build stage
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        make \
    && rm -rf /var/lib/apt/lists/*



WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .

RUN make install-geo-deps

RUN uv sync --frozen --no-editable

COPY --from=frontend-builder \
    /app/taxi_manager/react_frontend/static/react_frontend/dist \
    /app/taxi_manager/react_frontend/static/react_frontend/dist
    
# Runtime stage
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        make \
    && rm -rf /var/lib/apt/lists/*
  

WORKDIR /app

COPY --from=builder /app /app

RUN make install-geo-deps

# RUN make collectstatic

# EXPOSE 8000

# CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["make", "run-gunicorn"]

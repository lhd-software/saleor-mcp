# ─────────────────────────────────────────────
# Stage 1: Build Vite UI (ui-app → dist/mcp-app.html)
# ─────────────────────────────────────────────
FROM node:20-slim AS build-ui

WORKDIR /ui-app

COPY ui-app/package.json ui-app/package-lock.json* ./
RUN npm ci --omit=dev || npm install

COPY ui-app/ ./
RUN npm run build
# Output: /ui-app/dist/mcp-app.html

# ─────────────────────────────────────────────
# Stage 2: Install Python deps với uv
# ─────────────────────────────────────────────
FROM python:3.12 AS build-python

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_PROJECT_ENVIRONMENT=/usr/local

COPY pyproject.toml uv.lock ./
COPY src/ ./src/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# ─────────────────────────────────────────────
# Stage 3: Final slim image
# ─────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Copy Python packages and binaries
COPY --from=build-python /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=build-python /usr/local/bin/ /usr/local/bin/

# Copy application source
COPY --from=build-python /app/src/ ./src/

# Copy ui-app dist (required by main.py: open("ui-app/dist/mcp-app.html"))
COPY --from=build-ui /ui-app/dist/ ./ui-app/dist/

# Copy remaining configs needed at runtime
COPY pyproject.toml uvicorn_log_config.yaml ./

EXPOSE 8000

LABEL org.opencontainers.image.title="saleor/saleor-mcp" \
    org.opencontainers.image.description="A Model Context Protocol (MCP) server for Saleor Commerce (custom)" \
    org.opencontainers.image.url="https://saleor.io/" \
    org.opencontainers.image.source="https://github.com/saleor/saleor-mcp" \
    org.opencontainers.image.authors="Saleor Commerce (https://saleor.io)" \
    org.opencontainers.image.licenses="AGPL-3.0"

ENTRYPOINT ["uvicorn", "saleor_mcp.main:app", "--host=0.0.0.0", "--port=8000", "--log-config=uvicorn_log_config.yaml"]

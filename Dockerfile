# ─────────────────────────────────────────────
# Stage 1: Install Python deps với uv
# ─────────────────────────────────────────────
FROM python:3.12 AS build-python

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_PROJECT_ENVIRONMENT=/usr/local

# Copy files cần thiết cho build
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# ─────────────────────────────────────────────
# Stage 2: Final slim image
# ─────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Copy Python packages and binaries
COPY --from=build-python /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build-python /usr/local/bin/ /usr/local/bin/

# Copy source code
COPY --from=build-python /app/src/ ./src/

# Copy UI app đã build local (Quan trọng: Phải build npm run build local trước)
COPY ui-app/dist/ ./ui-app/dist/

# Expose port
EXPOSE 8000

# Chạy server
CMD ["uvicorn", "saleor_mcp.main:app", "--host", "0.0.0.0", "--port", "8000"]

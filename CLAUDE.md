# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Saleor MCP Server is a [Model Context Protocol](https://modelcontextprotocol.io) server that bridges AI assistants to Saleor Commerce's GraphQL API. It enables AI-first e-commerce experiences—product discovery, cart management, and checkout—via natural language.

Production instance: https://mcp.saleor.app/

## Commands

**Setup**
```bash
uv sync           # Install production dependencies
uv sync --dev     # Include dev dependencies
```

**Run server**
```bash
uv run saleor-mcp          # Start on localhost:6000
```

**Linting & type checking**
```bash
ruff check src/             # Lint
ruff format src/            # Format
ty src/                     # Type check
```

**Tests**
```bash
pytest                      # All tests
pytest src/saleor_mcp/tools/tests/test_products.py  # Single test file
pytest -k "test_name"       # Single test by name
```

**Regenerate GraphQL client** (after changing `.graphql` files or `schema.graphql`)
```bash
ariadne-codegen             # Reads config from pyproject.toml, outputs to src/saleor_mcp/saleor_client/
```

**Frontend UI**
```bash
cd ui-app
npm install
npm run build               # Outputs dist/mcp-app.html (single-file embedded in server)
npm run dev                 # Dev server
```

## Architecture

### Tool Routing

The server (`src/saleor_mcp/main.py`) mounts 7 FastMCP sub-routers. Each router is defined in `src/saleor_mcp/tools/` and handles a logical domain: `products`, `checkout`, `orders`, `customers`, `channels`, `promotions`, `utils`. There are also 3 UI-integrated tools defined directly in `main.py` (`open_product_explorer`, `open_cart`, `open_checkout`).

### Auth & Configuration

Every request must include `X-Saleor-API-URL` and `X-Saleor-Auth-Token` headers (or fall back to `SALEOR_API_URL`/`SALEOR_AUTH_TOKEN` env vars). `src/saleor_mcp/config.py` validates these and optionally enforces an `ALLOWED_DOMAIN_PATTERN` regex. `src/saleor_mcp/ctx_utils.py` builds the authenticated Saleor client from request context.

### GraphQL Client (Auto-generated)

`src/saleor_mcp/saleor_client/` is **entirely auto-generated** by `ariadne-codegen`. Do not edit files there manually. The source of truth is:
- `src/saleor_mcp/graphql/*.graphql` — query/mutation definitions (20 files)
- `schema.graphql` — full Saleor schema (954 KB)

When adding a new GraphQL operation: create a `.graphql` file, run `ariadne-codegen`, then use the generated method from `saleor_client/client.py`.

### Tool Pattern

Each tool is an `async` function decorated with `@router.tool()`. Tools use `Annotated` type hints for descriptions, return `{"data": ...}` on success or `{"error": "..."}` on failure, and log errors via `ctx.error()`. Mutation hints vs. read-only hints are set in the `annotations` dict on the decorator.

### UI Embedding

The Vite app (`ui-app/`) compiles to a single HTML file (`ui-app/dist/mcp-app.html`). The server embeds this file as a static resource. UI-integrated tools pass a `resourceUri` pointing to the embedded app in their return value.

### Testing

Tests mock the Saleor client and config headers—they never make real network calls (`pytest-socket` blocks sockets). Fixtures live in `src/saleor_mcp/conftest.py`. Tool tests are in `src/saleor_mcp/tools/tests/`.

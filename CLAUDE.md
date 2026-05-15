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
pytest                                                            # All tests
pytest src/saleor_mcp/tools/tests/test_products.py               # Single test file
pytest -k "test_name"                                             # Single test by name
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

The server (`src/saleor_mcp/main.py`) mounts 7 FastMCP sub-routers. Each router is in `src/saleor_mcp/tools/` and handles a domain: `products`, `checkout`, `orders`, `customers`, `channels`, `promotions`, `utils`. Four UI-integrated tools are defined directly in `main.py`: `open_product_explorer`, `get_product_details`, `open_cart`, `open_checkout`.

### Auth & Configuration

**Config resolution** (`src/saleor_mcp/config.py`):
- API URL: `X-Saleor-API-URL` header → `SALEOR_API_URL` env var
- Auth token priority (first match wins):
  1. `Authorization: Bearer <token>` (OAuth flow)
  2. `X-Saleor-Auth-Token` header (legacy)
  3. `SALEOR_AUTH_TOKEN` env var (dev fallback)
- `ALLOWED_DOMAIN_PATTERN` (optional): regex restricting allowed API URLs

`src/saleor_mcp/ctx_utils.py` builds the authenticated Saleor GraphQL client from request context via `get_saleor_client()`.

### Scope-Based Access Control

`src/saleor_mcp/auth/` implements OAuth 2.0 scope enforcement:

- **`scopes.py`**: Single source of truth — `TOOL_SCOPES` dict maps every tool name to a required scope. Three tiers:
  - `customer.read`: browse catalog, view own cart/order
  - `customer.write`: modify cart, place order
  - `admin`: list all channels/customers/orders/stocks/warehouses (staff only)
- **`verifier.py`**: Decodes JWT without cryptographic verification (Saleor backend is source of truth). Checks `exp` claim. Promotes `is_staff: true` claim to all three scopes. Falls back to accepting non-JWT app tokens when `SALEOR_REQUIRE_JWT_SHAPE=false`.
- **`middleware.py`**: `ScopeEnforcementMiddleware` — runs before each tool call and denies with JSON-RPC `-32001` if scopes don't match. Fails closed: unmapped tools are denied. If no `AccessToken` exists (no OAuth configured), middleware passes through (legacy mode).

**OAuth is opt-in**: Set `OAUTH_AUTHORIZATION_SERVERS` to enable. Without it, the server runs in legacy mode accepting `X-Saleor-Auth-Token` with no scope checks.

### GraphQL Client (Auto-generated)

`src/saleor_mcp/saleor_client/` is **entirely auto-generated** by `ariadne-codegen`. Do not edit files there manually. The source of truth is:
- `src/saleor_mcp/graphql/*.graphql` — query/mutation definitions
- `schema.graphql` — full Saleor schema (954 KB)

When adding a new GraphQL operation: create a `.graphql` file, run `ariadne-codegen`, then use the generated method from `saleor_client/client.py`.

### Tool Pattern

Each tool is an `async` function decorated with `@router.tool()`. Tools use `Annotated` type hints for descriptions, return `{"data": ...}` on success or `{"error": "..."}` on failure, and log errors via `ctx.error()`. The `tags` kwarg carries the required scope (e.g. `tags={"scope:customer.read"}`); `annotations` sets MCP hints like `readOnlyHint`.

### UI Embedding

The Vite app (`ui-app/`) compiles to `ui-app/dist/mcp-app.html` (single bundled file). The server embeds this as a static resource at `ui://saleor/product-explorer.html`. UI-integrated tools return `structured_content` with a `resourceUri` pointing to it. An image proxy (`/img?u=<url>`) rewrites Saleor thumbnail URLs because Saleor serves images with `Content-Disposition: attachment`, which sandboxed iframes reject.

### Testing

Tests mock the Saleor client and config headers — they never make real network calls (`pytest-socket` blocks sockets). Mock fixtures live in `src/saleor_mcp/conftest.py`. Tool tests are in `src/saleor_mcp/tools/tests/`; auth tests are in `src/saleor_mcp/auth/tests/`. Patch both `saleor_mcp.ctx_utils.get_config_from_headers` and the relevant `SaleorClient` method in each test.

## Key Environment Variables

| Variable | Purpose |
|----------|---------|
| `SALEOR_API_URL` | Saleor GraphQL endpoint (required if not in headers) |
| `SALEOR_AUTH_TOKEN` | Staff token (required if not in headers) |
| `ALLOWED_DOMAIN_PATTERN` | Regex restricting allowed API URLs |
| `OAUTH_AUTHORIZATION_SERVERS` | Comma-separated issuer URLs; enables OAuth mode |
| `SALEOR_REQUIRE_JWT_SHAPE` | `true` (default): reject non-JWT tokens; `false`: accept plain app tokens |
| `PUBLIC_BASE_URL` | Public URL used for image proxy rewriting |
| `ALLOWED_IMAGE_HOSTS` | Comma-separated hosts to proxy (defaults to `SALEOR_API_URL` host) |
| `LOGLEVEL` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

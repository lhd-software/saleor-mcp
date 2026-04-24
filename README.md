# Saleor MCP Server (store4ai custom)

A Model Context Protocol (MCP) server for Saleor Commerce — extended with checkout, promotions, customers, and interactive UI tools.

**Live instance:** `https://store4ai-mcp.bi193.com/mcp`

> Based on the [official Saleor MCP](https://mcp.saleor.app/) but with additional write capabilities and an interactive product explorer UI.

---

## Tools available

| Category | Tools |
|----------|-------|
| **Products** | `products`, `get_product_details`, `stocks`, `open_product_explorer` (UI) |
| **Checkout** | `create_cart`, `add_to_cart`, `update_cart_item`, `remove_from_cart`, `open_cart` (UI) |
| **Checkout flow** | `set_shipping_address`, `set_billing_address`, `set_shipping_method`, `get_checkout`, `open_checkout` (UI) |
| **Payment** | `create_payment`, `complete_checkout` |
| **Orders** | `orders`, `order_count`, `track_order` |
| **Promotions** | `list_promotions`, `evaluate_cart_promotions` |
| **Customers** | `customers` |
| **Channels** | `channels` |

---

## Quick start — Connect to live server

No installation needed. Just configure your AI client to point to the live server.

### Validate your token first

```bash
python bi193-shopping/scripts/test_token.py \
  --api-url "https://api.bi193.com/graphql/" \
  --token "YOUR_TOKEN"
```

### Generate config for your client

```bash
python bi193-shopping/scripts/setup_config.py \
  --api-url "https://api.bi193.com/graphql/" \
  --token "YOUR_TOKEN" \
  --client claude   # or: vscode / cursor / all
```

### Claude Desktop

File: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "store4ai-mcp": {
      "type": "http",
      "url": "https://store4ai-mcp.bi193.com/mcp",
      "headers": {
        "X-Saleor-API-URL": "https://api.bi193.com/graphql/",
        "X-Saleor-Auth-Token": "YOUR_TOKEN"
      }
    }
  }
}
```

### VSCode / Copilot

File: `.vscode/mcp.json`

```json
{
  "servers": {
    "store4ai-mcp": {
      "type": "http",
      "url": "https://store4ai-mcp.bi193.com/mcp",
      "headers": {
        "X-Saleor-API-URL": "https://api.bi193.com/graphql/",
        "X-Saleor-Auth-Token": "YOUR_TOKEN"
      }
    }
  }
}
```

### Cursor AI

File: `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "store4ai-mcp": {
      "type": "http",
      "url": "https://store4ai-mcp.bi193.com/mcp",
      "headers": {
        "X-Saleor-API-URL": "https://api.bi193.com/graphql/",
        "X-Saleor-Auth-Token": "YOUR_TOKEN"
      }
    }
  }
}
```

---

## Configuration

### Required headers (per request)

| Header | Description |
|--------|-------------|
| `X-Saleor-API-URL` | Your Saleor GraphQL endpoint, e.g. `https://api.example.com/graphql/` |
| `X-Saleor-Auth-Token` | Staff token with `MANAGE_PRODUCTS` and `MANAGE_ORDERS` permissions |

### Environment variables (server-side)

| Variable | Default | Description |
|----------|---------|-------------|
| `ALLOWED_DOMAIN_PATTERN` | *(empty — allow all)* | Regex to restrict allowed `X-Saleor-API-URL` values |
| `LOGLEVEL` | `INFO` | Logging level |

Example pattern to restrict to `bi193.com` only:
```
ALLOWED_DOMAIN_PATTERN=https:\/\/api\.bi193\.com\/graphql\/
```

---

## Shopping skill

The `bi193-shopping/` directory contains a Claude skill that handles the full shopping lifecycle:

```
bi193-shopping/
├── SKILL.md               # Flow instructions for Claude
└── scripts/
    ├── check_mcp.py       # Check if MCP server is healthy
    ├── setup_config.py    # Generate client config JSON
    └── test_token.py      # Validate API token + permissions
```

Import `bi193-shopping.skill` into your Claude client to get guided shopping flows (search → cart → checkout → track).

---

## Local development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Node.js 20+ (for UI build)

### Setup

```bash
git clone git@github.com:YOUR_ORG/saleor-mcp.git
cd saleor-mcp
uv sync
```

### Run locally

```bash
SALEOR_API_URL="https://api.bi193.com/graphql/" \
SALEOR_AUTH_TOKEN="YOUR_TOKEN" \
uv run saleor-mcp
```

Server starts on `http://localhost:6000`. Add to Claude Desktop:

```json
{
  "mcpServers": {
    "store4ai-mcp-local": {
      "command": "uv",
      "args": ["--directory", "/path/to/saleor-mcp", "run", "saleor-mcp"],
      "env": {
        "SALEOR_API_URL": "https://api.bi193.com/graphql/",
        "SALEOR_AUTH_TOKEN": "YOUR_TOKEN"
      }
    }
  }
}
```

### Build UI

```bash
cd ui-app
npm install
npm run build
# Output: ui-app/dist/mcp-app.html
```

### Regenerate GraphQL client

```bash
ariadne-codegen
```

---

## Deploy to EC2

### Requirements
- Docker + Docker Compose
- Nginx with SSL (`store4ai-mcp.bi193.com`)

### Steps

```bash
# On EC2
cd /opt/saleor-mcp
git pull
docker compose build
docker compose up -d

# Verify
curl https://store4ai-mcp.bi193.com/health
```

### Check server status

```bash
python bi193-shopping/scripts/check_mcp.py
```

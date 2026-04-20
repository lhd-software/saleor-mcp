# MCP App Development Guide — Saleor Product Explorer

Hướng dẫn từng bước xây dựng MCP App UI cho Saleor MCP Server, chạy trong Claude Desktop.

---

## Mục lục

1. [Kiến trúc tổng quan](#1-kiến-trúc-tổng-quan)
2. [Cấu trúc thư mục](#2-cấu-trúc-thư-mục)
3. [Setup Frontend (ui-app)](#3-setup-frontend-ui-app)
4. [Setup Backend (FastMCP)](#4-setup-backend-fastmcp)
5. [Data Flow chi tiết](#5-data-flow-chi-tiết)
6. [Xử lý hình ảnh trong sandbox](#6-xử-lý-hình-ảnh-trong-sandbox)
7. [Gotchas & Pitfalls](#7-gotchas--pitfalls)
8. [Build & Deploy](#8-build--deploy)
9. [Checklist trước khi ship](#9-checklist-trước-khi-ship)

---

## 1. Kiến trúc tổng quan

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Desktop                        │
│                                                          │
│  User prompt ──► Claude LLM ──► calls tool               │
│                                    │                      │
│                     ┌──────────────┼──────────────┐       │
│                     │  MCP Host    │              │       │
│                     │              ▼              │       │
│                     │    open_product_explorer    │       │
│                     │         (STDIO)             │       │
│                     │              │              │       │
│                     │              ▼              │       │
│                     │    FastMCP Server (Python)  │       │
│                     │         │          │        │       │
│                     │    Saleor API    httpx      │       │
│                     │    (GraphQL)   (thumbnails) │       │
│                     │              │              │       │
│                     │              ▼              │       │
│                     │   structuredContent         │       │
│                     │   {products: [...]}         │       │
│                     └──────────────┼──────────────┘       │
│                                    │                      │
│                                    ▼                      │
│                     ┌──────────────────────────┐          │
│                     │  iframe (sandboxed)       │          │
│                     │  ┌────────────────────┐  │          │
│                     │  │  mcp-app.html      │  │          │
│                     │  │  (Vite single-file) │  │          │
│                     │  │                    │  │          │
│                     │  │  ontoolresult() ◄──┼──┼── data   │
│                     │  │  renderProducts()  │  │          │
│                     │  └────────────────────┘  │          │
│                     └──────────────────────────┘          │
└─────────────────────────────────────────────────────────┘
```

**Quy tắc quan trọng nhất:**
- UI chạy trong **sandboxed iframe** — không có access đến network bên ngoài (CSP)
- UI nhận data qua **`ontoolresult`** callback — không tự fetch
- Tất cả binary data (images) phải được **embed as base64** từ server side

---

## 2. Cấu trúc thư mục

```
saleor-mcp/
├── src/saleor_mcp/
│   ├── main.py                  # FastMCP server + tool/resource registration
│   ├── saleor_client/
│   │   └── client.py            # Generated GraphQL client (hardcoded queries)
│   └── graphql/
│       └── ListProducts.graphql # GraphQL query source (for reference)
├── ui-app/                      # Frontend MCP App
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── mcp-app.html             # HTML template (entry point)
│   ├── src/
│   │   └── mcp-app.ts           # TypeScript application logic
│   └── dist/
│       └── mcp-app.html         # ← Build output (single-file, served by server)
└── docs/
```

---

## 3. Setup Frontend (ui-app)

### 3.1 Khởi tạo project

```bash
mkdir ui-app && cd ui-app
npm init -y
npm install @modelcontextprotocol/ext-apps
npm install -D typescript vite vite-plugin-singlefile
```

### 3.2 package.json

```json
{
  "name": "saleor-mcp-app",
  "version": "1.0.0",
  "type": "module",
  "private": true,
  "scripts": {
    "build": "INPUT=mcp-app.html vite build",
    "dev": "vite"
  },
  "dependencies": {
    "@modelcontextprotocol/ext-apps": "^1.6.0"
  },
  "devDependencies": {
    "typescript": "^6.0.3",
    "vite": "^8.0.8",
    "vite-plugin-singlefile": "^2.3.3"
  }
}
```

### 3.3 vite.config.ts

MCP Apps phải là **single HTML file** (JS + CSS inline). Dùng `vite-plugin-singlefile`:

```typescript
import { defineConfig } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

export default defineConfig({
  plugins: [viteSingleFile()],
  build: {
    outDir: "dist",
    rollupOptions: {
      input: process.env.INPUT,
    },
  },
});
```

### 3.4 HTML Template (mcp-app.html)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Saleor Product Explorer</title>
</head>
<body>
    <div id="app">
        <header>
            <h1>🛍 Saleor Explorer</h1>
            <span id="cart-badge" class="badge">Cart: 0</span>
        </header>
        <div id="status-bar">Connecting...</div>
        <div id="product-grid"></div>
    </div>

    <!-- Modal, overlays, etc. -->
    <div id="detail-overlay" class="overlay">
        <div class="modal">
            <div class="modal-header">
                <h2 id="detail-name">Product</h2>
                <button class="close-btn" id="close-modal">&times;</button>
            </div>
            <div class="modal-body">
                <div class="detail-desc" id="detail-desc"></div>
                <div class="detail-price" id="detail-price"></div>
                <div>
                    <strong style="font-size:11px;">Variants:</strong>
                    <div class="variant-list" id="variant-list"></div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" id="close-modal-2">Close</button>
                <button class="btn-primary" id="add-cart-btn">Add to Cart</button>
            </div>
        </div>
    </div>

    <script type="module" src="./src/mcp-app.ts"></script>
</body>
</html>
```

### 3.5 TypeScript Application (mcp-app.ts)

**Cách đúng** — chỉ dùng `ontoolresult` làm nguồn dữ liệu duy nhất:

```typescript
import { App } from "@modelcontextprotocol/ext-apps";

// 1. Create app instance
const app = new App({ name: "Saleor Product Explorer", version: "1.0.0" });

// 2. Register handlers BEFORE connecting
app.onerror = console.error;

// ✅ ontoolresult là nguồn dữ liệu DUY NHẤT
// Nó fire khi tool (open_product_explorer) hoàn thành
app.ontoolresult = (result: any) => {
  const sc = result.structuredContent;
  if (sc?.products && Array.isArray(sc.products)) {
    renderProducts(sc.products);
    return;
  }
  // Fallback: parse from content[].text
  processContentArray(result.content);
};

// 3. Connect — KHÔNG gọi bất kỳ loadProducts() nào
app.connect().then(() => {
  statusBar.textContent = "⏳ Loading products...";
  // ontoolresult sẽ tự fire với data đã filtered
}).catch((err: any) => {
  statusBar.textContent = "❌ Connect failed: " + err.message;
});
```

> ⚠️ **ĐỪNG BAO GIỜ** gọi `callServerTool()` trong `app.connect().then()` để "preload" data.
> Điều này tạo ra race condition — `ontoolresult` đã mang data filtered từ Claude,
> nhưng `callServerTool()` sẽ ghi đè bằng data unfiltered.

### 3.6 Gọi tool từ UI (cho actions như Add to Cart)

```typescript
// Dùng callServerTool chỉ cho USER ACTIONS (click button, etc.)
async function handleAddToCart() {
  try {
    await app.callServerTool({
      name: "create_cart",
      arguments: {
        channel: "default-channel",
        lines: [{ variantId: selectedVariantId, quantity: 1 }],
      },
    });
    // Update UI on success
  } catch (err: any) {
    console.warn("Cart call failed:", err.message);
  }
}
```

---

## 4. Setup Backend (FastMCP)

### 4.1 Đăng ký Resource (UI HTML)

```python
RESOURCE_URI = "ui://saleor/product-explorer.html"
RESOURCE_MIME_TYPE = "text/html;profile=mcp-app"

@mcp.resource(
    RESOURCE_URI,
    mime_type=RESOURCE_MIME_TYPE,
    # Note: meta.ui.csp may not be serialized correctly by FastMCP
    # Use base64 embedding for images instead
    meta={"ui": {"csp": {"resourceDomains": ["your-api-domain.com"]}}},
)
async def product_explorer_ui() -> str:
    """The Product Explorer UI application (Vite-built single-file)."""
    path = "ui-app/dist/mcp-app.html"
    with open(path, "r") as f:
        return f.read()
```

**Quy tắc:**
- `mime_type` PHẢI là `"text/html;profile=mcp-app"` — đây là signal cho Claude Desktop render iframe
- `RESOURCE_URI` dùng scheme `ui://` (convention)
- File phải là **single self-contained HTML** (Vite singlefile output)

### 4.2 Đăng ký Tool (mở UI + cung cấp data)

```python
@mcp.tool(
    meta={
        "ui": {
            "resourceUri": RESOURCE_URI,  # ← Liên kết tool với UI resource
        }
    }
)
async def open_product_explorer(
    ctx: Context,
    channel: str = "default-channel",
    first: int = 20,
    search: str = "",
) -> dict:
    """Open an interactive product explorer UI.

    IMPORTANT: Always pass 'search' based on user intent.
    Examples:
      - User wants shoes → search='shoes'
      - User wants gifts for kids → search='kids'
    Only omit search if user explicitly wants ALL products.
    """
    # 1. Fetch products from Saleor
    # 2. Embed thumbnails as base64
    # 3. Return normalized dict
    return {"products": [...], "totalCount": N}
```

**Quy tắc:**
- `meta.ui.resourceUri` PHẢI trùng với `RESOURCE_URI` → Claude Desktop biết render UI nào
- Tool return `dict` → được serialize thành `structuredContent` trong MCP response
- Tool docstring phải **hướng dẫn Claude truyền search param** — nếu không, Claude sẽ gọi tool không có argument

### 4.3 Normalize data trước khi trả về UI

**ĐỪNG** trả raw GraphQL response. Normalize thành flat format:

```python
# ❌ Sai — raw GraphQL
return data.products  # {edges: [{node: {id, name, thumbnail: {url}, pricing: {priceRange: ...}}}]}

# ✅ Đúng — normalized flat format
product = {
    "id": node.id,
    "name": node.name,
    "slug": node.slug,
    "description": node.description,
    "thumbnail": {"url": "data:image/png;base64,..."},  # ← base64!
    "pricing": {"amount": 28.0, "currency": "USD"},
    "variants": [{"id": "...", "name": "S"}, {"id": "...", "name": "M"}],
}
return {"products": [product, ...], "totalCount": len(products)}
```

---

## 5. Data Flow chi tiết

```
                          ┌─────────────┐
User: "xem áo hoodie"    │ Claude LLM  │
           │              │             │
           ▼              │  Decides to │
                          │  call tool  │
           │              └──────┬──────┘
           ▼                     │
  open_product_explorer          │
  (search="hoodie")              │
           │                     │
           ▼                     │
  ┌────────────────────┐         │
  │ FastMCP Server     │         │
  │                    │         │
  │ 1. Saleor GraphQL  │         │
  │    search="hoodie" │         │
  │    → 3 products    │         │
  │                    │         │
  │ 2. Fetch thumbnails│         │
  │    (parallel httpx)│         │
  │    follow_redirects│         │
  │    → base64 encode │         │
  │                    │         │
  │ 3. Return dict:    │         │
  │    {products: [3]} │         │
  └────────┬───────────┘         │
           │                     │
           ▼                     │
  structuredContent              │
  (MCP protocol)                 │
           │                     │
           ▼                     │
  ┌────────────────────┐         │
  │ iframe (mcp-app)   │         │
  │                    │         │
  │ ontoolresult(res)  │◄────────┘
  │   sc = res.structuredContent
  │   renderProducts(sc.products)
  │   → 3 hoodie cards │
  │   → with images!   │
  └────────────────────┘
```

---

## 6. Xử lý hình ảnh trong sandbox

### Vấn đề

Claude Desktop iframe có **Content Security Policy** nghiêm ngặt:
- `<img src="https://external-domain/...">` → **BLOCKED**
- `<img src="data:image/png;base64,...">` → **ALLOWED**

### Giải pháp: Server-side base64 embedding

```python
import asyncio
import base64
import httpx

async def fetch_thumb(http: httpx.AsyncClient, product: dict) -> None:
    thumb = product.get("thumbnail")
    if not thumb or not thumb.get("url") or thumb["url"].startswith("data:"):
        return
    try:
        resp = await http.get(thumb["url"], timeout=5.0)
        if resp.status_code == 200:
            ct = resp.headers.get("content-type", "image/jpeg").split(";")[0]
            b64 = base64.b64encode(resp.content).decode()
            product["thumbnail"] = {"url": f"data:{ct};base64,{b64}"}
    except Exception:
        pass  # giữ original URL as fallback

# ⚠️ PHẢI dùng follow_redirects=True — Saleor thumbnail URLs trả 302
async with httpx.AsyncClient(follow_redirects=True) as http:
    await asyncio.gather(*[fetch_thumb(http, p) for p in products])
```

### Tối ưu kích thước

Dùng `thumbnail(size: 128)` trong GraphQL query thay vì 256px mặc định:

```graphql
# Trong ListProducts.graphql VÀ trong client.py (hardcoded query)
thumbnail(size: 128) {
  url
}
```

| Size  | Avg/image | 20 products | Phù hợp? |
| :---- | :-------- | :---------- | :-------- |
| 256px | ~40KB     | ~900KB      | ❌ Quá lớn |
| 128px | ~15KB     | ~300KB      | ✅ OK     |
| 64px  | ~5KB      | ~100KB      | ✅ Nhỏ nhất, hơi mờ |

> **Lưu ý:** Sửa query ở **2 nơi** — file `.graphql` (reference) VÀ `client.py` (hardcoded, thực tế được dùng).

---

## 7. Gotchas & Pitfalls

### ❌ Đừng tự load data trong UI

```typescript
// ❌ WRONG — tạo race condition, ghi đè filtered data
app.connect().then(() => {
  loadProducts();  // gọi {first: 20} không search!
});

// ✅ RIGHT — chờ ontoolresult
app.connect().then(() => {
  statusBar.textContent = "⏳ Loading...";
});
```

### ❌ Đừng hardcode tool arguments trong UI

```typescript
// ❌ WRONG — UI không biết user muốn search gì
callServerTool({ name: "open_product_explorer", arguments: { first: 20 } })

// ✅ RIGHT — để Claude quyết định arguments qua ontoolresult
// UI chỉ nhận kết quả, không tự gọi tool để load data
```

### ❌ Đừng quên follow_redirects

```python
# ❌ httpx mặc định KHÔNG follow redirect
httpx.AsyncClient()  # → 302 → 0 bytes → no image

# ✅ Luôn bật
httpx.AsyncClient(follow_redirects=True)
```

### ❌ Đừng trả raw GraphQL response cho UI

```python
# ❌ UI phải biết cấu trúc GraphQL edges/nodes
return data.products

# ✅ Normalize thành flat dict
return {"products": [{"id": ..., "name": ..., "thumbnail": {"url": "data:..."}}]}
```

### ❌ Đừng tin meta.ui.csp hoạt động với FastMCP

```python
# ❌ FastMCP có thể không serialize _meta đúng spec
@mcp.resource(meta={"ui": {"csp": {"resourceDomains": ["api.example.com"]}}})

# ✅ Dùng base64 embedding — luôn hoạt động bất kể CSP config
```

### ❌ Đừng quên hướng dẫn Claude trong docstring

```python
# ❌ Claude sẽ gọi tool không arguments
"""Open product explorer."""

# ✅ Claude sẽ truyền search param
"""Open product explorer.
IMPORTANT: Always pass 'search' based on what user is looking for.
  - shoes → search='shoes'
  - gifts for kids → search='kids'
Only omit if user wants ALL products."""
```

---

## 8. Build & Deploy

### Development workflow

```bash
# 1. Sửa code trong ui-app/src/mcp-app.ts
# 2. Build
cd ui-app && npm run build

# 3. Restart Claude Desktop (Cmd+Q → reopen)
#    Server STDIO restart tự động theo

# 4. Test trong Claude Desktop
#    "cho tôi xem áo hoodie với product explorer"
```

### Claude Desktop config

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "saleor-mcp": {
      "command": "/path/to/saleor-mcp/.venv/bin/python3",
      "args": ["-m", "saleor_mcp.main"],
      "cwd": "/path/to/saleor-mcp",
      "env": {
        "PYTHONPATH": "src",
        "SALEOR_API_URL": "https://your-api.example.com/graphql/",
        "SALEOR_AUTH_TOKEN": "your-token-here"
      }
    }
  }
}
```

### Chạy server thủ công (dev)

```bash
cd /path/to/saleor-mcp
PYTHONPATH=src SALEOR_API_URL="..." SALEOR_AUTH_TOKEN="..." .venv/bin/python3 -m saleor_mcp.main
```

---

## 9. Checklist trước khi ship

### Backend

- [ ] Tool return `dict` (not raw GraphQL response)
- [ ] Thumbnail URLs embedded as base64 data URIs
- [ ] `httpx.AsyncClient(follow_redirects=True)` — Saleor returns 302
- [ ] `thumbnail(size: 128)` in **cả** `.graphql` file **và** `client.py`
- [ ] Tool docstring hướng dẫn Claude luôn truyền `search` param
- [ ] `meta.ui.resourceUri` trùng với resource URI

### Frontend

- [ ] `ontoolresult` là nguồn data duy nhất — không có `loadProducts()` tự gọi
- [ ] Không hardcode `{first: 20}` hay bất kỳ tool arguments nào
- [ ] CSS inline trong TypeScript (hoặc import) — Vite singlefile sẽ bundle
- [ ] `onerror` handler registered
- [ ] Build output là **single HTML file** (`vite-plugin-singlefile`)

### Config

- [ ] `mime_type = "text/html;profile=mcp-app"`
- [ ] Resource URI scheme là `ui://`
- [ ] Claude Desktop config có đúng `cwd`, `PYTHONPATH`, env vars
- [ ] `.gitignore` có `node_modules/`, `ui-app/dist/`, `.env*.local`

### Testing

- [ ] Test GraphQL query trực tiếp: `python3 -c "..."` với env vars
- [ ] Test thumbnail fetch: verify HTTP 200 (không phải 302) sau redirect
- [ ] Test base64 output size: `< 30KB per image` cho 128px
- [ ] Test trong Claude Desktop: search filtered → đúng số sản phẩm + có hình

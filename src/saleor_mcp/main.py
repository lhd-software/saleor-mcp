from fastmcp import Context, FastMCP
from fastmcp.server.middleware.timing import DetailedTimingMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles

from saleor_mcp.docs import generate_html
from saleor_mcp.tools import (
    channels_router,
    checkout_router,
    customers_router,
    orders_router,
    products_router,
    promotions_router,
    utils_router,
)

mcp = FastMCP("Saleor MCP Server")
mcp.add_middleware(DetailedTimingMiddleware())
mcp.mount(channels_router)
mcp.mount(checkout_router)
mcp.mount(customers_router)
mcp.mount(orders_router)
mcp.mount(products_router)
mcp.mount(promotions_router)
mcp.mount(utils_router)


RESOURCE_URI = "ui://saleor/product-explorer.html"
RESOURCE_MIME_TYPE = "text/html;profile=mcp-app"


@mcp.resource(
    RESOURCE_URI,
    mime_type=RESOURCE_MIME_TYPE,
    meta={"ui": {"csp": {"resourceDomains": ["api.bi193.com"]}}},
)
async def product_explorer_ui() -> str:
    """The Product Explorer UI application (Vite-built single-file)."""
    path = "ui-app/dist/mcp-app.html"
    with open(path, "r") as f:
        return f.read()


@mcp.tool(
    meta={
        "ui": {
            "resourceUri": RESOURCE_URI,
        }
    }
)
async def open_product_explorer(
    ctx: Context,
    channel: str = "default-channel",
    first: int = 20,
    search: str = "",
) -> dict:
    """Open an interactive product explorer UI to browse Saleor products visually.

    This tool renders a graphical product grid with thumbnails, prices, and variants.
    IMPORTANT: Always pass the 'search' parameter based on what the user is looking for.
    Examples:
      - User wants shoes → search='shoes'
      - User wants gifts for kids → search='kids'
      - User wants hoodies → search='hoodie'
    Only omit search if user explicitly wants to see ALL products.
    """
    import asyncio
    import base64
    import httpx
    from saleor_mcp.ctx_utils import get_saleor_client

    client = get_saleor_client()
    try:
        data = await client.list_products(
            first=first,
            after=None,
            channel=channel,
            sortBy=None,
            search=search or None,
            where=None,
        )
        products_data = data.products
        edges = products_data.edges if products_data and products_data.edges else []

        products = []
        for edge in edges:
            node = edge.node
            product = {
                "id": node.id,
                "name": node.name,
                "slug": getattr(node, "slug", ""),
                "description": getattr(node, "description", ""),
            }
            if hasattr(node, "thumbnail") and node.thumbnail:
                product["thumbnail"] = {"url": node.thumbnail.url}
            if hasattr(node, "pricing") and node.pricing:
                pr = node.pricing
                if hasattr(pr, "priceRange") and pr.priceRange and pr.priceRange.start:
                    gross = pr.priceRange.start.gross
                    product["pricing"] = {
                        "amount": float(gross.amount),
                        "currency": gross.currency,
                    }
            if hasattr(node, "productVariants") and node.productVariants:
                pvs = node.productVariants
                if hasattr(pvs, "edges") and pvs.edges:
                    product["variants"] = [
                        {"id": e.node.id, "name": e.node.name}
                        for e in pvs.edges
                    ]
            products.append(product)

        # Fetch all thumbnails in parallel → embed as base64 data URIs
        # Needed because Claude Desktop's iframe sandbox blocks external image URLs (CSP)
        async def fetch_thumb(http: httpx.AsyncClient, p: dict) -> None:
            thumb = p.get("thumbnail")
            if not thumb or not thumb.get("url") or thumb["url"].startswith("data:"):
                return
            try:
                resp = await http.get(thumb["url"], timeout=5.0)
                if resp.status_code == 200:
                    ct = resp.headers.get("content-type", "image/jpeg").split(";")[0]
                    b64 = base64.b64encode(resp.content).decode()
                    p["thumbnail"] = {"url": f"data:{ct};base64,{b64}"}
            except Exception:
                pass

        async with httpx.AsyncClient(follow_redirects=True) as http:
            await asyncio.gather(*[fetch_thumb(http, p) for p in products])

        return {"products": products, "totalCount": len(products)}
    except Exception as e:
        await ctx.error(str(e))
        return {"error": str(e), "products": []}







@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    return JSONResponse({"status": "healthy"})


app = mcp.http_app(stateless_http=True)
app.mount("/static", StaticFiles(directory="src/saleor_mcp/static"), name="static")


def main():
    mcp.run()


if __name__ == "__main__":
    main()

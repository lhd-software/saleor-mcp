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

        return {"view": "products", "products": products, "totalCount": len(products)}
    except Exception as e:
        await ctx.error(str(e))
        return {"error": str(e), "products": []}


def _serialize_checkout(checkout: object) -> dict:
    """Normalize Saleor checkout object to flat dict for UI."""
    c = checkout
    lines = []
    if hasattr(c, "lines") and c.lines:
        for ln in c.lines:
            line = {
                "id": ln.id,
                "quantity": ln.quantity,
                "variantName": ln.variant.name if hasattr(ln, "variant") and ln.variant else "",
            }
            lines.append(line)
    result: dict = {
        "id": c.id,
        "lines": lines,
    }
    if hasattr(c, "totalPrice") and c.totalPrice and c.totalPrice.gross:
        result["total"] = {
            "amount": float(c.totalPrice.gross.amount),
            "currency": c.totalPrice.gross.currency,
        }
    if hasattr(c, "shippingAddress") and c.shippingAddress:
        sa = c.shippingAddress
        result["shippingAddress"] = {
            "firstName": getattr(sa, "firstName", ""),
            "lastName": getattr(sa, "lastName", ""),
            "streetAddress1": getattr(sa, "streetAddress1", ""),
            "streetAddress2": getattr(sa, "streetAddress2", ""),
            "city": getattr(sa, "city", ""),
            "postalCode": getattr(sa, "postalCode", ""),
            "country": getattr(sa.country, "code", "VN") if hasattr(sa, "country") and sa.country else "VN",
            "phone": getattr(sa, "phone", ""),
        }
    if hasattr(c, "availableShippingMethods") and c.availableShippingMethods:
        result["shippingMethods"] = [
            {"id": m.id, "name": m.name, "price": float(m.price.amount) if m.price else 0}
            for m in c.availableShippingMethods
        ]
    if hasattr(c, "availablePaymentGateways") and c.availablePaymentGateways:
        result["paymentGateways"] = [
            {"id": g.id, "name": g.name} for g in c.availablePaymentGateways
        ]
    return result


@mcp.tool(meta={"ui": {"resourceUri": RESOURCE_URI}})
async def open_cart(
    ctx: Context,
    checkout_id: str,
) -> dict:
    """Open the cart UI showing current checkout lines, quantities, and totals.

    Use this after adding items to cart to let the user review before checkout.
    """
    from saleor_mcp.ctx_utils import get_saleor_client
    client = get_saleor_client()
    try:
        data = await client.checkout_details(id=checkout_id)
        if not data.checkout:
            return {"view": "cart", "error": "Checkout not found"}
        return {"view": "cart", "checkout": _serialize_checkout(data.checkout)}
    except Exception as e:
        await ctx.error(str(e))
        return {"view": "cart", "error": str(e)}


@mcp.tool(meta={"ui": {"resourceUri": RESOURCE_URI}})
async def open_checkout(
    ctx: Context,
    checkout_id: str,
    first_name: str = "",
    last_name: str = "",
    street_address: str = "",
    city: str = "",
    postal_code: str = "",
    country: str = "VN",
    phone: str = "",
) -> dict:
    """Open the checkout UI for address entry, shipping method selection, and payment.

    Use this when the user is ready to proceed from cart to checkout.
    IMPORTANT: If the user has mentioned their name, address, phone, or city in the
    conversation, pass those values here to pre-fill the form automatically.
    Examples:
      - User says "tôi ở 123 Nguyễn Huệ, Q1, HCM" → street_address="123 Nguyễn Huệ", city="Ho Chi Minh"
      - User says "tên tôi là Nguyễn Văn A" → first_name="Văn A", last_name="Nguyễn"
      - User says "ship về VN" → country="VN"
    """
    from saleor_mcp.ctx_utils import get_saleor_client
    client = get_saleor_client()
    try:
        data = await client.checkout_details(id=checkout_id)
        if not data.checkout:
            return {"view": "checkout", "error": "Checkout not found"}
        result = {"view": "checkout", "checkout": _serialize_checkout(data.checkout)}

        # Pass any address info from Claude's conversation context
        prefill = {}
        if first_name: prefill["firstName"] = first_name
        if last_name: prefill["lastName"] = last_name
        if street_address: prefill["streetAddress1"] = street_address
        if city: prefill["city"] = city
        if postal_code: prefill["postalCode"] = postal_code
        if country: prefill["country"] = country
        if phone: prefill["phone"] = phone
        if prefill:
            result["prefillAddress"] = prefill

        return result
    except Exception as e:
        await ctx.error(str(e))
        return {"view": "checkout", "error": str(e)}





@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    return JSONResponse({"status": "healthy"})


app = mcp.http_app(stateless_http=True)
app.mount("/static", StaticFiles(directory="src/saleor_mcp/static"), name="static")


def main():
    mcp.run()


if __name__ == "__main__":
    main()

import os
from urllib.parse import quote, urlparse

import httpx
from fastmcp import Context, FastMCP
from fastmcp.server.middleware.timing import DetailedTimingMiddleware
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
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

# Public URL at which this MCP server is reachable from the UI iframe.
# UI thumbnail URLs are rewritten to flow through {PUBLIC_BASE_URL}/img?u=<saleor_url>
# so Saleor's `content-disposition: attachment` header doesn't break inline <img> rendering.
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")


def _allowed_image_hosts() -> set[str]:
    """Hosts the image proxy will fetch from.

    Priority: explicit ALLOWED_IMAGE_HOSTS env (comma-separated) → host of
    SALEOR_API_URL env. Empty set means proxy refuses every URL.
    """
    explicit = os.getenv("ALLOWED_IMAGE_HOSTS", "").strip()
    if explicit:
        return {h.strip() for h in explicit.split(",") if h.strip()}
    saleor_url = os.getenv("SALEOR_API_URL", "").strip()
    if saleor_url:
        host = urlparse(saleor_url).hostname
        if host:
            return {host}
    return set()


def _proxy_thumb_url(original_url: str | None) -> str | None:
    """Rewrite a Saleor thumbnail URL to flow through this server's /img proxy."""
    if not original_url:
        return None
    if original_url.startswith("data:") or original_url.startswith(PUBLIC_BASE_URL):
        return original_url
    return f"{PUBLIC_BASE_URL}/img?u={quote(original_url, safe='')}"


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
    meta={"ui": {"csp": {"resourceDomains": [PUBLIC_BASE_URL]}}},
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
      - User wants shoes -> search='shoes'
      - User wants gifts for kids -> search='kids'
      - User wants hoodies -> search='hoodie'
    Only omit search if user explicitly wants to see ALL products.
    """
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
                proxied = _proxy_thumb_url(node.thumbnail.url)
                if proxied:
                    product["thumbnail"] = {"url": proxied}
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

        # Split UI payload (rich, with base64 thumbnails) from LLM content
        # (lightweight summary). Thumbnails can be ~100KB each; embedding them
        # in the LLM context bloats it past the request limit.
        summary_lines = [
            f"- {p['name']} (id={p['id']}, slug={p.get('slug','')}, "
            f"price={p.get('pricing',{}).get('amount','?')} "
            f"{p.get('pricing',{}).get('currency','')}, "
            f"variants={len(p.get('variants', []))})"
            for p in products
        ]
        summary = (
            f"Opened product explorer UI with {len(products)} product(s)"
            + (f" matching '{search}'." if search else ".")
            + ("\n" + "\n".join(summary_lines) if summary_lines else "")
        )
        return ToolResult(
            content=[TextContent(type="text", text=summary)],
            structured_content={
                "view": "products",
                "products": products,
                "totalCount": len(products),
            },
        )
    except Exception as e:
        await ctx.error(str(e))
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: {e}")],
            structured_content={"view": "products", "error": str(e), "products": []},
        )


def _serialize_checkout(checkout: object) -> dict:
    """Normalize Saleor checkout object to flat dict for UI."""
    c = checkout
    lines = []
    if hasattr(c, "lines") and c.lines:
        for ln in c.lines:
            # Safely extract variant and product info
            variant = getattr(ln, "variant", None)
            product = getattr(variant, "product", None) if variant else None
            
            v_name = getattr(variant, "name", "") or ""
            p_name = getattr(product, "name", "") or ""

            # Saleor sometimes echoes the variant ID in `name` — hide it in that case.
            v_id = getattr(variant, "id", "") if variant else ""
            if v_name and v_name == v_id:
                v_name = ""

            display_name = p_name if p_name else "Product"

            thumb_url = None
            if product and hasattr(product, "thumbnail") and product.thumbnail:
                raw_thumb = getattr(product.thumbnail, "url", None)
                thumb_url = _proxy_thumb_url(raw_thumb)

            lines.append({
                "id": getattr(ln, "id", ""),
                "quantity": getattr(ln, "quantity", 0),
                "variantName": v_name,
                "productName": display_name,
                "thumbnail": thumb_url,
            })
    result: dict = {
        "id": getattr(c, "id", ""),
        "email": getattr(c, "email", "") or "",
        "lines": lines,
    }
    # Currently selected shipping method, if any
    delivery = getattr(c, "deliveryMethod", None)
    if delivery is not None:
        result["selectedShippingMethodId"] = getattr(delivery, "id", "")
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
      - User says "tôi ở 123 Nguyễn Huệ, Q1, HCM" -> street_address="123 Nguyễn Huệ", city="Ho Chi Minh"
      - User says "tên tôi là Nguyễn Văn A" -> first_name="Văn A", last_name="Nguyễn"
      - User says "ship về VN" -> country="VN"
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


@mcp.custom_route("/img", methods=["GET"])
async def proxy_image(request: Request):
    """Proxy whitelisted upstream image URLs.

    Why: Saleor serves thumbnails with `content-disposition: attachment`, which
    Claude Desktop's sandboxed iframe treats as a forced download and refuses
    to render inline via <img>. We refetch and re-serve without that header
    (and with a generous cache so the host can cache by URL).
    """
    url = request.query_params.get("u", "")
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        return JSONResponse({"error": "invalid url"}, status_code=400)
    host = urlparse(url).hostname
    allowed = _allowed_image_hosts()
    if not host or host not in allowed:
        return JSONResponse(
            {"error": "host not allowed", "host": host, "allowed": sorted(allowed)},
            status_code=403,
        )
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as http:
            upstream = await http.get(url)
    except Exception as e:
        return JSONResponse({"error": f"upstream fetch failed: {e}"}, status_code=502)
    if upstream.status_code != 200:
        return JSONResponse(
            {"error": "upstream error", "status": upstream.status_code},
            status_code=502,
        )
    content_type = upstream.headers.get("content-type", "image/jpeg").split(";")[0]
    return Response(
        content=upstream.content,
        media_type=content_type,
        headers={
            "Cache-Control": "public, max-age=86400",
            "Access-Control-Allow-Origin": "*",
        },
    )


app = mcp.http_app(stateless_http=True)
app.mount("/static", StaticFiles(directory="src/saleor_mcp/static"), name="static")


def main():
    mcp.run()


if __name__ == "__main__":
    main()

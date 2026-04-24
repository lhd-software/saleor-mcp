from typing import Annotated, Any

from fastmcp import Context, FastMCP

from ..config import get_config_from_headers
from ..ctx_utils import get_saleor_client

utils_router = FastMCP("Utils MCP")


@utils_router.tool()
def current_domain() -> str:
    """Return the current domain of the connected Saleor instance."""

    headers = get_config_from_headers()
    return headers.api_url


@utils_router.tool(
    annotations={
        "title": "Catalog Overview",
        "readOnlyHint": True,
        "idempotentHint": True,
    }
)
async def catalog_overview(
    ctx: Context,
    channel: Annotated[str, "Channel slug."] = "default-channel",
) -> dict[str, Any]:
    """Return a compact catalog map for grounding product recommendations.

    Call this BEFORE searching when the shopping intent is vague (e.g. "a
    gift", "something for dinner"). Response is ~2 KB and lists: top-level
    categories with product counts and 3 sample product names each, plus
    active collections. Use it to:
      * narrow down which category/collection the user actually wants,
      * answer "what kinds of things do you sell?",
      * fall back to category suggestions when a keyword search returns 0.
    """
    client = get_saleor_client()
    try:
        data = await client.catalog_overview(channel=channel)
    except Exception as e:
        await ctx.error(str(e))
        return {"error": str(e), "categories": [], "collections": []}

    categories = []
    for edge in (data.categories.edges if data.categories else []):
        n = edge.node
        top = [
            {"id": e.node.id, "name": e.node.name, "slug": e.node.slug}
            for e in (n.products.edges if n.products and n.products.edges else [])
        ]
        categories.append({
            "id": n.id,
            "slug": n.slug,
            "name": n.name,
            "productCount": n.products.totalCount if n.products else 0,
            "topProducts": top,
        })

    collections = []
    for edge in (data.collections.edges if data.collections else []):
        n = edge.node
        collections.append({
            "id": n.id,
            "slug": n.slug,
            "name": n.name,
            "productCount": n.products.totalCount if n.products else 0,
        })

    return {
        "channel": channel,
        "categories": categories,
        "collections": collections,
    }

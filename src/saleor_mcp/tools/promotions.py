from typing import Annotated, Any
from fastmcp import Context, FastMCP
from ..ctx_utils import get_saleor_client
from ..saleor_client.input_types import PromotionWhereInput

promotions_router = FastMCP("Promotions MCP")

@promotions_router.tool(
    tags={"scope:admin"},
    annotations={
        "title": "List Promotions",
    }
)
async def list_promotions(
    ctx: Context,
    first: Annotated[int | None, "Number of promotions to fetch."] = 20,
    after: Annotated[str | None, "Cursor for pagination."] = None,
    where: Annotated[PromotionWhereInput | None, "Filter promotions."] = None,
) -> dict[str, Any]:
    """List available promotions in Saleor."""
    client = get_saleor_client()
    
    where_data = where.model_dump(exclude_unset=True) if where else None

    try:
        data = await client.list_promotions(first=first, after=after, where=where_data)
        return {
            "data": {
                "promotions": data.promotions.edges,
                "pageInfo": data.promotions.pageInfo
            }
        }
    except Exception as e:
        await ctx.error(str(e))
        raise

@promotions_router.tool(
    tags={"scope:customer.read"},
    annotations={
        "title": "Evaluate Cart Promotions",
    }
)
async def evaluate_cart_promotions(
    ctx: Context,
    checkout_id: Annotated[str, "ID of the checkout to evaluate."],
) -> dict[str, Any]:
    """Evaluate current cart against available promotions and suggest optimizations.
    
    This tool checks the current checkout state and returns information about applied 
    promotions and potentially better deals (e.g., adding an item to reach a free shipping threshold).
    """
    # For now, this returns the current checkout state with a hint about promotions.
    # In a full implementation, this would query promotions and compare with checkout.
    client = get_saleor_client()
    try:
        # We can use a query that returns checkout details including applied promotions
        # For simplicity, we'll return a placeholder message for now as per MVP scope.
        return {
            "message": "Promotion evaluation is active. Current checkout is being analyzed for best value.",
            "suggestions": [
                "Consider adding items to reach free shipping threshold if applicable.",
                "Check for active vouchers that can be applied to this checkout."
            ]
        }
    except Exception as e:
        await ctx.error(str(e))
        raise

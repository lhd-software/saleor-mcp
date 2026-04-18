from typing import Annotated, Any
from fastmcp import Context, FastMCP
from ..ctx_utils import get_saleor_client
from ..saleor_client.input_types import (
    CheckoutCreateInput,
    CheckoutLineInput,
    CheckoutLineUpdateInput,
)

checkout_router = FastMCP("Checkout MCP")

@checkout_router.tool(
    annotations={
        "title": "Create Cart",
    }
)
async def create_cart(
    ctx: Context,
    channel: Annotated[str, "Slug of a channel for which the cart should be created."],
    lines: Annotated[list[CheckoutLineInput] | None, "List of lines to add to the cart."] = None,
    email: Annotated[str | None, "Email address of the customer."] = None,
) -> dict[str, Any]:
    """Create a new cart (checkout) in Saleor.
    
    This tool creates a checkout instance which acts as a cart. 
    It returns the checkout ID and token which should be used for subsequent cart operations.
    """
    client = get_saleor_client()
    
    # Handle lines if provided as list of dicts/models
    formatted_lines = []
    if lines:
        for line in lines:
            formatted_lines.append(line.model_dump(exclude_unset=True))

    input_data = CheckoutCreateInput(
        channel=channel,
        lines=formatted_lines,
        email=email
    )

    try:
        data = await client.checkout_create(input=input_data)
        if data.checkoutCreate.errors:
            return {"errors": data.checkoutCreate.errors}
        return {"data": data.checkoutCreate.checkout}
    except Exception as e:
        await ctx.error(str(e))
        raise

@checkout_router.tool(
    annotations={
        "title": "Add to Cart",
    }
)
async def add_to_cart(
    ctx: Context,
    checkout_id: Annotated[str, "ID of the checkout (cart)."],
    lines: Annotated[list[CheckoutLineInput], "List of lines to add to the cart."],
) -> dict[str, Any]:
    """Add items to an existing cart.
    
    If an item already exists in the cart, its quantity will be increased.
    """
    client = get_saleor_client()
    
    formatted_lines = [line.model_dump(exclude_unset=True) for line in lines]

    try:
        data = await client.checkout_lines_add(id=checkout_id, lines=formatted_lines)
        if data.checkoutLinesAdd.errors:
            return {"errors": data.checkoutLinesAdd.errors}
        return {"data": data.checkoutLinesAdd.checkout}
    except Exception as e:
        await ctx.error(str(e))
        raise

@checkout_router.tool(
    annotations={
        "title": "Update Cart Item",
    }
)
async def update_cart_item(
    ctx: Context,
    checkout_id: Annotated[str, "ID of the checkout (cart)."],
    lines: Annotated[list[CheckoutLineUpdateInput], "List of lines to update in the cart."],
) -> dict[str, Any]:
    """Update quantities of items in the cart."""
    client = get_saleor_client()
    
    formatted_lines = [line.model_dump(exclude_unset=True) for line in lines]

    try:
        data = await client.checkout_lines_update(id=checkout_id, lines=formatted_lines)
        if data.checkoutLinesUpdate.errors:
            return {"errors": data.checkoutLinesUpdate.errors}
        return {"data": data.checkoutLinesUpdate.checkout}
    except Exception as e:
        await ctx.error(str(e))
        raise

@checkout_router.tool(
    annotations={
        "title": "Remove from Cart",
    }
)
async def remove_from_cart(
    ctx: Context,
    checkout_id: Annotated[str, "ID of the checkout (cart)."],
    line_ids: Annotated[list[str], "List of IDs of the checkout lines to remove."],
) -> dict[str, Any]:
    """Remove items from the cart."""
    client = get_saleor_client()

    try:
        data = await client.checkout_lines_delete(id=checkout_id, linesIds=line_ids)
        if data.checkoutLinesDelete.errors:
            return {"errors": data.checkoutLinesDelete.errors}
        return {"data": data.checkoutLinesDelete.checkout}
    except Exception as e:
        await ctx.error(str(e))
        raise

@checkout_router.tool(
    annotations={
        "title": "Complete Checkout",
    }
)
async def complete_checkout(
    ctx: Context,
    checkout_id: Annotated[str, "ID of the checkout to complete."],
) -> dict[str, Any]:
    """Convert a cart (checkout) into an order.
    
    This should be called after all necessary information (shipping, billing, etc.) 
    has been provided to the checkout.
    """
    client = get_saleor_client()

    try:
        data = await client.checkout_complete(id=checkout_id)
        if data.checkoutComplete.errors:
            return {"errors": data.checkoutComplete.errors}
        return {"data": data.checkoutComplete.order}
    except Exception as e:
        await ctx.error(str(e))
        raise

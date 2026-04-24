from typing import Annotated, Any
from fastmcp import Context, FastMCP
from ..ctx_utils import get_saleor_client
from ..saleor_client.input_types import (
    AddressInput,
    CheckoutCreateInput,
    CheckoutLineInput,
    CheckoutLineUpdateInput,
    PaymentInput,
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

@checkout_router.tool(
    annotations={
        "title": "Get Checkout Details",
    }
)
async def get_checkout(
    ctx: Context,
    checkout_id: Annotated[str, "ID of the checkout to fetch."],
) -> dict[str, Any]:
    """Fetch checkout details including available shipping methods and payment gateways.
    
    Use this to see which shipping methods are available after setting the shipping address.
    """
    client = get_saleor_client()
    try:
        data = await client.checkout_details(id=checkout_id)
        if not data.checkout:
            return {"error": "Checkout not found"}
        return {"data": data.checkout}
    except Exception as e:
        await ctx.error(str(e))
        raise

@checkout_router.tool(
    annotations={
        "title": "Set Checkout Email",
    }
)
async def set_checkout_email(
    ctx: Context,
    checkout_id: Annotated[str, "ID of the checkout."],
    email: Annotated[str, "Customer email address for the order."],
) -> dict[str, Any]:
    """Attach a customer email to the checkout.

    Required before complete_checkout can succeed when the checkout was created
    anonymously (no email). Collect the email as early as possible in the flow.
    """
    client = get_saleor_client()
    try:
        data = await client.checkout_email_update(id=checkout_id, email=email)
        if data.checkoutEmailUpdate.errors:
            return {"errors": data.checkoutEmailUpdate.errors}
        return {"data": data.checkoutEmailUpdate.checkout}
    except Exception as e:
        await ctx.error(str(e))
        raise

@checkout_router.tool(
    annotations={
        "title": "Set Shipping Address",
    }
)
async def set_shipping_address(
    ctx: Context,
    checkout_id: Annotated[str, "ID of the checkout."],
    shipping_address: Annotated[AddressInput, "Shipping address details."],
) -> dict[str, Any]:
    """Update the shipping address for a checkout.
    
    Setting the shipping address is required before selecting a shipping method.
    """
    client = get_saleor_client()
    try:
        data = await client.checkout_shipping_address_update(
            id=checkout_id, 
            shippingAddress=shipping_address.model_dump(exclude_unset=True)
        )
        if data.checkoutShippingAddressUpdate.errors:
            return {"errors": data.checkoutShippingAddressUpdate.errors}
        return {"data": data.checkoutShippingAddressUpdate.checkout}
    except Exception as e:
        await ctx.error(str(e))
        raise

@checkout_router.tool(
    annotations={
        "title": "Set Billing Address",
    }
)
async def set_billing_address(
    ctx: Context,
    checkout_id: Annotated[str, "ID of the checkout."],
    billing_address: Annotated[AddressInput, "Billing address details."],
) -> dict[str, Any]:
    """Update the billing address for a checkout."""
    client = get_saleor_client()
    try:
        data = await client.checkout_billing_address_update(
            id=checkout_id, 
            billingAddress=billing_address.model_dump(exclude_unset=True)
        )
        if data.checkoutBillingAddressUpdate.errors:
            return {"errors": data.checkoutBillingAddressUpdate.errors}
        return {"data": data.checkoutBillingAddressUpdate.checkout}
    except Exception as e:
        await ctx.error(str(e))
        raise

@checkout_router.tool(
    annotations={
        "title": "Set Shipping Method",
    }
)
async def set_shipping_method(
    ctx: Context,
    checkout_id: Annotated[str, "ID of the checkout."],
    shipping_method_id: Annotated[str, "ID of the shipping method to select."],
) -> dict[str, Any]:
    """Select a shipping method for the checkout.
    
    Available shipping methods can be found using the 'get_checkout' tool 
    after the shipping address has been set.
    """
    client = get_saleor_client()
    try:
        data = await client.checkout_shipping_method_update(
            id=checkout_id, 
            shippingMethodId=shipping_method_id
        )
        if data.checkoutShippingMethodUpdate.errors:
            return {"errors": data.checkoutShippingMethodUpdate.errors}
        return {"data": data.checkoutShippingMethodUpdate.checkout}
    except Exception as e:
        await ctx.error(str(e))
        raise

@checkout_router.tool(
    annotations={
        "title": "Create Payment",
    }
)
async def create_payment(
    ctx: Context,
    checkout_id: Annotated[str, "ID of the checkout."],
    payment_input: Annotated[PaymentInput, "Payment details including gateway and token."],
) -> dict[str, Any]:
    """Create a payment for the checkout.
    
    A payment must be created and successful before the checkout can be completed.
    For testing, you can often use a 'dummy' gateway if configured in Saleor.
    """
    client = get_saleor_client()
    try:
        data = await client.checkout_payment_create(
            id=checkout_id, 
            input=payment_input.model_dump(exclude_unset=True)
        )
        if data.checkoutPaymentCreate.errors:
            return {"errors": data.checkoutPaymentCreate.errors}
        return {"data": data.checkoutPaymentCreate.payment}
    except Exception as e:
        await ctx.error(str(e))
        raise

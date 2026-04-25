import hashlib
from typing import Annotated, Any

from fastmcp import Context, FastMCP

from ..config import get_config_from_headers
from ..ctx_utils import get_saleor_client
from ..saleor_client.input_types import (
    AddressInput,
    CheckoutCreateInput,
    CheckoutLineInput,
    CheckoutLineUpdateInput,
)

checkout_router = FastMCP("Checkout MCP")


# In-memory registry of the active checkout per auth token. Lost on server
# restart — acceptable for a single-tenant store. Source of truth across
# multiple UI iframes (which can't share localStorage since they run in
# isolated blob origins).
_active_checkouts: dict[str, str] = {}


def _active_key() -> str:
    try:
        cfg = get_config_from_headers()
    except Exception:
        return "_no_token"
    return hashlib.sha256(cfg.auth_token.encode()).hexdigest()[:24]


def _set_active_checkout(checkout_id: str | None) -> None:
    key = _active_key()
    if checkout_id:
        _active_checkouts[key] = checkout_id
    else:
        _active_checkouts.pop(key, None)


def _get_active_checkout() -> str | None:
    return _active_checkouts.get(_active_key())


@checkout_router.tool(
    tags={"scope:customer.write"},
    annotations={"title": "Add to Cart"}
)
async def add_to_cart(
    ctx: Context,
    lines: Annotated[list[CheckoutLineInput], "Lines to add (each needs variantId + quantity)."],
    checkout_id: Annotated[
        str | None,
        "Existing cart id. If omitted, a new cart is created in the given channel.",
    ] = None,
    channel: Annotated[
        str | None,
        "Channel slug — only used when creating a new cart. Defaults to 'default-channel'.",
    ] = None,
    email: Annotated[
        str | None,
        "Customer email — only used when creating a new cart.",
    ] = None,
) -> dict[str, Any]:
    """Add items to the cart, creating it if it doesn't exist.

    If `checkout_id` is omitted, creates a new cart (checkout) in the given
    channel and returns its id. Otherwise appends to the existing cart.
    Either way returns the updated checkout object.
    """
    client = get_saleor_client()
    formatted_lines = [line.model_dump(exclude_unset=True) for line in lines]

    if checkout_id:
        try:
            data = await client.checkout_lines_add(
                id=checkout_id, lines=formatted_lines
            )
            if data.checkoutLinesAdd.errors:
                return {"errors": data.checkoutLinesAdd.errors}
            return {"data": data.checkoutLinesAdd.checkout}
        except Exception as e:
            await ctx.error(str(e))
            raise

    input_data = CheckoutCreateInput(
        channel=channel or "default-channel",
        lines=formatted_lines,
        email=email,
    )
    try:
        data = await client.checkout_create(input=input_data)
        if data.checkoutCreate.errors:
            return {"errors": data.checkoutCreate.errors}
        checkout = data.checkoutCreate.checkout
        if checkout and checkout.id:
            _set_active_checkout(checkout.id)
        return {"data": checkout}
    except Exception as e:
        await ctx.error(str(e))
        raise


@checkout_router.tool(
    tags={"scope:customer.write"},
    annotations={"title": "Update Cart Item"}
)
async def update_cart_item(
    ctx: Context,
    checkout_id: Annotated[str, "ID of the checkout (cart)."],
    lines: Annotated[list[CheckoutLineUpdateInput], "Lines to update (each needs lineId + quantity)."],
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
    tags={"scope:customer.write"},
    annotations={"title": "Remove from Cart"}
)
async def remove_from_cart(
    ctx: Context,
    checkout_id: Annotated[str, "ID of the checkout (cart)."],
    line_ids: Annotated[list[str], "IDs of checkout lines to remove."],
) -> dict[str, Any]:
    """Remove line items from the cart."""
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
    tags={"scope:customer.read"},
    annotations={
        "title": "Current active checkout",
        "readOnlyHint": True,
    }
)
async def current_checkout(ctx: Context) -> dict[str, Any]:
    """Return the user's currently active checkout_id (if any) plus a compact summary.

    Use this when you don't have a fresh checkout_id in scope but need to
    answer questions about the cart — e.g. "what's in my cart?". The server
    tracks the active checkout per auth-token session, so you can recover it
    even across multiple UI-iframe instances. Returns {"checkout_id": null}
    if the user has not created a cart yet (or the last one was completed).
    """
    cid = _get_active_checkout()
    if not cid:
        return {"checkout_id": None}
    client = get_saleor_client()
    try:
        data = await client.checkout_details(id=cid)
        if not data.checkout:
            # Stale id (already ordered / expired) — forget it.
            _set_active_checkout(None)
            return {"checkout_id": None}
        lines = data.checkout.lines or []
        total = data.checkout.totalPrice.gross if data.checkout.totalPrice else None
        return {
            "checkout_id": cid,
            "line_count": len(lines),
            "total": (
                {"amount": float(total.amount), "currency": total.currency}
                if total else None
            ),
            "email": data.checkout.email or "",
        }
    except Exception as e:
        await ctx.error(str(e))
        return {"checkout_id": cid}


@checkout_router.tool(
    tags={"scope:customer.read"},
    annotations={"title": "Get Checkout Details"}
)
async def get_checkout(
    ctx: Context,
    checkout_id: Annotated[str, "ID of the checkout to fetch."],
) -> dict[str, Any]:
    """Fetch checkout details (lines, addresses, shipping methods, payment gateways)."""
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
    tags={"scope:customer.write"},
    annotations={"title": "Set Checkout Email"}
)
async def set_checkout_email(
    ctx: Context,
    checkout_id: Annotated[str, "ID of the checkout."],
    email: Annotated[str, "Customer email for the order."],
) -> dict[str, Any]:
    """Attach a customer email to the checkout. Required before place_order."""
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
    tags={"scope:customer.write"},
    annotations={"title": "Set Checkout Delivery"}
)
async def set_checkout_delivery(
    ctx: Context,
    checkout_id: Annotated[str, "ID of the checkout."],
    shipping_address: Annotated[AddressInput, "Shipping address."],
    billing_address: Annotated[
        AddressInput | None,
        "Billing address. Omit (with same_billing=True) to reuse shipping address.",
    ] = None,
    same_billing: Annotated[
        bool,
        "Use shipping address as billing. Ignored when billing_address is provided.",
    ] = True,
    shipping_method_id: Annotated[
        str | None,
        "Shipping method id. If omitted, method is not set (useful for a 2-step UI flow).",
    ] = None,
) -> dict[str, Any]:
    """Set shipping address, billing address, and (optionally) shipping method in one call.

    This consolidates what was previously 3 separate tools. On any failure, the
    returned `step` field identifies which sub-operation rejected the input
    ('shipping_address' / 'billing_address' / 'shipping_method'). On success,
    returns the updated checkout.
    """
    client = get_saleor_client()
    shipping_dump = shipping_address.model_dump(exclude_unset=True)

    try:
        r1 = await client.checkout_shipping_address_update(
            id=checkout_id, shippingAddress=shipping_dump
        )
        if r1.checkoutShippingAddressUpdate.errors:
            return {
                "step": "shipping_address",
                "errors": r1.checkoutShippingAddressUpdate.errors,
            }

        if billing_address is not None:
            billing_dump = billing_address.model_dump(exclude_unset=True)
        elif same_billing:
            billing_dump = shipping_dump
        else:
            return {
                "step": "billing_address",
                "errors": [{
                    "field": "billing_address",
                    "code": "REQUIRED",
                    "message": "billing_address is required when same_billing=False",
                }],
            }

        r2 = await client.checkout_billing_address_update(
            id=checkout_id, billingAddress=billing_dump
        )
        if r2.checkoutBillingAddressUpdate.errors:
            return {
                "step": "billing_address",
                "errors": r2.checkoutBillingAddressUpdate.errors,
            }

        if shipping_method_id:
            r3 = await client.checkout_shipping_method_update(
                id=checkout_id, shippingMethodId=shipping_method_id
            )
            if r3.checkoutShippingMethodUpdate.errors:
                return {
                    "step": "shipping_method",
                    "errors": r3.checkoutShippingMethodUpdate.errors,
                }
            return {"data": r3.checkoutShippingMethodUpdate.checkout}

        return {"data": r2.checkoutBillingAddressUpdate.checkout}
    except Exception as e:
        await ctx.error(str(e))
        raise


@checkout_router.tool(
    tags={"scope:customer.write"},
    annotations={"title": "Place Order"}
)
async def place_order(
    ctx: Context,
    checkout_id: Annotated[str, "ID of the checkout to convert into an order."],
    gateway_id: Annotated[
        str,
        "Payment gateway id (from get_checkout.availablePaymentGateways[].id).",
    ],
    token: Annotated[
        str | None,
        "Gateway-specific payment token. For 'mirumee.payments.dummy', use 'charged'.",
    ] = None,
) -> dict[str, Any]:
    """Create a payment and complete the checkout in one call → returns the Order.

    This is the final step. On failure the returned `step` field is either
    'payment' (create_payment rejected) or 'complete' (complete_checkout rejected).
    Only call after set_checkout_delivery has succeeded and a shipping method
    has been set.
    """
    client = get_saleor_client()
    payment_input: dict[str, Any] = {"gateway": gateway_id}
    if token:
        payment_input["token"] = token

    try:
        r1 = await client.checkout_payment_create(id=checkout_id, input=payment_input)
        if r1.checkoutPaymentCreate.errors:
            return {"step": "payment", "errors": r1.checkoutPaymentCreate.errors}

        r2 = await client.checkout_complete(id=checkout_id)
        if r2.checkoutComplete.errors:
            return {"step": "complete", "errors": r2.checkoutComplete.errors}

        # Checkout was converted to an order — clear from active registry.
        if _get_active_checkout() == checkout_id:
            _set_active_checkout(None)
        return {"data": r2.checkoutComplete.order}
    except Exception as e:
        await ctx.error(str(e))
        raise

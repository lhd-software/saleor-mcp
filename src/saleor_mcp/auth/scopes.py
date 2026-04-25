"""Scope registry for MCP tools.

Three scopes follow OAuth space-separated convention. A token's `scope`
claim is a string like `"customer.read customer.write"`.

* `customer.read`  — browse catalog, view own cart/order, no mutations
* `customer.write` — modify cart, place order on behalf of the user
* `admin`          — list all channels/customers/orders/promotions/stocks/warehouses

`TOOL_SCOPES` is the single source of truth used by the runtime
middleware. Each tool decorator in `tools/*.py` also carries a matching
`scope:<name>` tag for human-readable discovery, but the middleware
reads this dict, not tags.
"""

SCOPE_CUSTOMER_READ = "customer.read"
SCOPE_CUSTOMER_WRITE = "customer.write"
SCOPE_ADMIN = "admin"

ALL_SCOPES: tuple[str, ...] = (SCOPE_CUSTOMER_READ, SCOPE_CUSTOMER_WRITE, SCOPE_ADMIN)

# Tool name → required scope. Tool names are the function names registered
# with `@router.tool()` / `@mcp.tool()`. Keep this list in sync when adding
# new tools — a tool missing from this map will be denied by default.
TOOL_SCOPES: dict[str, str] = {
    # utils
    "current_domain": SCOPE_CUSTOMER_READ,
    "catalog_overview": SCOPE_CUSTOMER_READ,
    "me": SCOPE_CUSTOMER_READ,
    # products
    "products": SCOPE_CUSTOMER_READ,
    "get_product_details": SCOPE_CUSTOMER_READ,
    "open_product_explorer": SCOPE_CUSTOMER_READ,
    # checkout (read-side)
    "current_checkout": SCOPE_CUSTOMER_READ,
    "get_checkout": SCOPE_CUSTOMER_READ,
    "open_cart": SCOPE_CUSTOMER_READ,
    # checkout (write-side)
    "add_to_cart": SCOPE_CUSTOMER_WRITE,
    "update_cart_item": SCOPE_CUSTOMER_WRITE,
    "remove_from_cart": SCOPE_CUSTOMER_WRITE,
    "set_checkout_email": SCOPE_CUSTOMER_WRITE,
    "set_checkout_delivery": SCOPE_CUSTOMER_WRITE,
    "place_order": SCOPE_CUSTOMER_WRITE,
    "open_checkout": SCOPE_CUSTOMER_WRITE,
    # orders
    "track_order": SCOPE_CUSTOMER_READ,
    # promotions
    "evaluate_cart_promotions": SCOPE_CUSTOMER_READ,
    # admin-only
    "channels": SCOPE_ADMIN,
    "customers": SCOPE_ADMIN,
    "orders": SCOPE_ADMIN,
    "list_promotions": SCOPE_ADMIN,
    "stocks": SCOPE_ADMIN,
    "warehouse_details": SCOPE_ADMIN,
}


def tool_required_scope(tool_name: str) -> str | None:
    """Return the scope required for a given tool name, or None if unknown.

    Unknown tool names should be treated as denied.
    """
    return TOOL_SCOPES.get(tool_name)


def parse_scope_claim(claim: str | list[str] | None) -> set[str]:
    """Normalize an OAuth `scope` claim into a set of scope strings.

    Accepts either a single space-separated string (RFC 6749 §3.3) or a
    list (some IdPs use `scp` as JSON array).
    """
    if not claim:
        return set()
    if isinstance(claim, list):
        return {s for s in claim if s}
    return {s for s in claim.split() if s}

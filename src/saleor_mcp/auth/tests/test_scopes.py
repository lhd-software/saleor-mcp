from saleor_mcp.auth.scopes import (
    SCOPE_ADMIN,
    SCOPE_CUSTOMER_READ,
    SCOPE_CUSTOMER_WRITE,
    TOOL_SCOPES,
    parse_scope_claim,
    tool_required_scope,
)


def test_parse_scope_claim_string():
    assert parse_scope_claim("customer.read customer.write") == {
        "customer.read",
        "customer.write",
    }


def test_parse_scope_claim_list():
    assert parse_scope_claim(["customer.read", "admin"]) == {"customer.read", "admin"}


def test_parse_scope_claim_empty():
    assert parse_scope_claim(None) == set()
    assert parse_scope_claim("") == set()
    assert parse_scope_claim([]) == set()


def test_parse_scope_claim_extra_whitespace():
    assert parse_scope_claim("  customer.read   customer.write  ") == {
        "customer.read",
        "customer.write",
    }


def test_tool_required_scope_known():
    assert tool_required_scope("products") == SCOPE_CUSTOMER_READ
    assert tool_required_scope("add_to_cart") == SCOPE_CUSTOMER_WRITE
    assert tool_required_scope("channels") == SCOPE_ADMIN


def test_tool_required_scope_unknown_returns_none():
    assert tool_required_scope("nonexistent_tool_xyz") is None


def test_all_scope_values_are_one_of_three():
    valid = {SCOPE_CUSTOMER_READ, SCOPE_CUSTOMER_WRITE, SCOPE_ADMIN}
    for tool, scope in TOOL_SCOPES.items():
        assert scope in valid, f"{tool} → unknown scope {scope!r}"

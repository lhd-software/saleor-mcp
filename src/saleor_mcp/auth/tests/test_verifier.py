import base64
import json
import time

import pytest

from saleor_mcp.auth.scopes import (
    SCOPE_ADMIN,
    SCOPE_CUSTOMER_READ,
    SCOPE_CUSTOMER_WRITE,
)
from saleor_mcp.auth.verifier import SaleorTokenVerifier


def _make_jwt(payload: dict) -> str:
    """Build a JWT with a fake signature (verifier doesn't check it)."""
    header = base64.urlsafe_b64encode(b'{"alg":"RS256","typ":"JWT"}').rstrip(b"=").decode()
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    return f"{header}.{body}.fake-sig"


@pytest.mark.asyncio
async def test_decodes_customer_scope():
    token = _make_jwt({
        "sub": "user-1",
        "email": "u@example.com",
        "scope": "customer.read customer.write",
        "exp": int(time.time()) + 3600,
    })
    v = SaleorTokenVerifier()
    access = await v.verify_token(token)
    assert access is not None
    assert set(access.scopes) == {SCOPE_CUSTOMER_READ, SCOPE_CUSTOMER_WRITE}
    assert access.token == token


@pytest.mark.asyncio
async def test_rejects_expired_jwt():
    token = _make_jwt({"sub": "u", "scope": "customer.read", "exp": 1})  # 1970
    v = SaleorTokenVerifier()
    assert await v.verify_token(token) is None


@pytest.mark.asyncio
async def test_staff_claim_promotes_to_admin():
    token = _make_jwt({
        "sub": "staff-1",
        "is_staff": True,
        "scope": "",
        "exp": int(time.time()) + 3600,
    })
    v = SaleorTokenVerifier()
    access = await v.verify_token(token)
    assert access is not None
    assert SCOPE_ADMIN in access.scopes
    assert SCOPE_CUSTOMER_READ in access.scopes
    assert SCOPE_CUSTOMER_WRITE in access.scopes


@pytest.mark.asyncio
async def test_non_jwt_rejected_by_default():
    v = SaleorTokenVerifier()  # SALEOR_REQUIRE_JWT_SHAPE defaults to true
    assert await v.verify_token("not-a-jwt-token") is None


@pytest.mark.asyncio
async def test_non_jwt_accepted_when_opted_in():
    v = SaleorTokenVerifier(accept_non_jwt=True)
    access = await v.verify_token("opaque-app-token")
    assert access is not None
    # Non-JWT tokens get full staff scope set so app/staff tokens keep working.
    assert SCOPE_ADMIN in access.scopes


@pytest.mark.asyncio
async def test_empty_token_returns_none():
    v = SaleorTokenVerifier()
    assert await v.verify_token("") is None


@pytest.mark.asyncio
async def test_scope_array_claim_supported():
    token = _make_jwt({
        "sub": "u",
        "scp": ["customer.read", "customer.write"],
        "exp": int(time.time()) + 3600,
    })
    v = SaleorTokenVerifier()
    access = await v.verify_token(token)
    assert access is not None
    assert set(access.scopes) == {SCOPE_CUSTOMER_READ, SCOPE_CUSTOMER_WRITE}


@pytest.mark.asyncio
async def test_audience_becomes_client_id():
    token = _make_jwt({
        "sub": "u",
        "aud": "openclaw",
        "scope": "customer.read",
        "exp": int(time.time()) + 3600,
    })
    v = SaleorTokenVerifier()
    access = await v.verify_token(token)
    assert access is not None
    assert access.client_id == "openclaw"

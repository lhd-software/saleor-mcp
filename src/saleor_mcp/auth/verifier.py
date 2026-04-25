"""Token verifier that decodes Saleor JWT claims without cryptographic check.

Saleor backend remains the source of truth — it will reject any forged
or expired token when the MCP forwards the GraphQL call. The verifier
only needs to extract the OAuth `scope` claim so the scope-enforcement
middleware can gate tool calls.

If `SALEOR_REQUIRE_JWT_SHAPE=false` is set, tokens that aren't JWTs
(plain admin app tokens, for instance) are accepted with a default
scope set — useful for staff/app tokens used in development.
"""

import base64
import json
import logging
import os
import time
from typing import Any

from fastmcp.server.auth.auth import AccessToken, TokenVerifier

from .scopes import (
    SCOPE_ADMIN,
    SCOPE_CUSTOMER_READ,
    SCOPE_CUSTOMER_WRITE,
    parse_scope_claim,
)

logger = logging.getLogger(__name__)


def _decode_jwt_payload(token: str) -> dict[str, Any] | None:
    """Decode a JWT payload (middle segment), returning None if not a JWT.

    Does NOT verify the signature — Saleor handles that on the actual
    GraphQL call. URL-safe base64, with padding restored.
    """
    parts = token.split(".")
    if len(parts) != 3:
        return None
    payload = parts[1]
    padding = "=" * (-len(payload) % 4)
    try:
        raw = base64.urlsafe_b64decode(payload + padding)
        return json.loads(raw)
    except (ValueError, json.JSONDecodeError):
        return None


def _staff_scopes() -> list[str]:
    """All three scopes — used for non-JWT app/staff tokens."""
    return [SCOPE_CUSTOMER_READ, SCOPE_CUSTOMER_WRITE, SCOPE_ADMIN]


class SaleorTokenVerifier(TokenVerifier):
    """Verify a bearer token issued by the Saleor authorization server.

    Returns an `AccessToken` populated with the JWT's `scope` claim. Token
    cryptographic validation is delegated to Saleor (the resource backend).
    """

    def __init__(
        self,
        required_scopes: list[str] | None = None,
        accept_non_jwt: bool | None = None,
    ):
        super().__init__(required_scopes=required_scopes)
        if accept_non_jwt is None:
            accept_non_jwt = os.getenv("SALEOR_REQUIRE_JWT_SHAPE", "true").lower() != "true"
        self.accept_non_jwt = accept_non_jwt

    async def verify_token(self, token: str) -> AccessToken | None:
        if not token:
            return None

        claims = _decode_jwt_payload(token)
        if claims is None:
            if not self.accept_non_jwt:
                logger.debug("Rejected non-JWT token (SALEOR_REQUIRE_JWT_SHAPE=true)")
                return None
            return AccessToken(
                token=token,
                client_id="saleor-app",
                scopes=_staff_scopes(),
                expires_at=None,
                claims={},
            )

        # Optional: check exp claim. Saleor will also reject expired tokens
        # downstream, but rejecting here gives a faster + standard 401.
        exp = claims.get("exp")
        if isinstance(exp, int | float) and exp < time.time():
            logger.debug("Rejected expired JWT (exp=%s)", exp)
            return None

        scope_raw = claims.get("scope") or claims.get("scp")
        scopes = list(parse_scope_claim(scope_raw))

        # Saleor JWTs for staff users carry `is_staff: true`; promote them.
        if claims.get("is_staff") is True and SCOPE_ADMIN not in scopes:
            scopes.extend(_staff_scopes())

        client_id = (
            claims.get("aud")
            or claims.get("azp")
            or claims.get("client_id")
            or claims.get("iss")
            or "saleor-customer"
        )
        if isinstance(client_id, list):
            client_id = client_id[0] if client_id else "saleor-customer"

        return AccessToken(
            token=token,
            client_id=str(client_id),
            scopes=scopes,
            expires_at=int(exp) if isinstance(exp, int | float) else None,
            claims=claims,
        )

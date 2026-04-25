import logging
import os
import re
from dataclasses import dataclass

from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_http_headers

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL)
logging.getLogger("mcp.server.streamable_http").setLevel(logging.WARNING)


def validate_api_url(url, pattern):
    """Validate if the given URL matches the allowed domain pattern.

    Pattern should be a properly escaped regular expression.
    """
    # Add anchors if not present
    if not pattern.startswith("^"):
        pattern = "^" + pattern

    if not pattern.endswith("$"):
        pattern = pattern + "$"

    return bool(re.match(pattern, url))


@dataclass
class SaleorConfig:
    api_url: str
    auth_token: str


def _extract_bearer(header_value: str | None) -> str | None:
    if not header_value:
        return None
    parts = header_value.strip().split(None, 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return None


def get_config_from_headers() -> SaleorConfig:
    """Extract Saleor configuration from HTTP headers or environment variables.

    Token resolution order (first match wins):
      1. `Authorization: Bearer <token>` — OAuth-standard, used when the
         client went through the OAuth flow advertised in
         /.well-known/oauth-protected-resource.
      2. `X-Saleor-Auth-Token` — legacy header, kept for back-compat.
      3. `SALEOR_AUTH_TOKEN` env var — stdio / dev fallback.
    """
    allowed_domain_pattern = os.getenv("ALLOWED_DOMAIN_PATTERN", "")
    try:
        headers = get_http_headers()
    except Exception:
        headers = {}

    api_url = headers.get("x-saleor-api-url") or os.getenv("SALEOR_API_URL")
    if not api_url:
        raise ToolError(
            "Missing Saleor API URL (X-Saleor-API-URL header or SALEOR_API_URL env var)"
        )

    if allowed_domain_pattern and not validate_api_url(api_url, allowed_domain_pattern):
        raise ToolError(f"API URL '{api_url}' is not allowed")

    auth_token = (
        _extract_bearer(headers.get("authorization"))
        or headers.get("x-saleor-auth-token")
        or os.getenv("SALEOR_AUTH_TOKEN")
    )
    if not auth_token:
        raise ToolError(
            "Missing Saleor Auth Token (Authorization: Bearer <token>, "
            "X-Saleor-Auth-Token header, or SALEOR_AUTH_TOKEN env var)"
        )

    return SaleorConfig(
        api_url=api_url,
        auth_token=auth_token,
    )

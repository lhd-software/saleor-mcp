"""Middleware that gates each tool call by the access token's scopes."""

import logging
from typing import Any

from fastmcp.server.dependencies import get_access_token
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from mcp import types as mt
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData

from .scopes import tool_required_scope

logger = logging.getLogger(__name__)


# JSON-RPC custom error code for permission errors. -32001 is in the
# server-defined range per JSON-RPC spec.
SCOPE_DENIED_CODE = -32001


class ScopeEnforcementMiddleware(Middleware):
    """Reject tool calls whose required scope is not in the access token.

    Unknown tool names are denied (fail-closed). Tools without an entry
    in `TOOL_SCOPES` should be added there explicitly.
    """

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, Any],
    ) -> Any:
        tool_name = getattr(context.message, "name", "")
        required = tool_required_scope(tool_name)

        if required is None:
            raise McpError(
                ErrorData(
                    code=SCOPE_DENIED_CODE,
                    message=(
                        f"Tool '{tool_name}' has no scope mapping; refusing the call. "
                        "Register it in saleor_mcp.auth.scopes.TOOL_SCOPES."
                    ),
                )
            )

        token = get_access_token()
        if token is None:
            # No auth provider configured (legacy mode) — fall through.
            return await call_next(context)

        if required not in token.scopes:
            raise McpError(
                ErrorData(
                    code=SCOPE_DENIED_CODE,
                    message=(
                        f"Token is missing required scope '{required}' for tool "
                        f"'{tool_name}'. Token scopes: {sorted(token.scopes)}."
                    ),
                )
            )

        return await call_next(context)

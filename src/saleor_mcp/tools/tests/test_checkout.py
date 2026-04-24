from unittest.mock import patch
import pytest
from fastmcp import Client as MCPClient
from saleor_mcp.main import mcp
from saleor_mcp.saleor_client.client import Client as SaleorClient


@pytest.mark.asyncio
async def test_add_to_cart_creates_new(sample_checkout_response, mock_saleor_config):
    """Calling add_to_cart without checkout_id creates a new cart."""
    with (
        patch("saleor_mcp.ctx_utils.get_config_from_headers") as mock_get_config,
        patch.object(SaleorClient, "checkout_create") as mock_checkout_create,
    ):
        mock_get_config.return_value = mock_saleor_config
        mock_checkout_create.return_value = sample_checkout_response

        async with MCPClient(mcp) as mcp_client:
            result = await mcp_client.call_tool(
                "add_to_cart",
                {
                    "lines": [{"variantId": "UHJvZHVjdFZhcmlhbnQ6MQ==", "quantity": 1}],
                    "channel": "default-channel",
                    "email": "test@example.com",
                },
            )

        data = result.data["data"]
        assert data["id"] == "Q2hlY2tvdXQ6MQ=="
        assert data["token"] == "test-token-123"
        mock_checkout_create.assert_called_once()

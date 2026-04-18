from unittest.mock import patch
import pytest
from fastmcp import Client as MCPClient
from saleor_mcp.main import mcp
from saleor_mcp.saleor_client.client import Client as SaleorClient

@pytest.mark.asyncio
async def test_list_promotions(sample_promotions_response, mock_saleor_config):
    """Test listing promotions."""
    with (
        patch("saleor_mcp.ctx_utils.get_config_from_headers") as mock_get_config,
        patch.object(SaleorClient, "list_promotions") as mock_list_promotions,
    ):
        mock_get_config.return_value = mock_saleor_config
        mock_list_promotions.return_value = sample_promotions_response

        async with MCPClient(mcp) as mcp_client:
            result = await mcp_client.call_tool("list_promotions", {})

        data = result.data["data"]
        assert len(data["promotions"]) == 1
        assert data["promotions"][0]["node"]["name"] == "Summer Sale"
        mock_list_promotions.assert_called_once()

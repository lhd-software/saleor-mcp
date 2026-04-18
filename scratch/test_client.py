import asyncio
import os
from saleor_mcp.saleor_client.client import Client
from saleor_mcp.config import SaleorConfig

async def test():
    # Use dummy config or try to get it from env if you can
    api_url = "https://demo.saleor.io/graphql/"
    auth_token = "dummy" 
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    client = Client(url=api_url, headers=headers)
    
    try:
        print("Calling list_products...")
        data = await client.list_products(first=5)
        print(f"Success! Fetched {len(data.products.edges)} products")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.http_client.aclose()

if __name__ == "__main__":
    asyncio.run(test())

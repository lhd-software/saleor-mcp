import asyncio
import os
from saleor_mcp.saleor_client.client import Client
from saleor_mcp.config import SaleorConfig

async def test():
    # Use real config from test_env.py
    api_url = "https://api.bi193.com/graphql/"
    auth_token = "iim23V4z72d0Bg9BUS8PUGaDNQ671ha" 
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    client = Client(url=api_url, headers=headers)
    
    try:
        print("Calling list_products with default-channel...")
        data = await client.list_products(first=5, channel="default-channel")
        print(f"Success! Fetched {len(data.products.edges)} products")
        for edge in data.products.edges:
            product = edge.node
            print(f"- {product.name}: {product.slug}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.http_client.aclose()

if __name__ == "__main__":
    asyncio.run(test())

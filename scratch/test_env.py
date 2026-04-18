import asyncio
import os
from saleor_mcp.config import get_config_from_headers

async def test_env_config():
    os.environ["SALEOR_API_URL"] = "https://api.bi193.com/graphql/"
    os.environ["SALEOR_AUTH_TOKEN"] = "iim23V4z72d0Bg9BUS8PUGaDNQ671ha"
    
    try:
        # Mocking the request context is hard, but we can check if it falls back to env vars
        # when get_http_headers() returns empty dict (which it should outside of a request)
        config = get_config_from_headers()
        print(f"Success! API URL: {config.api_url}")
        print(f"Auth Token (masked): {config.auth_token[:5]}...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_env_config())

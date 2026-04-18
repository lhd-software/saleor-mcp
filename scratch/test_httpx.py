import asyncio
import httpx
import json

async def test():
    client = httpx.AsyncClient()
    try:
        # This should fail if we pass 'filter' to post
        await client.post("http://example.com", json={"query": "{ __typename }"}, filter={"foo": "bar"})
    except TypeError as e:
        print(f"Caught expected error: {e}")
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(test())

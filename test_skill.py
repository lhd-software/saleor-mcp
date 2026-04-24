#!/usr/bin/env python3
"""Test bi193-shopping skill — verify tools work"""

import asyncio
import httpx
from typing import Any

# MCP HTTP endpoint
MCP_URL = "http://localhost:6000"
HEADERS = {
    "X-Saleor-API-URL": "https://api.bi193.com/graphql/",
    "X-Saleor-Auth-Token": "pmKtQyFPIGuRNTroIE5NlOY1Bi470k",
}

async def call_mcp(method: str, params: dict) -> Any:
    """Call MCP tool"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(MCP_URL, json=payload, headers=HEADERS)
            result = response.json()
            return result
        except Exception as e:
            return {"error": str(e)}

async def main():
    print("🛒 Testing bi193-shopping skill...\n")
    
    # Test 1: Channels
    print("1️⃣  Testing channels tool...")
    result = await call_mcp("CallTool", {"name": "channels", "arguments": {}})
    if "result" in result:
        print(f"   ✅ Channels OK\n")
    else:
        print(f"   ❌ Error: {result}\n")
    
    # Test 2: Products search
    print("2️⃣  Testing product search (search='tee')...")
    result = await call_mcp("CallTool", {
        "name": "products",
        "arguments": {
            "search": "tee",
            "channel": "default-channel",
            "first": 5
        }
    })
    if "result" in result:
        print(f"   ✅ Product search OK\n")
    else:
        print(f"   ❌ Error: {result}\n")
    
    # Test 3: Open product explorer (would open UI)
    print("3️⃣  Testing open_product_explorer (UI)...")
    result = await call_mcp("CallTool", {
        "name": "open_product_explorer",
        "arguments": {
            "search": "dress",
            "channel": "default-channel"
        }
    })
    if "result" in result:
        print(f"   ✅ Product explorer OK\n")
    else:
        print(f"   ❌ Error: {result}\n")
    
    print("✅ All tests complete!")

if __name__ == "__main__":
    asyncio.run(main())

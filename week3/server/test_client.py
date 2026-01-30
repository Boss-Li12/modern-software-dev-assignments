"""
Test client for the Crypto Finance MCP Server
Demonstrates how to interact with the MCP HTTP server
"""

import httpx
import json
import asyncio
from typing import Dict, Any

# Server configuration
SERVER_URL = "http://localhost:8000"
API_KEY = "demo-key-12345"  # Should match MCP_API_KEY in .env

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


async def list_tools() -> Dict[str, Any]:
    """List available tools from the MCP server"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVER_URL}/mcp/list-tools",
            headers=headers
        )
        response.raise_for_status()
        return response.json()


async def call_tool(tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
    """Call a specific tool on the MCP server"""
    if arguments is None:
        arguments = {}
    
    payload = {
        "name": tool_name,
        "arguments": arguments
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVER_URL}/mcp/call-tool",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()


async def main():
    """Run example interactions with the MCP server"""
    
    print("=" * 60)
    print("Crypto Finance MCP Server - Test Client")
    print("=" * 60)
    print()
    
    # 1. List available tools
    print("1. Listing available tools...")
    print("-" * 60)
    tools_response = await list_tools()
    for tool in tools_response.get("tools", []):
        print(f"  • {tool['name']}: {tool['description']}")
    print()
    
    # 2. Get Bitcoin price
    print("2. Getting Bitcoin price...")
    print("-" * 60)
    btc_price = await call_tool("get_crypto_price", {"coin_id": "bitcoin"})
    print(json.dumps(btc_price, indent=2))
    print()
    
    # 3. Get Ethereum price in EUR
    print("3. Getting Ethereum price in EUR...")
    print("-" * 60)
    eth_price = await call_tool("get_crypto_price", {
        "coin_id": "ethereum",
        "vs_currency": "eur"
    })
    print(json.dumps(eth_price, indent=2))
    print()
    
    # 4. Get trending coins
    print("4. Getting trending coins...")
    print("-" * 60)
    trending = await call_tool("get_trending_coins")
    print(json.dumps(trending, indent=2))
    print()
    
    # 5. Get top 5 market data
    print("5. Getting top 5 cryptocurrencies by market cap...")
    print("-" * 60)
    market_data = await call_tool("get_market_data", {"limit": 5})
    print(json.dumps(market_data, indent=2))
    print()
    
    print("=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

"""
Example integration: Using the Crypto Finance MCP Server with an AI agent
This demonstrates how to integrate the MCP server with various AI frameworks
"""

import asyncio
import httpx
from typing import Dict, Any, List


class MCPClient:
    """Client for interacting with the Crypto Finance MCP Server"""
    
    def __init__(self, server_url: str, api_key: str):
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.tools = None
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """Fetch and cache available tools"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.server_url}/mcp/list-tools",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            self.tools = data.get("tools", [])
            return self.tools
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None, max_retries: int = 3) -> Any:
        """Call a specific MCP tool with retry logic for rate limits"""
        if arguments is None:
            arguments = {}
        
        payload = {
            "name": tool_name,
            "arguments": arguments
        }
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.server_url}/mcp/call-tool",
                        headers=self.headers,
                        json=payload,
                        timeout=30.0
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    # Extract content from MCP response
                    if result.get("isError"):
                        raise Exception(f"Tool error: {result.get('content', [{}])[0].get('text')}")
                    
                    return result.get("content", [{}])[0].get("text")
            
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    # Rate limit hit - wait and retry
                    wait_time = (2 ** attempt) * 2  # Exponential backoff: 2, 4, 8 seconds
                    if attempt < max_retries - 1:
                        print(f"⚠️  Rate limit hit. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                        await asyncio.sleep(wait_time)
                        continue
                raise
    
    def get_tool_schema_for_openai(self) -> List[Dict[str, Any]]:
        """Convert MCP tools to OpenAI function calling format"""
        if not self.tools:
            raise Exception("Tools not loaded. Call list_tools() first.")
        
        openai_tools = []
        for tool in self.tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["inputSchema"]
                }
            })
        
        return openai_tools
    
    def get_tool_schema_for_anthropic(self) -> List[Dict[str, Any]]:
        """Convert MCP tools to Anthropic Claude format"""
        if not self.tools:
            raise Exception("Tools not loaded. Call list_tools() first.")
        
        anthropic_tools = []
        for tool in self.tools:
            anthropic_tools.append({
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["inputSchema"]
            })
        
        return anthropic_tools


# ==============================================================================
# Example 1: Standalone usage (without AI model)
# ==============================================================================

async def example_standalone():
    """Example: Using MCP server directly"""
    print("=" * 70)
    print("Example 1: Standalone MCP Client")
    print("=" * 70)
    print()
    
    # Initialize client
    client = MCPClient(
        server_url="http://localhost:8000",
        api_key="demo-key-12345"
    )
    
    # List available tools
    print("📋 Available tools:")
    tools = await client.list_tools()
    for tool in tools:
        print(f"  • {tool['name']}")
    print()
    
    # Example 1: Get Bitcoin price
    print("💰 Bitcoin price:")
    btc_price = await client.call_tool("get_crypto_price", {"coin_id": "bitcoin"})
    print(f"  {btc_price}")
    print()
    
    # Example 2: Get trending coins
    print("🔥 Trending coins:")
    trending = await client.call_tool("get_trending_coins")
    print(f"  {trending}")
    print()


# ==============================================================================
# Example 2: Integration with OpenAI (pseudocode)
# ==============================================================================

async def example_openai_integration():
    """
    Example: Using MCP server with OpenAI function calling
    
    Note: This is pseudocode. You need to install openai package:
    pip install openai
    """
    print("=" * 70)
    print("Example 2: OpenAI Integration (Pseudocode)")
    print("=" * 70)
    print()
    
    # Initialize MCP client
    mcp_client = MCPClient(
        server_url="http://localhost:8000",
        api_key="demo-key-12345"
    )
    
    # Load tools
    await mcp_client.list_tools()
    
    # Convert to OpenAI format
    openai_tools = mcp_client.get_tool_schema_for_openai()
    
    print("🤖 OpenAI function calling schema:")
    print(f"  Tools available: {len(openai_tools)}")
    print()
    
    # Pseudocode for OpenAI integration:
    print("📝 Pseudocode for OpenAI:")
    print("""
    from openai import OpenAI
    
    client = OpenAI(api_key="your-api-key")
    
    # Chat with function calling
    messages = [{"role": "user", "content": "What's the current Bitcoin price?"}]
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=openai_tools
    )
    
    # If model wants to call a function
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Call MCP server
            result = await mcp_client.call_tool(function_name, function_args)
            
            # Send result back to model
            messages.append({
                "role": "function",
                "name": function_name,
                "content": result
            })
    
    # Get final response
    final_response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    """)
    print()


# ==============================================================================
# Example 3: Integration with Anthropic Claude (pseudocode)
# ==============================================================================

async def example_anthropic_integration():
    """
    Example: Using MCP server with Anthropic Claude
    
    Note: This is pseudocode. You need to install anthropic package:
    pip install anthropic
    """
    print("=" * 70)
    print("Example 3: Anthropic Claude Integration (Pseudocode)")
    print("=" * 70)
    print()
    
    # Initialize MCP client
    mcp_client = MCPClient(
        server_url="http://localhost:8000",
        api_key="demo-key-12345"
    )
    
    # Load tools
    await mcp_client.list_tools()
    
    # Convert to Anthropic format
    anthropic_tools = mcp_client.get_tool_schema_for_anthropic()
    
    print("🤖 Anthropic Claude tool schema:")
    print(f"  Tools available: {len(anthropic_tools)}")
    print()
    
    # Pseudocode for Anthropic integration:
    print("📝 Pseudocode for Anthropic:")
    print("""
    from anthropic import Anthropic
    
    client = Anthropic(api_key="your-api-key")
    
    # Chat with tool use
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        tools=anthropic_tools,
        messages=[{
            "role": "user",
            "content": "What are the top 3 trending cryptocurrencies right now?"
        }]
    )
    
    # If Claude wants to use a tool
    if message.stop_reason == "tool_use":
        for content_block in message.content:
            if content_block.type == "tool_use":
                tool_name = content_block.name
                tool_input = content_block.input
                
                # Call MCP server
                result = await mcp_client.call_tool(tool_name, tool_input)
                
                # Continue conversation with tool result
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1024,
                    tools=anthropic_tools,
                    messages=[
                        {"role": "user", "content": "What are the trending cryptos?"},
                        {"role": "assistant", "content": message.content},
                        {
                            "role": "user",
                            "content": [{
                                "type": "tool_result",
                                "tool_use_id": content_block.id,
                                "content": result
                            }]
                        }
                    ]
                )
    """)
    print()


# ==============================================================================
# Example 4: Building a simple crypto advisor agent
# ==============================================================================

class CryptoAdvisor:
    """Simple AI agent that provides crypto insights using MCP tools"""
    
    def __init__(self, mcp_client: MCPClient):
        self.mcp = mcp_client
    
    async def get_market_overview(self) -> str:
        """Get a comprehensive market overview"""
        # Get top 5 coins by market cap
        market_data = await self.mcp.call_tool("get_market_data", {"limit": 5})
        
        # Get trending coins
        trending = await self.mcp.call_tool("get_trending_coins")
        
        # Format summary
        summary = "📊 Crypto Market Overview\n"
        summary += "=" * 50 + "\n\n"
        summary += "🏆 Top 5 Cryptocurrencies:\n"
        summary += market_data + "\n\n"
        summary += "🔥 Trending Coins:\n"
        summary += trending + "\n"
        
        return summary
    
    async def compare_coins(self, coin1: str, coin2: str, currency: str = "usd") -> str:
        """Compare two cryptocurrencies"""
        # Get prices for both coins
        price1 = await self.mcp.call_tool("get_crypto_price", {
            "coin_id": coin1,
            "vs_currency": currency
        })
        
        price2 = await self.mcp.call_tool("get_crypto_price", {
            "coin_id": coin2,
            "vs_currency": currency
        })
        
        # Format comparison
        comparison = f"⚖️  Comparing {coin1.upper()} vs {coin2.upper()}\n"
        comparison += "=" * 50 + "\n\n"
        comparison += f"{coin1.upper()}:\n{price1}\n\n"
        comparison += f"{coin2.upper()}:\n{price2}\n"
        
        return comparison


async def example_crypto_advisor():
    """Example: Using a custom crypto advisor agent"""
    print("=" * 70)
    print("Example 4: Crypto Advisor Agent")
    print("=" * 70)
    print()
    
    # Initialize MCP client
    mcp_client = MCPClient(
        server_url="http://localhost:8000",
        api_key="demo-key-12345"
    )
    
    await mcp_client.list_tools()
    
    # Create advisor
    advisor = CryptoAdvisor(mcp_client)
    
    # Get market overview
    print("📊 Getting market overview...\n")
    overview = await advisor.get_market_overview()
    print(overview)
    print()
    
    # Compare Bitcoin and Ethereum
    print("⚖️  Comparing Bitcoin vs Ethereum...\n")
    comparison = await advisor.compare_coins("bitcoin", "ethereum")
    print(comparison)
    print()


# ==============================================================================
# Main execution
# ==============================================================================

async def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print(" Crypto Finance MCP Server - Integration Examples")
    print("=" * 70 + "\n")
    
    # Run examples
    await example_standalone()
    await example_openai_integration()
    await example_anthropic_integration()
    await example_crypto_advisor()
    
    print("=" * 70)
    print("✅ All examples completed!")
    print("=" * 70)
    print()
    print("💡 Tips:")
    print("  • Use the MCP client with any AI framework that supports function calling")
    print("  • Deploy the server to Vercel for remote access")
    print("  • Add more tools by extending main.py")
    print("  • Implement rate limiting on the client side for production use")
    print()


if __name__ == "__main__":
    asyncio.run(main())

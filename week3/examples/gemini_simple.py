"""
Simplified Gemini Pro Integration (without function calling)
Works with any Gemini SDK version
"""

import os
import asyncio
import httpx
from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
MCP_API_KEY = os.getenv("MCP_API_KEY", "demo-key-12345")


class MCPClient:
    """Client for interacting with the MCP server"""
    
    def __init__(self, server_url: str, api_key: str):
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call an MCP tool"""
        payload = {
            "name": tool_name,
            "arguments": arguments
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.server_url}/mcp/call-tool",
                headers=self.headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("isError"):
                return f"Error: {result.get('content', [{}])[0].get('text')}"
            
            return result.get("content", [{}])[0].get("text")


async def demo():
    """Run demo conversations"""
    
    print("=" * 70)
    print("🚀 Gemini Pro + MCP Server Integration Demo (Simplified)")
    print("=" * 70)
    print()
    
    # Configure Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('models/gemini-1.0-pro')
    
    # Initialize MCP client
    mcp_client = MCPClient(MCP_SERVER_URL, MCP_API_KEY)
    
    # Test scenarios
    tests = [
        {
            "name": "Bitcoin Price",
            "tool": "get_crypto_price",
            "args": {"coin_id": "bitcoin"},
            "prompt": "What's the current Bitcoin price?"
        },
        {
            "name": "Ethereum Price (EUR)",
            "tool": "get_crypto_price",
            "args": {"coin_id": "ethereum", "vs_currency": "eur"},
            "prompt": "What's Ethereum's price in euros?"
        },
        {
            "name": "Trending Coins",
            "tool": "get_trending_coins",
            "args": {},
            "prompt": "Which cryptocurrencies are trending?"
        },
        {
            "name": "Top 5 Market Cap",
            "tool": "get_market_data",
            "args": {"limit": 5},
            "prompt": "What are the top 5 cryptocurrencies by market cap?"
        }
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'=' * 70}")
        print(f"Test {i}/{len(tests)}: {test['name']}")
        print('=' * 70)
        
        # Call MCP tool
        print(f"\n🔧 Calling MCP tool: {test['tool']}")
        print(f"   Arguments: {test['args']}")
        
        try:
            result = await mcp_client.call_tool(test['tool'], test['args'])
            print(f"\n📊 MCP Result:")
            print(f"   {result}")
            
            # Ask Gemini to explain the data
            print(f"\n💬 User: {test['prompt']}")
            print(f"🤔 Asking Gemini to explain...")
            
            prompt = f"""Based on this cryptocurrency data, please provide a natural language summary:

 {result}

Please explain the key information in a conversational way."""
            
            response = model.generate_content(prompt)
            print(f"\n🤖 Gemini: {response.text}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        # Wait between requests
        if i < len(tests):
            print("\n⏳ Waiting 3 seconds...")
            await asyncio.sleep(3)
    
    print(f"\n{'=' * 70}")
    print("✅ All tests completed!")
    print('=' * 70)


async def interactive():
    """Interactive mode"""
    
    print("=" * 70)
    print("💬 Interactive Gemini + MCP Chat")
    print("=" * 70)
    print()
    print("Available commands:")
    print("  price <coin>        - Get cryptocurrency price")
    print("  trending            - Get trending cryptocurrencies")
    print("  top [N]             - Get top N cryptocurrencies")
    print("  quit/exit           - Exit")
    print()
    
    # Configure Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('models/gemini-1.0-pro')
    
    # Initialize MCP client
    mcp_client = MCPClient(MCP_SERVER_URL, MCP_API_KEY)
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            # Parse command
            parts = user_input.lower().split()
            command = parts[0] if parts else ""
            
            result = None
            
            if command == "price" and len(parts) >= 2:
                coin = parts[1]
                print(f"🔧 Getting price for {coin}...")
                result = await mcp_client.call_tool("get_crypto_price", {"coin_id": coin})
            
            elif command == "trending":
                print(f"🔧 Getting trending coins...")
                result = await mcp_client.call_tool("get_trending_coins", {})
            
            elif command == "top":
                limit = int(parts[1]) if len(parts) >= 2 else 10
                print(f"🔧 Getting top {limit} coins...")
                result = await mcp_client.call_tool("get_market_data", {"limit": limit})
            
            else:
                print("❓ Unknown command. Try: price bitcoin, trending, or top 5")
                continue
            
            if result:
                print(f"\n📊 Data: {result}")
                
                # Ask Gemini to explain
                print(f"🤔 Asking Gemini to explain...")
                prompt = f"Please explain this cryptocurrency data in simple terms:\n\n{result}"
                response = model.generate_content(prompt)
                print(f"\n🤖 Gemini: {response.text}")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


async def main():
    print("\n")
    print("🌟" * 35)
    print()
    print("  Gemini Pro × Crypto Finance MCP Server")
    print("  (Simplified Version - No Function Calling)")
    print()
    print("🌟" * 35)
    print()
    
    # Check configuration
    if GEMINI_API_KEY == "your-gemini-api-key":
        print("⚠️  WARNING: Please set GEMINI_API_KEY environment variable")
        print("   Get your API key from: https://makersuite.google.com/app/apikey")
        print()
        return
    
    # Ask user for mode
    print("Choose mode:")
    print("  1. Run demo (automated tests)")
    print("  2. Interactive chat mode")
    print()
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            await demo()
        elif choice == "2":
            await interactive()
        else:
            print("Invalid choice. Running demo...")
            await demo()
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())

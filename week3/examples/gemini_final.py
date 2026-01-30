"""
Gemini Pro Integration using NEW Google GenAI SDK
Works with google-genai package
"""

import os
import asyncio
from typing import Dict, Any
from google import genai
from dotenv import load_dotenv
import httpx

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
    print("🚀 Gemini + MCP Server Integration (New SDK)")
    print("=" * 70)
    print()
    
    # Initialize Gemini client
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Initialize MCP client
    mcp_client = MCPClient(MCP_SERVER_URL, MCP_API_KEY)
    
    # Test scenarios
    tests = [
        {
            "name": "Bitcoin Price",
            "tool": "get_crypto_price",
            "args": {"coin_id": "bitcoin"},
            "question": "What's the current Bitcoin price?"
        },
        {
            "name": "Ethereum Price (EUR)",
            "tool": "get_crypto_price",
            "args": {"coin_id": "ethereum", "vs_currency": "eur"},
            "question": "What's Ethereum's price in euros?"
        },
        {
            "name": "Trending Coins",
            "tool": "get_trending_coins",
            "args": {},
            "question": "Which cryptocurrencies are trending?"
        },
        {
            "name": "Top 5 Market Cap",
            "tool": "get_market_data",
            "args": {"limit": 5},
            "question": "What are the top 5 cryptocurrencies?"
        }
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'=' * 70}")
        print(f"Test {i}/{len(tests)}: {test['name']}")
        print('=' * 70)
        
        print(f"\n💬 User: {test['question']}")
        
        try:
            # Step 1: Call MCP tool
            print(f"🔧 Calling MCP tool: {test['tool']}...")
            result = await mcp_client.call_tool(test['tool'], test['args'])
            print(f"✅ Got data from MCP server")
            
            # Step 2: Ask Gemini to explain
            print(f"🤔 Asking Gemini to explain...")
            
            prompt = f"""User asked: "{test['question']}"

I fetched this cryptocurrency data:
{result}

Please provide a natural, conversational answer to the user's question based on this data."""
            
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            
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
    print("💡 Ask questions about cryptocurrencies!")
    print("   Examples:")
    print("   - What's the Bitcoin price?")
    print("   - Show me trending coins")
    print("   - Top 10 cryptocurrencies")
    print("   Type 'quit' to exit")
    print()
    
    # Initialize clients
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    mcp_client = MCPClient(MCP_SERVER_URL, MCP_API_KEY)
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            # Determine which tool to use based on keywords
            tool_name = None
            args = {}
            
            lower_input = user_input.lower()
            
            if "price" in lower_input or "cost" in lower_input:
                # Extract coin name
                for coin in ["bitcoin", "ethereum", "bnb", "cardano", "solana", "ripple", "xrp"]:
                    if coin in lower_input:
                        tool_name = "get_crypto_price"
                        args = {"coin_id": coin}
                        
                        # Check for currency
                        if "euro" in lower_input or "eur" in lower_input:
                            args["vs_currency"] = "eur"
                        break
            
            elif "trending" in lower_input or "hot" in lower_input or "popular" in lower_input:
                tool_name = "get_trending_coins"
                args = {}
            
            elif "top" in lower_input or "best" in lower_input or "market cap" in lower_input:
                tool_name = "get_market_data"
                # Try to extract number
                import re
                numbers = re.findall(r'\d+', user_input)
                args = {"limit": int(numbers[0]) if numbers else 10}
            
            if not tool_name:
                print("❓ I couldn't understand. Try asking about:")
                print("   - Bitcoin price")
                print("   - Trending coins")
                print("   - Top 10 cryptocurrencies")
                continue
            
            # Call MCP tool
            print(f"🔧 Getting data...")
            result = await mcp_client.call_tool(tool_name, args)
            
            # Ask Gemini to respond
            print(f"🤔 Thinking...")
            
            prompt = f"""User asked: "{user_input}"

I fetched this cryptocurrency data:
{result}

Please provide a helpful, conversational answer based on this data. Keep it concise and friendly."""
            
            response = gemini_client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            
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
    print("  Gemini 2.0 × Crypto Finance MCP Server")
    print()
    print("🌟" * 35)
    print()
    
    # Check configuration
    if GEMINI_API_KEY == "your-gemini-api-key":
        print("⚠️  WARNING: Please set GEMINI_API_KEY environment variable")
        print("   Get your API key from: https://makersuite.google.com/app/apikey")
        print()
        return
    
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

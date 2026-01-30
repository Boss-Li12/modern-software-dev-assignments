"""
Gemini Pro Integration using REST API
Direct HTTP calls to Gemini API
"""

import os
import asyncio
from typing import Dict, Any
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
MCP_API_KEY = os.getenv("MCP_API_KEY", "demo-key-12345")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


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


class GeminiClient:
    """Client for Gemini API using REST"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = GEMINI_API_URL
    
    async def generate(self, prompt: str) -> str:
        """Generate content using Gemini"""
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self.api_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract text from response
            return result["candidates"][0]["content"]["parts"][0]["text"]


async def demo():
    """Run demo conversations"""
    
    print("=" * 70)
    print("🚀 Gemini 2.0 + MCP Server Integration")
    print("=" * 70)
    print()
    print("💡 Using:")
    print(f"   • MCP Server: {MCP_SERVER_URL}")
    print(f"   • Model: Gemini 2.0 Flash")
    print()
    
    # Initialize clients
    gemini = GeminiClient(GEMINI_API_KEY)
    mcp = MCPClient(MCP_SERVER_URL, MCP_API_KEY)
    
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
            print(f"🔧 Calling MCP server...")
            mcp_result = await mcp.call_tool(test['tool'], test['args'])
            print(f"✅ Got data from MCP")
            
            # Step 2: Ask Gemini to explain
            print(f"🤔 Asking Gemini to explain...")
            
            prompt = f"""User asked: "{test['question']}"

I fetched this cryptocurrency data from the API:
{mcp_result}

Please provide a natural, friendly answer to the user's question based on this data. 
Keep it conversational and highlight the key information."""
            
            gemini_response = await gemini.generate(prompt)
            
            print(f"\n🤖 Gemini: {gemini_response}")
            
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
    gemini = GeminiClient(GEMINI_API_KEY)
    mcp = MCPClient(MCP_SERVER_URL, MCP_API_KEY)
    
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
            
            if "price" in lower_input or "cost" in lower_input or "worth" in lower_input:
                # Extract coin name
                for coin in ["bitcoin", "ethereum", "bnb", "cardano", "solana", "ripple", "xrp", "dogecoin"]:
                    if coin in lower_input:
                        tool_name = "get_crypto_price"
                        args = {"coin_id": coin}
                        
                        # Check for currency
                        if "euro" in lower_input or "eur" in lower_input:
                            args["vs_currency"] = "eur"
                        elif "yuan" in lower_input or "cny" in lower_input:
                            args["vs_currency"] = "cny"
                        break
            
            elif "trending" in lower_input or "hot" in lower_input or "popular" in lower_input:
                tool_name = "get_trending_coins"
                args = {}
            
            elif "top" in lower_input or "best" in lower_input or "market cap" in lower_input or "rank" in lower_input:
                tool_name = "get_market_data"
                # Try to extract number
                import re
                numbers = re.findall(r'\d+', user_input)
                args = {"limit": int(numbers[0]) if numbers else 10}
            
            if not tool_name:
                print("❓ I'm not sure what you're asking. Try:")
                print("   - 'Bitcoin price'")
                print("   - 'Trending coins'")
                print("   - 'Top 10 cryptocurrencies'")
                continue
            
            # Call MCP tool
            print(f"🔧 Getting data...")
            mcp_result = await mcp.call_tool(tool_name, args)
            
            # Ask Gemini to respond
            print(f"🤔 Thinking...")
            
            prompt = f"""User asked: "{user_input}"

I fetched this cryptocurrency data:
{mcp_result}

Please provide a helpful, conversational answer. Be concise but friendly."""
            
            gemini_response = await gemini.generate(prompt)
            
            print(f"\n🤖 Gemini: {gemini_response}")
        
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

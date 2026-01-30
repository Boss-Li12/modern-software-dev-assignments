"""
Gemini Pro Integration Example for Crypto Finance MCP Server
Demonstrates how to use Gemini Pro 1.5 with the MCP server
"""

import os
import asyncio
import httpx
from typing import Dict, Any, List, Optional
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


class GeminiMCPAgent:
    """Gemini Pro agent with MCP tool support"""
    
    def __init__(self, mcp_client: MCPClient):
        self.mcp = mcp_client
        
        # Configure Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Initialize model with tools (using function_declarations for SDK 0.3.2 compatibility)
        import google.generativeai.types as types
        
        self.model = genai.GenerativeModel(
            model_name='gemini-pro',  # Use gemini-pro for SDK 0.3.2
            tools=[
                types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(
                            name="get_crypto_price",
                            description="Get current price and market data for a cryptocurrency. Returns price, market cap, 24h volume, and 24h change.",
                            parameters=types.Schema(
                                type=types.Type.OBJECT,
                                properties={
                                    "coin_id": types.Schema(
                                        type=types.Type.STRING,
                                        description="CoinGecko coin ID (e.g., 'bitcoin', 'ethereum', 'cardano', 'solana')"
                                    ),
                                    "vs_currency": types.Schema(
                                        type=types.Type.STRING,
                                        description="Target currency code (usd, eur, gbp, jpy, cny)"
                                    )
                                },
                                required=["coin_id"]
                            )
                        ),
                        types.FunctionDeclaration(
                            name="get_trending_coins",
                            description="Get currently trending cryptocurrencies on CoinGecko. Returns top 7 trending coins with basic info.",
                            parameters=types.Schema(
                                type=types.Type.OBJECT,
                                properties={}
                            )
                        ),
                        types.FunctionDeclaration(
                            name="get_market_data",
                            description="Get market data for top cryptocurrencies ranked by market cap. Returns detailed market info including prices, volumes, and price changes.",
                            parameters=types.Schema(
                                type=types.Type.OBJECT,
                                properties={
                                    "vs_currency": types.Schema(
                                        type=types.Type.STRING,
                                        description="Target currency code"
                                    ),
                                    "limit": types.Schema(
                                        type=types.Type.INTEGER,
                                        description="Number of coins to return (1-100)"
                                    )
                                }
                            )
                        )
                    ]
                )
            ]
        )
        
        # Start chat session
        self.chat = self.model.start_chat(enable_automatic_function_calling=False)
    
    async def chat_with_tools(self, user_message: str) -> str:
        """
        Send a message to Gemini and handle tool calls
        
        Args:
            user_message: User's question or request
        
        Returns:
            Gemini's response as a string
        """
        print(f"\n💬 User: {user_message}")
        print("🤔 Gemini is thinking...")
        
        # Send message to Gemini
        response = self.chat.send_message(user_message)
        
        # Check if Gemini wants to call a function
        while response.candidates[0].content.parts:
            part = response.candidates[0].content.parts[0]
            
            # If Gemini responds with text
            if hasattr(part, 'text') and part.text:
                print(f"\n🤖 Gemini: {part.text}")
                return part.text
            
            # If Gemini wants to call a function
            if hasattr(part, 'function_call'):
                function_call = part.function_call
                function_name = function_call.name
                function_args = dict(function_call.args)
                
                print(f"\n🔧 Gemini wants to call: {function_name}")
                print(f"   Arguments: {function_args}")
                
                # Call the MCP server
                print(f"📡 Calling MCP server...")
                try:
                    result = await self.mcp.call_tool(function_name, function_args)
                    print(f"✅ Got result from MCP server")
                    
                    # Send function result back to Gemini
                    response = self.chat.send_message(
                        genai.types.Content(
                            parts=[genai.types.Part(
                                function_response=genai.types.FunctionResponse(
                                    name=function_name,
                                    response={"result": result}
                                )
                            )]
                        )
                    )
                    
                except Exception as e:
                    print(f"❌ Error calling MCP server: {e}")
                    
                    # Send error back to Gemini
                    response = self.chat.send_message(
                        genai.types.Content(
                            parts=[genai.types.Part(
                                function_response=genai.types.FunctionResponse(
                                    name=function_name,
                                    response={"error": str(e)}
                                )
                            )]
                        )
                    )
            else:
                # No text and no function call
                break
        
        return "I'm not sure how to respond to that."


async def example_conversations():
    """Run example conversations with Gemini"""
    
    print("=" * 70)
    print("🚀 Gemini Pro + MCP Server Integration Demo")
    print("=" * 70)
    print()
    print("💡 Using:")
    print(f"   • MCP Server: {MCP_SERVER_URL}")
    print(f"   • Model: Gemini 1.5 Pro")
    print()
    
    # Initialize MCP client
    mcp_client = MCPClient(MCP_SERVER_URL, MCP_API_KEY)
    
    # Create Gemini agent
    agent = GeminiMCPAgent(mcp_client)
    
    # Example conversations
    conversations = [
        "What's the current price of Bitcoin?",
        "Show me the top 5 cryptocurrencies by market cap",
        "Which cryptocurrencies are trending right now?",
        "What's the price of Ethereum in euros?",
        "Compare Bitcoin and Ethereum prices"
    ]
    
    for i, question in enumerate(conversations, 1):
        print(f"\n{'=' * 70}")
        print(f"Example {i}/{len(conversations)}")
        print('=' * 70)
        
        await agent.chat_with_tools(question)
        
        # Wait a bit between requests to respect rate limits
        if i < len(conversations):
            print("\n⏳ Waiting 5 seconds before next question...")
            await asyncio.sleep(5)
    
    print(f"\n{'=' * 70}")
    print("✅ All examples completed!")
    print('=' * 70)


async def interactive_mode():
    """Interactive chat mode with Gemini"""
    
    print("=" * 70)
    print("💬 Interactive Gemini + MCP Chat")
    print("=" * 70)
    print()
    print("💡 Ask questions about cryptocurrencies!")
    print("   Type 'quit' or 'exit' to stop")
    print()
    
    # Initialize
    mcp_client = MCPClient(MCP_SERVER_URL, MCP_API_KEY)
    agent = GeminiMCPAgent(mcp_client)
    
    while True:
        try:
            # Get user input
            user_input = input("\n💬 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            # Get Gemini's response
            await agent.chat_with_tools(user_input)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


async def main():
    """Main entry point"""
    
    print("\n")
    print("🌟" * 35)
    print()
    print("  Gemini Pro × Crypto Finance MCP Server")
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
    print("  1. Run example conversations (demo)")
    print("  2. Interactive chat mode")
    print()
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            await example_conversations()
        elif choice == "2":
            await interactive_mode()
        else:
            print("Invalid choice. Running examples...")
            await example_conversations()
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())

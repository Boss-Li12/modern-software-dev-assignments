"""
Gemini Pro Integration with TRUE Function Calling
Gemini decides which tool to call based on tool descriptions
"""

import os
import asyncio
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv
import json

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


# Define tools for Gemini Function Calling
TOOLS = [
    {
        "function_declarations": [
            {
                "name": "get_crypto_price",
                "description": "Get the current price and market data for a specific cryptocurrency. Use this when users ask about the price, value, or cost of a cryptocurrency like Bitcoin, Ethereum, etc. Returns price, market cap, 24h volume, and 24h price change.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "coin_id": {
                            "type": "string",
                            "description": "The CoinGecko coin ID (e.g., 'bitcoin', 'ethereum', 'cardano', 'solana', 'ripple', 'dogecoin', 'litecoin')"
                        },
                        "vs_currency": {
                            "type": "string",
                            "description": "The target currency code (default: 'usd'). Options: 'usd', 'eur', 'gbp', 'jpy', 'cny'",
                            "default": "usd"
                        }
                    },
                    "required": ["coin_id"]
                }
            },
            {
                "name": "get_trending_coins",
                "description": "Get the list of currently trending cryptocurrencies on CoinGecko. Use this when users ask about trending, hot, popular, or what's trending in crypto. Returns the top 7 trending coins with their basic information.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_market_data",
                "description": "Get market data for top cryptocurrencies ranked by market capitalization. Use this when users ask about top cryptocurrencies, market leaders, or want to see a list of cryptocurrencies. Returns detailed market information including prices, volumes, and price changes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "vs_currency": {
                            "type": "string",
                            "description": "Target currency code (default: 'usd')",
                            "default": "usd"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of coins to return, between 1 and 100 (default: 10)",
                            "default": 10
                        }
                    }
                }
            }
        ]
    }
]


class GeminiAgent:
    """Gemini agent with function calling support"""
    
    def __init__(self, api_key: str, mcp_client: MCPClient, verbose: bool = False):
        self.api_key = api_key
        self.mcp_client = mcp_client
        self.api_url = GEMINI_API_URL
        self.conversation_history = []
        self.verbose = verbose  # 👈 控制是否显示详细信息
    
    
    async def _call_gemini(self, contents: list, tools: Optional[list] = None) -> dict:
        """Call Gemini API"""
        payload = {
            "contents": contents
        }
        
        if tools:
            payload["tools"] = tools
        
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
            return response.json()
    
    async def chat(self, user_message: str) -> str:
        """
        Send a message to Gemini and handle function calling
        Gemini will decide which tool to call based on the user's question
        """
        print(f"\n💬 User: {user_message}")
        
        # Add user message to conversation
        self.conversation_history.append({
            "role": "user",
            "parts": [{"text": user_message}]
        })
        
        # Call Gemini with tools
        print("🤔 Gemini is thinking...")
        
        max_iterations = 5  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call Gemini
            response = await self._call_gemini(
                contents=self.conversation_history,
                tools=TOOLS
            )
            
            # Check if there are candidates
            if not response.get("candidates"):
                return "Sorry, I couldn't generate a response."
            
            candidate = response["candidates"][0]
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            
            if not parts:
                return "Sorry, I couldn't generate a response."
            
            first_part = parts[0]
            
            # Check if Gemini wants to call a function
            if "functionCall" in first_part:
                function_call = first_part["functionCall"]
                function_name = function_call.get("name")
                function_args = function_call.get("args", {})
                
                print(f"🔧 Gemini chose to call: {function_name}")
                print(f"   with arguments: {json.dumps(function_args, indent=2)}")
                
                # Add function call to history
                self.conversation_history.append({
                    "role": "model",
                    "parts": [{"functionCall": function_call}]
                })
                
                # Call the MCP tool
                print(f"📡 Calling MCP server...")
                try:
                    tool_result = await self.mcp_client.call_tool(function_name, function_args)
                    print(f"✅ Got result from MCP server")
                    
                    # 显示实际返回的数据
                    print(f"\n📊 MCP Tool Result:")
                    if self.verbose:
                        # 详细模式：显示完整数据
                        print(f"   {tool_result}")
                    else:
                        # 简洁模式：只显示前200个字符
                        preview = tool_result[:200] + "..." if len(tool_result) > 200 else tool_result
                        print(f"   {preview}")
                        if len(tool_result) > 200:
                            print(f"   (Use verbose mode to see full data)")
                    
                    # Add function response to history
                    self.conversation_history.append({
                        "role": "user",
                        "parts": [{
                            "functionResponse": {
                                "name": function_name,
                                "response": {
                                    "content": tool_result
                                }
                            }
                        }]
                    })
                    
                    # 显示发送给 Gemini 的数据
                    print(f"\n📤 Sending tool result back to Gemini...")
                    if self.verbose:
                        print(f"   Gemini will now read this data and generate a natural language response")
                    
                    
                except Exception as e:
                    print(f"❌ Error calling tool: {e}")
                    self.conversation_history.append({
                        "role": "user",
                        "parts": [{
                            "functionResponse": {
                                "name": function_name,
                                "response": {
                                    "error": str(e)
                                }
                            }
                        }]
                    })
                
                # Continue loop to get Gemini's text response
                continue
            
            # If Gemini responds with text (final response)
            if "text" in first_part:
                final_response = first_part["text"]
                
                # Add to history
                self.conversation_history.append({
                    "role": "model",
                    "parts": [{"text": final_response}]
                })
                
                print(f"\n🤖 Gemini: {final_response}")
                return final_response
            
            # If we get here, something unexpected happened
            break
        
        return "Sorry, I had trouble processing your request."
    
    def reset(self):
        """Reset conversation history"""
        self.conversation_history = []


async def demo(verbose=False):
    """Run demo conversations"""
    
    print("=" * 70)
    print("🚀 Gemini 2.0 Function Calling + MCP Server")
    print("=" * 70)
    print()
    if verbose:
        print("💡 VERBOSE MODE: You'll see COMPLETE data flow!")
        print("   - Gemini's tool selection")
        print("   - FULL tool results from MCP")
        print("   - How Gemini processes the data")
    else:
        print("💡 In this demo, Gemini DECIDES which tool to call!")
        print("   You'll see Gemini analyze the question and choose the right tool.")
    print()
    
    # Initialize
    mcp_client = MCPClient(MCP_SERVER_URL, MCP_API_KEY)
    agent = GeminiAgent(GEMINI_API_KEY, mcp_client, verbose=verbose)  # 👈 传入 verbose
    
    
    # Test questions - Gemini will decide which tool to use!
    questions = [
        "What's the current price of Bitcoin?",
        "Show me Ethereum's price in euros",
        "Which cryptocurrencies are trending right now?",
        "What are the top 5 cryptocurrencies by market cap?",
        "How much is Solana worth?",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'=' * 70}")
        print(f"Question {i}/{len(questions)}")
        print('=' * 70)
        
        try:
            await agent.chat(question)
            agent.reset()  # Reset for next question
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        # Wait between requests
        if i < len(questions):
            print("\n⏳ Waiting 3 seconds...")
            await asyncio.sleep(3)
    
    print(f"\n{'=' * 70}")
    print("✅ All demos completed!")
    print('=' * 70)


async def interactive():
    """Interactive chat mode"""
    
    print("=" * 70)
    print("💬 Interactive Gemini Function Calling Chat")
    print("=" * 70)
    print()
    print("💡 Ask any question about cryptocurrencies!")
    print("   Gemini will automatically decide which tool to use.")
    print()
    print("   Examples:")
    print("   - What's the Bitcoin price?")
    print("   - Show trending coins")
    print("   - Top 10 cryptocurrencies")
    print("   - Ethereum in euros")
    print()
    print("   Type 'quit' to exit, 'reset' to clear conversation")
    print()
    
    # Initialize
    mcp_client = MCPClient(MCP_SERVER_URL, MCP_API_KEY)
    agent = GeminiAgent(GEMINI_API_KEY, mcp_client)
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == 'reset':
                agent.reset()
                print("🔄 Conversation reset!")
                continue
            
            # Let Gemini handle it!
            await agent.chat(user_input)
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


async def main():
    print("\n")
    print("🌟" * 35)
    print()
    print("  Gemini 2.0 Function Calling × MCP Server")
    print("  (Gemini decides which tool to use!)")
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
    print("  1. Run demo (normal)")
    print("  2. Run demo (verbose - see FULL data flow)")
    print("  3. Interactive chat mode")
    print()
    
    try:
        choice = input("Enter choice (1/2/3): ").strip()
        
        if choice == "1":
            await demo(verbose=False)
        elif choice == "2":
            await demo(verbose=True)  # 👈 详细模式
        elif choice == "3":
            await interactive()
        else:
            print("Invalid choice. Running normal demo...")
            await demo(verbose=False)
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())

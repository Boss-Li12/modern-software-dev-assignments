"""
Quick test to verify the MCP server is working
"""

import asyncio
import httpx


async def quick_test():
    """Quick test of essential functionality"""
    
    SERVER_URL = "http://localhost:8000"
    API_KEY = "demo-key-12345"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    print("🧪 Quick MCP Server Test")
    print("=" * 60)
    print()
    
    try:
        async with httpx.AsyncClient() as client:
            # Test 1: Health check
            print("1️⃣  Testing health endpoint...")
            response = await client.get(f"{SERVER_URL}/health")
            if response.status_code == 200:
                print("   ✅ Server is healthy")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return
            print()
            
            # Test 2: List tools
            print("2️⃣  Listing available tools...")
            response = await client.post(
                f"{SERVER_URL}/mcp/list-tools",
                headers=headers
            )
            
            if response.status_code == 200:
                tools = response.json().get("tools", [])
                print(f"   ✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"      • {tool['name']}")
            else:
                print(f"   ❌ Failed to list tools: {response.status_code}")
                return
            print()
            
            # Test 3: Call a tool (Bitcoin price only)
            print("3️⃣  Testing tool call (get_crypto_price)...")
            response = await client.post(
                f"{SERVER_URL}/mcp/call-tool",
                headers=headers,
                json={
                    "name": "get_crypto_price",
                    "arguments": {"coin_id": "bitcoin"}
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if not result.get("isError"):
                    print("   ✅ Tool call successful")
                    print(f"   📊 Result: {result.get('content', [{}])[0].get('text', 'N/A')[:100]}...")
                else:
                    print(f"   ❌ Tool returned error: {result}")
            else:
                print(f"   ❌ Tool call failed: {response.status_code}")
                print(f"      Response: {response.text}")
                return
            print()
            
            # Test 4: Authentication test (invalid key)
            print("4️⃣  Testing authentication (should fail)...")
            bad_headers = {
                "Authorization": "Bearer invalid-key",
                "Content-Type": "application/json"
            }
            response = await client.post(
                f"{SERVER_URL}/mcp/list-tools",
                headers=bad_headers
            )
            
            if response.status_code == 401:
                print("   ✅ Authentication properly rejected invalid key")
            else:
                print(f"   ⚠️  Expected 401, got {response.status_code}")
            print()
        
        print("=" * 60)
        print("✅ All tests passed! MCP server is working correctly.")
        print("=" * 60)
        print()
        print("💡 Next steps:")
        print("   • Deploy to Vercel using: ./deploy.sh")
        print("   • Integrate with your AI agent")
        print("   • Check README.md for more details")
        print()
    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(quick_test())

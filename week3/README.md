# Week 3 — Crypto Finance MCP Server

A Model Context Protocol (MCP) HTTP server that provides real-time cryptocurrency financial data through the CoinGecko API. This server can be integrated with AI agents and MCP-aware clients to query crypto market information.

## 🌟 Features

- **Remote HTTP MCP Server** with full authentication support
- **3 Cryptocurrency Tools**:
  - `get_crypto_price` - Get real-time price and market data for any cryptocurrency
  - `get_trending_coins` - Discover currently trending cryptocurrencies
  - `get_market_data` - Get comprehensive market data for top cryptocurrencies by market cap
- **API Key Authentication** using Bearer tokens
- **Robust Error Handling** for API failures, timeouts, and rate limits
- **Production-Ready** with logging, CORS support, and health checks
- **Easy Deployment** to Vercel or any cloud platform

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- (Optional) Vercel CLI for deployment

## 🚀 Quick Start

### 1. Installation

```bash
# Navigate to the server directory
cd week3/server

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` and set your API key:

```env
MCP_API_KEY=your-secure-api-key-here
HOST=0.0.0.0
PORT=8000
```

**Important**: Generate a secure random API key for production use:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Run Locally

Start the server:

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will be available at `http://localhost:8000`

### 4. Test the Server

Run the test client in a separate terminal:

```bash
python test_client.py
```

Or test manually with curl:

```bash
# List available tools
curl -X POST http://localhost:8000/mcp/list-tools \
  -H "Authorization: Bearer demo-key-12345" \
  -H "Content-Type: application/json"

# Get Bitcoin price
curl -X POST http://localhost:8000/mcp/call-tool \
  -H "Authorization: Bearer demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"name": "get_crypto_price", "arguments": {"coin_id": "bitcoin"}}'
```

## 🛠️ Tool Reference

### 1. get_crypto_price

Get current price and market data for a cryptocurrency.

**Parameters:**
- `coin_id` (string, required): CoinGecko coin ID (e.g., "bitcoin", "ethereum", "cardano")
- `vs_currency` (string, optional): Target currency code. Default: "usd". Options: "usd", "eur", "gbp", "jpy", "cny"

**Example Request:**
```json
{
  "name": "get_crypto_price",
  "arguments": {
    "coin_id": "bitcoin",
    "vs_currency": "usd"
  }
}
```

**Example Response:**
```json
{
  "content": [{
    "type": "text",
    "text": "{
      \"coin\": \"bitcoin\",
      \"currency\": \"usd\",
      \"price\": 42350.12,
      \"market_cap\": 829500000000,
      \"volume_24h\": 25400000000,
      \"change_24h\": 2.34,
      \"timestamp\": \"2026-01-30T08:00:00.000000\"
    }"
  }],
  "isError": false
}
```

### 2. get_trending_coins

Get currently trending cryptocurrencies on CoinGecko.

**Parameters:** None

**Example Request:**
```json
{
  "name": "get_trending_coins",
  "arguments": {}
}
```

**Example Response:**
```json
{
  "content": [{
    "type": "text",
    "text": "{
      \"trending_coins\": [
        {
          \"id\": \"bitcoin\",
          \"name\": \"Bitcoin\",
          \"symbol\": \"BTC\",
          \"market_cap_rank\": 1,
          \"price_btc\": 1.0
        },
        ...
      ],
      \"count\": 7,
      \"timestamp\": \"2026-01-30T08:00:00.000000\"
    }"
  }],
  "isError": false
}
```

### 3. get_market_data

Get market data for top cryptocurrencies ranked by market cap.

**Parameters:**
- `vs_currency` (string, optional): Target currency code. Default: "usd". Options: "usd", "eur", "gbp", "jpy", "cny"
- `limit` (integer, optional): Number of coins to return (1-100). Default: 10

**Example Request:**
```json
{
  "name": "get_market_data",
  "arguments": {
    "vs_currency": "usd",
    "limit": 5
  }
}
```

**Example Response:**
```json
{
  "content": [{
    "type": "text",
    "text": "{
      \"markets\": [
        {
          \"id\": \"bitcoin\",
          \"symbol\": \"btc\",
          \"name\": \"Bitcoin\",
          \"current_price\": 42350.12,
          \"market_cap\": 829500000000,
          \"market_cap_rank\": 1,
          \"total_volume\": 25400000000,
          \"price_change_24h\": 2.34,
          \"ath\": 69045.0,
          \"atl\": 67.81
        },
        ...
      ],
      \"currency\": \"usd\",
      \"count\": 5,
      \"timestamp\": \"2026-01-30T08:00:00.000000\"
    }"
  }],
  "isError": false
}
```

## 🔐 Authentication

The server uses API key authentication via Bearer tokens in the Authorization header.

**Header Format:**
```
Authorization: Bearer your-api-key-here
```

If you're using this with an AI agent or MCP client, configure it to include this header in all requests.

## 🌐 Deployment to Vercel

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Deploy

```bash
# From the week3 directory
vercel

# Follow the prompts and set environment variables
```

### 3. Set Environment Variables

In Vercel dashboard or via CLI:

```bash
vercel env add MCP_API_KEY
# Enter your secure API key when prompted
```

### 4. Production Deployment

```bash
vercel --prod
```

Your MCP server will be available at a public URL like `https://your-project.vercel.app`

## 🔌 Integration with MCP Clients

### Example: Using with OpenAI SDK

```python
import httpx

async def query_mcp_tool(tool_name: str, arguments: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://your-server.vercel.app/mcp/call-tool",
            headers={
                "Authorization": "Bearer your-api-key",
                "Content-Type": "application/json"
            },
            json={
                "name": tool_name,
                "arguments": arguments
            }
        )
        return response.json()

# Example usage
result = await query_mcp_tool("get_crypto_price", {"coin_id": "bitcoin"})
```

### Example: Using with Claude SDK

```python
from anthropic import Anthropic

client = Anthropic(api_key="your-api-key")

# Configure MCP server as a tool
tools = [
    {
        "name": "get_crypto_price",
        "description": "Get current price and market data for a cryptocurrency",
        "input_schema": {
            "type": "object",
            "properties": {
                "coin_id": {
                    "type": "string",
                    "description": "CoinGecko coin ID"
                }
            },
            "required": ["coin_id"]
        }
    }
]

# Use in conversation
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "What's the current price of Bitcoin?"}]
)
```

## 📊 API Endpoints

- `GET /` - Server information
- `GET /health` - Health check
- `POST /mcp/list-tools` - List available MCP tools
- `POST /mcp/call-tool` - Execute an MCP tool

## 🔄 Rate Limiting

The server respects CoinGecko's rate limits:
- Free tier: ~10-50 requests/minute
- The server returns HTTP 429 when rate limited
- Implement client-side backoff when receiving 429 responses

## 🐛 Error Handling

The server provides meaningful error messages for:
- Invalid coin IDs (404)
- Missing required parameters (400)
- API timeouts (504)
- Rate limit exceeded (429)
- Authentication failures (401)
- Internal errors (500)

All errors are logged to `mcp_server.log` for debugging.

## 📝 Common CoinGecko Coin IDs

- Bitcoin: `bitcoin`
- Ethereum: `ethereum`
- Cardano: `cardano`
- Solana: `solana`
- Polkadot: `polkadot`
- Dogecoin: `dogecoin`
- Ripple: `ripple`

For a complete list, visit: https://api.coingecko.com/api/v3/coins/list

## 🧪 Testing

The `test_client.py` script demonstrates all available tools:

```bash
python test_client.py
```

This will:
1. List all available tools
2. Get Bitcoin price in USD
3. Get Ethereum price in EUR
4. Get trending cryptocurrencies
5. Get top 5 market data

## 📦 Project Structure

```
week3/
├── server/
│   ├── main.py              # MCP server implementation
│   ├── test_client.py       # Test client script
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Environment variable template
│   └── mcp_server.log       # Server logs (generated)
├── vercel.json              # Vercel deployment config
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 🎯 Assignment Requirements Checklist

- ✅ **External API**: CoinGecko API for cryptocurrency data
- ✅ **2+ MCP Tools**: 3 tools implemented (price, trending, market data)
- ✅ **Error Handling**: Graceful handling of HTTP failures, timeouts, rate limits
- ✅ **Documentation**: Complete setup and usage guide
- ✅ **Deployment Mode**: Remote HTTP server (extra credit)
- ✅ **Authentication**: API key support (extra credit)

## 🚨 Troubleshooting

### Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
PORT=8001 python main.py
```

### Module not found
```bash
# Ensure you're in the server directory
cd week3/server

# Reinstall dependencies
pip install -r requirements.txt
```

### CoinGecko API errors
- Check your internet connection
- Verify the coin ID is correct
- Wait a minute if rate limited (429 error)

## 📚 References

- [MCP Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [CoinGecko API Documentation](https://www.coingecko.com/en/api/documentation)
- [Vercel Python Deployment](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 📄 License

This is an educational project for Modern Software Development assignments.

## 👤 Author

Created for Week 3 Assignment - MCP Server Implementation

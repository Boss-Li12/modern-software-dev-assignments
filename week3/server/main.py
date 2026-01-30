"""
MCP HTTP Server for Cryptocurrency Financial Data
Wraps CoinGecko API to provide crypto market data through MCP protocol
"""

import os
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import httpx
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Configure logging (no stdout for production)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler()  # Keep for development, remove in production
    ]
)
logger = logging.getLogger(__name__)

# Configuration
API_KEY = os.getenv("MCP_API_KEY", "demo-key-12345")  # For MCP authentication
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
REQUEST_TIMEOUT = 10  # seconds

app = FastAPI(
    title="Crypto Finance MCP Server",
    description="MCP server providing cryptocurrency market data via CoinGecko API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= MCP Protocol Models =============

class ToolParameter(BaseModel):
    type: str
    description: str
    enum: Optional[List[str]] = None
    default: Optional[Any] = None


class Tool(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]


class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class ToolCallResponse(BaseModel):
    content: List[Dict[str, Any]]
    isError: bool = False


# ============= Authentication =============

def verify_api_key(authorization: Optional[str] = Header(None)) -> bool:
    """Verify API key from Authorization header"""
    if not authorization:
        logger.warning("Missing authorization header")
        return False
    
    # Expected format: "Bearer <api_key>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning("Invalid authorization format")
        return False
    
    provided_key = parts[1]
    is_valid = provided_key == API_KEY
    
    if not is_valid:
        logger.warning(f"Invalid API key attempt: {provided_key[:8]}...")
    
    return is_valid


# ============= CoinGecko API Client =============

class CoinGeckoClient:
    """Client for interacting with CoinGecko API"""
    
    def __init__(self):
        self.base_url = COINGECKO_BASE_URL
        self.timeout = REQUEST_TIMEOUT
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to CoinGecko API with error handling"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"Making request to CoinGecko: {endpoint}")
                response = await client.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
        
        except httpx.TimeoutException:
            logger.error(f"Timeout requesting {endpoint}")
            raise HTTPException(status_code=504, detail="CoinGecko API timeout")
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {endpoint}")
            if e.response.status_code == 429:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later."
                )
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"CoinGecko API error: {e.response.text}"
            )
        
        except Exception as e:
            logger.error(f"Unexpected error requesting {endpoint}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    
    async def get_coin_price(self, coin_id: str, vs_currency: str = "usd") -> Dict[str, Any]:
        """Get current price of a cryptocurrency"""
        params = {
            "ids": coin_id,
            "vs_currencies": vs_currency,
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true"
        }
        return await self._make_request("simple/price", params)
    
    async def get_trending_coins(self) -> Dict[str, Any]:
        """Get trending cryptocurrencies"""
        return await self._make_request("search/trending")
    
    async def get_market_data(self, vs_currency: str = "usd", limit: int = 10) -> List[Dict[str, Any]]:
        """Get market data for top cryptocurrencies"""
        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": min(limit, 100),
            "page": 1,
            "sparkline": "false"
        }
        return await self._make_request("coins/markets", params)


coingecko = CoinGeckoClient()


# ============= MCP Tool Implementations =============

async def get_crypto_price_tool(coin_id: str, vs_currency: str = "usd") -> Dict[str, Any]:
    """
    Get current price and market data for a cryptocurrency
    
    Args:
        coin_id: CoinGecko coin ID (e.g., 'bitcoin', 'ethereum')
        vs_currency: Target currency (default: 'usd')
    
    Returns:
        Price data including market cap, volume, and 24h change
    """
    logger.info(f"Getting price for {coin_id} in {vs_currency}")
    
    data = await coingecko.get_coin_price(coin_id, vs_currency)
    
    if not data or coin_id not in data:
        raise HTTPException(
            status_code=404,
            detail=f"Coin '{coin_id}' not found. Please check the coin ID."
        )
    
    coin_data = data[coin_id]
    
    return {
        "coin": coin_id,
        "currency": vs_currency,
        "price": coin_data.get(vs_currency),
        "market_cap": coin_data.get(f"{vs_currency}_market_cap"),
        "volume_24h": coin_data.get(f"{vs_currency}_24h_vol"),
        "change_24h": coin_data.get(f"{vs_currency}_24h_change"),
        "timestamp": datetime.utcnow().isoformat()
    }


async def get_trending_coins_tool() -> Dict[str, Any]:
    """
    Get currently trending cryptocurrencies
    
    Returns:
        List of trending coins with basic info
    """
    logger.info("Getting trending coins")
    
    data = await coingecko.get_trending_coins()
    
    if "coins" not in data:
        raise HTTPException(status_code=500, detail="Unexpected API response format")
    
    trending = []
    for item in data["coins"][:7]:  # Top 7 trending
        coin = item.get("item", {})
        trending.append({
            "id": coin.get("id"),
            "name": coin.get("name"),
            "symbol": coin.get("symbol"),
            "market_cap_rank": coin.get("market_cap_rank"),
            "price_btc": coin.get("price_btc")
        })
    
    return {
        "trending_coins": trending,
        "count": len(trending),
        "timestamp": datetime.utcnow().isoformat()
    }


async def get_market_data_tool(vs_currency: str = "usd", limit: int = 10) -> Dict[str, Any]:
    """
    Get market data for top cryptocurrencies by market cap
    
    Args:
        vs_currency: Target currency (default: 'usd')
        limit: Number of coins to return (max 100)
    
    Returns:
        Market data for top coins
    """
    logger.info(f"Getting market data for top {limit} coins in {vs_currency}")
    
    limit = max(1, min(limit, 100))  # Clamp between 1 and 100
    
    data = await coingecko.get_market_data(vs_currency, limit)
    
    if not data:
        raise HTTPException(status_code=500, detail="No market data available")
    
    markets = []
    for coin in data:
        markets.append({
            "id": coin.get("id"),
            "symbol": coin.get("symbol"),
            "name": coin.get("name"),
            "current_price": coin.get("current_price"),
            "market_cap": coin.get("market_cap"),
            "market_cap_rank": coin.get("market_cap_rank"),
            "total_volume": coin.get("total_volume"),
            "price_change_24h": coin.get("price_change_percentage_24h"),
            "ath": coin.get("ath"),  # All-time high
            "atl": coin.get("atl")   # All-time low
        })
    
    return {
        "markets": markets,
        "currency": vs_currency,
        "count": len(markets),
        "timestamp": datetime.utcnow().isoformat()
    }


# ============= MCP Protocol Endpoints =============

@app.get("/")
async def root():
    """Server info endpoint"""
    return {
        "name": "crypto-finance-mcp",
        "version": "1.0.0",
        "protocol": "MCP",
        "description": "Cryptocurrency financial data MCP server"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/mcp/list-tools")
async def list_tools(request: Request, authorization: Optional[str] = Header(None)):
    """List available MCP tools"""
    
    if not verify_api_key(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    tools = [
        Tool(
            name="get_crypto_price",
            description="Get current price and market data for a cryptocurrency. Returns price, market cap, 24h volume, and 24h change.",
            inputSchema={
                "type": "object",
                "properties": {
                    "coin_id": {
                        "type": "string",
                        "description": "CoinGecko coin ID (e.g., 'bitcoin', 'ethereum', 'cardano')"
                    },
                    "vs_currency": {
                        "type": "string",
                        "description": "Target currency code",
                        "default": "usd",
                        "enum": ["usd", "eur", "gbp", "jpy", "cny"]
                    }
                },
                "required": ["coin_id"]
            }
        ),
        Tool(
            name="get_trending_coins",
            description="Get currently trending cryptocurrencies on CoinGecko. Returns top 7 trending coins with basic info.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_market_data",
            description="Get market data for top cryptocurrencies ranked by market cap. Returns detailed market info including prices, volumes, and price changes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vs_currency": {
                        "type": "string",
                        "description": "Target currency code",
                        "default": "usd",
                        "enum": ["usd", "eur", "gbp", "jpy", "cny"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of coins to return (1-100)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    }
                }
            }
        )
    ]
    
    logger.info("Listed tools successfully")
    return {"tools": [tool.dict() for tool in tools]}


@app.post("/mcp/call-tool")
async def call_tool(
    tool_request: ToolCallRequest,
    authorization: Optional[str] = Header(None)
):
    """Execute an MCP tool"""
    
    if not verify_api_key(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    tool_name = tool_request.name
    arguments = tool_request.arguments
    
    logger.info(f"Calling tool: {tool_name} with args: {arguments}")
    
    try:
        # Route to appropriate tool
        if tool_name == "get_crypto_price":
            coin_id = arguments.get("coin_id")
            if not coin_id:
                raise HTTPException(status_code=400, detail="Missing required parameter: coin_id")
            
            vs_currency = arguments.get("vs_currency", "usd")
            result = await get_crypto_price_tool(coin_id, vs_currency)
        
        elif tool_name == "get_trending_coins":
            result = await get_trending_coins_tool()
        
        elif tool_name == "get_market_data":
            vs_currency = arguments.get("vs_currency", "usd")
            limit = arguments.get("limit", 10)
            result = await get_market_data_tool(vs_currency, limit)
        
        else:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        logger.info(f"Tool {tool_name} executed successfully")
        
        return ToolCallResponse(
            content=[{
                "type": "text",
                "text": str(result)
            }],
            isError=False
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {str(e)}")
        return ToolCallResponse(
            content=[{
                "type": "text",
                "text": f"Error: {str(e)}"
            }],
            isError=True
        )


# ============= Main Entry Point =============

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting MCP server on {host}:{port}")
    logger.info(f"API key authentication enabled: {API_KEY[:8]}...")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

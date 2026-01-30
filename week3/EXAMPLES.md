# 使用示例

本文档展示如何使用 Crypto Finance MCP Server 的常见场景。

## 前置条件

确保服务器正在运行：

```bash
cd week3/server
python main.py
```

服务器将在 `http://localhost:8000` 上运行。

## 示例 1: 查询比特币价格

### curl 命令

```bash
curl -X POST http://localhost:8000/mcp/call-tool \
  -H "Authorization: Bearer demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_crypto_price",
    "arguments": {
      "coin_id": "bitcoin"
    }
  }'
```

### Python 代码

```python
import httpx
import asyncio

async def get_bitcoin_price():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'http://localhost:8000/mcp/call-tool',
            headers={
                'Authorization': 'Bearer demo-key-12345',
                'Content-Type': 'application/json'
            },
            json={
                'name': 'get_crypto_price',
                'arguments': {'coin_id': 'bitcoin'}
            }
        )
        print(response.json())

asyncio.run(get_bitcoin_price())
```

### 示例响应

```json
{
  "content": [{
    "type": "text",
    "text": "{'coin': 'bitcoin', 'currency': 'usd', 'price': 82586, 'market_cap': 1650552220364, 'volume_24h': 90068047263, 'change_24h': -6.24, 'timestamp': '2026-01-30T08:00:00.000000'}"
  }],
  "isError": false
}
```

## 示例 2: 获取不同货币的价格

### 获取以太坊的欧元价格

```bash
curl -X POST http://localhost:8000/mcp/call-tool \
  -H "Authorization: Bearer demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_crypto_price",
    "arguments": {
      "coin_id": "ethereum",
      "vs_currency": "eur"
    }
  }'
```

### 支持的货币

- `usd` - 美元
- `eur` - 欧元
- `gbp` - 英镑
- `jpy` - 日元
- `cny` - 人民币

## 示例 3: 获取热门加密货币

```bash
curl -X POST http://localhost:8000/mcp/call-tool \
  -H "Authorization: Bearer demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_trending_coins",
    "arguments": {}
  }'
```

### 示例响应

```json
{
  "content": [{
    "type": "text",
    "text": "{'trending_coins': [{'id': 'bitcoin', 'name': 'Bitcoin', 'symbol': 'BTC', 'market_cap_rank': 1, 'price_btc': 1.0}, {'id': 'solana', 'name': 'Solana', 'symbol': 'SOL', 'market_cap_rank': 7, 'price_btc': 0.00139}], 'count': 7, 'timestamp': '2026-01-30T08:00:00.000000'}"
  }],
  "isError": false
}
```

## 示例 4: 获取市场数据

### 获取前10名加密货币

```bash
curl -X POST http://localhost:8000/mcp/call-tool \
  -H "Authorization: Bearer demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_market_data",
    "arguments": {
      "limit": 10
    }
  }'
```

### 获取前5名（以欧元计价）

```bash
curl -X POST http://localhost:8000/mcp/call-tool \
  -H "Authorization: Bearer demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_market_data",
    "arguments": {
      "vs_currency": "eur",
      "limit": 5
    }
  }'
```

## 示例 5: 在 AI Agent 中使用

### 与 OpenAI GPT-4 集成

```python
from openai import OpenAI
import httpx
import json

client = OpenAI(api_key="your-openai-key")

# 定义可用工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_crypto_price",
            "description": "Get current price and market data for a cryptocurrency",
            "parameters": {
                "type": "object",
                "properties": {
                    "coin_id": {
                        "type": "string",
                        "description": "CoinGecko coin ID (e.g., bitcoin, ethereum)"
                    },
                    "vs_currency": {
                        "type": "string",
                        "description": "Target currency code",
                        "default": "usd"
                    }
                },
                "required": ["coin_id"]
            }
        }
    }
]

# 发起对话
messages = [{"role": "user", "content": "What's the current price of Bitcoin?"}]

response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=tools
)

# 如果GPT-4想调用工具
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        # 调用我们的MCP服务器
        async with httpx.AsyncClient() as http_client:
            mcp_response = await http_client.post(
                'http://localhost:8000/mcp/call-tool',
                headers={'Authorization': 'Bearer demo-key-12345'},
                json={
                    'name': tool_call.function.name,
                    'arguments': json.loads(tool_call.function.arguments)
                }
            )
            result = mcp_response.json()
        
        # 将结果返回给GPT-4
        messages.append({
            "role": "function",
            "name": tool_call.function.name,
            "content": result['content'][0]['text']
        })

# 获取最终响应
final_response = client.chat.completions.create(
    model="gpt-4",
    messages=messages
)

print(final_response.choices[0].message.content)
```

## 示例 6: 错误处理

### 无效的 coin ID

```bash
curl -X POST http://localhost:8000/mcp/call-tool \
  -H "Authorization: Bearer demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_crypto_price",
    "arguments": {
      "coin_id": "invalid-coin"
    }
  }'
```

**响应**：
```json
{
  "detail": "Coin 'invalid-coin' not found. Please check the coin ID."
}
```

### 无效的 API Key

```bash
curl -X POST http://localhost:8000/mcp/list-tools \
  -H "Authorization: Bearer wrong-key" \
  -H "Content-Type: application/json"
```

**响应**：
```json
{
  "detail": "Invalid or missing API key"
}
```

### 速率限制

当触发 CoinGecko 的速率限制时：

```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

**建议**: 等待1-2分钟后重试，或实现客户端的指数退避重试策略。

## 示例 7: 健康检查

```bash
curl http://localhost:8000/health
```

**响应**：
```json
{
  "status": "healthy",
  "timestamp": "2026-01-30T08:00:00.000000"
}
```

## 示例 8: 列出所有可用工具

```bash
curl -X POST http://localhost:8000/mcp/list-tools \
  -H "Authorization: Bearer demo-key-12345" \
  -H "Content-Type: application/json"
```

**响应**：
```json
{
  "tools": [
    {
      "name": "get_crypto_price",
      "description": "Get current price and market data for a cryptocurrency...",
      "inputSchema": {...}
    },
    {
      "name": "get_trending_coins",
      "description": "Get currently trending cryptocurrencies...",
      "inputSchema": {...}
    },
    {
      "name": "get_market_data",
      "description": "Get market data for top cryptocurrencies...",
      "inputSchema": {...}
    }
  ]
}
```

## 常用加密货币 ID

| 名称 | CoinGecko ID |
|------|-------------|
| Bitcoin | `bitcoin` |
| Ethereum | `ethereum` |
| Cardano | `cardano` |
| Solana | `solana` |
| Polkadot | `polkadot` |
| Ripple | `ripple` |
| Dogecoin | `dogecoin` |
| Binance Coin | `binancecoin` |
| Chainlink | `chainlink` |
| Litecoin | `litecoin` |

完整列表: https://api.coingecko.com/api/v3/coins/list

## 运行测试脚本

### 完整测试

```bash
cd week3/server
python test_client.py
```

这将运行所有工具的完整测试套件。

### 快速测试

```bash
cd week3/server
python quick_test.py
```

快速验证服务器基本功能。

## 部署到远程服务器

### 使用 Vercel

```bash
cd week3
./deploy.sh
```

然后在 Vercel 仪表板中设置环境变量 `MCP_API_KEY`。

部署后，将所有 `http://localhost:8000` 替换为你的 Vercel URL (例如 `https://your-project.vercel.app`)。

## 最佳实践

1. **速率限制**: 实现客户端缓存和请求节流
2. **错误处理**: 始终检查 `isError` 字段
3. **认证**: 在生产环境使用强随机 API key
4. **超时**: 设置适当的请求超时 (建议 10-30 秒)
5. **重试**: 对 429 错误实现指数退避重试

## 故障排除

### 连接被拒绝

确保服务器正在运行：
```bash
python main.py
```

### 401 错误

检查 API key 是否正确：
```bash
# 查看 .env 文件
cat .env

# 确保 Authorization header 格式正确
Authorization: Bearer your-api-key
```

### 429 错误

等待 1-2 分钟后重试，CoinGecko 有速率限制。

---

更多信息请参考 [README.md](README.md) 和 [writeup.md](writeup.md)。

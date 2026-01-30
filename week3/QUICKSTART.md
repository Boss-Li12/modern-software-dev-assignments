# 🚀 快速启动指南

只需5分钟即可运行你的加密货币MCP服务器！

## 📋 前提条件

- Python 3.8+
- pip

## ⚡ 快速启动（3步）

### 1️⃣ 安装依赖

```bash
cd week3/server
pip install -r requirements.txt
```

### 2️⃣ 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# (可选) 生成安全的API密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"
# 将生成的密钥复制到 .env 文件的 MCP_API_KEY
```

### 3️⃣ 启动服务器

```bash
python main.py
```

✅ **完成！** 服务器现在运行在 `http://localhost:8000`

## 🧪 快速测试

在**新的终端窗口**中运行：

```bash
cd week3/server
python quick_test.py
```

你应该看到：
```
✅ Server is healthy
✅ Found 3 tools
✅ Tool call successful
✅ Authentication properly rejected invalid key
```

## 🎯 第一次API调用

### 使用 curl:

```bash
curl -X POST http://localhost:8000/mcp/call-tool \
  -H "Authorization: Bearer demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"name": "get_crypto_price", "arguments": {"coin_id": "bitcoin"}}'
```

### 使用 Python:

```python
import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        r = await client.post(
            'http://localhost:8000/mcp/call-tool',
            headers={'Authorization': 'Bearer demo-key-12345'},
            json={'name': 'get_crypto_price', 'arguments': {'coin_id': 'bitcoin'}}
        )
        print(r.json())

asyncio.run(test())
```

## 📚 接下来做什么？

1. **查看所有工具**: [README.md](README.md#工具参考)
2. **更多示例**: [EXAMPLES.md](EXAMPLES.md)
3. **集成AI**: [examples/integration_examples.py](examples/integration_examples.py)
4. **部署到云端**: [README.md](README.md#部署到vercel)

## 🔧 故障排除

### 端口已被占用
```bash
# 换个端口
PORT=8001 python main.py
```

### 模块未找到
```bash
# 重新安装依赖
pip install -r requirements.txt
```

### CoinGecko 429 错误
等待1-2分钟，这是正常的速率限制。

## 💡 可用的工具

| 工具名称 | 功能 |
|---------|------|
| `get_crypto_price` | 获取加密货币价格 |
| `get_trending_coins` | 获取热门币种 |
| `get_market_data` | 获取市场数据 |

## 🎉 恭喜！

你的MCP服务器已经运行！现在你可以：

- ✅ 查询实时加密货币价格
- ✅ 追踪市场趋势
- ✅ 集成到AI agents
- ✅ 部署到生产环境

**需要帮助？** 查看 [README.md](README.md) 或 [EXAMPLES.md](EXAMPLES.md)

---

**下一步**: 部署到 Vercel 让全世界都能访问你的MCP服务器！

```bash
./deploy.sh
```

# 🚀 Gemini Pro 集成快速开始

## ⚡ 5 分钟开始使用 Gemini Pro

### 步骤 1: 获取 Gemini API Key

1. 访问 https://makersuite.google.com/app/apikey
2. 使用 Google 账号登录
3. 点击 "Create API key" 或 "Get API key"
4. 复制生成的 API key

### 步骤 2: 安装依赖

```bash
cd week3/examples
pip install -r requirements.txt
```

这会安装：
- `google-generativeai` - Gemini SDK
- `httpx` - HTTP 客户端
- `python-dotenv` - 环境变量管理

### 步骤 3: 配置环境变量

```bash
# 复制模板
cp .env.example .env

# 编辑 .env 文件
nano .env  # 或使用你喜欢的编辑器
```

在 `.env` 文件中设置：

```bash
GEMINI_API_KEY=你的-gemini-api-key
MCP_SERVER_URL=http://localhost:8000
MCP_API_KEY=demo-key-12345
```

### 步骤 4: 启动 MCP 服务器

**在一个终端窗口中**：

```bash
cd week3/server
python main.py
```

看到 "Uvicorn running on http://0.0.0.0:8000" 表示成功！

### 步骤 5: 运行 Gemini 集成

**在另一个终端窗口中**：

```bash
cd week3/examples
python gemini_integration.py
```

然后选择模式：
- 选择 `1` - 运行示例对话（自动演示）
- 选择 `2` - 交互式聊天模式

---

## 💬 示例对话

当你运行交互模式时，可以这样问：

```
💬 You: 比特币现在多少钱？

🤔 Gemini is thinking...
🔧 Gemini wants to call: get_crypto_price
   Arguments: {'coin_id': 'bitcoin', 'vs_currency': 'usd'}
📡 Calling MCP server...
✅ Got result from MCP server

🤖 Gemini: 比特币当前价格是 $82,777 USD。
         在过去24小时内下跌了 5.76%。
         市值约为 16,500 亿美元。
```

---

## 🎯 可以尝试的问题

### 基础查询
- "比特币现在多少钱？"
- "What's the price of Ethereum?"
- "以太坊的欧元价格是多少？"

### 市场分析
- "Show me the top 5 cryptocurrencies"
- "哪些加密货币现在最热门？"
- "给我看看市场前10名"

### 比较分析
- "Compare Bitcoin and Ethereum"
- "比特币和以太坊哪个更好？"
- "Which crypto has the highest volume?"

### 趋势分析
- "What are the trending coins today?"
- "Which cryptocurrencies are gaining popularity?"

---

## 🌐 使用生产服务器（Vercel）

### 部署到 Vercel

**前提条件**：安装 Node.js 和 npm

```bash
# 安装 Vercel CLI
npm install -g vercel

# 登录
vercel login

# 部署
cd week3
vercel --prod
```

### 更新环境变量

部署后，更新 `.env` 文件：

```bash
GEMINI_API_KEY=你的-gemini-api-key
MCP_SERVER_URL=https://your-project.vercel.app
MCP_API_KEY=你的-安全-api-key
```

**重要**: 在 Vercel 仪表板中也要设置 `MCP_API_KEY` 环境变量！

---

## 🔧 故障排除

### 问题 1: "Please set GEMINI_API_KEY"

**原因**: 环境变量未设置

**解决**:
```bash
# 检查 .env 文件
cat .env

# 确保 GEMINI_API_KEY 已设置
export GEMINI_API_KEY="your-actual-key"
```

### 问题 2: "Connection refused"

**原因**: MCP 服务器未运行

**解决**:
```bash
# 在另一个终端启动服务器
cd week3/server
python main.py
```

### 问题 3: "Invalid API key"

**原因**: Gemini API key 无效

**解决**:
1. 重新生成 API key: https://makersuite.google.com/app/apikey
2. 更新 `.env` 文件
3. 重新运行脚本

### 问题 4: "Rate limit exceeded"

**原因**: CoinGecko API 速率限制

**解决**: 等待 1-2 分钟后重试

---

## 📊 架构图

```
用户问题
    ↓
Gemini Pro 1.5
    ↓
工具声明（Function Declarations）
    ├─ get_crypto_price
    ├─ get_trending_coins
    └─ get_market_data
    ↓
Gemini 决定调用哪个工具
    ↓
你的 Python 代码
    ↓
MCP Server (Vercel 或本地)
    ↓
CoinGecko API
    ↓
返回数据
    ↓
Gemini 生成自然语言回复
    ↓
用户看到结果
```

---

## 💡 技术要点

### Gemini Function Calling

Gemini 支持两种模式：

1. **自动模式** (`enable_automatic_function_calling=True`)
   - Gemini 自动调用函数并处理结果
   - 更简单但灵活性较低

2. **手动模式** (`enable_automatic_function_calling=False`) ⭐ **我们使用的**
   - 你控制何时调用函数
   - 可以添加日志、错误处理、速率限制等
   - 更适合生产环境

### 工具定义格式

```python
{
    "name": "get_crypto_price",  # 函数名
    "description": "...",         # Gemini 读取这个来决定何时调用
    "parameters": {               # JSON Schema 格式
        "type": "object",
        "properties": {
            "coin_id": {"type": "string", "description": "..."},
            ...
        },
        "required": ["coin_id"]
    }
}
```

---

## 🎓 进阶使用

### 自定义 System Instruction

```python
model = genai.GenerativeModel(
    model_name='gemini-1.5-pro',
    tools=[...],
    system_instruction="You are a cryptocurrency expert. Always provide prices in USD unless specified otherwise."
)
```

### 多轮对话

Gemini 会记住对话历史：

```
You: What's Bitcoin's price?
Gemini: Bitcoin is currently $82,777.

You: How about Ethereum?  # Gemini 知道你在问价格
Gemini: Ethereum is $2,735.
```

### 添加更多工具

在 `gemini_integration.py` 的 tools 列表中添加：

```python
{
    "name": "your_new_tool",
    "description": "...",
    "parameters": {...}
}
```

---

## 📚 相关文档

- **Gemini API**: https://ai.google.dev/docs
- **Function Calling Guide**: https://ai.google.dev/docs/function_calling
- **MCP 协议**: https://modelcontextprotocol.io
- **CoinGecko API**: https://www.coingecko.com/en/api

---

## ✅ 成功标志

如果你看到以下输出，说明一切正常：

```
🚀 Gemini Pro + MCP Server Integration Demo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Using:
   • MCP Server: http://localhost:8000
   • Model: Gemini 1.5 Pro

💬 User: What's the current price of Bitcoin?
🤔 Gemini is thinking...
🔧 Gemini wants to call: get_crypto_price
   Arguments: {'coin_id': 'bitcoin'}
📡 Calling MCP server...
✅ Got result from MCP server

🤖 Gemini: Bitcoin is currently priced at $82,777 USD...
```

---

## 🎉 下一步

现在你已经有了：
- ✅ 一个可工作的 MCP 服务器
- ✅ Gemini Pro 集成
- ✅ 交互式聊天界面

**可以尝试**：
1. 添加更多加密货币工具
2. 创建 Web 界面
3. 部署到 Vercel
4. 集成到你的应用中

祝你使用愉快！🚀

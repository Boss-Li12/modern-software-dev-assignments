# 从零实现 Gemini Function Calling：让 AI 自己决定调用哪个工具

## 前言

最近在做 AI Agent 相关的项目，终于搞明白了 Function Calling 的真正原理。很多教程都在讲"AI 可以调用工具"，但到底是**AI 自己选择工具**，还是**代码通过关键词匹配选择工具**？这两者有本质区别。

今天分享一个完整的实践案例：用 Gemini 2.0 + MCP 协议实现真正的 Function Calling，包括本地开发和 Vercel 部署方案。完整代码已开源，本文会详细解释每一步的原理。

---

## 一、什么是真正的 Function Calling？

### 错误示范：代码决定工具（假的 Function Calling）

很多人（包括我最开始）会这样写：

```python
user_input = "Bitcoin price?"

# 代码通过关键词匹配决定用哪个工具
if "price" in user_input:
    tool_name = "get_crypto_price"
    result = call_mcp_tool(tool_name, {"coin_id": "bitcoin"})
    
# 让 AI 把结果翻译成自然语言
response = gemini.generate(f"Explain this: {result}")
```

**问题在于**：工具选择完全由代码的 `if-else` 决定，AI 只是个"翻译器"，并没有参与决策。

### 正确示范：AI 决定工具（真的 Function Calling）

```python
# 1. 定义工具（给 AI 看的说明书）
tools = {
    "get_crypto_price": {
        "description": "Get price when users ask about cryptocurrency prices",
        "parameters": {"coin_id": "string"}
    }
}

# 2. 发送给 Gemini（带工具定义）
response = gemini.call(
    user_message="Bitcoin price?",
    tools=tools
)

# 3. Gemini 返回它的决定
if response.has_function_call():
    tool_name = response.function_call.name      # "get_crypto_price"
    tool_args = response.function_call.args      # {"coin_id": "bitcoin"}
    
    # 4. 执行 Gemini 选择的工具
    result = call_mcp_tool(tool_name, tool_args)
```

**关键区别**：
- ❌ 假的：代码用 `if` 判断关键词
- ✅ 真的：工具名和参数都来自 Gemini 的 API 响应

---

## 二、架构设计：MCP 协议 + Gemini Function Calling

### 整体架构

我们的系统分为三层：

```
用户 → Python Client → MCP Server → CoinGecko API
         ↓
    Gemini API (决定调用哪个工具)
```

**MCP Server**（Model Context Protocol）：
- 提供标准化的工具接口
- 3个工具：获取价格、热门币种、市场数据
- 使用 FastAPI 实现，支持 Bearer Token 认证

**Gemini Function Calling**：
- 接收工具定义和用户问题
- 分析语义，决定调用哪个工具
- 提取参数，返回 `functionCall`

### 本地开发 vs Vercel 部署

#### 方案 1：本地开发（localhost）

```
┌─────────────────────────────────────────┐
│  你的电脑                                │
│                                          │
│  ┌──────────────┐    ┌──────────────┐  │
│  │ Python Client│───→│ MCP Server   │  │
│  │ (Gemini调用) │    │ localhost:8000│  │
│  └──────┬───────┘    └──────────────┘  │
│         │                                │
└─────────┼────────────────────────────────┘
          ↓
   ┌──────────────┐
   │ Gemini API   │ (Google 服务器)
   │ 决定调用工具  │
   └──────────────┘
```

**特点**：
- ✅ 开发调试方便
- ✅ 完全免费
- ❌ 只能本地访问
- ❌ Gemini 无法直接调用 MCP（需要 Python Client 中转）

#### 方案 2：Vercel 部署（云端）

```
┌─────────────────┐         ┌─────────────────┐
│  你的电脑        │         │  Vercel 云端     │
│  Python Client  │────────→│  MCP Server     │
└────────┬────────┘         │  (https://xxx)  │
         │                  └─────────────────┘
         ↓
   ┌──────────────┐
   │ Gemini API   │
   │ 决定调用工具  │
   └──────────────┘
```

**特点**：
- ✅ 全球访问
- ✅ 可以集成到其他服务
- ✅ Vercel 免费套餐足够
- ⚠️ 需要配置环境变量

**你的理解完全正确**！无论本地还是云端，Gemini 都是**决定调用哪个工具**，实际的 HTTP 请求由 Python Client 发起。Gemini 没有直接调用 MCP 的能力，它只是返回一个"决定"（functionCall），告诉你的代码应该调用什么。

---

## 三、核心实现：代码详解

### 1. 定义 MCP 工具

```python
TOOLS = [
    {
        "function_declarations": [
            {
                "name": "get_crypto_price",
                "description": """Get price when users ask about 
                the price, value, or cost of a cryptocurrency.""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "coin_id": {
                            "type": "string",
                            "description": "Coin ID like 'bitcoin', 'ethereum'"
                        },
                        "vs_currency": {
                            "type": "string",
                            "description": "Currency code: usd, eur, cny",
                            "default": "usd"
                        }
                    },
                    "required": ["coin_id"]
                }
            }
        ]
    }
]
```

**关键点**：`description` 非常重要！Gemini 通过阅读这个描述来决定是否使用这个工具。

### 2. 发送给 Gemini（带工具定义）

```python
async def _call_gemini(self, user_message: str, tools: list) -> dict:
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": user_message}]}
        ],
        "tools": tools  # ← 告诉 Gemini 有这些工具可用
    }
    
    response = await httpx.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        headers={"X-goog-api-key": GEMINI_API_KEY},
        json=payload
    )
    
    return response.json()
```

### 3. Gemini 的响应（决定调用工具）

```python
response = await _call_gemini("What's Bitcoin price?", TOOLS)

# Gemini 返回的 JSON
{
  "candidates": [{
    "content": {
      "parts": [{
        "functionCall": {              # ← Gemini 决定调用函数
          "name": "get_crypto_price",  # ← Gemini 选的工具
          "args": {                    # ← Gemini 提取的参数
            "coin_id": "bitcoin"
          }
        }
      }]
    }
  }]
}
```

**注意**：这里的 `functionCall` 是 Gemini 生成的，不是代码写死的！

### 4. 执行 Gemini 的决定

```python
if "functionCall" in response:
    function_call = response["functionCall"]
    
    # 直接使用 Gemini 返回的值
    tool_name = function_call["name"]    # "get_crypto_price"
    tool_args = function_call["args"]     # {"coin_id": "bitcoin"}
    
    # 调用 MCP Server
    result = await mcp_client.call_tool(tool_name, tool_args)
    
    # 把结果返回给 Gemini
    final_response = await _call_gemini(
        function_response=result
    )
```

### 5. 完整的对话流程

```python
async def chat(self, user_message: str):
    # 第 1 轮：用户提问 + 工具定义 → Gemini
    response1 = await self._call_gemini(user_message, tools=TOOLS)
    
    # Gemini 返回 functionCall
    function_name = response1["functionCall"]["name"]
    function_args = response1["functionCall"]["args"]
    
    # 调用 MCP 工具
    tool_result = await mcp_client.call_tool(function_name, function_args)
    # 返回: {'price': 82106, 'coin': 'bitcoin', ...}
    
    # 第 2 轮：工具结果 → Gemini
    response2 = await self._call_gemini(
        function_response=tool_result,
        tools=TOOLS
    )
    
    # Gemini 生成最终回答
    return response2["text"]
    # "The current price of Bitcoin is $82,106."
```

---

## 四、实际运行效果

### Verbose 模式输出（完整数据流）

```
💬 User: What's the current price of Bitcoin?
🤔 Gemini is thinking...

🔧 Gemini chose to call: get_crypto_price
   with arguments: {
     "coin_id": "bitcoin"
   }

📡 Calling MCP server...
✅ Got result from MCP server

📊 MCP Tool Result:
   {'coin': 'bitcoin', 'currency': 'usd', 'price': 82106, 
    'market_cap': 1641163059743.98, 'volume_24h': 91125423921.63}

📤 Sending tool result back to Gemini...
   Gemini will now read this data and generate a natural language response

🤖 Gemini: The current price of Bitcoin is $82,106.
```

### 智能参数提取

**问题**："Show me Ethereum's price in euros"

**Gemini 的理解**：
- "Ethereum" → `coin_id = "ethereum"`
- "euros" → `vs_currency = "eur"`

**调用**：
```python
get_crypto_price(coin_id="ethereum", vs_currency="eur")
```

**结果**：
```
🤖 Gemini: Ethereum is currently priced at 2,274.89 EUR.
```

---

## 五、部署到 Vercel（从本地到云端）

### 本地开发配置

```bash
# .env 文件
MCP_SERVER_URL=http://localhost:8000
MCP_API_KEY=demo-key-12345
GEMINI_API_KEY=your-api-key

# 启动 MCP Server
cd server
python main.py

# 运行 Gemini Client
cd examples
python gemini_function_calling.py
```

### Vercel 部署步骤

#### 1. 准备 vercel.json

```json
{
  "version": 2,
  "builds": [
    {
      "src": "server/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "server/main.py"
    }
  ]
}
```

#### 2. 部署到 Vercel

```bash
# 安装 Vercel CLI
npm install -g vercel

# 登录并部署
vercel login
vercel --prod

# 获得 URL: https://your-project.vercel.app
```

#### 3. 配置环境变量

在 Vercel Dashboard 设置：
- `API_KEY`: 生成一个安全的密钥
- `COINGECKO_API_KEY`: （可选）CoinGecko Pro API Key

#### 4. 更新客户端配置

```bash
# 本地 .env 改为：
MCP_SERVER_URL=https://your-project.vercel.app
MCP_API_KEY=vercel上配置的密钥
GEMINI_API_KEY=your-gemini-key
```

#### 5. 测试部署

```bash
python gemini_function_calling.py

# 输出显示：
💡 Using:
   • MCP Server: https://your-project.vercel.app
   • Model: Gemini 2.0 Flash

🔧 Gemini chose to call: get_crypto_price
📡 Calling MCP server... (Vercel)
✅ Got result from MCP server
```

**现在你的 MCP Server 在云端了！** 任何人都可以通过 API Key 访问。

---

## 六、关键收获

### 1. Function Calling 的本质

**AI 的角色**：
- ✅ 理解自然语言
- ✅ 阅读工具描述
- ✅ 决定调用哪个工具
- ✅ 提取参数
- ✅ 生成最终回答

**代码的角色**：
- ❌ 不做语义理解
- ❌ 不做工具选择
- ✅ 只负责执行 AI 的决定
- ✅ 调用实际的工具 API

### 2. 本地 vs 云端的理解误区

**误区**："Gemini 可以直接调用我的 MCP Server"

**真相**：
- Gemini 只是返回一个 `functionCall` 对象
- 实际的 HTTP 请求由你的代码发起
- 本地开发：代码调用 `localhost:8000`
- 云端部署：代码调用 `https://xxx.vercel.app`

**这就是为什么需要 Python Client**：它是 Gemini 和 MCP Server 之间的"桥梁"。

### 3. 可扩展性

添加新工具非常简单：

```python
# 只需添加工具定义
TOOLS.append({
    "name": "get_crypto_news",
    "description": "Get latest cryptocurrency news",
    "parameters": {...}
})

# Gemini 自动知道什么时候用！
# 不需要修改任何 if-else 逻辑
```

---

## 七、成本分析

### 免费方案（适合学习和小项目）

- **MCP Server**: Vercel 免费套餐（100GB 带宽/月）
- **Gemini API**: 免费套餐（15 RPM，1500 RPD）
- **CoinGecko**: 免费套餐（30 请求/分钟）

**总成本**: $0/月

### 付费升级（生产环境）

- **Vercel Pro**: $20/月（无限带宽）
- **Gemini API**: 按量计费（约 $0.002/1K tokens）
- **CoinGecko Pro**: $99/月（更高限额）

对于中小型应用，免费套餐完全够用。

---

## 八、总结

这个项目让我深刻理解了 Function Calling 的原理：

1. **AI 是决策者**：Gemini 通过阅读工具描述来决定调用哪个工具
2. **代码是执行者**：接收 AI 的决定，调用实际的 API
3. **MCP 是标准化**：统一的工具协议，方便集成

**从本地到云端的演进**：
- 本地：快速开发，调试方便
- Vercel：全球访问，生产就绪
- 原理不变：都是 Gemini 决定 + 代码执行

完整代码已开源，包含详细注释和使用文档。如果你也在做 AI Agent，希望这个实践对你有帮助！

---

## 参考资料

- **Gemini API 文档**: https://ai.google.dev/docs
- **MCP 协议**: https://modelcontextprotocol.io
- **Vercel 部署**: https://vercel.com/docs
- **项目源码**: （可以放你的 GitHub 链接）

有问题欢迎留言交流！

---

**全文约 1980 字**

# 🎯 Function Calling 对比：真正的 AI 工具选择

## ❌ 错误方式：代码决定工具

### gemini_rest.py (之前的版本)

```python
# 代码通过关键词匹配决定用哪个工具
lower_input = user_input.lower()

if "price" in lower_input:
    # 代码决定用这个工具
    tool_name = "get_crypto_price"
    args = {"coin_id": "bitcoin"}
    
elif "trending" in lower_input:
    tool_name = "get_trending_coins"
    args = {}

# 直接调用工具
result = await mcp.call_tool(tool_name, args)

# 让 Gemini 解释结果
response = await gemini.generate(f"Explain this data: {result}")
```

**问题**:
- ❌ AI 没有参与决策
- ❌ 代码写死了规则
- ❌ 无法处理复杂问题
- ❌ 不是真正的 Function Calling

---

## ✅ 正确方式：Gemini 决定工具

### gemini_function_calling.py (新版本)

```python
# 1. 定义工具（包含详细描述）
TOOLS = [
    {
        "function_declarations": [
            {
                "name": "get_crypto_price",
                "description": "Get the current price and market data for a specific cryptocurrency. Use this when users ask about the price, value, or cost...",
                "parameters": {...}
            },
            {
                "name": "get_trending_coins",
                "description": "Get the list of currently trending cryptocurrencies. Use this when users ask about trending, hot, popular...",
                "parameters": {...}
            }
        ]
    }
]

# 2. 发送给 Gemini（带工具定义）
response = await gemini_api.call(
    user_message="What's the Bitcoin price?",
    tools=TOOLS  # 👈 Gemini 可以看到所有工具
)

# 3. Gemini 分析并决定
if response.has_function_call():
    # Gemini 选择了工具！
    function_name = response.function_call.name  # "get_crypto_price"
    function_args = response.function_call.args  # {"coin_id": "bitcoin"}
    
    # 4. 执行 Gemini 选择的工具
    result = await mcp.call_tool(function_name, function_args)
    
    # 5. 把结果返回给 Gemini
    final_response = await gemini_api.call(
        function_response=result
    )
```

**优势**:
- ✅ **AI 自主决策** - Gemini 根据描述选择工具
- ✅ **灵活处理** - 能理解各种表达方式
- ✅ **自动参数** - Gemini 提取并设置参数
- ✅ **真正的 Function Calling**

---

## 📊 实际效果对比

### 问题: "Show me Ethereum's price in euros"

#### ❌ 代码决定方式
```
代码分析:
  - 发现关键词 "price"
  - 发现关键词 "ethereum"
  - 发现关键词 "euros"
  
代码决定:
  tool_name = "get_crypto_price"
  args = {"coin_id": "ethereum", "vs_currency": "eur"}
```

#### ✅ Gemini 决定方式
```
Gemini 分析:
  - 用户想知道价格
  - 查看工具: get_crypto_price 的描述说可以获取价格
  - 需要 coin_id 参数，用户说的是 "Ethereum"
  - 需要 vs_currency 参数，用户说的是 "euros" (eur)
  
Gemini 决定:
  functionCall: {
    name: "get_crypto_price",
    args: {
      "coin_id": "ethereum",
      "vs_currency": "eur"
    }
  }
```

---

## 🎓 为什么 Function Calling 重要？

### 1. **AI 的本质用途**
Function Calling 展示了 AI 的核心价值：
- 理解自然语言
- 理解工具能力（通过描述）
- 做出智能决策

### 2. **扩展性**
```python
# ❌ 代码决定：每增加一个工具就要写 if-else
if "price" in input:
    ...
elif "trending" in input:
    ...
elif "news" in input:  # 新工具，要改代码
    ...

# ✅ Gemini 决定：只需添加工具定义
TOOLS.append({
    "name": "get_crypto_news",
    "description": "Get latest cryptocurrency news..."
})
# Gemini 自动知道什么时候用！
```

### 3. **处理复杂问题**
```
用户: "Compare Bitcoin and Ethereum prices, and also show me what's trending"

❌ 代码决定: 无法处理（有多个意图）

✅ Gemini 决定: 
  1. 调用 get_crypto_price("bitcoin")
  2. 调用 get_crypto_price("ethereum")
  3. 调用 get_trending_coins()
  4. 综合结果生成回答
```

---

## 🔄 完整流程

```
┌─────────────────┐
│  用户提问       │ "What's the Bitcoin price?"
└────────┬────────┘
         ↓
┌────────────────────────────────────────┐
│  Gemini 2.0                            │
│  - 看到用户问题                         │
│  - 看到 3 个工具定义                    │
│  - 理解每个工具的作用                   │
│  - 决定: get_crypto_price 最合适       │
│  - 设置参数: coin_id="bitcoin"         │
└────────┬───────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│  代码收到 function_call                │
│  {                                      │
│    name: "get_crypto_price",           │
│    args: {coin_id: "bitcoin"}          │
│  }                                      │
└────────┬───────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│  代码调用 MCP 服务器                   │
│  POST /mcp/call-tool                   │
│  {name: "get_crypto_price", ...}       │
└────────┬───────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│  MCP 服务器 → CoinGecko API            │
│  获取 Bitcoin 数据                      │
└────────┬───────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│  代码把结果返回给 Gemini               │
│  functionResponse: {                   │
│    content: "{'price': 82408, ...}"    │
│  }                                      │
└────────┬───────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│  Gemini 生成最终回答                   │
│  "The current price of Bitcoin         │
│   is $82,408."                         │
└────────────────────────────────────────┘
```

---

## 📝 代码文件对比

| 文件 | 方式 | 适用场景 |
|------|------|---------|
| `gemini_rest.py` | ❌ 代码决定工具 | 快速演示，固定流程 |
| `gemini_function_calling.py` | ✅ Gemini 决定工具 | **生产环境，推荐使用** |
| `gemini_simple.py` | ❌ 无 AI 工具选择 | 测试 MCP 服务器 |

---

## 🎯 推荐使用

**⭐ 使用 `gemini_function_calling.py`**

这才是真正的 AI Agent：
- Gemini 理解用户意图
- Gemini 选择合适的工具
- Gemini 设置正确的参数
- Gemini 综合结果生成回答

---

## 🚀 立即试用

```bash
cd week3/examples
python gemini_function_calling.py

# 选择 2 (交互模式)
# 然后随便问问题，看 Gemini 如何选择工具！
```

**试试这些问题**:
- "What's the Bitcoin price?" → Gemini 会选 get_crypto_price
- "Show trending coins" → Gemini 会选 get_trending_coins
- "Top 10 cryptocurrencies" → Gemini 会选 get_market_data
- "Ethereum in euros" → Gemini 会选 get_crypto_price + eur 参数

每次你都会看到：
```
🔧 Gemini chose to call: <tool_name>
   with arguments: {...}
```

**这就是真正的 Function Calling！** 🎉

# 🎯 Function Calling 代码详解

## 核心原理：Gemini 如何自动选择工具

### 第一步：定义工具（告诉 Gemini 有哪些工具）

```python
# 这是关键！我们定义了 3 个工具，包含详细描述
TOOLS = [
    {
        "function_declarations": [
            {
                # 工具名称
                "name": "get_crypto_price",
                
                # ⭐ 关键：详细的描述，Gemini 会读这个！
                "description": """
                Get the current price and market data for a specific cryptocurrency.
                Use this when users ask about the price, value, or cost of a 
                cryptocurrency like Bitcoin, Ethereum, etc.
                """,
                
                # ⭐ 参数定义，Gemini 会根据这个提取参数
                "parameters": {
                    "type": "object",
                    "properties": {
                        "coin_id": {
                            "type": "string",
                            "description": "The coin ID (e.g., 'bitcoin', 'ethereum')"
                        },
                        "vs_currency": {
                            "type": "string", 
                            "description": "Currency code (usd, eur, gbp...)",
                            "default": "usd"
                        }
                    },
                    "required": ["coin_id"]
                }
            }
        ]
    }
]

# ❓ 问题：Gemini 怎么知道什么时候用这个工具？
# ✅ 答案：Gemini 读 description！
#    - 用户问 "Bitcoin price"
#    - Gemini 看到 description 说 "Use this when users ask about price"
#    - Gemini 决定：用这个工具！
```

---

### 第二步：发送给 Gemini（带工具定义）

```python
async def _call_gemini(self, contents: list, tools: Optional[list] = None) -> dict:
    """调用 Gemini API"""
    
    payload = {
        "contents": contents  # 👈 对话历史（包括用户问题）
    }
    
    # ⭐ 关键：如果提供了 tools，Gemini 就能看到并使用它们
    if tools:
        payload["tools"] = tools  # 👈 工具定义
    
    # 发送到 Gemini
    response = await client.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        json=payload
    )
    
    return response.json()

# ❓ 发送了什么给 Gemini？
# ✅ 答案：
#    {
#      "contents": [{"role": "user", "parts": [{"text": "What's Bitcoin price?"}]}],
#      "tools": [
#        {
#          "function_declarations": [
#            {"name": "get_crypto_price", "description": "...", ...}
#          ]
#        }
#      ]
#    }
#
# Gemini 同时看到：
#   1. 用户问题："What's Bitcoin price?"
#   2. 可用工具：get_crypto_price, get_trending_coins, get_market_data
#   3. 每个工具的描述和参数
```

---

### 第三步：Gemini 的响应（决定调用工具）

```python
async def chat(self, user_message: str) -> str:
    # 1. 添加用户消息到历史
    self.conversation_history.append({
        "role": "user",
        "parts": [{"text": user_message}]  # 👈 "What's Bitcoin price?"
    })
    
    # 2. 调用 Gemini（带工具定义）
    response = await self._call_gemini(
        contents=self.conversation_history,
        tools=TOOLS  # 👈 告诉 Gemini 有这些工具可用
    )
    
    # 3. 检查 Gemini 的响应
    candidate = response["candidates"][0]
    parts = candidate["content"]["parts"]
    first_part = parts[0]
    
    # ⭐ 关键判断：Gemini 想调用函数吗？
    if "functionCall" in first_part:
        # 👇 是的！Gemini 决定调用函数了！
        
        function_call = first_part["functionCall"]
        function_name = function_call["name"]      # 👈 Gemini 选择的工具名
        function_args = function_call["args"]       # 👈 Gemini 提取的参数
        
        print(f"🔧 Gemini chose to call: {function_name}")
        print(f"   with arguments: {function_args}")
        
        # ... 接下来调用 MCP 工具

# ❓ Gemini 返回了什么？
# ✅ 实际响应示例：
#    {
#      "candidates": [{
#        "content": {
#          "parts": [{
#            "functionCall": {                    👈 Gemini 决定调用函数
#              "name": "get_crypto_price",        👈 Gemini 选择的工具
#              "args": {                          👈 Gemini 提取的参数
#                "coin_id": "bitcoin"             👈 从 "Bitcoin price" 提取出来的
#              }
#            }
#          }]
#        }
#      }]
#    }
```

---

### 第四步：执行 Gemini 选择的工具

```python
    # 接上面的代码...
    
    if "functionCall" in first_part:
        function_call = first_part["functionCall"]
        function_name = function_call["name"]      # "get_crypto_price"
        function_args = function_call["args"]       # {"coin_id": "bitcoin"}
        
        # ⭐ 这里才是实际调用 MCP 工具
        # 注意：工具名和参数都是 Gemini 决定的！
        tool_result = await self.mcp_client.call_tool(
            function_name,   # 👈 Gemini 选的
            function_args    # 👈 Gemini 提的
        )
        
        print(f"✅ Got result: {tool_result}")
        
        # 结果类似：
        # {'coin': 'bitcoin', 'price': 82408, ...}

# ❓ 代码怎么知道调用哪个工具？
# ✅ 答案：完全由 Gemini 决定！
#    - function_name 是 Gemini 返回的
#    - function_args 是 Gemini 提取的
#    - 代码只是执行 Gemini 的决定
```

---

### 第五步：把结果返回给 Gemini

```python
        # 接上面的代码...
        
        # 把工具结果返回给 Gemini
        self.conversation_history.append({
            "role": "user",  # 👈 角色是 user（表示这是函数的返回值）
            "parts": [{
                "functionResponse": {           # 👈 告诉 Gemini 这是函数返回
                    "name": function_name,      # 哪个函数
                    "response": {
                        "content": tool_result  # 函数返回的数据
                    }
                }
            }]
        })
        
        # 再次调用 Gemini（现在它有工具结果了）
        response = await self._call_gemini(
            contents=self.conversation_history,
            tools=TOOLS
        )
        
        # 这次 Gemini 会生成文本回答
        final_text = response["candidates"][0]["content"]["parts"][0]["text"]
        # "The current price of Bitcoin is $82,408."

# ❓ 为什么要再次调用 Gemini？
# ✅ 答案：第一次调用，Gemini 决定调用工具
#         第二次调用，Gemini 看到工具结果，生成自然语言回答
```

---

## 完整流程图解

```
用户输入: "What's Bitcoin price?"
         ↓
┌────────────────────────────────────────────────────┐
│ 步骤 1: 调用 Gemini                                 │
│ payload = {                                        │
│   "contents": [                                    │
│     {"role": "user", "parts": [                    │
│       {"text": "What's Bitcoin price?"}           │
│     ]}                                             │
│   ],                                               │
│   "tools": [                                       │
│     {"function_declarations": [                    │
│       {"name": "get_crypto_price",                 │
│        "description": "Get price when users ask...",│
│        "parameters": {...}                         │
│       }                                            │
│     ]}                                             │
│   ]                                                │
│ }                                                  │
└────────┬───────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────┐
│ Gemini 的思考过程（在 Google 服务器上）            │
│                                                    │
│ 1. 读取用户问题: "What's Bitcoin price?"          │
│ 2. 查看可用工具:                                  │
│    - get_crypto_price: "Get price when users ask" │
│    - get_trending_coins: "Get trending coins..."  │
│    - get_market_data: "Get top coins..."          │
│                                                    │
│ 3. 分析匹配:                                       │
│    用户问 "price" → get_crypto_price 匹配！       │
│                                                    │
│ 4. 提取参数:                                       │
│    用户提到 "Bitcoin" → coin_id = "bitcoin"       │
│                                                    │
│ 5. 决定: 调用 get_crypto_price(coin_id="bitcoin") │
└────────┬───────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────┐
│ 步骤 2: Gemini 返回 functionCall                   │
│ response = {                                       │
│   "candidates": [{                                 │
│     "content": {                                   │
│       "parts": [{                                  │
│         "functionCall": {           ← 不是文本！   │
│           "name": "get_crypto_price",              │
│           "args": {"coin_id": "bitcoin"}           │
│         }                                          │
│       }]                                           │
│     }                                              │
│   }]                                               │
│ }                                                  │
└────────┬───────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────┐
│ 步骤 3: 代码检测到 functionCall                    │
│                                                    │
│ if "functionCall" in first_part:  ← 检测到！      │
│     function_name = "get_crypto_price"             │
│     function_args = {"coin_id": "bitcoin"}         │
│                                                    │
│     print("🔧 Gemini chose:", function_name)       │
└────────┬───────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────┐
│ 步骤 4: 调用 MCP 工具（执行 Gemini 的决定）        │
│                                                    │
│ result = await mcp_client.call_tool(              │
│     "get_crypto_price",        ← Gemini 选的      │
│     {"coin_id": "bitcoin"}     ← Gemini 提取的    │
│ )                                                  │
│                                                    │
│ # MCP 服务器返回:                                  │
│ result = "{'price': 82408, 'coin': 'bitcoin', ...}"│
└────────┬───────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────┐
│ 步骤 5: 把结果返回给 Gemini                        │
│                                                    │
│ conversation_history.append({                      │
│   "role": "user",                                  │
│   "parts": [{                                      │
│     "functionResponse": {                          │
│       "name": "get_crypto_price",                  │
│       "response": {"content": result}              │
│     }                                              │
│   }]                                               │
│ })                                                 │
│                                                    │
│ # 再次调用 Gemini                                  │
│ response = await _call_gemini(                     │
│     contents=conversation_history,                 │
│     tools=TOOLS                                    │
│ )                                                  │
└────────┬───────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────┐
│ Gemini 第二次思考                                  │
│                                                    │
│ 1. 看到用户问题: "What's Bitcoin price?"          │
│ 2. 看到我调用了: get_crypto_price                 │
│ 3. 看到结果: {'price': 82408, ...}                │
│ 4. 生成自然语言回答                                │
└────────┬───────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────┐
│ 步骤 6: Gemini 返回文本回答                        │
│                                                    │
│ response = {                                       │
│   "candidates": [{                                 │
│     "content": {                                   │
│       "parts": [{                                  │
│         "text": "The current price of Bitcoin is $82,408." │
│       }]                                           │
│     }                                              │
│   }]                                               │
│ }                                                  │
└────────┬───────────────────────────────────────────┘
         ↓
    显示给用户
```

---

## 关键证据：Gemini 自己决定

### 证据 1: 不同问题，不同工具选择

```python
# 问题 1
User: "What's Bitcoin price?"
Gemini 决定 → functionCall: {name: "get_crypto_price", args: {coin_id: "bitcoin"}}

# 问题 2  
User: "Which coins are trending?"
Gemini 决定 → functionCall: {name: "get_trending_coins", args: {}}

# 问题 3
User: "Top 5 cryptocurrencies"
Gemini 决定 → functionCall: {name: "get_market_data", args: {limit: 5}}
```

**代码完全一样**，但 Gemini 根据问题选择了不同的工具！

### 证据 2: Gemini 智能提取参数

```python
# 示例 1: 提取 coin_id
User: "How much is Solana worth?"
Gemini → {coin_id: "solana"}  # Gemini 理解 "Solana" 是币种

# 示例 2: 提取 coin_id + vs_currency
User: "Ethereum price in euros"
Gemini → {coin_id: "ethereum", vs_currency: "eur"}  
         # Gemini 理解 "euros" = "eur"

# 示例 3: 提取 limit
User: "Show me top 3"
Gemini → {limit: 3}  # Gemini 理解 "3" 是数量
```

**代码没有任何正则表达式或关键词匹配**！

### 证据 3: 代码中没有 if-else

```python
# ❌ 如果是代码决定，会看到：
if "price" in user_input:
    tool_name = "get_crypto_price"
elif "trending" in user_input:
    tool_name = "get_trending_coins"
# ...

# ✅ 实际代码：
response = await self._call_gemini(contents, tools=TOOLS)
if "functionCall" in response:
    function_name = response["functionCall"]["name"]  # 直接用 Gemini 返回的
    function_args = response["functionCall"]["args"]   # 直接用 Gemini 返回的
```

**没有任何逻辑判断**，完全依赖 Gemini 的返回！

---

## 总结

### AI 自动调用体现在：

1. **工具选择**: Gemini 读描述，自己决定用哪个工具
2. **参数提取**: Gemini 理解问题，自己提取参数值
3. **代码被动**: 代码只是执行 Gemini 的决定，不做任何判断

### 关键代码行：

```python
# 这一行是关键：把工具定义发送给 Gemini
response = await self._call_gemini(contents, tools=TOOLS)

# 这一行证明是 AI 决定：直接使用 Gemini 返回的值
function_name = response["candidates"][0]["content"]["parts"][0]["functionCall"]["name"]
```

**如果 Gemini 从不返回 functionCall，工具永远不会被调用！**  
**正因为 Gemini 返回了 functionCall，工具才被调用！**

这就是真正的 Function Calling！🎉

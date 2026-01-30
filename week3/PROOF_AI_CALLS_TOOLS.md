# 🎯 如何证明是 AI 自动调用工具

## 快速回答

**看这一行代码就知道了**：

```python
# gemini_function_calling.py 第 150 行左右
function_name = first_part["functionCall"]["name"]      # 👈 这个值是 Gemini 返回的！
function_args = first_part["functionCall"]["args"]      # 👈 这个值也是 Gemini 返回的！

# 然后直接使用
result = await self.mcp_client.call_tool(function_name, function_args)
```

**如果这两个值来自代码的 if-else，那就是假的**。  
**如果这两个值来自 Gemini 的 API 响应，那就是真的**。

---

## 详细证明

### 证据 1: 代码中没有工具选择逻辑

**打开 `gemini_function_calling.py`，搜索关键词**：

```bash
# ❌ 在代码中搜索不到这些（因为没有）：
if "price" in user_input
if "bitcoin" in user_input  
if "trending" in user_input

# ✅ 只能搜到这些（直接用 Gemini 返回值）：
function_name = ... ["functionCall"]["name"]
function_args = ... ["functionCall"]["args"]
```

### 证据 2: 查看实际的 API 调用

**关键代码（第 106-115 行）**：

```python
async def _call_gemini(self, contents: list, tools: Optional[list] = None) -> dict:
    """Call Gemini API"""
    
    payload = {
        "contents": contents  # 用户问题
    }
    
    if tools:
        payload["tools"] = tools  # 👈 把工具定义发给 Gemini
    
    # 发送到 Gemini API
    response = await client.post(GEMINI_API_URL, json=payload)
    return response.json()
```

**发送给 Gemini 的 JSON**：

```json
{
  "contents": [
    {
      "role": "user",
      "parts": [{"text": "What's Bitcoin price?"}]
    }
  ],
  "tools": [
    {
      "function_declarations": [
        {
          "name": "get_crypto_price",
          "description": "Get price when users ask about price...",
          "parameters": {...}
        },
        {
          "name": "get_trending_coins",
          "description": "Get trending coins when users ask...",
          ...
        }
      ]
    }
  ]
}
```

**Gemini 看到了**：
1. 用户问题："What's Bitcoin price?"
2. 可用工具：get_crypto_price, get_trending_coins, get_market_data
3. 每个工具的描述和参数

### 证据 3: 查看 Gemini 的响应

**Gemini 返回的 JSON**（真实API响应）：

```json
{
  "candidates": [{
    "content": {
      "parts": [{
        "functionCall": {              ← Gemini 决定调用函数！
          "name": "get_crypto_price",  ← Gemini 选择的工具
          "args": {                    ← Gemini 提取的参数
            "coin_id": "bitcoin"
          }
        }
      }]
    }
  }]
}
```

**注意**：
- `functionCall` 是 Gemini 返回的，不是代码生成的
- `name` 和 `args` 都是 Gemini 决定的

### 证据 4: 代码只是被动执行

**关键代码（第 149-157 行）**：

```python
# 检查 Gemini 是否返回了 functionCall
if "functionCall" in first_part:
    function_call = first_part["functionCall"]
    
    # 👇 直接使用 Gemini 返回的值，没有任何修改
    function_name = function_call["name"]      # Gemini 选的
    function_args = function_call["args"]       # Gemini 提的
    
    # 调用 MCP 工具
    result = await self.mcp_client.call_tool(
        function_name,   # 👈 来自 Gemini
        function_args    # 👈 来自 Gemini
    )
```

**代码没有做任何判断**，只是：
1. 检查 Gemini 是否返回了 `functionCall`
2. 如果有，提取 `name` 和 `args`
3. 调用对应的工具

---

## 实验验证

### 实验 1: 运行演示，查看输出

```bash
cd week3/examples
python gemini_function_calling.py <<< "1"
```

**输出**：
```
Question 1/5
💬 User: What's the current price of Bitcoin?
🤔 Gemini is thinking...
🔧 Gemini chose to call: get_crypto_price    ← 看！Gemini 选择的
   with arguments: {
  "coin_id": "bitcoin"                        ← 看！Gemini 提取的
}
```

**这个输出来自哪里？**

```python
# 代码第 155-157 行
print(f"🔧 Gemini chose to call: {function_name}")
print(f"   with arguments: {json.dumps(function_args, indent=2)}")
```

`function_name` 和 `function_args` 都来自 Gemini 的 API 响应！

### 实验 2: 不同问题，不同工具

**问题 1**: "What's Bitcoin price?"  
**Gemini 选择**: `get_crypto_price(coin_id="bitcoin")`

**问题 2**: "Which coins are trending?"  
**Gemini 选择**: `get_trending_coins()`

**问题 3**: "Top 5 cryptocurrencies"  
**Gemini 选择**: `get_market_data(limit=5)`

**代码完全一样**，但工具选择不同！  
→ 证明是 Gemini 决定的，不是代码！

### 实验 3: 修改工具描述，观察变化

**修改工具描述**：

```python
# 原始描述
"description": "Get price when users ask about the price, value, or cost..."

# 修改后
"description": "This tool is ONLY for trending coins"  # 故意写错
```

**结果**：Gemini 不会为 "Bitcoin price" 调用这个工具了！  
→ 证明 Gemini 真的在读描述！

---

## 对比代码决定方式

### gemini_rest.py（代码决定）

```python
# 代码决定用哪个工具
lower_input = user_input.lower()

if "price" in lower_input:
    tool_name = "get_crypto_price"  # ← 代码写死的
    
    if "bitcoin" in lower_input:
        coin_id = "bitcoin"          # ← 代码匹配的
    
    result = await mcp.call_tool(tool_name, {"coin_id": coin_id})
```

### gemini_function_calling.py（AI 决定）

```python
# AI 决定用哪个工具
response = await self._call_gemini(contents, tools=TOOLS)

if "functionCall" in response:
    tool_name = response["functionCall"]["name"]   # ← Gemini 返回的
    tool_args = response["functionCall"]["args"]   # ← Gemini 返回的
    
    result = await mcp.call_tool(tool_name, tool_args)
```

---

## 关键区别

|  | 代码决定 | AI 决定 |
|---|---|---|
| **工具名来源** | `if-else` 硬编码 | Gemini API 响应 |
| **参数来源** | 字符串匹配/正则 | Gemini API 响应 |
| **代码中的逻辑** | 大量 `if` 判断 | 只有一个 `if "functionCall"` |
| **扩展性** | 每个工具要改代码 | 只需添加工具定义 |

---

## 最终证据：API 日志

**如果你有网络抓包工具，可以看到**：

**请求到 Gemini**：
```http
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent
Content-Type: application/json

{
  "contents": [{"role": "user", "parts": [{"text": "Bitcoin price?"}]}],
  "tools": [{
    "function_declarations": [
      {"name": "get_crypto_price", "description": "..."}
    ]
  }]
}
```

**Gemini 响应**：
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "candidates": [{
    "content": {
      "parts": [{
        "functionCall": {
          "name": "get_crypto_price",
          "args": {"coin_id": "bitcoin"}
        }
      }]
    }
  }]
}
```

**代码接收到这个响应，提取出 `functionCall`，然后执行**。

---

## 总结

### AI 自动调用体现在 3 个地方：

1. **工具定义发送给 AI**
   ```python
   payload["tools"] = TOOLS  # 告诉 Gemini 有这些工具
   ```

2. **AI 返回 functionCall**
   ```python
   response["candidates"][0]["content"]["parts"][0]["functionCall"]
   ```

3. **代码被动执行**
   ```python
   function_name = response["functionCall"]["name"]  # 直接用 Gemini 的决定
   ```

### 如果没有 AI：

- 代码中会看到 `if "price" in user_input`
- 工具名会是硬编码的字符串
- 参数会用正则表达式提取

### 有了 AI：

- 代码中只有 `if "functionCall" in response`
- 工具名来自 Gemini 的 JSON 响应
- 参数也来自 Gemini 的 JSON 响应

**这就是真正的 Function Calling！** 🎉

---

## 验证步骤

**你可以自己验证**：

1. 打开 `gemini_function_calling.py`
2. 搜索 `if "price"` → 找不到（没有关键词匹配）
3. 搜索 `"functionCall"` → 找到了（检测 Gemini 的返回）
4. 运行 `python gemini_function_calling.py`，查看输出
5. 观察 "🔧 Gemini chose to call" 这一行

**这就是证据！** ✅

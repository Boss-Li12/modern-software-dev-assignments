# 🎉 最终使用指南

## ✅ 你现在拥有的完整系统

### 1. **MCP 服务器** (运行中)
- 地址: http://localhost:8000
- 3个工具: 价格、热门、市场数据
- 认证: Bearer Token

### 2. **真正的 Gemini Function Calling** ⭐ **推荐**
- 文件: `gemini_function_calling.py`
- Gemini 自己决定调用哪个工具
- 完整的对话历史
- 多轮工具调用支持

### 3. **简化版本** (用于学习)
- `gemini_rest.py` - 代码决定工具
- `gemini_simple.py` - 基础演示

---

## 🚀 立即开始

### 方式 1: 演示模式（推荐入门）

```bash
cd week3/examples
python gemini_function_calling.py
# 输入: 1

# 你会看到 Gemini 自动选择工具：
# 问题 1: What's Bitcoin price?
#   → Gemini 选择: get_crypto_price(coin_id="bitcoin")
#
# 问题 2: Ethereum in euros?
#   → Gemini 选择: get_crypto_price(coin_id="ethereum", vs_currency="eur")
#
# 问题 3: Trending coins?
#   → Gemini 选择: get_trending_coins()
```

### 方式 2: 交互模式（体验完整功能）

```bash
cd week3/examples
python gemini_function_calling.py  
# 输入: 2

# 然后随便问问题！
```

---

## 💬 试试这些问题

### 基础问题
```
You: What's the Bitcoin price?
Gemini: 🔧 chose get_crypto_price(coin_id="bitcoin")
结果: $82,408
```

### 带参数的问题
```
You: Show me Ethereum's price in euros
Gemini: 🔧 chose get_crypto_price(coin_id="ethereum", vs_currency="eur")
结果: 2284.81 EUR
```

### 不同工具
```
You: Which cryptocurrencies are trending?
Gemini: 🔧 chose get_trending_coins()
结果: Bitcoin, Moonbirds, Tether Gold...
```

### 智能理解
```
You: Top 3 by market cap
Gemini: 🔧 chose get_market_data(limit=3)
结果: Bitcoin, Ethereum, Tether
```

---

## 🎯 关键特性

### ✅ Gemini 自主决策
- 看到问题："What's the Bitcoin price?"
- 看到工具定义
- 自己决定用 `get_crypto_price`
- 自己提取参数 `coin_id="bitcoin"`

### ✅ 智能参数提取
```
You: "How much is Solana worth?"
Gemini: 
  - 理解 "how much" = 价格查询
  - 理解 "Solana" = coin_id="solana"
  - 调用 get_crypto_price(coin_id="solana")
```

### ✅ 多语言支持
```
You: "Ethereum价格是多少欧元?"
Gemini:
  - 识别 Ethereum
  - 识别 欧元 = eur
  - 调用 get_crypto_price(coin_id="ethereum", vs_currency="eur")
```

---

## 📊 技术对比

| 功能 | gemini_rest.py | gemini_function_calling.py ⭐ |
|------|---------------|------------------------------|
| **工具选择** | ❌ 代码关键词匹配 | ✅ Gemini AI 决策 |
| **参数提取** | ❌ 代码正则匹配 | ✅ Gemini 理解提取 |
| **扩展性** | ❌ 每个工具需写规则 | ✅ 只需添加工具定义 |
| **复杂问题** | ❌ 无法处理 | ✅ 可以多轮调用 |
| **Function Calling** | ❌ 假的 | ✅ 真的 |
| **推荐使用** | 学习参考 | **生产环境** |

---

## 🎓 学习价值

### 你学到了：

1. **MCP 协议**
   - Tool definitions
   - Request/Response 格式
   - Bearer 认证

2. **Gemini Function Calling**
   - 工具定义格式
   - functionCall/functionResponse
   - 对话历史管理

3. **AI Agent 设计模式**
   - 工具选择
   - 参数提取
   - 结果综合

4. **REST API 集成**
   - Gemini API 调用
   - MCP 服务器调用
   - 错误处理

---

## 📁 项目文件结构

```
week3/
├── server/
│   └── main.py              # MCP 服务器 (运行中)
│
├── examples/
│   ├── gemini_function_calling.py  ⭐ **主文件（推荐）**
│   ├── gemini_rest.py       # 简化版本
│   ├── gemini_simple.py     # 基础演示
│   ├── .env                  # 配置文件
│   └── requirements.txt     # 依赖
│
└── 文档/
    ├── FUNCTION_CALLING_EXPLAINED.md  # Function Calling 详解
    ├── SUCCESS_REPORT.md              # 成功报告
    ├── DEPLOYMENT_GUIDE.md            # 部署指南
    └── COMPLETE_SOLUTION.md           # 完整方案
```

---

## ⚡ 快速命令

### 启动 MCP 服务器（如果没运行）
```bash
cd week3/server
python main.py
```

### 运行 Gemini Function Calling
```bash
cd week3/examples
python gemini_function_calling.py
```

### 查看配置
```bash
cd week3/examples
cat .env
```

---

## 🐛 故障排除

### 问题 1: MCP 服务器没运行
```bash
# 检查服务器
curl http://localhost:8000/health

# 如果失败，启动服务器
cd week3/server
python main.py
```

### 问题 2: Gemini API Key 错误
```bash
# 检查 .env 文件
cd week3/examples
cat .env | grep GEMINI_API_KEY

# 应该看到:
# GEMINI_API_KEY=AIzaSy...
```

### 问题 3: 429 限流错误
```
原因: Gemini 免费套餐限流 (15 RPM)
解决: 等待 1-2 分钟后重试
代码已自动添加 3 秒延迟
```

---

## 💡 进阶使用

### 1. 多轮对话
```python
# 交互模式支持上下文
You: What's the Bitcoin price?
Gemini: $82,408

You: And Ethereum?  # Gemini 记得是在问价格
Gemini: 🔧 chose get_crypto_price(coin_id="ethereum")
```

### 2. 重置对话
```python
# 交互模式中
You: reset
# 清除历史，开始新对话
```

### 3. 查看工具选择
```python
# 每次都会显示
🔧 Gemini chose to call: get_crypto_price
   with arguments: {
  "coin_id": "bitcoin"
}
```

---

## 🎯 下一步建议

### 本周：
1. ✅ 试用所有问题示例
2. ✅ 阅读 FUNCTION_CALLING_EXPLAINED.md
3. ✅ 理解工具定义格式

### 下周：
1. 添加新工具（如：新闻、历史价格）
2. 支持中文对话
3. 添加错误恢复机制

### 未来：
1. 创建 Web 界面
2. 部署到 Vercel
3. 添加用户认证

---

## 🎉 总结

你现在拥有一个**完整的、生产就绪的** AI Agent 系统：

✅ **MCP 服务器** - 提供加密货币数据  
✅ **Gemini Function Calling** - AI 自主决策工具使用  
✅ **完整文档** - 包含原理和使用说明  
✅ **可扩展架构** - 轻松添加新工具

**这是真正的 Function Calling，Gemini 自己决定调用哪个工具！** 🚀

---

## 🎊 立即开始体验

```bash
cd week3/examples
python gemini_function_calling.py
```

选择模式，然后看 Gemini 如何智能地选择工具吧！

**祝你使用愉快！** 🌟

# 🚀 部署到 Vercel 和 Gemini 集成指南

## 📋 方案一：部署到 Vercel（免费）

Vercel 提供免费的 serverless 部署，每月有充足的免费额度。

### 第一步：安装 Vercel CLI

```bash
# 使用 npm 安装（需要先安装 Node.js）
npm install -g vercel

# 或使用 yarn
yarn global add vercel
```

### 第二步：登录 Vercel

```bash
vercel login
```

这会打开浏览器让你登录（支持 GitHub、GitLab、Bitbucket 账号）。

### 第三步：准备部署

确保你在 `week3/` 目录下：

```bash
cd /Users/boss_li12/Desktop/file/project_playground/modern-software-dev-assignments/week3
```

### 第四步：部署

```bash
# 首次部署
vercel

# 按照提示操作：
# 1. Setup and deploy? [Y/n] → Y
# 2. Which scope? → 选择你的账号
# 3. Link to existing project? [y/N] → N
# 4. What's your project's name? → crypto-mcp-server（或其他名字）
# 5. In which directory is your code located? → ./
# 6. Want to override the settings? [y/N] → N

# 部署到生产环境
vercel --prod
```

### 第五步：配置环境变量

部署后，需要在 Vercel 后台设置环境变量：

#### 方法 1：通过命令行

```bash
# 生成一个安全的 API key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 设置环境变量（将 <your-secret-key> 替换为上面生成的 key）
vercel env add MCP_API_KEY
# 输入 key 后按回车
# 选择环境：Production, Preview, Development → 选择 Production

# 重新部署以应用环境变量
vercel --prod
```

#### 方法 2：通过 Vercel 仪表板

1. 访问 https://vercel.com/dashboard
2. 找到你的项目 `crypto-mcp-server`
3. 进入 **Settings** → **Environment Variables**
4. 添加变量：
   - **Name**: `MCP_API_KEY`
   - **Value**: `your-secure-api-key`
   - **Environment**: Production
5. 点击 **Save**
6. 重新部署项目

### 第六步：获取部署 URL

部署成功后，你会得到一个 URL，类似：

```
https://crypto-mcp-server-xxx.vercel.app
```

### 第七步：测试部署

```bash
# 测试健康检查
curl https://crypto-mcp-server-xxx.vercel.app/health

# 测试工具列表
curl -X POST https://crypto-mcp-server-xxx.vercel.app/mcp/list-tools \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json"

# 测试工具调用
curl -X POST https://crypto-mcp-server-xxx.vercel.app/mcp/call-tool \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_crypto_price",
    "arguments": {"coin_id": "bitcoin"}
  }'
```

---

## 🤖 方案二：集成 Gemini Pro

现在服务器已部署，让我们创建 Gemini Pro 集成。

### Gemini API 集成原理

Gemini API 支持两种工具调用方式：
1. **Function Calling** - 类似 OpenAI，Gemini 决定何时调用函数
2. **Manual Tool Use** - 手动解析 Gemini 的响应并调用工具

### 安装 Gemini SDK

```bash
pip install google-generativeai
```

### Gemini 集成代码

查看 `examples/gemini_integration.py` 文件（我接下来会创建）。

### 使用步骤

1. **获取 Gemini API Key**：
   - 访问 https://makersuite.google.com/app/apikey
   - 点击 "Get API key" 或 "Create API key"
   - 创建新的 API key 或使用现有的

2. **设置环境变量**：
   ```bash
   export GEMINI_API_KEY="your-gemini-api-key"
   export MCP_SERVER_URL="https://crypto-mcp-server-xxx.vercel.app"
   export MCP_API_KEY="your-mcp-api-key"
   ```

3. **运行集成示例**：
   ```bash
   cd week3/examples
   python gemini_integration.py
   ```

---

## 🎯 完整工作流程

```
用户: "比特币现在多少钱？"
  ↓
Gemini Pro API
  ↓
看到可用的 function declarations
  ↓
决定调用 get_crypto_price 函数
  ↓
你的代码接收到 function call
  ↓
调用 Vercel 上的 MCP 服务器
  ↓
MCP 服务器调用 CoinGecko API
  ↓
返回数据到 Gemini
  ↓
Gemini 生成自然语言回复
  ↓
"比特币当前价格是 $82,777，在过去24小时下跌了 5.76%"
```

---

## 💰 成本估算

### Vercel 免费额度（每月）
- ✅ 100GB 带宽
- ✅ 100GB-Hours 函数执行时间
- ✅ 无限请求数
- ✅ 自动 HTTPS
- ✅ 全球 CDN

**结论**: 对于个人使用和学习完全免费！

### Gemini API 免费额度
- ✅ 每分钟 15 次请求
- ✅ 每天 1500 次请求
- ✅ 每分钟 100 万 tokens

**结论**: 学习和开发阶段完全够用！

---

## 🔒 安全建议

### 1. API Key 管理

**不要**将 API key 硬编码在代码中！

**正确做法**：
```python
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MCP_API_KEY = os.getenv("MCP_API_KEY")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")
```

### 2. 环境变量配置

创建 `.env` 文件（已在 .gitignore 中）：

```bash
# .env
GEMINI_API_KEY=your-gemini-api-key
MCP_SERVER_URL=https://crypto-mcp-server-xxx.vercel.app
MCP_API_KEY=your-mcp-api-key
```

加载环境变量：

```python
from dotenv import load_dotenv
load_dotenv()
```

### 3. 速率限制

建议在客户端实现速率限制：

```python
import time
from functools import wraps

def rate_limit(calls_per_minute=15):
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            
            result = await func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator
```

---

## 🐛 故障排除

### 问题 1: Vercel 部署失败

**可能原因**: Python 版本不兼容

**解决方案**: 创建 `runtime.txt` 文件：
```
python-3.10
```

### 问题 2: 环境变量未生效

**解决方案**: 
1. 检查环境变量名称是否正确
2. 重新部署：`vercel --prod`
3. 查看 Vercel 日志：`vercel logs`

### 问题 3: CORS 错误

**解决方案**: 已在 `main.py` 中配置 CORS 中间件

### 问题 4: Gemini API 超时

**解决方案**: 增加超时时间：
```python
response = model.generate_content(
    ...,
    request_options={"timeout": 60}
)
```

---

## 📚 相关资源

- **Vercel 文档**: https://vercel.com/docs
- **Gemini API 文档**: https://ai.google.dev/docs
- **CoinGecko API**: https://www.coingecko.com/en/api/documentation
- **MCP 协议**: https://modelcontextprotocol.io

---

## ✅ 检查清单

部署前确认：
- [ ] Node.js 已安装
- [ ] Vercel CLI 已安装并登录
- [ ] 已生成安全的 API key
- [ ] `.gitignore` 包含 `.env` 文件

Gemini 集成前确认：
- [ ] 已获取 Gemini API key
- [ ] 已部署 MCP 服务器到 Vercel
- [ ] 已安装 `google-generativeai` 包
- [ ] 已设置环境变量

---

## 🎉 完成！

现在你可以：
1. ✅ 在任何地方访问你的 MCP 服务器
2. ✅ 使用 Gemini Pro 调用加密货币数据
3. ✅ 构建自己的 AI 应用

**下一步建议**：
- 添加更多工具
- 实现缓存层
- 添加使用统计
- 创建 Web 界面

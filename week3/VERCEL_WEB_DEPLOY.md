# 🚀 通过网页部署到 Vercel（无需 CLI）

## 方法 1: GitHub + Vercel（推荐，最简单）

### 步骤 1: 推送代码到 GitHub

```bash
cd /Users/boss_li12/Desktop/file/project_playground/modern-software-dev-assignments

# 初始化 git （如果还没有）
git init

# 添加所有文件
git add week3/

# 提交
git commit -m "Add Week 3 MCP Server with Gemini integration"

# 创建 GitHub 仓库后，添加远程仓库
git remote add origin https://github.com/你的用户名/your-repo.git

# 推送
git push -u origin main
```

### 步骤 2: 通过 Vercel 导入项目

1. **访问** https://vercel.com/
2. **登录** 使用 GitHub 账号
3. **点击** "Add New" → "Project"
4. **导入** 你的 GitHub 仓库
5. **配置项目**:
   - **Root Directory**: `week3`
   - **Framework Preset**: Other
   - **Build Command**: 留空
   - **Output Directory**: `.`

### 步骤 3: 设置环境变量

在 Vercel 项目设置中：

1. 点击 **Settings** → **Environment Variables**
2. 添加环境变量:
   - **Name**: `MCP_API_KEY`
   - **Value**: `o1IWi6Y2CzTdj0sqSqv_mh8TjhoPzv3vNRs6n6RqqDE`
   - **Environment**: Production
3. 点击 **Save**

### 步骤 4: 部署

点击 **Deploy** 按钮，Vercel 会自动部署！

几分钟后，你会得到一个 URL，例如：
```
https://modern-software-dev-assignments-xxx.vercel.app
```

---

## 方法 2: 本地使用（跳过部署）

如果你暂时不想部署到 Vercel，可以直接使用本地服务器：

### 你的 MCP 服务器已经在运行！

```bash
# 服务器地址
http://localhost:8000

# API Key
demo-key-12345
```

直接进入下一部分：配置 Gemini！

---

## 下一步：配置 Gemini API

无论你选择哪种部署方式，都可以继续配置 Gemini。

查看: **GEMINI_SETUP.md**

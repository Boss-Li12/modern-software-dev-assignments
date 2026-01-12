# Week 1 - LLM Prompting 六大技巧总结

## 技巧一览表

| 技巧 | 核心思想 | 适用场景 | 复杂度 |
|------|---------|---------|--------|
| K-Shot Prompting | 给示例让模型模仿 | 模式识别、格式转换 | ⭐ |
| Chain-of-Thought | 引导逐步推理 | 数学、逻辑推理 | ⭐⭐ |
| Tool Calling | 输出结构化工具调用 | 与外部系统交互 | ⭐⭐ |
| Self-Consistency | 多次采样+投票 | 需要高可靠性的任务 | ⭐⭐ |
| RAG | 检索文档+生成 | 需要外部知识的任务 | ⭐⭐⭐ |
| Reflexion | 从错误中学习改进 | 代码生成、迭代优化 | ⭐⭐⭐ |

---

## 1. K-Shot Prompting（少样本提示）

### 问题描述
让模型反转字符串 `httpstatus` → `sutatsptth`，但模型直接处理时经常出错。

### 解决路径
```
问题 → 提供多个输入→输出示例 → 模型学会模式 → 正确输出
```

### Prompt 结构
```
You reverse strings character by character. Read the input from right to left.

Example 1:
Input: cat
Characters from right to left: t, a, c
Output: tac

Example 2:
Input: httpstatus
Characters from right to left: s, u, t, a, t, s, p, t, t, h
Output: sutatsptth

[更多示例...]
```

### 核心要点
- **示例要贴近实际任务** - 复杂度应接近真实输入
- **展示推理过程** - 不仅给结果，还展示如何得到结果
- **格式一致** - 每个示例遵循相同格式

---

## 2. Chain-of-Thought（思维链）

### 问题描述
计算 `3^12345 (mod 100) = 43`，这需要用数学技巧（欧拉定理），大模型不直接思考容易出错。

### 解决路径
```
问题 → 提供解题步骤框架 → 模型逐步推理 → 正确答案
```

### Prompt 结构
```
You are a mathematician who solves problems step by step.

For modular exponentiation problems like a^n (mod m), follow these steps:

Step 1: Use Euler's theorem. Calculate φ(m).
Step 2: By Euler's theorem, a^φ(m) ≡ 1 (mod m).
Step 3: Reduce the exponent: n mod φ(m).
Step 4: Calculate a^(n mod φ(m)) mod m.
Step 5: State the final answer as "Answer: <number>".

Think step by step and show all your work.
```

### 核心要点
- **"Let's think step by step"** - 触发逐步推理
- **提供解题框架** - 告诉模型应该怎么分步
- **减少跳步** - 每一步都要求展示

---

## 3. Tool Calling（工具调用）

### 问题描述
让模型调用 `output_every_func_return_type()` 函数来分析 Python 文件。

### 解决路径
```
描述可用工具 → 定义调用格式 → 模型输出 JSON → 程序解析执行
```

### Prompt 结构
```
You have access to the following tool:

Tool name: output_every_func_return_type
Description: Analyzes a Python file and returns function return types.
Parameters:
  - file_path (string, optional): Path to the Python file.

When asked to call a tool, respond ONLY with JSON:
{"tool": "<tool_name>", "args": {"param1": "value1"}}

Example:
{"tool": "output_every_func_return_type", "args": {"file_path": ""}}
```

### 核心要点
- **模型只输出 JSON** - 不执行任何代码
- **程序解析并执行** - 你的代码负责真正调用函数
- **格式必须严格** - 否则解析会失败

### 工作流程图
```
┌─────────┐      JSON 文本      ┌─────────┐      执行      ┌─────────┐
│  LLM    │  ───────────────►  │ 你的代码 │  ─────────►  │  工具   │
└─────────┘                     └─────────┘               └─────────┘
     │                               │
     │ {"tool": "xxx",               │ 解析 JSON
     │  "args": {...}}               │ 调用真正的函数
     ▼                               ▼
```

---

## 4. Self-Consistency（自洽性）

### 问题描述
Henry 的60英里自行车之旅，两次停留之间走了多少英里？需要高可靠性答案。

### 解决路径
```
问题 → 多次独立推理（高温度）→ 收集所有答案 → 多数投票 → 最可靠答案
```

### Prompt 结构
```
You are a careful math problem solver. Solve problems step by step.

For distance problems, follow these steps:
1. Identify the total distance
2. Identify each position/location mentioned
3. Calculate the distance between positions by subtraction
4. Double-check your arithmetic

Example:
Problem: A 100-mile road has markers at mile 30 and mile 80. Distance between them?
Step 1: First marker at mile 30
Step 2: Second marker at mile 80  
Step 3: Distance = 80 - 30 = 50 miles
Answer: 50
```

### 核心要点
- **高温度采样** - `temperature=1` 产生多样性
- **多次运行** - 本例运行5次
- **投票机制** - 选择出现最多的答案

### 与 Chain-of-Thought 对比

| 特性 | Chain-of-Thought | Self-Consistency |
|------|-----------------|------------------|
| 运行次数 | 1次 | 多次（5次+） |
| 温度 | 低（0.3） | 高（1.0） |
| 答案选择 | 直接取 | 投票 |
| 可靠性 | 一般 | 更高 |

---

## 5. RAG（检索增强生成）

### 问题描述
根据 API 文档生成 `fetch_user_name()` 函数，需要用到外部知识。

### 解决路径
```
问题 → 检索相关文档 → 文档 + 问题一起输入 LLM → 基于文档生成
```

### 两个关键组件

**1. Context Provider（检索器）**
```python
def YOUR_CONTEXT_PROVIDER(corpus: List[str]) -> List[str]:
    # 返回相关文档
    return corpus  # 包含 api_docs.txt
```

**2. System Prompt（生成器指导）**
```
You are a Python developer who writes code based strictly on provided documentation.

Rules:
1. Use ONLY the information from the provided context/documentation
2. Do not make up or assume any API endpoints, URLs, or authentication methods
3. Follow the exact API specification given in the documentation
```

### 核心要点
- **不要编造** - 只用文档提供的信息
- **减少幻觉** - 有据可查
- **可更新** - 更换文档即可更新知识

### RAG 流程图
```
┌─────────────┐     检索     ┌─────────────┐     增强     ┌─────────────┐
│  用户问题   │  ────────►  │  知识库     │  ────────►  │  LLM 生成   │
└─────────────┘              └─────────────┘              └─────────────┘
                                   │
                                   │ api_docs.txt:
                                   │ Base URL: https://...
                                   │ GET /users/{id}
                                   │ Header: X-API-Key
                                   ▼
```

---

## 6. Reflexion（反思）

### 问题描述
生成 `is_valid_password()` 函数，初次生成可能不完整，需要迭代改进。

### 解决路径
```
生成初始代码 → 运行测试 → 失败 → 反馈错误给 LLM → 改进代码 → 成功
```

### 两个关键组件

**1. Reflexion Prompt**
```
You are a coding assistant that improves code based on test failures.

You will receive:
1. The previous implementation that failed some tests
2. A list of test failures with diagnostic information

Your task:
1. Analyze what went wrong based on the failure messages
2. Fix the implementation to pass all tests
```

**2. Context Builder**
```python
def your_build_reflexion_context(prev_code: str, failures: List[str]) -> str:
    failure_list = "\n".join(f"- {f}" for f in failures)
    return f"""Previous implementation that failed:
```python
{prev_code}
```

Test failures:
{failure_list}

Please fix the implementation to pass all tests.
"""
```

### 实际运行过程

```
┌──────────────────────────────────────────────────────────────────┐
│ 初始生成：                                                        │
│ def is_valid_password(password):                                  │
│     return len(password) >= 8 and any(c.isalpha() ...) ❌        │
├──────────────────────────────────────────────────────────────────┤
│ 测试失败：                                                        │
│ - password1! → missing uppercase                                  │
│ - Password1 → missing special                                     │
├──────────────────────────────────────────────────────────────────┤
│ 反思后改进：                                                      │
│ def is_valid_password(password):                                  │
│     return (len(password) >= 8                                    │
│             and any(c.islower() for c in password)  # 新增        │
│             and any(c.isupper() for c in password)  # 新增        │
│             and any(c.isdigit() for c in password)                │
│             and any(c in '!@#$%^&*()-_' ...))       # 新增 ✅    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 技巧对比矩阵

| 维度 | K-Shot | CoT | Tool | Self-Con | RAG | Reflexion |
|------|--------|-----|------|----------|-----|-----------|
| **知识来源** | 示例 | 无 | 无 | 无 | 外部文档 | 错误反馈 |
| **运行次数** | 1 | 1 | 1 | 多次 | 1 | 2+ |
| **需要外部系统** | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ |
| **适合推理** | ❌ | ✅ | ❌ | ✅ | ❌ | ✅ |
| **适合创作** | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ |
| **可迭代** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 如何选择技巧？

```
                    ┌─────────────────────────────────┐
                    │       你的任务是什么？           │
                    └─────────────┬───────────────────┘
                                  │
            ┌─────────────────────┼─────────────────────┐
            │                     │                     │
            ▼                     ▼                     ▼
    ┌───────────────┐    ┌───────────────┐    ┌───────────────┐
    │ 格式转换/模仿 │    │ 数学/逻辑推理 │    │ 需要外部知识  │
    └───────┬───────┘    └───────┬───────┘    └───────┬───────┘
            │                    │                    │
            ▼                    ▼                    ▼
       K-Shot              Chain-of-Thought         RAG
                                  │
                                  │ 需要更高可靠性？
                                  ▼
                           Self-Consistency

    ┌───────────────┐    ┌───────────────┐
    │ 调用外部工具  │    │ 需要迭代改进  │
    └───────┬───────┘    └───────┬───────┘
            │                    │
            ▼                    ▼
      Tool Calling           Reflexion
```

---

## 总结

1. **K-Shot**: 给模型看示例 → 模型模仿
2. **CoT**: 让模型慢慢想 → 减少推理错误
3. **Tool Calling**: 让模型决定调用什么 → 程序执行
4. **Self-Consistency**: 问多次 → 投票选最佳
5. **RAG**: 先找资料 → 再回答
6. **Reflexion**: 试错 → 反思 → 改进

这六种技巧可以组合使用，根据具体任务灵活选择！

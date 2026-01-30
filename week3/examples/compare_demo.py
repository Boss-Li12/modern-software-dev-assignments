"""
对比演示：代码决定 vs AI 决定

运行这个文件可以看到两种方式的区别
"""

import asyncio


# ==================== 方式 1: 代码决定（错误） ====================

async def code_decides_wrong_way(user_input: str):
    """❌ 错误方式：代码通过关键词匹配决定调用哪个工具"""
    
    print("=" * 60)
    print("❌ 方式 1: 代码决定")
    print("=" * 60)
    print(f"用户输入: {user_input}")
    print()
    
    # 代码分析关键词
    lower_input = user_input.lower()
    
    # ❌ 代码决定用哪个工具
    if "price" in lower_input or "cost" in lower_input:
        tool_name = "get_crypto_price"
        print("✓ 代码检测到关键词 'price'")
        print(f"✓ 代码决定使用工具: {tool_name}")
        
        # ❌ 代码提取参数
        if "bitcoin" in lower_input:
            coin_id = "bitcoin"
        elif "ethereum" in lower_input:
            coin_id = "ethereum"
        else:
            coin_id = "unknown"
        
        print(f"✓ 代码提取参数: coin_id={coin_id}")
        
        # ❌ 代码检测货币
        if "euro" in lower_input or "eur" in lower_input:
            vs_currency = "eur"
        else:
            vs_currency = "usd"
        
        print(f"✓ 代码提取参数: vs_currency={vs_currency}")
        
    elif "trending" in lower_input:
        tool_name = "get_trending_coins"
        print("✓ 代码检测到关键词 'trending'")
        print(f"✓ 代码决定使用工具: {tool_name}")
        
    elif "top" in lower_input:
        tool_name = "get_market_data"
        print("✓ 代码检测到关键词 'top'")
        print(f"✓ 代码决定使用工具: {tool_name}")
        
    else:
        tool_name = "unknown"
        print("✗ 代码无法识别意图")
    
    print()
    print("总结：")
    print("  - 工具选择: ❌ 代码的 if-else 决定")
    print("  - 参数提取: ❌ 代码的字符串匹配")
    print("  - AI 参与度: ❌ 0%")
    print()


# ==================== 方式 2: AI 决定（正确） ====================

async def ai_decides_correct_way(user_input: str):
    """✅ 正确方式：AI 看工具描述，自己决定"""
    
    print("=" * 60)
    print("✅ 方式 2: AI 决定（Gemini Function Calling）")
    print("=" * 60)
    print(f"用户输入: {user_input}")
    print()
    
    # 1. 定义工具（给 AI 看的）
    tools = [
        {
            "name": "get_crypto_price",
            "description": "Get price when users ask about price, cost, or value of a cryptocurrency",
            "parameters": {
                "coin_id": {"type": "string", "description": "Coin ID like 'bitcoin', 'ethereum'"},
                "vs_currency": {"type": "string", "description": "Currency code like 'usd', 'eur'"}
            }
        },
        {
            "name": "get_trending_coins",
            "description": "Get trending coins when users ask about trending, hot, or popular coins"
        },
        {
            "name": "get_market_data",
            "description": "Get top coins ranked by market cap when users ask about top or best coins"
        }
    ]
    
    print("步骤 1: 代码准备工具定义")
    print(f"  可用工具: {[t['name'] for t in tools]}")
    print()
    
    # 2. 模拟发送给 Gemini
    print("步骤 2: 发送给 Gemini")
    payload = {
        "contents": [{"text": user_input}],
        "tools": tools  # ← 告诉 Gemini 有这些工具
    }
    print(f"  发送内容:")
    print(f"    - 用户问题: '{user_input}'")
    print(f"    - 可用工具数: {len(tools)}")
    print()
    
    # 3. 模拟 Gemini 的思考过程
    print("步骤 3: Gemini 的思考过程（在 Google 服务器上）")
    print("  Gemini 分析:")
    print(f"    1. 用户问题: '{user_input}'")
    print(f"    2. 查看工具描述:")
    
    for tool in tools:
        print(f"       - {tool['name']}: {tool['description'][:50]}...")
    
    # 模拟 Gemini 的决定
    if "price" in user_input.lower():
        chosen_tool = "get_crypto_price"
        print(f"    3. 匹配: 用户问 price → {chosen_tool} 工具描述提到 price")
        print(f"    4. 提取参数:")
        
        if "ethereum" in user_input.lower():
            coin_id = "ethereum"
        else:
            coin_id = "bitcoin"
        print(f"       - coin_id: 从 '{user_input}' 提取出 '{coin_id}'")
        
        if "euro" in user_input.lower():
            vs_currency = "eur"
        else:
            vs_currency = "usd"
        print(f"       - vs_currency: 从 '{user_input}' 推断出 '{vs_currency}'")
        
        function_args = {"coin_id": coin_id, "vs_currency": vs_currency}
    
    elif "trending" in user_input.lower():
        chosen_tool = "get_trending_coins"
        print(f"    3. 匹配: 用户问 trending → {chosen_tool} 工具描述提到 trending")
        function_args = {}
    
    else:
        chosen_tool = "get_market_data"
        print(f"    3. 匹配: 默认使用 {chosen_tool}")
        function_args = {"limit": 10}
    
    print()
    
    # 4. 模拟 Gemini 返回
    print("步骤 4: Gemini 返回 functionCall")
    gemini_response = {
        "candidates": [{
            "content": {
                "parts": [{
                    "functionCall": {
                        "name": chosen_tool,      # ← Gemini 选的工具
                        "args": function_args     # ← Gemini 提取的参数
                    }
                }]
            }
        }]
    }
    print(f"  Gemini 决定:")
    print(f"    tool: {chosen_tool}")
    print(f"    args: {function_args}")
    print()
    
    # 5. 代码执行 Gemini 的决定
    print("步骤 5: 代码执行 Gemini 的决定")
    function_call = gemini_response["candidates"][0]["content"]["parts"][0]["functionCall"]
    tool_name = function_call["name"]    # ← 直接用 Gemini 返回的
    tool_args = function_call["args"]    # ← 直接用 Gemini 返回的
    
    print(f"  代码调用: {tool_name}({tool_args})")
    print()
    
    print("总结：")
    print("  - 工具选择: ✅ Gemini 根据描述决定")
    print("  - 参数提取: ✅ Gemini 理解语义提取")
    print("  - AI 参与度: ✅ 100%")
    print()


# ==================== 对比演示 ====================

async def compare_both_ways():
    """对比两种方式"""
    
    test_inputs = [
        "What's the Bitcoin price?",
        "Show me Ethereum's price in euros",
        "Which cryptocurrencies are trending?",
    ]
    
    for user_input in test_inputs:
        print("\n" + "🔷" * 30)
        print(f"\n测试输入: \"{user_input}\"\n")
        
        # 方式 1: 代码决定
        await code_decides_wrong_way(user_input)
        
        # 方式 2: AI 决定
        await ai_decides_correct_way(user_input)
        
        print("🔷" * 30 + "\n")


# ==================== 关键差异总结 ====================

def print_key_differences():
    """打印关键差异"""
    
    print("\n" + "=" * 70)
    print("📊 关键差异总结")
    print("=" * 70)
    print()
    
    print("┌─────────────────┬──────────────────────┬──────────────────────┐")
    print("│      特性       │    ❌ 代码决定       │    ✅ AI 决定        │")
    print("├─────────────────┼──────────────────────┼──────────────────────┤")
    print("│ 工具选择方式    │ if-else 关键词匹配   │ AI 读描述自己决定    │")
    print("│ 参数提取方式    │ 字符串查找/正则      │ AI 语义理解提取      │")
    print("│ 代码中的判断    │ 大量 if-else         │ 几乎没有            │")
    print("│ 扩展性          │ 每个工具要改代码     │ 只需添加工具定义     │")
    print("│ 处理复杂问题    │ 无法处理            │ 可以理解复杂语义     │")
    print("│ 多语言支持      │ 每种语言要写规则     │ 自动支持            │")
    print("│ Function Calling│ 假的                │ 真的                │")
    print("└─────────────────┴──────────────────────┴──────────────────────┘")
    print()
    
    print("证明 AI 决定的关键代码：")
    print("```python")
    print("# 方式 1: 代码决定")
    print("if 'price' in user_input:")
    print("    tool_name = 'get_crypto_price'  # ← 代码硬编码")
    print()
    print("# 方式 2: AI 决定")
    print("response = gemini.call(user_input, tools=TOOLS)")
    print("tool_name = response['functionCall']['name']  # ← Gemini 返回的")
    print("```")
    print()


if __name__ == "__main__":
    print("\n🎯 Function Calling 对比演示\n")
    
    asyncio.run(compare_both_ways())
    
    print_key_differences()
    
    print("\n💡 结论:")
    print("  在 gemini_function_calling.py 中:")
    print("  - 代码没有 if-else 判断工具")
    print("  - 代码没有正则提取参数")
    print("  - 工具名和参数都来自 Gemini 的 functionCall 返回")
    print("  - 这就是真正的 AI 自动调用！🎉")
    print()

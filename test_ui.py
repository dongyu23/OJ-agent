from playwright.sync_api import sync_playwright

def test_oj_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("1. 导航到 http://localhost:5001")
        page.goto('http://localhost:5001')
        
        print("2. 等待页面完全加载 (networkidle)")
        page.wait_for_load_state('networkidle')
        
        print("3. 检查页面元素")
        title = page.title()
        print(f"   页面标题: {title}")
        
        # 验证编辑器是否渲染
        print("4. 验证编辑器加载状态")
        page.wait_for_selector('.monaco-editor')
        print("   Monaco Editor 加载成功")
        
        # 验证输入框交互
        print("5. 测试聊天输入框")
        chat_input = page.locator('#chat-input')
        chat_input.fill("测试消息: 你好，请帮我分析时间复杂度")
        
        # 截取发送前的状态
        page.screenshot(path='/workspace/pre_send.png')
        print("   已保存发送前截图 pre_send.png")
        
        print("6. 点击发送按钮")
        send_btn = page.locator('#send-btn')
        send_btn.click()
        
        # 等待发送按钮状态改变（应该会变 disabled）
        page.wait_for_selector('#send-btn[disabled]', timeout=2000)
        print("   发送按钮已进入 disabled 状态 (防重复提交生效)")
        
        print("7. 等待 AI 回复...")
        # 等待意图识别框出现
        page.wait_for_selector('.intent-box', timeout=10000)
        print("   收到意图分析结果 (Intent Box 显示成功)")
        
        # 等待回复气泡出现（新的气泡）
        page.wait_for_selector('.ai-message .msg-bubble', timeout=15000)
        print("   收到 AI 回复内容")
        
        # 等待输入框恢复可用状态（等待 AI 回复结束）
        page.wait_for_selector('#send-btn:not([disabled])', timeout=30000)
        print("   AI 回复完成，发送按钮恢复可用状态")
        
        # 截取发送后的状态
        page.screenshot(path='/workspace/post_send.png', full_page=True)
        print("   已保存发送后截图 post_send.png")
        
        # 获取最新的聊天记录
        last_msg = page.locator('.ai-message .msg-bubble').last.text_content()
        print(f"   AI 最终回复摘要: {last_msg[:100]}...")
        
        print("8. 测试结束，所有 UI 交互正常。")
        browser.close()

if __name__ == '__main__':
    test_oj_ui()

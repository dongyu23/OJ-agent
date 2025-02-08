import streamlit as st
import requests
import json
from typing import Dict, Any

# 设置页面配置
st.set_page_config(
    page_title="AI编程助手",
    page_icon="🤖",
    layout="wide"
)

# 设置API URL
API_URL = "http://localhost:5001/api"

def send_request(query: str, problem_content: str, editor_code: str) -> Dict[str, Any]:
    """发送请求到API服务器"""
    try:
        # 检查API健康状态
        health_response = requests.get(f"{API_URL}/health")
        health_response.raise_for_status()
        
        # 准备请求数据
        data = {
            "query": query,
            "problem_content": problem_content,
            "editor_code": editor_code
        }
        
        # 发送分析请求
        response = requests.post(f"{API_URL}/analyze", json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API请求错误: {str(e)}")
        return {}

def main():
    # 标题
    st.title("🤖 AI编程助手")
    st.markdown("基于camel-ai多智能体框架的智能编程助手系统")

    # 创建两列布局
    left_col, right_col = st.columns([3, 2])

    with left_col:
        # 输入区域
        st.subheader("📝 输入区域")
        
        # 默认的问题描述
        default_problem = """小S有一个由字符 'U' 和 'C' 组成的字符串 S，并希望在编辑距离不超过给定值 m 的条件下，尽可能多地在字符串中找到 "UCC" 子串。

编辑距离定义为将字符串 S 转化为其他字符串时所需的最少编辑操作次数。允许的每次编辑操作是插入、删除或替换单个字符。你需要计算在给定的编辑距离限制 m 下，能够包含最多 "UCC" 子串的字符串可能包含多少个这样的子串。

例如，对于字符串"UCUUCCCCC"和编辑距离限制m = 3，可以通过编辑字符串生成最多包含3个"UCC"子串的序列。

约束条件：
字符串长度不超过1000

测试样例
样例1：
输入：m = 3,s = "UCUUCCCCC"
输出：3

样例2：
输入：m = 6,s = "U"
输出：2

样例3：
输入：m = 2,s = "UCCUUU"
输出：2

解释
样例1：可以将字符串修改为 "UCCUCCUCC"（2 次替换操作，不超过给定值 m = 3），包含 3 个 "UCC" 子串。
样例2：后面插入 5 个字符 "CCUCC"（5 次插入操作，不超过给定值 m = 6），可以将字符串修改为 "UCCUCC"，包含 2 个 "UCC" 子串。
样例3：替换最后 2 个字符，可以将字符串修改为 "UCCUCC"，包含 2 个 "UCC" 子串。"""
        
        # 题目内容
        problem_content = st.text_area(
            "题目内容",
            value=default_problem,
            height=200,
            key="problem_content"
        )
        
        # 默认的代码模板
        default_code = """def solution(m: int, s: str) -> int:
    # PLEASE DO NOT MODIFY THE FUNCTION SIGNATURE
    # write code here
    pass

if __name__ == '__main__':
    print(solution(m=3, s="UCUUCCCCC") == 3)
    print(solution(m=6, s="U") == 2)
    print(solution(m=2, s="UCCUUU") == 2)"""
        
        # 代码编辑器
        editor_code = st.text_area(
            "代码编辑器",
            value=default_code,
            height=200,
            key="editor_code"
        )
        
        # 用户问题输入
        query = st.text_input(
            "你的问题",
            placeholder="输入你的问题，比如：这段代码的时间复杂度是多少？",
            key="query"
        )

        # 发送按钮
        if st.button("发送请求", type="primary"):
            if not query:
                st.warning("请输入问题")
                return
                
            with st.spinner("正在处理请求..."):
                result = send_request(query, problem_content, editor_code)
                
                if result:
                    # 存储结果到session_state
                    st.session_state.last_result = result
                    # 触发右侧更新
                    st.session_state.should_update = True
                    st.rerun()

    with right_col:
        # 结果显示区域
        st.subheader("📊 结果展示")
        
        if hasattr(st.session_state, 'last_result') and st.session_state.last_result:
            result = st.session_state.last_result
            
            # 意图识别结果
            with st.expander("🎯 意图识别结果", expanded=True):
                st.markdown(f"""
                - **识别的意图**: {result.get('intent', '未知')}
                - **是否安全**: {'✅ 安全' if result.get('safe') else '❌ 不安全'}
                - **处理动作**: {result.get('action', '未知')}
                - **需要代码**: {'是' if result.get('need_code') else '否'}
                """)
                st.markdown(f"**响应**: {result.get('response', '')}")
            
            # 任务执行结果
            if result.get('task_success') is not None:
                with st.expander("🛠️ 任务执行结果", expanded=True):
                    st.markdown(f"""
                    - **执行状态**: {'✅ 成功' if result.get('task_success') else '❌ 失败'}
                    """)
                    st.markdown(f"**执行响应**: {result.get('task_response', '')}")
            
            # 预测的问题
            predicted_questions = result.get('predicted_questions', [])
            if predicted_questions:
                with st.expander("🔮 预测的后续问题", expanded=True):
                    for i, pred in enumerate(predicted_questions, 1):
                        st.markdown(f"{i}. {pred.get('question', '')}")
                        if st.button(f"使用问题 {i}", key=f"use_q_{i}"):
                            st.session_state.query = pred.get('question', '')
                            st.rerun()

if __name__ == "__main__":
    main()

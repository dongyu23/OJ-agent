import streamlit as st
import requests
import json
import logging
from typing import Optional, Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API配置
API_URL = "http://localhost:5001"

def create_response_containers():
    """创建用于显示响应的容器"""
    if "response_containers" not in st.session_state:
        st.session_state.response_containers = {
            "intent": st.empty(),
            "task": st.empty(),
            "questions": st.empty()
        }
    return st.session_state.response_containers

def process_stream_response(response: requests.Response, containers: Dict):
    """处理流式响应"""
    intent_shown = False
    task_response = ""
    
    try:
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        
                        # 处理意图分析结果
                        if data["type"] == "intent" and not intent_shown:
                            intent_result = data["data"]
                            containers["intent"].markdown(f"""
                            ### 意图分析结果
                            - 意图: {intent_result['intent']}
                            - 安全性: {'安全' if intent_result['safe'] else '不安全'}
                            - 操作: {intent_result['action']}
                            - 需要代码: {'是' if intent_result['need_code'] else '否'}
                            - 响应: {intent_result['response']}
                            """)
                            intent_shown = True
                        
                        # 处理任务执行结果
                        elif data["type"] == "content":
                            task_response += data["data"]
                            containers["task"].markdown(f"""
                            ### 任务执行结果
                            {task_response}
                            """)
                        
                        # 处理预测的问题
                        elif data["type"] == "predicted_questions":
                            questions = data["data"]
                            if questions:
                                questions_md = "### 预测的后续问题\n"
                                for q in questions:
                                    questions_md += f"- {q['question']}\n"
                                containers["questions"].markdown(questions_md)
                        
                        # 处理错误
                        elif data["type"] == "error":
                            st.error(f"发生错误: {data['data']}")
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON解析错误: {str(e)}")
                        st.error("解析响应时出错")
                        
    except Exception as e:
        logger.error(f"处理流式响应时出错: {str(e)}")
        st.error(f"处理响应时出错: {str(e)}")

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
                
            # 创建响应容器
            containers = create_response_containers()
            
            try:
                # 发送流式请求
                with st.spinner("正在处理..."):
                    response = requests.post(
                        f"{API_URL}/api/analyze/stream",
                        json={
                            "query": query,
                            "problem_content": problem_content,
                            "editor_code": editor_code
                        },
                        stream=True,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        # 处理流式响应
                        process_stream_response(response, containers)
                    else:
                        st.error(f"请求失败: {response.status_code}")
                        
            except requests.exceptions.Timeout:
                st.error("请求超时，请重试")
            except requests.exceptions.RequestException as e:
                st.error(f"请求出错: {str(e)}")
            except Exception as e:
                st.error(f"处理出错: {str(e)}")

    with right_col:
        # 帮助信息
        st.subheader("💡 使用说明")
        st.markdown("""
        1. 在左侧输入区域填写题目内容和代码
        2. 输入你的问题，比如：
           - 这段代码的时间复杂度是多少？
           - 如何优化这个算法？
           - 有什么边界情况需要考虑？
        3. 点击"发送请求"按钮获取AI助手的回答
        """)

if __name__ == "__main__":
    main()

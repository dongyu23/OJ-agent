import os
import json
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from camel.configs import QwenConfig
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from camel.agents import ChatAgent
from next_question_predictor import init_predictor

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
API_KEY = os.getenv('QWEN_API_KEY')

class TaskExecutor:
    def __init__(self):
        self.problem_content = ""  # 存储题目内容
        self.editor_code = ""      # 存储编辑区代码
        self.assistant = self._create_assistant()
        self.predictor = None      # 问题预测器

    def _create_assistant(self) -> ChatAgent:
        """创建AI助手实例"""
        try:
            qwen_model = ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
                model_type="Qwen/Qwen2.5-72B-Instruct",
                api_key=API_KEY,
                url="https://api-inference.modelscope.cn/v1",
                model_config_dict=QwenConfig(temperature=0.2).as_dict(),
            )
            
            system_prompt = """你是一个专业的编程助手，负责执行用户的编程相关任务。
根据不同的任务类型，你需要提供相应的帮助：

1. 对于代码分析任务：
   - 分析代码的时间复杂度和空间复杂度
   - 指出代码中可能的性能瓶颈
   - 提供优化建议

2. 对于解题思路任务：
   - 分析问题的关键点
   - 提供清晰的解题步骤
   - 推荐合适的算法和数据结构

3. 对于代码检查任务：
   - 检查代码的正确性
   - 指出潜在的bug
   - 提供改进建议

4. 对于代码提示任务：
   - 提供符合最佳实践的代码示例
   - 解释关键的代码片段
   - 给出注释和文档建议

请确保你的回答：
1. 针对具体任务类型提供相应的专业建议
2. 给出清晰、可执行的建议
3. 必要时提供代码示例
4. 解释你的建议理由
"""
            
            return ChatAgent(
                system_message=system_prompt,
                model=qwen_model,
                message_window_size=10,
                output_language='Chinese'
            )
        except Exception as e:
            logger.error(f"创建AI助手时出错: {str(e)}")
            raise

    def set_problem_content(self, content: str):
        """设置题目内容"""
        self.problem_content = content
        logger.info("已更新题目内容")

    def set_editor_code(self, code: str):
        """设置编辑区代码"""
        if code.strip():  # 只有当代码不为空时才设置
            self.editor_code = code
            logger.info("已更新编辑区代码")
        else:
            logger.info("编辑区代码为空，跳过更新")

    def _prepare_context(self, intent: str, need_code: bool) -> str:
        """根据意图和需求准备上下文"""
        context = f"题目内容:\n{self.problem_content}\n\n"
        
        if need_code and self.editor_code:
            context += f"用户代码:\n{self.editor_code}\n\n"
            
        context += f"请根据以上内容，"
        
        if intent == "code_analysis":
            context += "分析代码的复杂度和性能，并提供优化建议。"
        elif intent == "problem_solving":
            context += "提供清晰的解题思路和方法。"
        elif intent == "code_check":
            context += "检查代码的正确性，指出潜在问题。"
        elif intent == "code_suggestion":
            context += "提供改进建议和代码示例。"
            
        return context

    def execute_task(self, intent: str, query: str, need_code: bool) -> Dict[str, Any]:
        """执行具体任务"""
        try:
            # 准备任务上下文
            context = self._prepare_context(intent, need_code)
            full_query = f"{context}\n\n用户问题: {query}"
            
            logger.info(f"执行任务 - 意图: {intent}, 需要代码: {need_code}")
            
            # 获取AI响应
            response = self.assistant.step(full_query)
            self.assistant.reset()  # 重置会话状态
            
            if not response or not response.msgs:
                raise ValueError("AI助手没有返回任何响应")

            task_response = response.msgs[0].content
                
            # 预测可能的后续问题
            if self.predictor is None:
                logger.info("初始化问题预测器...")
                self.predictor = init_predictor(os.getenv('QWEN_API_KEY'))
                
            current_context = {
                'problem_content': self.problem_content,
                'editor_code': self.editor_code if need_code else '',
                'query': query
            }
            
            logger.info("开始预测后续问题...")
            next_questions = self.predictor.predict_next_questions(
                current_context=current_context,
                task_response=task_response
            )
            logger.info(f"预测到 {len(next_questions)} 个问题")
            
            result = {
                "success": True,
                "response": task_response,
                "intent": intent,
                "need_code": need_code,
                "predicted_questions": next_questions
            }
            
            logger.info(f"完整结果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"执行任务时出错: {str(e)}")
            return {
                "success": False,
                "response": f"执行任务时出错: {str(e)}",
                "intent": intent,
                "need_code": need_code,
                "predicted_questions": []
            }

# 创建全局执行器实例
task_executor = TaskExecutor()

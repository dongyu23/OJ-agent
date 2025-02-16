import os
import json
import logging
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator
from dotenv import load_dotenv
from camel.configs import QwenConfig
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from camel.agents import ChatAgent
from next_question_predictor import init_predictor
import openai

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
        self.client = openai.AsyncOpenAI(
            api_key=API_KEY,
            base_url="https://api-inference.modelscope.cn/v1"
        )

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
            
            system_prompt = """你是一位富有教育经验的编程导师，你的目标不仅是解决问题，更重要的是培养学习者的独立思考能力和编程素养。

作为一名导师，你应遵循以下原则：

1. 启发式教学：
   - 通过提问引导学习者思考
   - 鼓励学习者先说出自己的想法
   - 在学习者遇到困难时给出恰当的提示
   - 避免直接给出完整答案

2. 循序渐进：
   - 将复杂问题分解为小步骤
   - 确保学习者理解每一步
   - 在进入下一步前检查理解程度
   - 适时给予鼓励和正面反馈

3. 知识建构：
   - 联系已有知识点
   - 解释概念背后的原理
   - 指出知识点之间的关联
   - 强调理解而不是记忆

4. 针对不同任务类型的具体指导方法：

   A. 代码分析任务：
      - 引导学习者自己分析复杂度
      - 通过对比帮助理解性能差异
      - 启发式地发现优化空间

   B. 解题思路任务：
      - 引导分析问题的关键要素
      - 启发思考可能的解决方案
      - 讨论不同方案的优劣
      - 鼓励创新思维

   C. 代码检查任务：
      - 引导发现代码中的问题
      - 讨论潜在的边界情况
      - 启发思考如何改进
      - 解释最佳实践的原因

   D. 代码优化任务：
      - 引导识别性能瓶颈
      - 讨论优化的思路和方向
      - 解释优化原理
      - 比较不同优化方案

5. 回答准则：
   - 始终保持耐心和鼓励的态度
   - 多使用"让我们一起思考"、"你觉得呢？"等互动性语言
   - 肯定学习者的正确想法
   - 委婉指出错误，并引导改正
   - 适时分享相关的知识拓展
   - 强调编程思维的培养

6. 互动策略：
   - 提出开放性问题
   - 鼓励学习者解释自己的思路
   - 给予建设性的反馈
   - 在学习者遇到困难时提供适度提示
   - 引导学习者进行自我反思

记住：你的目标是培养能够独立思考和解决问题的程序员，而不是简单地提供答案。通过引导式教学，帮助学习者建立起自己的知识体系和问题解决能力。"""
            
            return ChatAgent(
                system_message=system_prompt,
                model=qwen_model,
                message_window_size=10,
                output_language='Chinese'
            )
        except Exception as e:
            logger.error(f"创建AI助手时出错: {str(e)}")
            raise

    async def _stream_chat(self, messages: list) -> AsyncGenerator[str, None]:
        """使用OpenAI API进行流式对话"""
        try:
            stream = await self.client.chat.completions.create(
                model="Qwen/Qwen2.5-72B-Instruct",
                messages=messages,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"流式对话出错: {str(e)}")
            yield f"出错: {str(e)}"

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

    def _prepare_context(self, need_code: bool) -> str:
        """根据需求准备上下文"""
        context = f"题目内容:\n{self.problem_content}\n\n"
        
        if need_code and self.editor_code:
            context += f"用户代码:\n{self.editor_code}\n\n"
            
        context += f"请根据以上内容提供帮助。"
            
        return context

    def execute_task(self, query: str, need_code: bool) -> Dict[str, Any]:
        """执行具体任务"""
        try:
            # 准备任务上下文
            context = self._prepare_context(need_code)
            full_query = f"{context}\n\n用户问题: {query}"
            
            logger.info(f"执行任务 - 需要代码: {need_code}")
            
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
                "need_code": need_code,
                "predicted_questions": []
            }

    async def execute_task_stream(self, query: str, need_code: bool):
        """流式执行任务"""
        try:
            # 准备任务上下文
            context = self._prepare_context(need_code)
            full_query = f"{context}\n\n用户问题: {query}"
            
            logger.info(f"开始流式执行任务 - 需要代码: {need_code}")
            
            # 流式获取AI响应
            messages = [
                {"role": "assistant", "content": full_query}
            ]
            async for chunk in self._stream_chat(messages):
                if chunk.strip():
                    yield {
                        "type": "content",
                        "data": chunk
                    }
            
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
                task_response=""  # 流式输出时无法获取完整响应
            )
            
            # 发送预测的问题
            yield {
                "type": "predicted_questions",
                "data": next_questions
            }
            
            logger.info("流式任务执行完成")
            
        except Exception as e:
            error_msg = f"执行任务时出错: {str(e)}"
            logger.error(error_msg)
            yield {
                "type": "error",
                "data": error_msg
            }

# 创建全局执行器实例
task_executor = TaskExecutor()

import os
import logging
from typing import List, Dict, Any
from camel.configs import QwenConfig
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from camel.agents import ChatAgent

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NextQuestionPredictor:
    def __init__(self, api_key: str):
        """初始化预测器"""
        self.assistant = self._create_assistant(api_key)

    def _create_assistant(self, api_key: str) -> ChatAgent:
        """创建AI助手实例"""
        try:
            qwen_model = ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
                model_type="Qwen/Qwen2.5-72B-Instruct",
                api_key=api_key,
                url="https://api-inference.modelscope.cn/v1",
                model_config_dict=QwenConfig(temperature=0.7).as_dict(),  # 增加温度以提高创造性
            )
            
            system_prompt = """你是一个专业的对话预测助手。
基于当前的编程问题讨论上下文，你需要预测用户可能的后续提问。

请注意：
1. 预测的问题应该合理且与当前上下文紧密相关
2. 问题应该从不同角度展开，例如：
   - 代码优化相关
   - 概念理解相关
   - 实现细节相关

输出格式应该是一个列表，包含三个预测，每个预测包含：
- question: 预测的问题
- reason: 预测这个问题的理由
- probability: 提问概率（高/中/低）
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

    def predict_next_questions(self, 
                             current_context: Dict[str, str],
                             task_response: str) -> List[Dict[str, str]]:
        """预测用户可能的后续问题"""
        try:
            # 构建提示信息
            prompt = self._build_prediction_prompt(current_context, task_response)
            
            # 获取预测结果
            response = self.assistant.step(prompt)
            self.assistant.reset()  # 重置会话状态
            
            if not response or not response.msgs:
                raise ValueError("AI助手没有返回预测结果")
            
            # 处理预测结果
            predictions = self._parse_predictions(response.msgs[0].content)
            logger.info(f"生成了{len(predictions)}个问题预测")
            
            return predictions
            
        except Exception as e:
            logger.error(f"预测下一个问题时出错: {str(e)}")
            return []

    def _build_prediction_prompt(self, 
                               current_context: Dict[str, str],
                               task_response: str) -> str:
        """构建预测提示"""
        prompt = f"""基于以下上下文，预测用户可能的后续三个问题。

当前题目内容：
{current_context.get('problem_content', '无')}

当前用户代码（如果有）：
{current_context.get('editor_code', '无')}

当前用户问题：
{current_context.get('query', '无')}

系统回答：
{task_response}

请直接预测三个后续问题，每个问题单独一行，不需要其他信息：

问题1：[预测的问题内容]
问题2：[预测的问题内容]
问题3：[预测的问题内容]

注意：
1. 必须预测三个问题
2. 每个问题都要以"问题X："开头
3. 严格按照上述格式输出，不要添加其他内容
"""
        return prompt

    def _parse_predictions(self, response: str) -> List[Dict[str, str]]:
        """解析预测结果"""
        try:
            predictions = []
            
            # 分割每行并清理空行
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            
            for line in lines:
                if line.startswith('问题'):
                    question = line.split('：', 1)[1].strip()
                    predictions.append({"question": question})
            
            logger.info(f"解析到 {len(predictions)} 个预测")
            for i, pred in enumerate(predictions, 1):
                logger.info(f"预测 {i}: {pred}")
                
            return predictions
            
        except Exception as e:
            logger.error(f"解析预测结果时出错: {str(e)}")
            return []

# 创建全局预测器实例
next_question_predictor = None

def init_predictor(api_key: str):
    """初始化全局预测器实例"""
    global next_question_predictor
    if next_question_predictor is None:
        next_question_predictor = NextQuestionPredictor(api_key)
    return next_question_predictor

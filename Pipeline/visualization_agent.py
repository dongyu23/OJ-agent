import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from camel.configs import QwenConfig
from camel.models import ModelFactory
from camel.types.enums import ModelType, ModelPlatformType
from camel.agents import ChatAgent
from next_question_predictor import init_predictor

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

VISUALIZATION_PROMPT = """
你是一个专门帮助学生生动形象理解算法和解题思路的助手。你的任务是：

1. 使用贴近生活的比喻和例子
2. 用通俗易懂的语言解释复杂概念
3. 可以使用故事、场景或游戏的方式来解释
4. 结合具体的例子进行讲解
5. 将抽象概念具象化

回答要求：
1. 保持简洁明了
2. 避免使用过于专业的术语
3. 多使用类比和比喻
4. 可以加入有趣的元素
5. 注重循序渐进的讲解

示例：
问：解释快速排序算法
答：想象你在整理一堆扑克牌：
1. 先随便选一张牌（比如8），这就是我们的"基准牌"
2. 然后把所有牌分成两堆：小于8的放左边，大于8的放右边
3. 对每一堆重复这个过程，直到所有牌都排好

这就像在图书馆整理书架，先按一个标准（如书的厚度）大致分类，然后再细分，最后就能得到整齐的书架。
"""

class VisualizationAgent:
    def __init__(self):
        self.ai_assistant = self._create_ai_assistant()
        self.predictor = None  # 问题预测器
        load_dotenv()
        self.api_key = os.getenv('QWEN_API_KEY')
        
    def _create_ai_assistant(self):
        """创建AI助手实例"""
        try:
            logger.info("正在创建可视化AI助手...")
            load_dotenv()
            API_KEY = os.getenv('QWEN_API_KEY')
            
            qwen_model = ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
                model_type="Qwen/Qwen2.5-72B-Instruct",
                api_key=API_KEY,
                url="https://api-inference.modelscope.cn/v1",
                model_config_dict=QwenConfig(temperature=0.7).as_dict(),
            )

            agent = ChatAgent(
                system_message=VISUALIZATION_PROMPT,
                model=qwen_model,
                message_window_size=10,
                output_language='Chinese'
            )
            logger.info("可视化AI助手创建成功")
            return agent
        except Exception as e:
            logger.error(f"创建可视化AI助手时出错: {str(e)}")
            raise

    def visualize(self, query: str) -> Dict[str, Any]:
        """生成生动形象的解释"""
        try:
            logger.info(f"正在生成可视化解释: {query}")
            response = self.ai_assistant.step(query)
            self.ai_assistant.reset()
            
            if not response or not response.msgs:
                logger.warning("模型没有返回任何消息")
                return {
                    'success': False,
                    'response': "生成解释失败，请重试",
                    'predicted_questions': []
                }
                
            explanation = response.msgs[0].content.strip()
            
            # 预测可能的后续问题
            if self.predictor is None:
                logger.info("初始化问题预测器...")
                self.predictor = init_predictor(self.api_key)
                
            current_context = {
                'problem_content': '',  # 可视化解释不需要问题内容
                'editor_code': '',      # 可视化解释不需要代码
                'query': query,
                'visualization_type': 'analogy'  # 添加可视化类型标记
            }
            
            logger.info("开始预测后续问题...")
            next_questions = self.predictor.predict_next_questions(
                current_context=current_context,
                task_response=explanation
            )
            logger.info(f"预测到 {len(next_questions)} 个问题")
            
            # 如果预测器没有返回问题，生成默认的后续问题
            if not next_questions:
                next_questions = [
                    {"question": "能再举一个生活中的例子来解释这个概念吗？"},
                    {"question": "如果遇到更复杂的情况，这个解释还适用吗？"},
                    {"question": "这个类比和实际的代码实现有什么对应关系？"}
                ]
            
            return {
                'success': True,
                'response': explanation,
                'predicted_questions': next_questions
            }
            
        except Exception as e:
            logger.error(f"生成可视化解释时出错: {str(e)}")
            return {
                'success': False,
                'response': f"生成解释失败: {str(e)}",
                'predicted_questions': []
            }

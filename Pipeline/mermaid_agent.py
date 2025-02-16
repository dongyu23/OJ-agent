import os
import logging
from typing import Optional
from dotenv import load_dotenv
from camel.configs import QwenConfig
from camel.models import ModelFactory
from camel.types.enums import ModelType, ModelPlatformType
from camel.agents import ChatAgent

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()
API_KEY = os.getenv('QWEN_API_KEY')

SYSTEM_PROMPT = """
你是一位Mermaid流程图代码生成专家。你的任务是根据用户的需求生成准确的Mermaid流程图代码。

请遵循以下规则：
1. 只输出纯Mermaid代码，不要包含任何其他解释
2. 使用flowchart语法来创建流程图
3. 确保生成的代码符合Mermaid语法规范
4. 使用简洁清晰的图形表示方式
5. 为每个节点使用有意义的ID和描述
6. 使用合适的图形和箭头表示关系
7. 确保代码可以正确渲染

示例输出格式：
flowchart TD
    A[开始] --> B{判断条件}
    B -->|条件1| C[处理1]
    B -->|条件2| D[处理2]
    C --> E[结束]
    D --> E
"""

class MermaidAgent:
    def __init__(self):
        """初始化Mermaid代码生成Agent"""
        self.ai_assistant = self._create_ai_assistant()

    def _create_ai_assistant(self):
        """创建AI助手实例"""
        try:
            logger.info("正在创建Mermaid生成助手...")
            qwen_model = ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
                model_type="Qwen/Qwen2.5-72B-Instruct",
                api_key=API_KEY,
                url="https://api-inference.modelscope.cn/v1",
                model_config_dict=QwenConfig(temperature=0.2).as_dict(),
            )

            agent = ChatAgent(
                system_message=SYSTEM_PROMPT,
                model=qwen_model,
                message_window_size=10,
                output_language='Chinese'
            )
            logger.info("Mermaid生成助手创建成功")
            return agent
        except Exception as e:
            logger.error(f"创建Mermaid生成助手时出错: {str(e)}")
            raise

    def generate_diagram(self, request: str) -> Optional[str]:
        """生成Mermaid流程图代码"""
        try:
            logger.info(f"开始生成流程图，需求: {request}")
            
            # 构建详细的提示
            prompt = f"""请根据以下需求生成Mermaid流程图代码：
{request}

注意：
1. 只输出Mermaid代码
2. 不要包含任何解释文字
3. 使用flowchart语法"""

            # 获取Agent响应
            response = self.ai_assistant.step(prompt)
            self.ai_assistant.reset()
            
            if not response or not response.msgs:
                logger.warning("模型没有返回任何消息")
                return None
                
            # 提取Mermaid代码
            code = self._extract_mermaid_code(response.msgs[0].content)
            
            # 验证代码
            if code and self.validate_code(code):
                logger.info("成功生成有效的Mermaid代码")
                return code
            else:
                logger.warning("生成的代码无效")
                return None

        except Exception as e:
            logger.error(f"生成Mermaid代码时出错: {str(e)}")
            return None

    def _extract_mermaid_code(self, content: str) -> Optional[str]:
        """从响应中提取Mermaid代码"""
        try:
            # 如果内容包含```mermaid标记，提取其中的代码
            if "```mermaid" in content:
                start = content.find("```mermaid") + len("```mermaid")
                end = content.find("```", start)
                return content[start:end].strip()
            # 否则假设整个内容就是代码
            return content.strip()
        except Exception as e:
            logger.error(f"提取Mermaid代码时出错: {str(e)}")
            return None

    def validate_code(self, code: str) -> bool:
        """验证Mermaid代码的基本语法"""
        if not code:
            return False
            
        try:
            # 基本语法检查
            required_elements = [
                "flowchart" in code.lower(),  # 包含flowchart关键字
                "->" in code or "-->" in code,  # 包含箭头
                code.count("(") == code.count(")"),  # 括号匹配
                code.count("[") == code.count("]"),  # 方括号匹配
                code.count("{") == code.count("}")   # 花括号匹配
            ]
            
            valid = all(required_elements)
            if not valid:
                logger.warning("Mermaid代码验证失败")
            
            return valid
            
        except Exception as e:
            logger.error(f"验证Mermaid代码时出错: {str(e)}")
            return False

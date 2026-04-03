from camel.models import ModelFactory
from camel.types.enums import ModelPlatformType
from camel.configs import QwenConfig
import os

qwen_model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    model_type="GLM-4.7",
    api_key="sk-PCV43uGsNiwy_a4W2CnpCQ",
    url="https://llmapi.paratera.com/v1",
    model_config_dict=QwenConfig(temperature=0.2).as_dict(),
)

from camel.agents import ChatAgent
agent = ChatAgent(
    system_message="你好",
    model=qwen_model,
)
print(agent.step("你好").msgs[0].content)

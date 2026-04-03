import os
from openai import OpenAI

client = OpenAI(
    api_key="sk-PCV43uGsNiwy_a4W2CnpCQ",
    base_url="https://llmapi.paratera.com",
)

try:
    response = client.chat.completions.create(
        model="glm-4.7",
        messages=[{"role": "user", "content": "你好"}],
    )
    print(response.choices[0].message.content)
except Exception as e:
    print("Error:", e)

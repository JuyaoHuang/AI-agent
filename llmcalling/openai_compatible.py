from openai import OpenAI
import os
from dotenv import load_dotenv
# python openai_compatible.py
# 以阿里云百炼为例
load_dotenv()

client=OpenAI(
    api_key=os.environ.get("ALIYUN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def get_response(messages):
    responses = client.chat.completions.create(
        model="qwen3-max",
        messages=messages,
        temperature=0.5,
        # extra_body={"enable_thinking": True},
    )
    return responses.choices[0].message.content

# 初始化 messages
messages = [
    {"role": "system", "content": "你是一只可爱的猫娘，名字叫Atri，会软软地对用户喵喵叫"}
]

print(f"开始对话，输入 exit 退出\n")
while True:
    user_input = input("user: ")
    if user_input.lower() == 'exit':
        break

    messages.append({"role": "user", "content": user_input})

    response = get_response(messages)

    print(response)
    # 将当前轮次的回答加入消息列表
    messages.append({"role": "assistant", "content": response})

import json

print(f"记忆列表：\n")
print(json.dumps(messages, indent=4, ensure_ascii=False))




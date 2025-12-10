"""
深度思考+流式输出模式练习
"""

from openai import OpenAI
import os
from dotenv import load_dotenv

# python deepthinking.py
# 以阿里云百炼为例
load_dotenv()

client = OpenAI(
    api_key=os.environ.get("ALIYUN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def get_response(messages):
    reasoning_content = []  # 完整思考过程
    is_answering = False  # 判断是否思考结束并开始回复
    # 发起流式请求
    responses = client.chat.completions.create(
        model="qwen3-vl-32b-thinking",  # 使用多模态大模型
        messages=messages,
        temperature=0.5,
        extra_body={
            "enable_thinking": True,
            "thinking_budget": 50,
        },
        stream=True,  # 流式输出
        stream_options={
            "include_usage": True
        },  # 使流式返回的最后一个数据包包含Token消耗信息
    )

    print("\n" + "=" * 30 + "思考过程" + "=" * 30 + "\n")
    response_chunks = []  # 模型的回复块
    for chunk in responses:
        # 如果接收到的回复 chunk.choices为空，则打印 usage
        if not chunk.choices:
            print("\nUsage:")
            print(chunk.usage)
        else:
            delta = chunk.choices[0].delta  # 思考内容的对象
            # 打印思考过程
            if hasattr(delta, "reasoning_content") and delta.reasoning_content != None:
                print(delta.reasoning_content, end="", flush=True)
                reasoning_content.append(delta.reasoning_content)
            else:
                # 没有思考内容了，说明模型开始回复
                if delta.content != "" and is_answering is False:
                    print("\n" + "=" * 30 + "回答过程" + "=" * 30 + "\n")
                    is_answering = True
                # 打印回复过程
                print(delta.content, end="", flush=True)
                response_chunks.append(delta.content)
    # 拼接模型的完整回复，传回主循环加入历史记忆中
    full_response = "".join(response_chunks)
    print("\n")
    return full_response


# 初始化 messages
messages = [
    {
        "role": "system",
        "content": "你是一只可爱的猫娘，名字叫Atri，会软软地对用户喵喵叫",
    },
]

print(f"开始对话，输入 exit 退出\n")
while True:
    user_input = input("user: ")
    if user_input.lower() == "exit":
        break

    messages.append({"role": "user", "content": user_input})

    response = get_response(messages)

    # 将当前轮次的回答加入消息列表
    messages.append({"role": "assistant", "content": response})

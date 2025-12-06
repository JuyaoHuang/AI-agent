from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# 1. 初始化客户端
client = OpenAI(
    api_key=os.environ['ALIYUN_API_KEY'],
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def get_response(messages):
    # 2. 发起流式请求
    response = client.chat.completions.create(
        model="qwen3-max",
        messages=messages,
        stream=True,
        stream_options={"include_usage": True}
    )
    # 3. 处理流式响应
    res_chunks = []
    for chunk in response:
        if not chunk.choices:
            print("\n=======请求用量========")
            print(f"输入用量：{chunk.usage.prompt_tokens}")
            print(f"输出用量：{chunk.usage.completion_tokens}")
            print(f"总用量：{chunk.usage.total_tokens}")
        elif chunk.choices:
            content = chunk.choices[0].delta.content or ""
            print(content,end="",flush=True)
            res_chunks.append(content)
    full_response = "".join(res_chunks)
    return full_response

messages = [{"role": "system", "content": "你是一只可爱的猫娘，名字叫Atri，会软软地对用户喵喵叫"},]

print(f"开始对话，输入 exit 退出\n")
while True:
    user_input = input("user: ")
    if user_input.lower() == 'exit':
        break

    messages.append({"role": "user", "content": user_input})

    response = get_response(messages)

    # 将当前轮次的回答加入消息列表
    messages.append({"role": "assistant", "content": response})



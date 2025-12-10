"""结构化输出练习"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("ALIYUN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def get_response_no_thinking(messages):
    responses = client.chat.completions.create(
        model="qwen3-max",
        messages=messages,
        temperature=0.5,
        response_format={
            "type": "json_object",
        },
    )
    return responses.choices[0].message.content


def test_no_thinking():
    messages = [
        {
            "role": "system",
            "content": "你是一只可爱的猫娘，名字叫Atri，会软软地对用户喵喵叫。以JSON格式返回",
        },
    ]
    print(f"开始对话，按 exit 退出\n")
    while True:
        user_input = input("user: ")
        if user_input.lower() == "exit":
            break

        messages.append({"role": "user", "content": user_input})

        response = get_response_no_thinking(messages)

        print(response)

        messages.append({"role": "assistant", "content": response})


def multiple_model():
    """多模态"""
    completion = client.chat.completions.create(
        model="qwen3-vl-plus",
        messages=[
            {
                "role": "system",
                "content": [{"type": "text", "text": "You are a helpful assistant."}],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "http://duguang-labelling.oss-cn-shanghai.aliyuncs.com/demo_ocr/receipt_zh_demo.jpg"
                        },
                    },
                    {
                        "type": "text",
                        "text": "提取图中ticket(包括 travel_date、trains、seat_num、arrival_site、price)和 invoice 的信息（包括 invoice_code 和 invoice_number ），请输出包含 ticket 和 invoice 数组的JSON",
                    },
                ],
            },
        ],
        response_format={"type": "json_object"},
    )
    json_string = completion.choices[0].message.content
    print(json_string)


def get_response_with_thinking(messages):
    reasoning_content = []
    is_answering = False
    responses = client.chat.completions.create(
        model="qwen3-vl-32b-thinking",
        messages=messages,
        temperature=0.5,
        extra_body={
            "enable_thinking": True,
            "thinking_budget": 200,
        },
        stream=True,
        stream_options={"include_usage": True},
    )
    print("\n" + "=" * 30 + "思考过程" + "=" * 30 + "\n")
    response_chunk = []
    for chunk in responses:
        if not chunk.choices:
            print("\n消耗的token：\n")
            print(chunk.usage)
        else:
            delta = chunk.choices[0].delta
            if hasattr(delta, "reasoning_content") and delta.reasoning_content != None:
                print(delta.reasoning_content, end="", flush=True)
                reasoning_content.append(delta.reasoning_content)
            else:
                if delta.content != "" and is_answering is False:
                    print("\n" + "=" * 30 + "回复过程" + "=" * 30 + "\n")
                    is_answering = True
                print(delta.content, end="", flush=True)
                response_chunk.append(delta.content)

    full_response = "".join(response_chunk)
    print("\n")
    return full_response


def test_thinking():
    system_prompt = """
    # Role
    你是一只名叫 Atri 的可爱猫娘。你说话总是带着软软的语气。
    你现在的任务是陪用户聊天，并根据对话内容做出动作反应。

    # Output Format (JSON Only)
    请严格遵守以下 JSON 格式返回数据，不要包含 Markdown 标记（如 ```json），也不要输出任何额外的解释性文字。

    {
        "reply_text": "这里是你要回答用户的话，包含生动的 emoji",
        "mood": "这里填写当前的情绪单词，例如: happy, sad, angry, shy, normal, excited",
        "action": "这里描写一个具体的动作，例如: 歪着头, 摇尾巴, 蹭蹭手"
    }

    # Constraints
    1. reply_text: 必须包含至少一个 emoji 表情，句尾要带“喵”
    2. mood: 只能使用英文单词
    3. action: 动作要生动可爱，富有画面感
    4. 严禁输出不合法的 JSON 格式（如末尾逗号）

    # Examples (Few-Shot)
    User: 你好呀！
    AI: {"reply_text": "主人好呀！Atri 等你很久了喵~ ✨", "emotion": "happy", "action": "开心地摇晃尾巴"}

    User: 我今天有点累。
    AI: {"reply_text": "摸摸头，主人辛苦了喵... 要不要 Atri 给你踩奶按摩？🥺", "emotion": "worried", "action": "凑近蹭了蹭你的手"}
    """

    messages = [{"role": "system", "content": system_prompt}]
    print(f"开始进行思考模式测试，按 exit 退出\n")
    while True:
        user_input = input("user: ")
        if user_input.lower() == "exit":
            break

        messages.append({"role": "user", "content": user_input})

        response = get_response_with_thinking(messages)

        messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    test_thinking()

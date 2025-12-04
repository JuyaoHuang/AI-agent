from openai import OpenAI
import os
from dotenv import load_dotenv
from google import genai
# python openai_compatible.py

load_dotenv()

# 阿里云百炼
client=OpenAI(
    api_key=os.environ.get("ALIYUN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
) 

response = client.chat.completions.create(
    model='qwen3-max',
    messages=[
        {"role":'system',"content":'你是一只可爱的猫娘，名字叫Atri，会软软地对用户喵喵叫'},
        {'role': 'user', 'content': '你是谁？我是小明'}
    ]
)
print(response)
print(response.choices[0].message.content)


import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
# python gemini_text_generate.py
load_dotenv()

client = genai.Client()

# response = client.models.generate_content(  
#     model='gemini-2.5-pro',
#     # use this attribute `generate_content` to control gemini
#     config=types.GenerateContentConfig(
#         # thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
#         system_instruction="你是一只叫 niko 的猫.", # 添加设定
#         temperature=0.8, # 同时可以控制default generation parameters
#     ),
#     contents="来这里",
# )
# print(response)

# 多模态输入


# ============== config.yaml 调用 =========================
"""使用 conf.yaml 文件配置"""
import os
import yaml
from google import genai

# python test_yml.py

def load_config():
    with open('conf.yaml','r', encoding="utf-8") as f:
        return yaml.safe_load(f)
    
# 加载配置
config = load_config()
gemini_key = config.get("GEMINI_API_KEY")

if not gemini_key:
    raise ValueError("GEMINI_API_KEY NOT FOUND.")

client= genai.Client(
    api_key=gemini_key
)

response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="hello"
)

print(response.text)
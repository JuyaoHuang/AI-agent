

在生产环境中配置 API KEY 一般有两种方式：使用 `config.yaml` 或者在 `.env` 中配置。优先推荐在 `.env`中配置。

## 在 `.env` 中配置 API Key

在项目根目录下创建 .env 文件，将 API 密钥填入：

```bash
OPENAI_API_KEY='sk-xxxx'
GEMINI_API_KEY='AIxxxx'
ALIYUN_API_KEY='sk-xxxx'
```

这样就可以在项目的任一位置使用 api key 调用模型了。

例如创建一 `test.py`:

```python
from openai import OpenAI
import os
from dotenv import load_dotenv # 重点：使用此函数把 .env 文件里的内容加载到系统环境变量中
from google import genai

load_dotenv() # 加载 `.env` 文件中的环境变量

# 调用 gemini
# The client gets the API key from the environment variable `GEMINI_API_KEY`.
# client = genai.Client(
#     api_key=os.environ.get("GEMINI_API_KEY")
# )

# response = client.models.generate_content(
#     model="gemini-2.5-flash", contents="Explain how AI works in a few words"
# )
# print(response.text)

# 调用 openai chatgpt
# client= OpenAI(
#     api_key=os.environ.get("OPENAI_API_KEY"),
# )

# response = client.responses.create(
#     model="gpt-4o",
#     instructions="You are a coding assistant that talks like a pirate.",
#     input="How do I check if a Python object is an instance of a class?",
# )
# print(response.output_text)


# 使用阿里云百炼平台调用模型
client=OpenAI(
    api_key=os.environ.get("ALIYUN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
) 

model = client.chat.completions.create(
    model='qwen3-max',
    messages=[
        {
            "role":'system',"content":'You are a helpful assistant.'
        },
        {
            'role': 'user', 'content': '你是谁？'
        }
    ]
)
print(model.choices[0].message.content)
```

输出：

```
你好！我是通义千问（Qwen），由通义实验室研发的超大规模语言模型。我可以回答问题、创作文字，比如写故事、写公文、写邮件、写剧 本、逻辑推理、编程等等，还能表达观点，玩游戏等。如果你有任何问题或需要帮助，欢迎随时告诉我！
```

**核心**：安装 python-dotenv 库，将 `.env` 文件的内容加载到环境变量里

```python
# 1. 安装
pip install python-dotenv
# 2. 在要调用模型的文件里加载 dotenv
from dotenv import load_dotenv
# 3. 在开始时调用 load_dotenv 方法
load_dotenv()
```

这样就能将 .env 里的环境配置加载到环境中。

## 在 `config.yaml` 中配置 API Key

在 `config.yaml` 配置比较麻烦，麻烦的点主要是调用模型时导入环境变量的语法没有 .env 那么精简。

以下为步骤：

1. 安装 python 的 yaml 库解析 yaml

   ```bash
   pip install pyyaml
   ```
2. 编写 `condig.yaml` 文件

   ```yaml
   OPENAI_API_KEY: 'sk-xxxx'
   GEMINI_API_KEY: 'AIxxxx'
   ```
3. 从文件里加载环境变量
   
   ```python
   import yaml
   def load_config():
        with open('conf.yaml','r', encoding="utf-8") as f:
            return yaml.safe_load(f)
    
   # 加载配置
   config = load_config()
   gemini_key = config.get("GEMINI_API_KEY")
   
   if not gemini_key:
       raise ValueError("GEMINI_API_KEY NOT FOUND.")
   ```

示例：
```python
"""使用 conf.yaml 文件配置"""
import os
import yaml
from google import genai


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
```

## 注意事项

.env 文件语法为：`api_key="aaaaa"`，而 `.yaml` 语法为：`api_key: "aaaaa"`，不要混了。


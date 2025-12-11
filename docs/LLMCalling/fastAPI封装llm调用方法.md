## 项目二简介

**构建一个高级API封装器**：

使用FastAPI，创建一个简单的后端服务。它接收一个任务描述（比如“总结这段文字”或“把这段英文翻译成中文”），然后在内部构建一个高质量的 Prompt，调用 LLM API，最后将 LLM 返回的干净结果作为 API 的响应返回
目的: 将 LLM的 强大能力，封装成可以轻松调用的、可靠的后端服务

## 解决方案

### 简单实现

使用 fastAPI 封装一个 API 端点，该端点实现 `接收文本 -> 构建 prompt -> 调用 llm -> 返回清洗好的、符合约束的 JSON 内容`。

> 注意，所有内容都在一个 API 里实现，实际上这过于臃肿了。
> 可以将“构建 prompt”和“llm 调用”这两部分给抽象为独立的模块。例如 prompts module, stateless llm module。之后再有其他新的端点需要实现上面的流程，只需要传入需要的参数即可，不需要写重复的代码。

### 结构化实现

> 为保证文章阅读的流畅性，该部分后续给出。

将简单实现的流程的一些内容抽象封装为模块进行调用。

## 简单方案的实现步骤

**1. 初始化 fastAPI 应用**

```python
import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
# 由于国内可能存在的 CDN 流量限制，故手动定义 fastapi 自带的 swagger ui 页面的静态资源加载
# 以下的包的作用是使用国内镜像源加载 fastAPI 自带的 seagger ui 页面
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.docs import get_redoc_html

load_dotenv()
app = FastAPI(title="Atri Translator", docs_url=None, redoc_url=None)
```

**2. 使用国内镜像CDN加速站加载 swagger ui**

```python
# Add swagger-ui mirror
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.29.1/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.29.1/swagger-ui.css",
    )
@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
    )
```

**3. 初始化 llm 客户端**

```python
client = OpenAI(
    api_key=os.environ.get("ALIYUN_API_KEY"),
    base_url=os.environ.get("ALIYUN_BASE_URL"),
)
```

**4. 定义 pydantic 模型**

以构建一个翻译器为例，定义两个数据模型：一个用于发送消息，一个用于接收返回的消息。

```python
class TranslateRequest(BaseModel):
    text: str = Field(..., description="需要翻译的原文", min_length=1)
    target_lang: str = Field("English", description="目标语言，默认为英语")
class TranslateResponse(BaseModel):
    original_text: str
    translated_text: str
    detected_language: str = "unknown"
```

**5. 处理服务请求**

使用 fastAPI 的路由定义和异步请求方式，完成核心的发送-接收逻辑。

```python
# 定义接收的 API 请求的路由
@app.post("/api/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """
    access text -> build Prompt -> llmcalling -> return JSON well-clear
    :param request:
    :return: JSON well-clear
    """
```

**构建系统 prompt**：

```python
    system_prompt = f"""
    你是一个精通多国语言的资深翻译引擎。
    任务：
    1. 将用户输入的文本翻译成 {request.target_lang}。
    2. 自动检测原文的语言。
    3. 必须严格以 JSON 格式输出，包含以下字段：
        - translated_text: 翻译后的内容
        - source_lang: 原文的语言（如 Chinese, English, French）
    示例：
    {{
        "translated_text": "hello",
        "source_lang": "en"
    }}
    """
```

**构建 API 请求**

```python
    response = client.chat.completions.create(
        model="qwen3-max",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.text},
        ],
        temperature=0.3,
    )
```

**接收返回内容并转为字典**（因为返回的是 JSON ）

```python
    content = response.choices[0].message.content
    # turn json into dict
    data = json.loads(content)
```

**将拿到的字典内容返回给客户端**

```python
      # return to client
      return TranslateResponse(
          original_text=request.text,
          translated_text=data.get("translated_text", "Fail to translate"),
          detected_language=data.get("source_lang", "unknown"),
      )
```

**定义根目录路由**（用于测试 UI 界面正常打开）

```python
@app.get("/")
async def root():
    return {"message": "AI server is running! please open thr link /docs to see docs."}
```

**运行指令**

```bash
uvicorn main:app --reload
```

或者

```bash
fastapi dev main.py --port 8000
```

然后打开 `http://127.0.0.0:8000`。

> 如果出现长时间打不开 UI 页面的情况，有可能是端口被占用。使用 `--port` 指令切换端口。

## 重构

就像前文说的，处理 `接收请求 -> 构建 prompt -> llm 调用 -> 解析响应 -> 返回需要的数据结构` 的所有代码全部堆积在一个 API 端点里。这样代码容易臃肿，且有几个部分是可以**代码复用**的。例如 prompt 构建、llm 调用和解析响应。

因此可以做出以下重构：
1. 借用 MVC 设计思路，将逻辑划分为：服务层、配置层。
2. 配置层：进行 fastapi 的配置，例如标题、描述、启动端口、启动入口等
3. 服务层：业务处理、prompt工厂、Pydantic模型定义、llm 调用

```bash
project_two
 ┣ config
 ┃ ┣ config.py
 ┣ services
 ┃ ┣ llmcalling.py 
 ┃ ┣ prompt_factory.py 
 ┃ ┣ schema.py
 ┃ ┣ server.py
 ┣ main.py
```

这样的结构增加了可扩展性和稳定性。
> 实际上配置文件在 /project_two 下创建 .env 作为子配置文件（项目根目录有根`.env`），
> 从环境里读取所有配置才是生产环境的标准做法

这样对于业务处理代码部分（API 端点）不必再写多余的代码以及考虑 llm 调用、prompt 构建、结构解析等部分的代码，直接调用相关的方法即可。

**对于 `server.py`**，其原本的业务处理逻辑不变，但是代码已被精简为：

```python
@app.post("/api/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """
    access text -> build Prompt -> llmcalling -> return JSON well-clear
    :param request:
    :return: JSON well-clear
    """
     system_prompt = PromptFactory.get_translate_prompt(request.target_lang)

     messages = [
         {"role": "system", "content": system_prompt},
         {"role": "user", "content": request.text},
     ]
     content = llmcalling("qwen3-max", messages, 0.3)

     # turn json into dict
     data = json.loads(content)

     # return to client
     return TranslateResponse(
         original_text=request.text,
         translated_text=data.get("translated_text", "Fail to translate"),
         detected_language=data.get("source_lang", "unknown"),
     )
```
只需构建好传入模型的 `message` 部分，再将结果返回即可。代码高度精简和可读。

而需要构建新的（例如角色扮演等和 llm 互动）API 端点时，也是一样的处理逻辑，只需要在 prompt 工厂里新增系统 prompt即可。

那么既然可扩展性如此之强，可在现有基础上扩展新的服务，并将其封装为一个前后端集成的 web 应用。



**重构后的代码可在此 commit 查看**：https://github.com/JuyaoHuang/AI-agent/pull/9/commits/9544f2f8c77739cce1cef9a379c2463cc5b7555f

> 该 commit 还没有将 llmcalling 抽象出来。

## 新的实践

Issue 链接：https://github.com/JuyaoHuang/AI-agent/issues/8

**项目 2 的基本需求已完成**。项目结构已成功重构为标准的 MVC 架构。基于此坚实的基础，我计划进一步扩展项目的功能。

### 目标

此问题跟踪以下扩展的实现：

- 实现 /api/summary 端点：创建一个用于文本摘要的新 API 路由，利用 PromptFactory 管理摘要相关的提示，为此任务建立一个新的 LLM 调用流程。

- 开发客户端模拟脚本：编写一个 Python 脚本来模拟真实用户的请求，从客户端的角度验证 API 的行为和性能。


- 全栈集成（Streamlit）：将现有的 Streamlit 前端（来自项目 1）与新构建的 FastAPI 后端集成，实现无缝的前后端通信。


### 实施方案及技术细节

- **重构 LLM 服务**：将核心 LLM 调用逻辑抽象为可重用的服务方法/类，以减少代码重复并提高可维护性。

- **客户端逻辑**：使用 Python requests 库处理 API 调用并解析返回的 JSON 数据结构。

- **前端渲染**：在 Streamlit UI 上渲染解析后的 API 响应。
- 目标：实现流式输出（如适用）以提升用户体验。

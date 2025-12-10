"""
项目2：构建一个高级API封装器
任务:
使用FastAPI，创建一个简单的后端服务。
它接收一个任务描述（比如“总结这段文字”或“把这段英文翻译成中文”），
然后在内部构建一个高质量的 Prompt，调用 LLM API，最后将 LLM 返回的干净结果作为 API 的响应返回
目的: 将LLM的强大能力，封装成你可以轻松调用的、可靠的后端服务
"""

import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.docs import get_redoc_html

load_dotenv()
app = FastAPI(title="Atri Translator", docs_url=None, redoc_url=None)


# Add swagger-ui mirror
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        # 替换为 unpkg 源，或者你可以找其他的国内镜像
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


client = OpenAI(
    api_key=os.environ.get("ALIYUN_API_KEY"),
    base_url=os.environ.get("ALIYUN_BASE_URL"),
)


class TranslateRequest(BaseModel):
    text: str = Field(..., description="需要翻译的原文", min_length=1)
    target_lang: str = Field("English", description="目标语言，默认为英语")


class TranslateResponse(BaseModel):
    original_text: str
    translated_text: str
    detected_language: str = "unknown"


# core api
@app.post("/api/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """
    access text -> build Prompt -> llmcalling -> return JSON well-clear
    :param request:
    :return: JSON well-clear
    """
    try:
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

        response = client.chat.completions.create(
            model="qwen3-max",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.text},
            ],
            temperature=0.3,
        )

        content = response.choices[0].message.content
        # turn json into dict
        data = json.loads(content)

        # return to client
        return TranslateResponse(
            original_text=request.text,
            translated_text=data.get("translated_text", "Fail to translate"),
            detected_language=data.get("source_lang", "unknown"),
        )
    except Exception as e:
        print(f"Error:{e}\n")
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/")
async def root():
    return {"message": "AI server is running! please open thr link /docs to see docs."}


"""
run: uvicorn main:app --reload
or fastapi dev main.py --port 8080
"""

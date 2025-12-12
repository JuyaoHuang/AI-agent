"""
项目2：构建一个高级API封装器
任务:
使用FastAPI，创建一个简单的后端服务。
它接收一个任务描述（比如“总结这段文字”或“把这段英文翻译成中文”），
然后在内部构建一个高质量的 Prompt，调用 LLM API，最后将 LLM 返回的干净结果作为 API 的响应返回
目的: 将LLM的强大能力，封装成你可以轻松调用的、可靠的后端服务
"""


import json
import re
from fastapi import FastAPI, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.docs import get_redoc_html
from .prompt_factory import PromptFactory
from .llmcalling import LLMCalling
from .schema import (
    TranslateRequest,
    TranslateResponse,
    SummaryRequest,
    SummaryResponse,
    )


app = FastAPI(title="Atri Translator", docs_url=None, redoc_url=None)


# 辅助函数：清洗模型可能返回的 ```json 代码块标注
def clean_json_string(text:str) -> str:
    """清理模型返回的可能存在的 markdown 标记:```json """
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```", "", text)
    return text.strip()


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


@app.post("/api/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """
    access text -> build Prompt -> llmcalling -> return JSON well-clear
    :param request:
    :return: JSON well-clear
    """
    try:
        system_prompt = PromptFactory.get_translate_prompt(request.target_lang)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.text},
        ]
        content = LLMCalling.llmcalling("qwen3-max", messages, 0.3)

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


@app.post("/api/summary", response_model=SummaryResponse)
async def summary(request: SummaryRequest):
    """处理总结长文本请求的端点"""
    system_prompt = PromptFactory.get_summary_prompt(250)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request.text},
    ]
    content = LLMCalling.llmcalling("qwen3-max", messages, 0.5)
    # 清洗潜在的 json md标注
    content = clean_json_string(content)
    data = json.loads(content)

    return SummaryResponse(
        summary=data.get("summary", "Fail to summary"),
        tags=data.get("tags",[])
    )


@app.get("/")
async def root():
    return {"message": "AI server is running! please open thr link /docs to see docs."}


if __name__ == "__main__":
    import uvicorn
    from ..config.config import app_config

    print("启动 FastAPI 服务器 ...")
    print(f"API 文档地址: http://localhost:{app_config.SERVER_PORT}/docs")
    print(f"ReDoc 文档地址: http://localhost:{app_config.SERVER_PORT}/redoc")

    uvicorn.run(
        app, host=app_config.SERVER_HOST, port=app_config.SERVER_PORT, reload=True
    )
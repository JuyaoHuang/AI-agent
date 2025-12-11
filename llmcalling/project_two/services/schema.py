from pydantic import BaseModel, Field


class TranslateRequest(BaseModel):
    text: str = Field(..., description="需要翻译的原文", min_length=1)
    target_lang: str = Field("English", description="目标语言，默认为英语")


class TranslateResponse(BaseModel):
    original_text: str
    translated_text: str
    detected_language: str = "unknown"


from pydantic import BaseModel, Field
from typing import List, Optional

class TranslateRequest(BaseModel):
    text: str = Field(..., description="需要翻译的原文", min_length=1)
    target_lang: str = Field("English", description="目标语言，默认为英语")


class TranslateResponse(BaseModel):
    original_text: str
    translated_text: str
    detected_language: str = "unknown"


class SummaryRequest(BaseModel):
    text: str = Field(..., description="需要总结的长文本", min_length=1)
    word_limit : int = Field(100, description="限制的字数，默认 100 字", ge=10, le=500)


class SummaryResponse(BaseModel):
    summary: str = Field(...)
    tags: List[str] = Field(...)

import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Generator

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("ALIYUN_API_KEY"),
    base_url=os.environ.get("ALIYUN_BASE_URL"),
)


class LLMCalling:

    # @staticmethod 作用是把一个类中的方法变成静态方法
    # 使得调用此方法时不需要传入类的 self 参数，
    # 它只是为了代码管理的方便，被扔进了类这个容器里
    @staticmethod
    def llmcalling(model: str, messages: list, temperature: float) -> str:
        """
        :param model: 模型名字
        :param messages: 发送的消息
        :param temperature: 温度值
        :return: 完整的响应
        """
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )

        return response.choices[0].message.content

    @staticmethod
    def llmcalling_stream_block(model: str, messages: list, temperature: int) -> Generator[str, None, None]:
        """
        以流式输出的形式返回每一个块（不使用思考模式）
        :param model:
        :param messages:
        :param temperature:
        :return:
        """
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                # 使用 yield 代替 return，将数据实现流式输出
                yield content





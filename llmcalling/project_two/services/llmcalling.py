import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.environ.get("ALIYUN_API_KEY"),
    base_url=os.environ.get("ALIYUN_BASE_URL"),
)


def llmcalling(model: str, messages: list, temperature: int) -> str:
    """

    :param model:
    :param messages:
    :param temperature:
    :return:
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )

    return response.choices[0].message.content
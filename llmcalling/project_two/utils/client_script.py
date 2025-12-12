import requests

BASE_URL = "http://127.0.0.1:8028"

def api_translate(text: str, target_lang: str):
    """调用后端翻译接口"""
    url = f"{BASE_URL}/api/translate"
    payload = {
        "text": text,
        "target_lang": target_lang
    }

    print("正在调用翻译 API...")

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API 调用失败: {response.text}"}
    except requests.exceptions.ConnectionError:
        return {"error": "无法连接到后端服务，请检查 FastAPI 是否已启动 (Port 8028)"}


def api_summary(text: str, word_limit: int):
    """调用后端摘要接口"""
    url = f"{BASE_URL}/api/summary"
    payload = {
        "text": text,
        "word_limit": word_limit
    }
    print("正在调用总结摘要 API...")
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API 调用失败: {response.text}"}
    except requests.exceptions.ConnectionError:
        return {"error": "无法连接到后端服务，请检查 FastAPI 是否已启动 (Port 8028)"}


if __name__ == '__main__':
    print("测试：翻译或者总结\n")
    op = input("输入要调用的API: ")
    if op == '翻译':
        text = input("输入要翻译的内容：")
        lang = input("输入要翻译的语言：")
        response = api_translate(text, lang)
        print(response)
    elif op == "总结":
        text = input("输入要总结的长文本：")
        word_limit = int(input("输入限制的字数："))
        response = api_summary(text, word_limit)
        print(response)

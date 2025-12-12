import requests


def translate_test(text: str, target_lang: str):
    url = "http://127.0.0.1:8028/api/translate"
    payload = {
        "text": text,
        "target_lang": target_lang
    }

    print("正在调用翻译 API...")
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        data = response.json()
        print(f"翻译结果: {data['translated_text']}")
        print(f"识别语言: {data['detected_language']}")
    else:
        print("调用失败:", response.text)


def summary_test(text: str, word_limit: int):
    url = "http://127.0.0.1:8028/api/summary"
    pay_load = {
        "text": text,
        "word_limit": word_limit
    }
    print("正在调用总结摘要 API...")
    response = requests.post(url, json=pay_load)
    if response.status_code == 200:
        data = response.json()
        print(f"摘要：{data['summary']}")
        print(f"标签：{data['tags']}")
    else:
        print("调用失败:", response.text)


if __name__ == '__main__':
    print("测试：翻译或者总结\n")
    op = input("输入要调用的API: ")
    if op == '翻译':
        text = input("输入要翻译的内容：")
        lang = input("输入要翻译的语言：")
        translate_test(text, lang)
    elif op == "总结":
        text = input("输入要总结的长文本：")
        word_limit = int(input("输入限制的字数："))
        summary_test(text, word_limit)

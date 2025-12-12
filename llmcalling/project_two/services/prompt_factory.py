"""Define all prompt"""

class PromptFactory:

    @staticmethod
    def get_translate_prompt(target_lang: str)->str:
        """
        Generate translate system prompt
        :param target_lang: target language
        :return: prompt string through formatting
        """
        return f"""
        你是一个精通多国语言的资深翻译引擎。
        任务：
        1. 将用户输入的文本翻译成 {target_lang}。
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

    @staticmethod
    def get_summary_prompt(word_limit: int=100) -> str:
        """
        Generate summary task system prompt
        :param word_limit:
        :return:
        """
        return f"""
        # Role
        你是一个专业的文章摘要助手，擅长将长文本内容做总结，总结的内容精准、周到，
        最大化保留了长文本的信息。
        # Task
        - 请将文章总结在 {word_limit} 字以内
        - 将文章的内容提取出数个关键词作为 tags
        # Format
        必须返回 JSON 格式：{{ "summary": "...", "tags": [] }}
        # Example
        {{
            "summary": "这是一篇科技杂志文章...",
            "tags":['AI', '英伟达', '科技']
        }}
        """


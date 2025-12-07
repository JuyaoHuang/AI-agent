"""
Prompt Engine 练习
reference:
1. 角色扮演
2. CoT
3. 结构化输出/约束
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("ALIYUN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def get_responses(messages):
    reasoning_content = []
    is_answering = False
    responses = client.chat.completions.create(
        model="qwen3-vl-32b-thinking",
        messages=messages,
        temperature=0.5,
        extra_body={
            "enable_thinking": True,
            "thinking_budget": 500,
        },
        stream=True,
        stream_options={"include_usage": True}
    )
    print("\n" + "=" * 30 + "思考过程" + "=" * 30 + "\n")
    response_chunk = []
    for chunk in responses:
        if not chunk.choices:
            print("\n消耗的token：\n")
            print(chunk.usage)
        else:
            delta = chunk.choices[0].delta
            if hasattr(delta, "reasoning_content") and delta.reasoning_content != None:
                print(delta.reasoning_content, end="", flush=True)
                reasoning_content.append(delta.reasoning_content)
            else:
                if delta.content != "" and is_answering is False:
                    print("\n" + "=" * 30 + "回复过程" + "=" * 30 + "\n")
                    is_answering = True
                print(delta.content, end="", flush=True)
                response_chunk.append(delta.content)

    full_response = "".join(response_chunk)
    print("\n")
    return full_response


prompt_dict = {
    "RCTFE_prompt": """
    # Role
    你是一个专门负责电商转化的 AI 文案助手。你精通用户心理学，特别是“痛点营销”。

    # Context
    用户输入是一段关于产品的原始参数数据。你需要将其转化为直击用户痛点的营销文案。

    # Task
    分析用户提供的产品参数，识别出它解决了什么具体问题，然后编写文案。

    # Steps (思维链 CoT)
    1. 首先，分析产品参数，找出核心卖点。
    2. 思考这个卖点解决了用户的什么烦恼（痛点）。
    3. 最后，基于痛点编写文案。

    # Examples (Few-Shot)
    输入: "雨伞，重 100g，碳纤维骨架"
    输出:
    {
      "pain_point": "普通雨伞太重，包里放不下。",
      "selling_point": "只有 100g，比手机还轻。",
      "copy": "忘记带伞是因为伞太重？这把碳纤维雨伞只有 100g，让你的包包从此减负。"
    }

    # Input Data
    产品: QuietPod 耳机
    参数: 主动降噪深度 45dB，续航 30 小时，佩戴无感。

    # Output Format (JSON Only)
    请仅返回 JSON 格式数据，不要包含 Markdown 标记。格式如下：
    {
      "pain_point": "string",
      "selling_point": "string",
      "copy": "string"
    }
    """,
    "RASCEF_prompt": """
    # Role (角色)
    你是一名专注于“转化率优化 (CRO)”的资深电商文案策划。你擅长将枯燥的技术参数转化为直击用户痛点的各种场景化描述。
    
    # Action (行动)
    请根据提供的产品信息，撰写一段用于产品落地页（Landing Page）的销售文案。文案必须能激发购买欲望，并引导用户下单。
    
    # Content (上下文/背景)
    - 产品名称：QuietPod Pro
    - 核心参数：主动降噪深度 45dB，单次续航 30 小时，重量仅 3.5g。
    - 目标受众：需要在开放式办公室工作的程序员、长期出差的商务人士。
    - 用户痛点：无法集中注意力，环境噪音导致焦虑，普通耳机戴久了耳朵疼。
    
    # Script (步骤)---- CoT
    请严格遵循以下步骤进行创作：
    1. 吸引 (Hook)：用一个反问句开场，直接点出目标受众当前的痛点（噪音干扰）。
    2. 连接 (Connect)：解释为什么这个痛点很糟糕（影响效率/心情），产生共鸣。
    3. 解决方案 (Solution)：引入产品，并将“参数”转化为“利益点”（例如：不要说45dB，要说“就像进入了图书馆”）。
    4. 行动 (Call to Action)：给出一个强有力的结尾，鼓励尝试。
    
    # Example (示例)
    [输入]: 
    产品：极速干发帽；参数：吸水力强，3分钟干发；痛点：吹头发太累，伤发质。
    [输出]:
    *还在为每晚吹头发浪费半小时而烦恼吗？
    高温吹风不仅让人烦躁，更是枯草发质的元凶。是时候改变了。
    介绍全新的“极速干发帽”——它不是普通的毛巾，而是你的时间救星。
    超微纤维技术瞬间吸走水分，无需通电，只需 3 分钟，即可享受清爽。把时间留给追剧，而不是举着沉重的吹风机。
    今晚就给你的头发放个假。
    
    # Format (格式)
    请输出 Markdown 格式，包含：
    - 标题 (H3)
    - 正文 (分段，口语化)
    - 核心卖点列表 (使用 ✅ 符号作为列表头)
    """,
    "BPSTAO_prompt": """
    # Background
    我们需要为新款降噪耳机 "QuietPod Pro" 撰写一段品牌宣言。
    目前的耳机市场充斥着对“重低音”和“酷炫外观”的宣传，但我们的产品主打极致的“静谧”和“舒适”，专为需要长时间保持专注的深度工作者（Deep Workers）设计。
    核心参数：45dB 降噪，佩戴无感，30小时续航。
    
    # Purpose
    文案的目的是建立品牌的高端形象，而不是单纯的促销。
    我们需要让用户觉得，购买的不是一个电子配件，而是一张通往“心流状态（Flow State）”的门票。激发用户对“专注”的向往。
    
    # Style
    请模仿 苹果官方文案（Apple Style） 结合 《原子习惯》作者 James Clear 的写作风格。
    特点：极简主义、短句为主、富有哲理、直击本质。拒绝任何花哨的形容词
    
    # Tone
    冷静的 (Calm)、自信的 (Confident)、理性的 (Intellectual)
    不要使用感叹号，不要使用促销口吻（如“买到就是赚到”）
    
    # Audience
    高级软件工程师、作家、学术研究者
    他们讨厌噪音，讨厌被打扰，重视效率，愿意为生产力工具付费。他们能一眼看穿廉价的营销话术
    
    # Output
    请生成一段适用于官网首页（Hero Section）的中文文案。
    格式要求：
    1. 一个由 2-4 个单词组成的主标题
    2. 一段不超过 50 字的副标题
    3. 三个简短的价值主张（不谈参数，只谈体验）
    """,
    "CRISPE_prompt": """
    # Capacity and Role
    你是一名精通社交媒体算法的 Instagram/小红书 内容创作者。你擅长制造“爆款”文案，懂得如何通过情绪共鸣引发年轻人的互动
    
    # Insight
    现在的年轻人（Gen Z 和千禧一代）在通勤路上非常痛苦。地铁的轰鸣声、旁边人的大声交谈、婴儿的哭闹，让他们感到“感官过载（Sensory Overload）”
    他们买降噪耳机不是为了听歌，而是为了“逃避现实”和“保命”。
    产品 QuietPod Pro 的 45dB 降噪就是他们的“救命稻草”
    
    # Statement
    请为 QuietPod Pro 撰写一篇社交媒体种草文案
    不要写成硬广，要写成像是朋友之间的好物分享
    
    # Personality (个性/格式)
    风格要 Relatable (有共鸣的)、Witty (机智幽默的)
    多使用 Emoji 🥹🎧✨
    格式：短段落，视觉化语言
    
    # Experiment
    请提供 3 个不同角度 的文案选项，以便我做 A/B 测试：
    1.  选项 A (幽默吐槽风)：重点吐槽地铁里的奇葩噪音
    2.  选项 B (emo 氛围风)：重点描写下班后的疲惫和独处的治愈
    3.  选项 C (极简种草风)：简单粗暴，直击痛点
    """,
    "RASCEF_optimize_prompt": """
    角色: 你是一名专注于“转化率优化 (CRO)”的资深电商文案策划。你擅长将枯燥的技术参数转化为直击用户痛点的各种场景化描述。
    行动: 请根据提供的产品信息，撰写一段用于产品落地页（Landing Page）的销售文案。文案必须能激发购买欲望，并引导用户下单。
    步骤: 请严格遵循以下步骤进行创作：(1) 吸引 (Hook)：用一个反问句开场，直接点出目标受众当前的痛点（噪音干扰）。(2) 连接 (Connect)：解释为什么这个痛点很糟糕（影响效率/心情），产生共鸣。(3) 解决方案 (Solution)：引入产品，并将“参数”转化为“利益点”（例如：不要说45dB，要说“就像进入了图书馆”）。(4) 行动 (Call to Action)：给出一个强有力的结尾，鼓励尝试。
    上下文: 产品名称：QuietPod Pro核心参数：主动降噪深度 45dB，单次续航 30 小时，重量仅 3.5g。目标受众：需要在开放式办公室工作的程序员、长期出差的商务人士。用户痛点：无法集中注意力，环境噪音导致焦虑，普通耳机戴久了耳朵疼。
    示例: 【案例】产品：QuietPod Pro；参数：主动降噪深度 45dB，单次续航 30 小时，重量仅 3.5g；痛点：开放式办公环境中的噪音干扰，长时间佩戴耳机的不适感。输出：### 受够了开放式办公室的噪音轰炸？让QuietPod Pro成为你的私人隔音室！* 是否曾因同事的电话声、打印机的轰鸣而无法集中精神？这些噪音不仅破坏了你的工作节奏，还让你的心情跌入谷底。* 现在，想象一下，只需轻轻一按，整个世界仿佛静止，就像进入了图书馆一样宁静。这就是QuietPod Pro带来的奇迹。* 主动降噪技术，深度达到惊人的45dB，相当于将你置身于一片寂静之中。长达30小时的续航能力，让你无论是在办公室还是长途飞行中，都能持续享受宁静。轻盈的3.5g设计，即使长时间佩戴也毫无负担。* 不再让噪音成为你的困扰，QuietPod Pro，你的专注守护者。立即体验，让高效工作成为日常。
    格式: 请输出 Markdown 格式，包含：标题 (H3)，正文 (分段，口语化)，核心卖点列表 (使用 ✅ 符号作为列表头)。
    """,
}


def main():
    messages = [{"role": "system", "content": prompt_dict["RASCEF_optimize_prompt"]}]
    print(f"开始进行思考模式测试，按 exit 退出\n")

    user_input = "设计一个推销 QuietPod 降噪耳机的文案"

    messages.append({"role": "user", "content": user_input})

    response = get_responses(messages)

    messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()




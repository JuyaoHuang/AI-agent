"""
项目1：构建一个多功能角色聊天机器人

目标: 熟练使用 OpenAI API和 Prompt Engineering
任务: 创建一个简单的 Web 界面（用 Streamlit ），
用户可以选择不同的角色（如“Python编程助手”、“英语口语教练”、“苏格拉底”），
程序会根据选择，使用不同的System Prompt与用户进行高质量对话。
收获: 精通API调用、掌握核心的提示工程技巧

run:
streamlit run llmcalling/project_one/character_build.py
"""

import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
from prompt_infactor import system_prompts

load_dotenv()

st.set_page_config(page_title="AI Character Building", page_icon="🥰")

client = OpenAI(
    api_key=os.environ.get("ALIYUN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# Sidebar building
with st.sidebar:
    st.header("🎭 Choose a character")
    selected_role = st.selectbox("Please choose an AI chatbot: ", list(system_prompts.keys()))

    system_prompt = system_prompts[selected_role]

    if st.button("Clear chat history"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.write(f"Current Prompt: \n{system_prompt}")


# state management
# if messages not in statement, initialize it
if "messages" not in st.session_state:
    st.session_state.messages = []

# Character change logic
if "current_role" not in st.session_state:
    st.session_state.current_role = selected_role
elif st.session_state.current_role != selected_role:
    # current role is not selected role => chat character has changed
    # clear chat history
    st.session_state.messages = []
    st.session_state.current_role = selected_role

# Render chat history and display in the box
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "reasoning" in msg and msg["reasoning"]:
            with st.status("Finish thinking", state="complete", expanded=False):
                st.markdown(msg["reasoning"])
        st.write(msg["content"])

# Controller: process user input
if user_input := st.chat_input("Chat with it..."):
    # 1. show user input
    with st.chat_message("User:"):
        st.write(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})

    # 2. build API request with complete message: [system prompt] + [history]
    api_messages = [
        {"role": "system", "content": system_prompt},
    ] + st.session_state.messages

    # 3. get stream responses
    with st.chat_message("assistant"):
        status_box = st.status("🤔 AI 正在深度思考...", expanded=True)
        with status_box:
            reasoning_placeholder = st.empty()
        content_placeholder = st.empty()

        responses = client.chat.completions.create(
            model="qwen3-vl-32b-thinking",
            messages=api_messages,
            temperature=0.6,
            # 注意：只有特定模型支持 extra_body 参数，如果报错请确认模型文档
            extra_body={
                "enable_thinking": True,
                "thinking_budget": 500,
            },
            stream=True,
            stream_options={"include_usage": True}
        )

        # 4. process returned chunks
        reasoning_chunks = []
        content_chunks = []
        for chunk in responses:
            # process message contain token used which is the last chunk
            if not chunk.choices:
                usage = f"Consume Token: {chunk.usage.total_tokens}"
                status_box.update(label="Thinking end.  " + usage, state="complete", expanded=False)
                print(usage, end='', flush=True)
            else:
                delta = chunk.choices[0].delta
                # process reasoning content
                access_chunk = getattr(delta, "reasoning_content", None)
                if access_chunk:
                    print(access_chunk, end='', flush=True)
                    reasoning_chunks.append(access_chunk)
                    # refresh UI in real time
                    reasoning_placeholder.markdown("".join(reasoning_chunks))

                # process response content
                if delta.content:
                    print(delta.content, end='', flush=True)
                    content_chunks.append(delta.content)
                    content_placeholder.markdown("".join(content_chunks) + "▌")

        full_reasoning = "".join(reasoning_chunks)
        full_content = "".join(content_chunks)

        # remove "▌" and show complete response content
        content_placeholder.markdown(full_content)

        st.session_state.messages.append({
            "role": "assistant",
            "content": full_content,
            "reasoning": full_reasoning,
        })


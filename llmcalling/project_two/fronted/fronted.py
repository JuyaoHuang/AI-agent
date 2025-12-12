"""前端 Streamlit 应用"""
import streamlit as st
import sys
import os
# 获取当前脚本所在的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 将这个路径加入到 Python 的搜索路径 (sys.path) 中
if current_dir not in sys.path:
    sys.path.append(current_dir)
# 别理会 IDE 的报错
from utils.client_script import api_summary, api_translate


st.set_page_config(page_title="Atri tools box", page_icon="🧰", layout="wide")

st.title("🚀Atri tools box")

st.sidebar.title("功能导航")
page = st.sidebar.radio("选择工具", ["🌍 智能翻译", "📝 文章摘要"])

if page == "🌍 智能翻译":
    st.header("多语言智能翻译")

    # 左右布局：左边输入，右边显示结果
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("输入")
        input_text = st.text_area("请输入要翻译的文本", height=200, placeholder="在此输入...")
        target_lang = st.selectbox(
            "选择目标语言",
            ["English", "Chinese", "Japanese", "French", "German", "Spanish"]
        )

        # 提交按钮
        submit_btn = st.button("开始翻译", use_container_width=True)

    with col2:
        st.subheader("结果")
        # 占位符，用于显示等待状态或结果
        result_container = st.empty()

        if submit_btn and input_text:
            with st.spinner("AI 正在思考中..."):
                result = api_translate(input_text, target_lang)

                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success("翻译完成！")
                    st.text_area("译文", value=result['translated_text'], height=150)
                    st.info(f"检测到的源语言: {result['detected_language']}")


elif page == "📝 文章摘要":
    st.header("长文本智能摘要")

    input_text = st.text_area("请输入长文章", height=250)

    # 滑块控制字数
    word_limit = st.slider("摘要字数限制", min_value=50, max_value=500, value=100, step=10)

    if st.button("生成摘要"):
        if not input_text:
            st.warning("请先输入文本！")
        else:
            with st.spinner("AI 正在阅读文章并总结..."):
                result = api_summary(input_text, word_limit)

                if "error" in result:
                    st.error(result["error"])
                else:
                    st.divider()
                    st.subheader("📄 摘要内容")
                    st.write(result['summary'])

                    st.subheader("🏷️ 关键标签")
                    # 使用 Streamlit 的标签组件 (st.pills 是新版功能，旧版可用 st.caption)
                    try:
                        st.pills("Tags", result['tags'])
                    except AttributeError:
                        st.write(" | ".join([f"`{tag}`" for tag in result['tags']]))


st.sidebar.markdown("---")
st.sidebar.caption("Backend: FastAPI | Frontend: Streamlit")

# streamlit run llmcalling/project_two/fronted/fronted.py


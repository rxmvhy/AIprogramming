import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="AI 앱", page_icon="🤖")

# 모든 페이지에서 사용할 API 키 입력칸
with st.sidebar:
    api_key = st.text_input("OpenAI API Key", type="password")

# 입력된 키로 client를 만들고 세션에 저장
if api_key:
    st.session_state["openai_client"] = OpenAI(api_key=api_key)
    st.session_state["openai_api_key"] = api_key
else:
    st.session_state.pop("openai_client", None)
    st.session_state.pop("openai_api_key", None)

# 페이지 목록
pg = st.navigation([
    st.Page("app_pages/Home.py", title="Home", icon=":material/home:"),
    st.Page("app_pages/Chat.py", title="Chat", icon=":material/chat:"),
    st.Page("app_pages/Chatbot.py", title="Chatbot", icon=":material/local_library:"),
    st.Page("app_pages/ChatPDF.py", title="ChatPDF", icon=":material/picture_as_pdf:"),
])

# 선택된 페이지 실행
pg.run()
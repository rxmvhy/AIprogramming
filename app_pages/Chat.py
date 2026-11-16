import streamlit as st


def clear_chat():
    # Clear 버튼을 누르면 대화 기록을 비움
    st.session_state["messages"] = []


def text_chunks(stream):
    # API 스트림에서 텍스트 조각만 꺼내 화면에 전달
    for event in stream:
        if event.type == "response.output_text.delta":
            yield event.delta


st.title("Chat")

# streamlit_app.py에서 만든 OpenAI client 확인
if "openai_client" not in st.session_state:
    st.info("왼쪽 사이드바에 OpenAI API Key를 입력하세요.")
    st.stop()

# 처음 페이지를 열었을 때 대화 목록 만들기
if "messages" not in st.session_state:
    st.session_state["messages"] = []

client = st.session_state["openai_client"]

# 클릭하면 clear_chat 함수가 실행됨
st.button("Clear", on_click=clear_chat)

# 저장된 이전 대화 표시
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 채팅 입력창
prompt = st.chat_input("메시지를 입력하세요")

if prompt:
    # 사용자 질문을 대화 기록에 추가하고 화면에 표시
    st.session_state["messages"].append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Responses API에 전체 대화 기록을 보내고 응답을 스트리밍
    assistant_response = ""

    with st.chat_message("assistant"):
        try:
            stream = client.responses.create(
                model="gpt-6-luna",
                input=st.session_state["messages"],
                stream=True
            )

            assistant_response = st.write_stream(text_chunks(stream))

        except Exception as error:
            st.error(f"응답 생성 중 오류가 발생했습니다: {error}")

    # 받은 답변도 기록해 다음 질문에서 참고하게 함
    if assistant_response:
        st.session_state["messages"].append({
            "role": "assistant",
            "content": assistant_response
        })
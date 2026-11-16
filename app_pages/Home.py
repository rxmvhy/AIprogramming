import base64
import streamlit as st


@st.cache_data(show_spinner=False)
def get_answer(question, api_key_for_cache, _client):
    response = _client.responses.create(
        model="gpt-6-luna",
        input=question
    )
    return response.output_text


st.title("Home")
st.header("AI 질문 답변")

if "openai_client" not in st.session_state:
    st.info("왼쪽 사이드바에 OpenAI API Key를 입력하세요.")
    st.stop()

client = st.session_state["openai_client"]
api_key = st.session_state["openai_api_key"]

question = st.text_area("질문을 입력하세요")

if st.button("답변 받기"):
    if not question.strip():
        st.warning("질문을 입력하세요.")
    else:
        try:
            with st.spinner("답변을 생성하고 있어요..."):
                answer = get_answer(question, api_key, client)
            st.write(answer)
        except Exception as error:
            st.error(f"답변 요청 중 오류가 발생했습니다: {error}")


st.divider()
st.header("이미지 생성")

image_prompt = st.text_area(
    "만들고 싶은 이미지를 설명하세요",
    key="image_prompt"
)

if st.button("이미지 생성"):
    if not image_prompt.strip():
        st.warning("이미지 프롬프트를 입력하세요.")
    else:
        try:
            with st.spinner("이미지를 생성하고 있어요..."):
                img = client.images.generate(
                    model="gpt-image-2.6-flare",
                    prompt=image_prompt
                )

                image_bytes = base64.b64decode(
                    img.data[0].b64_json
                )

            st.image(image_bytes)

        except Exception as error:
            st.error(f"이미지 생성 중 오류가 발생했습니다: {error}")
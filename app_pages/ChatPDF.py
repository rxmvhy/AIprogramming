import streamlit as st


def text_chunks(stream):
    # 스트림에서 답변 텍스트만 꺼냄
    for event in stream:
        if event.type == "response.output_text.delta":
            yield event.delta


st.title("ChatPDF")

if "openai_client" not in st.session_state:
    st.info("왼쪽 사이드바에 OpenAI API Key를 입력하세요.")
    st.stop()

client = st.session_state["openai_client"]

# 대화와 파일 정보를 세션에 보관
if "pdf_messages" not in st.session_state:
    st.session_state["pdf_messages"] = []

if "pdf_upload_version" not in st.session_state:
    st.session_state["pdf_upload_version"] = 0

# 파일은 한 개만 받음
uploaded_file = st.file_uploader(
    "질문할 PDF 파일을 업로드하세요",
    type=["pdf"],
    accept_multiple_files=False,
    key=f"pdf_uploader_{st.session_state['pdf_upload_version']}"
)

# 파일이 선택됐고, 아직 vector store가 없을 때만 한 번 생성
if uploaded_file is not None and "pdf_vector_store_id" not in st.session_state:
    vector_store = None
    uploaded = None

    try:
        with st.spinner("PDF를 업로드하고 검색할 수 있게 준비하고 있어요..."):
            uploaded = client.files.create(
                file=(uploaded_file.name, uploaded_file.getvalue()),
                purpose="assistants"
            )

            vector_store = client.vector_stores.create(
                name=uploaded_file.name
            )

            indexed_file = client.vector_stores.files.create_and_poll(
                vector_store_id=vector_store.id,
                file_id=uploaded.id
            )

            if indexed_file.status != "completed":
                raise RuntimeError(
                    f"PDF 색인에 실패했습니다: {indexed_file.status}"
                )

        st.session_state["pdf_vector_store_id"] = vector_store.id
        st.session_state["pdf_file_id"] = uploaded.id
        st.session_state["pdf_filename"] = uploaded_file.name

    except Exception as error:
        # 업로드나 색인에 실패하면 만들어진 리소스를 정리
        if vector_store is not None:
            client.vector_stores.delete(
                vector_store_id=vector_store.id
            )
        if uploaded is not None:
            client.files.delete(file_id=uploaded.id)

        st.error(f"PDF 준비 중 오류가 발생했습니다: {error}")
        st.stop()


# PDF 준비가 끝났으면 대화 기능 표시
if "pdf_vector_store_id" in st.session_state:
    st.success(f"업로드 완료: {st.session_state['pdf_filename']}")

    clear_col, leave_col = st.columns(2)

    # Clear: 대화만 지우고 vector store는 유지
    if clear_col.button("Clear"):
        st.session_state["pdf_messages"] = []

    # Leave: vector store와 업로드 파일을 지우고 업로드 화면으로 돌아감
    if leave_col.button("Leave"):
        try:
            client.vector_stores.delete(
                vector_store_id=st.session_state["pdf_vector_store_id"]
            )
            client.files.delete(
                file_id=st.session_state["pdf_file_id"]
            )

            st.session_state.pop("pdf_vector_store_id", None)
            st.session_state.pop("pdf_file_id", None)
            st.session_state.pop("pdf_filename", None)
            st.session_state["pdf_messages"] = []

            # 파일 선택창을 초기화
            st.session_state["pdf_upload_version"] += 1
            st.rerun()

        except Exception as error:
            st.error(f"파일 정리 중 오류가 발생했습니다: {error}")

    # 저장된 대화 표시
    for message in st.session_state["pdf_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("PDF 내용에 대해 질문하세요")

    if prompt:
        st.session_state["pdf_messages"].append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        answer = ""

        with st.chat_message("assistant"):
            try:
                stream = client.responses.create(
                    model="gpt-6-luna",
                    instructions=(
                        "업로드한 PDF의 내용만 근거로 답하세요. "
                        "PDF에서 확인할 수 없는 내용은 추측하지 말고 "
                        "'PDF에서 확인할 수 없습니다'라고 답하세요."
                    ),
                    input=st.session_state["pdf_messages"],
                    tools=[{
                        "type": "file_search",
                        "vector_store_ids": [
                            st.session_state["pdf_vector_store_id"]
                        ]
                    }],
                    stream=True
                )

                answer = st.write_stream(text_chunks(stream))

            except Exception as error:
                st.error(f"답변 생성 중 오류가 발생했습니다: {error}")

        if answer:
            st.session_state["pdf_messages"].append({
                "role": "assistant",
                "content": answer
            })

else:
    st.info("먼저 PDF 파일을 업로드하세요.")
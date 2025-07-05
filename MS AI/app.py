import streamlit as st
from config import settings
from llm import LLM

llm = LLM(
    settings.openai_endpoint,
    settings.openai_api_key,
    settings.chat_model,
    settings.search_endpoint,
    settings.search_api_key,
    settings.index_name
    )

# 페이지 설정
st.set_page_config(page_title="인시던트 분석 대화형 에이전트 ", page_icon="🤖", layout="wide")

# 제목
st.title("🤖 인시던트 분석 대화형 에이전트")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 초기 환영 메시지
if not st.session_state.messages:
    st.session_state.messages.append({"role": "assistant", "content": "안녕하세요! 인시던트 분석 에이전트입니다."})

# 기존 메시지 출력
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").markdown(message["content"])
    else:
        st.chat_message("assistant").markdown(message["content"])

# 사용자 입력 받기
user_input = st.chat_input("내용을 입력하세요")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    def extract_last_user_message(messages):
        for m in reversed(messages):
            if m.get("role") == "user" and m.get("content"):
                return m["content"]
        return ""

    with st.spinner("분석 중입니다..."):
        try:
            user_query = extract_last_user_message(st.session_state.messages)
            analysis_result = llm.get_openai_response(user_query)
        except Exception as e:
            analysis_result = f"❌ 에러 발생: {e}"

    st.session_state.messages.append({"role": "assistant", "content": analysis_result})
    st.chat_message("assistant").markdown(analysis_result)

# 하단 정보
st.markdown("---")
st.caption("© 2025 인시던트 분석 대화형 에이전트 // MVP")
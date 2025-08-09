import streamlit as st
import datetime
from collections import defaultdict
from langchain_qa_new import convo_qa_chain, convert_streamlit_history_to_langchain

# 페이지 설정
st.set_page_config(page_title="ITSM 이력QA 에이전트", page_icon="🤖", layout="wide")

# ===== 테마 스타일 정의 =====
THEMES = {
    "라이트": """
        body { background-color: #ffffff; color: #000; }
        .stChatMessage { background-color: #f9f9f9; border-radius: 10px; padding: 10px; }
    """,
    "다크": """
        body { background-color: #1e1e1e; color: #fff; }
        .stChatMessage { background-color: #2c2c2c; border-radius: 10px; padding: 10px; }
    """,
    "네온": """
        body { background-color: #0f0f0f; color: #39ff14; }
        .stChatMessage { background-color: #1a1a1a; border-radius: 10px; padding: 10px; }
    """
}

if "theme" not in st.session_state:
    st.session_state.theme = "다크"

st.markdown(f"<style>{THEMES[st.session_state.theme]}</style>", unsafe_allow_html=True)

# 제목
st.title("🤖 ITSM 이력QA 에이전트")

# 대화 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 초기 환영 메시지
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "안녕하세요! ITSM 이력QA 에이전트입니다.",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d")
    })

# ===== 사이드바 =====
with st.sidebar:
    st.header("🎨 설정")
    theme_choice = st.radio("테마 선택", list(THEMES.keys()))
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()

    st.header("🔍 대화 검색")
    search_term = st.text_input("검색어를 입력하세요")

    st.header("📊 대화 통계")
    st.write(f"총 메시지 수: {len(st.session_state.messages)}")

    st.header("💬 대화 이력")
    if st.session_state.messages:
        grouped = defaultdict(list)
        for msg in st.session_state.messages:
            date = msg.get("timestamp", "날짜없음")
            grouped[date].append(msg)
        for date in sorted(grouped.keys()):
            with st.expander(f"📅 {date}"):
                for msg in grouped[date]:
                    role = "👤" if msg["role"] == "user" else "🤖"
                    st.markdown(f"{role} {msg['content']}")
    else:
        st.info("아직 대화 이력이 없습니다.")

# ===== 메시지 표시 =====
messages_to_display = st.session_state.messages
if search_term:
    messages_to_display = [
        m for m in messages_to_display if search_term.lower() in m["content"].lower()
    ]

for msg in messages_to_display:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ===== 사용자 입력 =====
if prompt := st.chat_input("질문을 입력하세요."):
    today = datetime.date.today().isoformat()
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": today
    })
    with st.chat_message("user"):
        st.markdown(prompt)

    chat_history = convert_streamlit_history_to_langchain(st.session_state.messages[:-1])

    with st.spinner("답변 생성 중..."):
        result = convo_qa_chain.invoke({
            "input": prompt,
            "chat_history": chat_history
        })
        answer = result["answer"] if "answer" in result else str(result)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "timestamp": today
    })
    with st.chat_message("assistant"):
        st.markdown(answer)
        if "context" in result and result["context"]:
            st.markdown("---")
            with st.expander("🔎 참고한 자료 펼치기"):
                st.markdown("**🔎 참고 문서:**")
                if isinstance(result["context"], list):
                    for i, doc in enumerate(result["context"], 1):
                        st.markdown(f"**[{i}]** {doc.page_content}")
                else:
                    st.markdown(result["context"])

# ===== 하단 정보 =====
st.markdown("---")
st.caption("© ITSM 이력QA 에이전트 // MVP")

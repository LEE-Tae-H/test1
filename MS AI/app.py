import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import re
import datetime
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
    st.session_state.messages.append({
        "role": "assistant",
        "content": "안녕하세요! 인시던트 분석 에이전트입니다.",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d")
    })

# 기존 메시지 출력
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").markdown(message["content"])
    else:
        st.chat_message("assistant").markdown(message["content"])

# 왼쪽 사이드바에 대화 이력 메뉴 추가
with st.sidebar:
    st.header("💬 대화 이력")
    if "messages" in st.session_state and st.session_state.messages:
        from collections import defaultdict
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

# 사용자 입력 받기
user_input = st.chat_input("내용을 입력하세요")

def set_korean_font():
    try:
        # 시스템 폰트 중 'Nanum'이 포함된 것 검색
        nanum_fonts = [f for f in fm.findSystemFonts(fontpaths=None, fontext='ttf') if 'Nanum' in f]
        if nanum_fonts:
            font_path = nanum_fonts[0]
            font_name = fm.FontProperties(fname=font_path).get_name()
            plt.rc('font', family=font_name)
        else:
            # 대체 한글 폰트 사용
            plt.rc('font', family='Malgun Gothic')  # Windows
    except Exception as e:
        st.warning(f"폰트 설정 오류: {e}")
        plt.rc('font', family='Malgun Gothic')  # fallback



def run_graph_code_blocks(analysis_result):
    import re
    set_korean_font()
    # 예: "A: 10건, B: 5건, C: 3건"
    items = re.findall(r'([가-힣A-Za-z0-9_]+)\s*:\s*([0-9]+)건', analysis_result)
    if items:
        labels = [item[0] for item in items]
        values = [int(item[1]) for item in items]
        fig, ax = plt.subplots()
        ax.bar(labels, values)
        ax.set_ylabel("장애 건수")
        ax.set_title("서비스별 장애 건수")
        plt.xticks(rotation=30)
        st.pyplot(fig)
    else:
        st.info("그래프를 그릴 수 있는 데이터가 포함되어 있지 않습니다.")


if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d")
    })
    st.chat_message("user").markdown(user_input)

    with st.spinner("분석 중입니다..."):
        try:
            user_query = user_input  # 질문만 전달
            analysis_result = llm.get_openai_response(user_query)
        except Exception as e:
            analysis_result = f"❌ 에러 발생: {e}"

    # 그래프 요청이 포함된 경우 코드 블록 추출 및 실행
    if any(keyword in user_input for keyword in ["그래프", "차트", "시각화"]):
        run_graph_code_blocks(analysis_result)

    st.session_state.messages.append({
        "role": "assistant",
        "content": analysis_result,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d")
    })
    st.chat_message("assistant").markdown(analysis_result)

# 하단 정보
st.markdown("---")
st.caption("© 2025 인시던트 분석 대화형 에이전트 // MVP")
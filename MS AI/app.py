import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import re
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
# prompt.md 파일을 읽어서 프롬프트로 사용
prompt_path = "prompt.md"
if os.path.exists(prompt_path):
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_text = f.read()
    response = llm.get_openai_response(prompt_text)
    print(response)
else:
    print(f"{prompt_path} 파일이 존재하지 않습니다.")

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


# incident_utf.csv를 미리 읽어 df로 제공
def run_graph_code_blocks(analysis_result):
    code_blocks = re.findall(r"```python(.*?)```", analysis_result, re.DOTALL)
    # incident_utf.csv를 미리 읽어 df로 제공
    try:
        df = pd.read_csv("incident_utf.csv", encoding="utf-8")
    except Exception as e:
        st.error(f"incident_utf.csv 파일을 읽을 수 없습니다: {e}")
        df = None
    if code_blocks:
        local_vars = {"pd": pd, "plt": plt, "st": st, "np": np, "df": df}
        for code in code_blocks:
            try:
                exec(code, {}, local_vars)
            except Exception as e:
                st.error(f"그래프 코드 실행 중 오류: {e}")
    else:
        st.info("그래프 코드가 포함되어 있지 않습니다.")


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
            # 그래프 요청이 있으면 프롬프트에 안내 문구 추가
            if any(keyword in user_input for keyword in ["그래프", "차트", "시각화"]):
                try:
                    df = pd.read_csv("incident_utf.csv", encoding="utf-8")
                    col_list = df.columns.tolist()
                    col_str = ", ".join([f"'{col}'" for col in col_list])
                    user_query += (
                        f"\n\nincident_utf.csv의 실제 컬럼명은 다음과 같아: [{col_str}]. "
                        "Streamlit 환경에서 incident_utf.csv 파일을 pandas로 읽고, df라는 이름의 데이터프레임을 사용해서 matplotlib로 그래프를 그리고, "
                        "plt.show() 대신 st.pyplot()을 사용해서 반드시 파이썬 코드 블록(예: ```python ... ```)으로 답변해줘. "
                        "그래프가 잘 보이도록 한글 폰트 설정도 추가해줘. "
                        "단, 폰트 경로를 직접 지정하지 말고, plt.rc('font', family='Malgun Gothic') 또는 plt.rc('font', family='NanumGothic')만 사용해."
                        "incident_utf.csv 파일을 제외한 다른 파일은 참고하지 말아줘."
                    )
                except Exception as e:
                    st.warning(f"컬럼명 추출 오류: {e}")
            analysis_result = llm.get_openai_response(user_query)
        except Exception as e:
            analysis_result = f"❌ 에러 발생: {e}"


    # 그래프 요청이 포함된 경우 코드 블록 추출 및 실행
    if any(keyword in user_input for keyword in ["그래프", "차트", "시각화"]):
        run_graph_code_blocks(analysis_result)

    st.session_state.messages.append({"role": "assistant", "content": analysis_result})
    st.chat_message("assistant").markdown(analysis_result)

# 하단 정보
st.markdown("---")
st.caption("© 2025 인시던트 분석 대화형 에이전트 // MVP")
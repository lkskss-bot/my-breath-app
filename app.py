import streamlit as st
import time
import pandas as pd
from datetime import datetime
import os
import streamlit.components.v1 as components

# --- 페이지 설정 ---
st.set_page_config(page_title="호흡 연습", page_icon="🧘", layout="centered")

# --- 음성 안내 함수 ---
def announce_step(text, speech_enabled):
    if speech_enabled and text:
        components.html(
            f"""<script>
                var msg = new SpeechSynthesisUtterance('{text}');
                msg.lang = 'ko-KR';
                window.speechSynthesis.speak(msg);
            </script>""", height=0,
        )

# --- 스타일 커스텀 (아이폰 17 물리적 레이아웃 고정) ---
st.markdown("""
    <style>
    .top-padding { height: 60px; } 
    .block-container { padding: 0.5rem; max-width: 100% !important; }

    /* 타이머 영역 높이 고정 */
    .fixed-height-container {
        height: 150px; display: flex; flex-direction: column;
        justify-content: center; align-items: center; text-align: center;
    }

    /* 시작/종료 버튼 강제 중앙 고정 */
    .stButton {
        display: flex !important;
        justify-content: center !important;
        width: 100%;
    }
    .stButton > button {
        width: 100% !important;
        max-width: 320px;
        border-radius: 12px;
        height: 3.8em;
        background-color: #3B8ED0;
        color: white;
        font-weight: bold;
        margin: 0 auto !important;
    }

    /* 설정 섹션 테이블화 (줄바꿈 원천 차단) */
    .setting-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }
    .setting-table td {
        padding: 5px 2px;
        vertical-align: middle;
    }
    .label-text { font-size: 13px; font-weight: bold; white-space: nowrap; }

    /* 숫자 입력창 크기 강제 축소 */
    div[data-testid="stNumberInput"] {
        min-width: 65px !important;
        max-width: 75px !important;
    }
    div[data-testid="stNumberInput"] label { display: none; }
    
    .footer { position: fixed; left: 0; bottom: 5px; width: 100%; color: #444; text-align: center; font-size: 9px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="top-padding"></div>', unsafe_allow_html=True)

# --- 데이터 관리 ---
LOG_FILE = "breathing_log.csv"
def load_data():
    if os.path.exists(LOG_FILE):
        try: return pd.read_csv(LOG_FILE)
        except: return pd.DataFrame(columns=["DATE", "PATTERN", "CYCLES", "TIME"])
    return pd.DataFrame(columns=["DATE", "PATTERN", "CYCLES", "TIME"])

def save_data_callback():
    if 'start_time' in st.session_state and st.session_state.running:
        total_time = int(time.time() - st.session_state.start_time)
        pattern_str = f"{st.session_state.inhale}-{st.session_state.hold1}-{st.session_state.exhale}-{st.session_state.hold2}"
        new_data = pd.DataFrame([[datetime.now().strftime("%m-%d %H:%M"), pattern_str, st.session_state.cycles, total_time]], 
                                columns=["DATE", "PATTERN", "CYCLES", "TIME"])
        df = load_data()
        pd.concat([df, new_data], ignore_index=True).to_csv(LOG_FILE, index=False)
        st.session_state.running = False
        st.session_state.save_success = True

# --- 세션 초기화 ---
if 'running' not in st.session_state: st.session_state.running = False
if 'cycles' not in st.session_state: st.session_state.cycles = 0
if 'save_success' not in st.session_state: st.session_state.save_success = False
if 'speech_enabled' not in st.session_state: st.session_state.speech_enabled = True
for key, val in {'inhale': 4, 'exhale': 4, 'hold1': 4, 'hold2': 4}.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 메인 UI ---
st.markdown("<h1 style='text-align:center; font-size:22px; color:#3B8ED0; margin:0;'>🧘 호흡 연습</h1>", unsafe_allow_html=True)

ui_placeholder = st.empty()
button_placeholder = st.container()

if not st.session_state.running:
    with ui_placeholder.container():
        st.markdown("<div class='fixed-height-container'><p style='color:#888; font-size:14px;'>준비가 되면 시작 버튼을 누르세요</p></div>", unsafe_allow_html=True)
    
    with button_placeholder:
        if st.button("START (시작)"):
            st.session_state.running = True
            st.session_state.start_time = time.time()
            st.session_state.cycles = 0
            st.rerun()

    # 설정 및 음성 토글 (한 줄 배치)
    st.write("---")
    s_col1, s_col2 = st.columns([2, 1])
    with s_col1: st.markdown("<p style='font-weight:bold; margin-top:10px;'>⚙️ 설정</p>", unsafe_allow_html=True)
    with s_col2: st.session_state.speech_enabled = st.toggle("음성 ON", value=st.session_state.speech_enabled)

    # 4단 가로 배치 (테이블 구조 모사)
    col1, col2, col3, col4 = st.columns([1, 2, 1, 2])
    with col1: st.markdown("<p class='label-text' style='margin-top:10px;'>들숨</p>", unsafe_allow_html=True)
    with col2: st.session_state.inhale = st.number_input("in", 1, 20, st.session_state.inhale, key="in_17")
    with col3: st.markdown("<p class='label-text' style='margin-top:10px;'>멈춤1</p>", unsafe_allow_html=True)
    with col4: st.session_state.hold1 = st.number_input("h1", 0, 20, st.session_state.hold1, key="h1_17")

    col5, col6, col7, col8 = st.columns([1, 2, 1, 2])
    with col5: st.markdown("<p class='label-text' style='margin-top:10px;'>날숨</p>", unsafe_allow_html=True)
    with col6: st.session_state.exhale = st.number_input("ex", 1, 20, st.session_state.exhale, key="ex_17")
    with col7: st.markdown("<p class='label-text' style='margin-top:10px;'>멈춤2</p>", unsafe_allow_html=True)
    with col8: st.session_state.hold2 = st.number_input("h2", 0, 20, st.session_state.hold2, key="h2_17")

    # 최근 기록
    st.markdown("<p style='margin-top:20px; font-weight:bold; border-bottom:1px solid #444;'>📊 최근 기록</p>", unsafe_allow_html=True)
    df = load_data()
    if not df.empty:
        st.table(df.tail(3).iloc[::-1])

else:
    with button_placeholder:
        st.button("STOP & SAVE (중단 및 저장)", on_click=save_data_callback)

    pattern_list = [
        ("INHALE", st.session_state.inhale, "#3B8ED0", "들이마십니다"),
        ("HOLD", st.session_state.hold1, "#2CC985", "멈춥니다"),
        ("EXHALE", st.session_state.exhale, "#E74C3C", "내뱉습니다"),
        ("HOLD", st.session_state.hold2, "#F39C12", "비우고 멈춥니다")
    ]
    
    while st.session_state.running:
        for idx, (name, dur, color, speech_text) in enumerate(pattern_list):
            if dur == 0 or not st.session_state.running: continue
            announce_step(speech_text, st.session_state.speech_enabled)
            for remaining in range(dur, 0, -1):
                if not st.session_state.running: break
                elapsed = int(time.time() - st.session_state.start_time)
                mins, secs = divmod(elapsed, 60)
                with ui_placeholder.container():
                    st.markdown(f"""
                    <div class='fixed-height-container'>
                        <div style='width:90%; text-align:right; font-size:11px; color:#777;'>⏱ {mins:02d}:{secs:02d} | 🔄 {st.session_state.cycles}회</div>
                        <p style='color:{color}; font-size:22px; font-weight:bold; margin:5px 0;'>{name}</p>
                        <div style='font-size:70px; font-weight:bold; color:{color}; line-height:1;'>{remaining}</div>
                        <p style='font-size:13px; color:#888;'>{speech_text}</p>
                    </div>
                    """, unsafe_allow_html=True)
                time.sleep(1)
            if idx == 3 and st.session_state.running:
                st.session_state.cycles += 1

st.markdown('<div class="footer">Lim의 첫 모바일 작품 with Gemini</div>', unsafe_allow_html=True)

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

# --- 스타일 커스텀 (초슬림 모바일 최적화) ---
st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; padding-bottom: 0rem; }
    h1 { font-size: 22px !important; text-align: center; margin-bottom: 5px; color: #3B8ED0; }
    .stCaption { text-align: center; margin-bottom: 5px; font-size: 10px !important; }
    
    /* 숫자 입력 칸 간격 줄이기 */
    div[data-testid="stNumberInput"] { margin-bottom: -15px; }
    
    /* 버튼 스타일 */
    .stButton>button {
        width: 100%; border-radius: 10px; height: 3em;
        background-color: #3B8ED0; color: white; font-weight: bold; border: none;
    }
    
    /* 타이머 및 상태 텍스트 압축 */
    .timer-text { font-size: 50px !important; font-weight: bold; text-align: center; margin: 0px; line-height: 1.2; }
    .status-text { font-size: 18px !important; text-align: center; font-weight: bold; margin-top: 5px; }
    .guide-text { font-size: 12px; text-align: center; color: gray; margin-bottom: 5px; }
    
    /* 푸터 */
    .footer { position: fixed; left: 0; bottom: 5px; width: 100%; color: #444; text-align: center; font-size: 9px; }
    </style>
    """, unsafe_allow_html=True)

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
st.title("🧘 호흡 연습")

# 중앙 버튼 컨테이너 (시작/중단 버튼 위치 고정)
button_placeholder = st.container()

if not st.session_state.running:
    if st.session_state.save_success:
        st.success("✅ 저장 완료!")
        st.session_state.save_success = False

    with button_placeholder:
        if st.button("START (시작)"):
            st.session_state.running = True
            st.session_state.start_time = time.time()
            st.session_state.cycles = 0
            st.rerun()

    # 설정 구역
    st.write("")
    col_set, col_voice = st.columns([1, 1])
    with col_set:
        st.markdown("**⚙️ 설정**", unsafe_allow_html=True)
    with col_voice:
        st.session_state.speech_enabled = st.toggle("음성 ON", value=st.session_state.speech_enabled)

    # 2x2 그리드 배치 (들숨-멈춤1 / 날숨-멈춤2)
    c1, c2 = st.columns(2)
    st.session_state.inhale = c1.number_input("들숨 (Inhale)", 1, 20, st.session_state.inhale)
    st.session_state.hold1 = c2.number_input("멈춤1 (Hold)", 0, 20, st.session_state.hold1)
    
    c3, c4 = st.columns(2)
    st.session_state.exhale = c3.number_input("날숨 (Exhale)", 1, 20, st.session_state.exhale)
    st.session_state.hold2 = c4.number_input("멈춤2 (Hold)", 0, 20, st.session_state.hold2)

    # 최근 기록 요약 (접기 가능)
    with st.expander("📊 기록 보기", expanded=False):
        df = load_data()
        if not df.empty: st.table(df.tail(3).iloc[::-1])

else:
    # 실행 중일 때 버튼 위치 동일하게 유지
    with button_placeholder:
        st.button("STOP & SAVE (중단 및 저장)", on_click=save_data_callback)
    
    ui_space = st.empty()
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
                with ui_space.container():
                    st.markdown(f"<div style='text-align:right; font-size:11px; margin-top:10px;'>⏱ {mins:02d}:{secs:02d} | 🔄 {st.session_state.cycles}회</div>", unsafe_allow_html=True)
                    st.markdown(f"<p class='status-text' style='color:{color};'>{name}</p>", unsafe_allow_html=True)
                    st.markdown(f"<div class='timer-text' style='color:{color};'>{remaining}</div>", unsafe_allow_html=True)
                    st.markdown(f"<p class='guide-text'>{speech_text}</p>", unsafe_allow_html=True)
                time.sleep(1)
            if idx == 3 and st.session_state.running:
                st.session_state.cycles += 1

st.markdown('<div class="footer">Lim의 첫 모바일 작품 with Gemini</div>', unsafe_allow_html=True)

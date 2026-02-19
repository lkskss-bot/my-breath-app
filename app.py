import streamlit as st
import time
import pandas as pd
from datetime import datetime
import os
import streamlit.components.v1 as components

# --- 페이지 설정 ---
st.set_page_config(page_title="Mindful Breath", page_icon="🧘", layout="centered")

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

# --- 스타일 커스텀 (모바일 최적화) ---
st.markdown("""
    <style>
    /* 전체 여백 줄이기 */
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    .stApp { background-color: #0E1117; }
    
    /* 타이틀 및 텍스트 크기 축소 */
    h1 { font-size: 24px !important; text-align: center; margin-bottom: 0px; }
    .stCaption { text-align: center; margin-bottom: 10px; }
    
    /* 버튼 스타일 및 중앙 배치 */
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background-color: #3B8ED0; color: white; font-weight: bold; border: none;
        margin-top: 10px;
    }
    
    /* 타이머 섹션 콤팩트화 */
    .timer-text { font-size: 60px !important; font-weight: bold; text-align: center; margin: 5px 0; }
    .status-text { font-size: 20px !important; text-align: center; font-weight: bold; margin-bottom: 0px; }
    .guide-text { font-size: 14px; text-align: center; color: gray; margin-bottom: 10px; }
    
    /* 하단 푸터 고정 */
    .footer { position: fixed; left: 0; bottom: 5px; width: 100%; color: #444; text-align: center; font-size: 10px; }
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
for key, val in {'inhale': 4, 'exhale': 4, 'hold1': 4, 'hold2': 4}.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 메인 UI ---
st.title("🧘 MINDFUL BREATH")
st.caption("v4.5 Mobile Optimized")

# 중앙 버튼 배치를 위한 컨테이너
button_placeholder = st.container()

if not st.session_state.running:
    if st.session_state.save_success:
        st.success("✅ 저장 완료!")
        st.session_state.save_success = False

    with button_placeholder:
        if st.button("START PRACTICE (연습 시작)"):
            st.session_state.running = True
            st.session_state.start_time = time.time()
            st.session_state.cycles = 0
            st.rerun()

    with st.expander("⚙️ 설정 및 기록", expanded=False):
        speech_on = st.toggle("음성 안내", value=True)
        st.session_state.speech_enabled = speech_on
        c1, c2 = st.columns(2)
        st.session_state.inhale = c1.number_input("Inhale", 1, 20, st.session_state.inhale)
        st.session_state.exhale = c1.number_input("Exhale", 1, 20, st.session_state.exhale)
        st.session_state.hold1 = c2.number_input("Hold 1", 0, 20, st.session_state.hold1)
        st.session_state.hold2 = c2.number_input("Hold 2", 0, 20, st.session_state.hold2)
        
        st.write("---")
        df = load_data()
        if not df.empty: st.table(df.tail(3).iloc[::-1])

else:
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
                    st.markdown(f"<div style='text-align:right; font-size:12px;'>⏱ {mins:02d}:{secs:02d} | 🔄 {st.session_state.cycles}회</div>", unsafe_allow_html=True)
                    st.markdown(f"<p class='status-text' style='color:{color};'>{name}</p>", unsafe_allow_html=True)
                    st.markdown(f"<div class='timer-text' style='color:{color};'>{remaining}</div>", unsafe_allow_html=True)
                    st.markdown(f"<p class='guide-text'>{speech_text}</p>", unsafe_allow_html=True)
                time.sleep(1)
            if idx == 3 and st.session_state.running:
                st.session_state.cycles += 1

st.markdown('<div class="footer">Lim의 첫 모바일 작품 with Gemini</div>', unsafe_allow_html=True)

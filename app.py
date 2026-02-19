import streamlit as st
import time
import pandas as pd
from datetime import datetime
import os
import streamlit.components.v1 as components

# --- 페이지 설정 ---
st.set_page_config(page_title="Mindful Breath", page_icon="🧘", layout="centered")

# --- 음성 안내 함수 (스위치 상태에 따라 동작) ---
def announce_step(text, speech_enabled):
    if speech_enabled and text:
        components.html(
            f"""
            <script>
                var msg = new SpeechSynthesisUtterance('{text}');
                msg.lang = 'ko-KR';
                msg.rate = 1.0; 
                window.speechSynthesis.speak(msg);
            </script>
            """,
            height=0,
        )

# --- 스타일 커스텀 ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    .stButton>button {
        width: 100%; border-radius: 15px; height: 3em;
        background-color: #3B8ED0; color: white; font-weight: bold; border: none;
    }
    .timer-text { font-size: 80px; font-weight: bold; text-align: center; color: #3B8ED0; margin: 20px 0; }
    .status-text { font-size: 24px; text-align: center; font-weight: bold; }
    .footer {
        position: fixed; left: 0; bottom: 10px; width: 100%;
        color: #555555; text-align: center; font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 관리 함수 ---
LOG_FILE = "breathing_log.csv"

def load_data():
    if os.path.exists(LOG_FILE):
        try:
            return pd.read_csv(LOG_FILE)
        except:
            return pd.DataFrame(columns=["DATE", "PATTERN", "CYCLES", "TIME"])
    return pd.DataFrame(columns=["DATE", "PATTERN", "CYCLES", "TIME"])

def save_data_callback():
    if 'start_time' in st.session_state and st.session_state.running:
        total_time = int(time.time() - st.session_state.start_time)
        pattern_str = f"{st.session_state.inhale}-{st.session_state.hold1}-{st.session_state.exhale}-{st.session_state.hold2}"
        
        new_data = pd.DataFrame([[
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            pattern_str, 
            st.session_state.cycles, 
            total_time
        ]], columns=["DATE", "PATTERN", "CYCLES", "TIME"])
        
        df = load_data()
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(LOG_FILE, index=False)
        
        st.session_state.running = False
        st.session_state.save_success = True

# --- 세션 상태 초기화 ---
if 'running' not in st.session_state: st.session_state.running = False
if 'cycles' not in st.session_state: st.session_state.cycles = 0
if 'save_success' not in st.session_state: st.session_state.save_success = False

for key, val in {'inhale': 4, 'exhale': 4, 'hold1': 4, 'hold2': 4}.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 메인 UI ---
st.title("🧘 MINDFUL BREATH")

if not st.session_state.running:
    if st.session_state.save_success:
        st.success("✅ 기록이 안전하게 저장되었습니다!")
        st.session_state.save_success = False

    with st.expander("⚙️ 설정 (Settings)", expanded=True):
        # 음성 ON/OFF 스위치 추가
        speech_on = st.toggle("음성 안내 활성화", value=True, help="호흡 단계별로 음성 가이드를 제공합니다.")
        st.session_state.speech_enabled = speech_on
        
        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.inhale = st.number_input("Inhale (들숨)", 1, 20, st.session_state.inhale)
            st.session_state.exhale = st.number_input("Exhale (날숨)", 1, 20, st.session_state.exhale)
        with col2:
            st.session_state.hold1 = st.number_input("Hold 1 (멈춤)", 0, 20, st.session_state.hold1)
            st.session_state.hold2 = st.number_input("Hold 2 (멈춤)", 0, 20, st.session_state.hold2)
    
    if st.button("START PRACTICE (연습 시작)"):
        st.session_state.running = True
        st.session_state.start_time = time.time()
        st.session_state.cycles = 0
        st.rerun()

    st.markdown("---")
    st.subheader("📊 최근 기록 (Recent Logs)")
    df = load_data()
    if not df.empty:
        st.table(df.tail(5).iloc[::-1])
    else:
        st.info("아직 기록이 없습니다.")

else:
    st.button("STOP & SAVE (중단 및 저장)", on_click=save_data_callback)
    placeholder = st.empty()
    pattern_list = [
        ("INHALE", st.session_state.inhale, "#3B8ED0", "숨을 깊게 마십니다", "들이마십니다"),
        ("HOLD", st.session_state.hold1, "#2CC985", "머금고 멈춥니다", "멈춥니다"),
        ("EXHALE", st.session_state.exhale, "#E74C3C", "천천히 내뱉습니다", "내뱉습니다"),
        ("HOLD", st.session_state.hold2, "#F39C12", "비우고 멈춥니다", "비우고 멈춥니다")
    ]
    
    while st.session_state.running:
        for idx, (name, dur, color, guide, speech_text) in enumerate(pattern_list):
            if dur == 0 or not st.session_state.running: continue
            
            # 음성 ON/OFF 상태를 확인하여 안내 실행
            announce_step(speech_text, st.session_state.speech_enabled)
            
            for remaining in range(dur, 0, -1):
                if not st.session_state.running: break
                elapsed = int(time.time() - st.session_state.start_time)
                mins, secs = divmod(elapsed, 60)
                with placeholder.container():
                    st.markdown(f"<div style='text-align:right;'>⏱ {mins:02d}:{secs:02d} | 🔄 {st.session_state.cycles}회</div>", unsafe_allow_html=True)
                    st.markdown(f"<p class='status-text' style='color:{color};'>{name}</p>", unsafe_allow_html=True)
                    st.markdown(f"<div class='timer-text' style='color:{color};'>{remaining}</div>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align:center; color:gray;'>{guide}</p>", unsafe_allow_html=True)
                time.sleep(1)
            
            if idx == 3 and st.session_state.running:
                st.session_state.cycles += 1

st.markdown('<div class="footer">Lim의 첫 모바일 작품 with Gemini</div>', unsafe_allow_html=True)

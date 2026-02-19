import streamlit as st
import time
import pandas as pd
from datetime import datetime
import os

# --- 페이지 설정 ---
st.set_page_config(page_title="Mindful Breath", page_icon="🧘", layout="centered")

# --- 스타일 커스텀 ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        height: 3em;
        background-color: #3B8ED0;
        color: white;
        font-weight: bold;
        border: none;
    }
    .timer-text {
        font-size: 80px;
        font-weight: bold;
        text-align: center;
        color: #3B8ED0;
        margin: 20px 0;
    }
    .status-text {
        font-size: 24px;
        text-align: center;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 로드/저장 함수 ---
LOG_FILE = "breathing_log.csv"

def load_data():
    if os.path.exists(LOG_FILE):
        return pd.read_csv(LOG_FILE)
    return pd.DataFrame(columns=["DATE", "PATTERN", "CYCLES", "TIME"])

def save_data(pattern, cycles, total_seconds):
    new_data = pd.DataFrame([[
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        pattern, cycles, total_seconds
    ]], columns=["DATE", "PATTERN", "CYCLES", "TIME"])
    
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        df = pd.concat([df, new_data], ignore_index=True)
    else:
        df = new_data
    df.to_csv(LOG_FILE, index=False)

# --- 세션 상태 초기화 (중요: 변수들을 세션에 저장) ---
if 'running' not in st.session_state:
    st.session_state.running = False
if 'inhale' not in st.session_state:
    st.session_state.inhale = 4
if 'exhale' not in st.session_state:
    st.session_state.exhale = 4
if 'hold1' not in st.session_state:
    st.session_state.hold1 = 4
if 'hold2' not in st.session_state:
    st.session_state.hold2 = 4

# --- 메인 UI ---
st.title("🧘 MINDFUL BREATH")
st.caption("마음 챙김 호흡 가이드 (v4.5 Mobile)")

# 연습 중이 아닐 때만 설정창 표시
if not st.session_state.running:
    with st.expander("⚙️ 호흡 설정 (Settings)", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.inhale = st.number_input("Inhale (들숨)", 1, 20, st.session_state.inhale)
            st.session_state.exhale = st.number_input("Exhale (날숨)", 1, 20, st.session_state.exhale)
        with col2:
            st.session_state.hold1 = st.number_input("Hold 1 (멈춤)", 0, 20, st.session_state.hold1)
            st.session_state.hold2 = st.number_input("Hold 2 (멈춤)", 0, 20, st.session_state.hold2)
        
        sound_on = st.toggle("사운드 알림 (Sound)", value=True)
    
    if st.button("START PRACTICE (연습 시작)"):
        st.session_state.running = True
        st.rerun()

    st.markdown("---")
    st.subheader("📊 최근 기록 (Recent Logs)")
    df = load_data()
    if not df.empty:
        st.table(df.tail(5).iloc[::-1])
    else:
        st.info("아직 기록이 없습니다.")

# 연습 화면
else:
    placeholder = st.empty()
    # 중단 버튼 클릭 시 즉시 상태 변경 및 리런
    if st.button("STOP & SAVE (중단 및 저장)"):
        st.session_state.running = False
        st.rerun()
    
    pattern_list = [
        ("INHALE (들숨)", st.session_state.inhale, "#3B8ED0", "숨을 깊게 마십니다"),
        ("HOLD (멈춤)", st.session_state.hold1, "#2CC985", "머금고 멈춥니다"),
        ("EXHALE (날숨)", st.session_state.exhale, "#E74C3C", "천천히 내뱉습니다"),
        ("HOLD (멈춤)", st.session_state.hold2, "#F39C12", "비우고 멈춥니다")
    ]
    
    cycles = 0
    start_practice_time = time.time()
    
    try:
        while st.session_state.running:
            for idx, (name, dur, color, guide) in enumerate(pattern_list):
                if dur == 0: continue
                
                for remaining in range(dur, 0, -1):
                    elapsed = int(time.time() - start_practice_time)
                    mins, secs = divmod(elapsed, 60)
                    
                    with placeholder.container():
                        st.markdown(f"<div style='text-align:right;'>⏱ {mins:02d}:{secs:02d} | 🔄 {cycles}회</div>", unsafe_allow_html=True)
                        st.markdown(f"<p class='status-text' style='color:{color};'>{name}</p>", unsafe_allow_html=True)
                        st.markdown(f"<div class='timer-text' style='color:{color};'>{remaining}</div>", unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align:center; color:gray;'>{guide}</p>", unsafe_allow_html=True)
                    
                    time.sleep(1)
                
                if idx == 3:
                    cycles += 1
            
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
    
    # 종료 후 데이터 저장
    total_time = int(time.time() - start_practice_time)
    pattern_str = f"{st.session_state.inhale}-{st.session_state.hold1}-{st.session_state.exhale}-{st.session_state.hold2}"
    save_data(pattern_str, cycles, total_time)
    st.session_state.running = False
    st.success("기록이 저장되었습니다!")
    time.sleep(1)
    st.rerun()

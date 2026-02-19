import streamlit as st
import time
import pandas as pd
from datetime import datetime
import os

# --- 페이지 설정 ---
st.set_page_config(page_title="Mindful Breath", page_icon="🧘", layout="centered")

# --- 스타일 커스텀 (iOS 느낌의 디자인) ---
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

# --- 세션 상태 초기화 ---
if 'running' not in st.session_state:
    st.session_state.running = False

# --- 메인 UI ---
st.title("🧘 MINDFUL BREATH")
st.caption("마음 챙김 호흡 가이드 (v4.5 Mobile)")

# 설정 섹션 (연습 중에는 숨김)
if not st.session_state.running:
    with st.expander("⚙️ 호흡 설정 (Settings)", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            inhale = st.number_input("Inhale (들숨)", 1, 20, 4)
            exhale = st.number_input("Exhale (날숨)", 1, 20, 4)
        with col2:
            hold1 = st.number_input("Hold 1 (멈춤)", 0, 20, 4)
            hold2 = st.number_input("Hold 2 (멈춤)", 0, 20, 4)
        
        sound_on = st.toggle("사운드 알림 (Sound)", value=True)
    
    if st.button("START PRACTICE (연습 시작)"):
        st.session_state.running = True
        st.session_state.start_time = time.time()
        st.rerun()

    # 최근 기록 표 (메인 화면)
    st.markdown("---")
    st.subheader("📊 최근 기록 (Recent Logs)")
    df = load_data()
    if not df.empty:
        st.table(df.tail(5).iloc[::-1]) # 최신 5개 역순 표기
    else:
        st.info("아직 기록이 없습니다.")

# 연습 화면 (타이머 작동 중)
else:
    placeholder = st.empty()
    stop_btn = st.button("STOP & SAVE (중단 및 저장)")
    
    pattern_list = [
        ("INHALE (들숨)", inhale, "#3B8ED0", "숨을 깊게 마십니다"),
        ("HOLD (멈춤)", hold1, "#2CC985", "머금고 멈춥니다"),
        ("EXHALE (날숨)", exhale, "#E74C3C", "천천히 내뱉습니다"),
        ("HOLD (멈춤)", hold2, "#F39C12", "비우고 멈춥니다")
    ]
    
    cycles = 0
    start_practice_time = time.time()
    
    try:
        while st.session_state.running:
            if stop_btn: # 버튼 클릭 감지
                st.session_state.running = False
                break
                
            for idx, (name, dur, color, guide) in enumerate(pattern_list):
                if dur == 0: continue
                
                # 단계 전환 시 사운드 효과 (웹 브라우저 비프음 대용)
                # 주의: 브라우저 보안 정책상 첫 클릭 후 소리가 날 수 있음
                
                for remaining in range(dur, 0, -1):
                    if stop_btn: break
                    
                    elapsed = int(time.time() - start_practice_time)
                    mins, secs = divmod(elapsed, 60)
                    
                    with placeholder.container():
                        st.markdown(f"<div style='text-align:right;'>⏱ {mins:02d}:{secs:02d} | 🔄 {cycles}회</div>", unsafe_allow_html=True)
                        st.markdown(f"<p class='status-text' style='color:{color};'>{name}</p>", unsafe_allow_html=True)
                        st.markdown(f"<div class='timer-text' style='color:{color};'>{remaining}</div>", unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align:center; color:gray;'>{guide}</p>", unsafe_allow_html=True)
                    
                    time.sleep(1)
                
                if idx == 3: # 한 사이클 완료
                    cycles += 1
            
            if not st.session_state.running: break

    except Exception as e:
        pass
    
    # 종료 후 데이터 저장
    total_time = int(time.time() - start_practice_time)
    pattern_str = f"{inhale}-{hold1}-{exhale}-{hold2}"
    save_data(pattern_str, cycles, total_time)
    st.session_state.running = False
    st.success("기록이 저장되었습니다!")
    time.sleep(1)
    st.rerun()

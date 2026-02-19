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

# --- 스타일 커스텀 (아이폰 가로 고정 집중) ---
st.markdown("""
    <style>
    .top-padding { height: 40px; } 
    .block-container { padding: 0.5rem 0.5rem; }
    
    /* 타이머 영역 높이 고정 */
    .fixed-height-container {
        height: 140px; display: flex; flex-direction: column;
        justify-content: center; align-items: center; text-align: center;
    }

    /* 버튼 중앙 정렬 및 가로 꽉 채우기 */
    div.stButton > button {
        display: block; margin: 0 auto !important;
        width: 100% !important; border-radius: 12px; height: 3.5em;
        background-color: #3B8ED0; color: white; font-weight: bold;
    }

    /* 설정 + 음성 ON 한 줄 배치 */
    .settings-row {
        display: flex; justify-content: space-between; align-items: center;
        margin: 10px 0; border-top: 1px solid #333; padding-top: 10px;
    }

    /* 가로 한 줄 입력 칸 강제 고정 */
    .input-flex-container {
        display: flex; justify-content: space-between; align-items: center;
        gap: 5px; margin-bottom: 10px; white-space: nowrap;
    }
    .input-box-unit {
        display: flex; align-items: center; gap: 5px; width: 48%;
    }
    .input-label { font-size: 13px; font-weight: bold; min-width: 35px; }
    
    /* 스냅샷 숫자 입력창 크기 조절 */
    div[data-testid="stNumberInput"] { width: 70px !important; }
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
st.markdown("<h1 style='text-align:center; font-size:22px; color:#3B8ED0;'>🧘 호흡 연습</h1>", unsafe_allow_html=True)

ui_placeholder = st.empty()
button_placeholder = st.container()

if not st.session_state.running:
    with ui_placeholder.container():
        st.markdown("<div class='fixed-height-container'><p style='color:#777; font-size:14px;'>준비가 되면 시작 버튼을 누르세요</p></div>", unsafe_allow_html=True)
    
    with button_placeholder:
        if st.button("START (시작)"):
            st.session_state.running = True
            st.session_state.start_time = time.time()
            st.session_state.cycles = 0
            st.rerun()

    # 설정 및 음성 토글 (한 줄 배치)
    col_s1, col_s2 = st.columns([1, 1])
    with col_s1: st.markdown("<p style='margin-top:15px; font-weight:bold;'>⚙️ 설정</p>", unsafe_allow_html=True)
    with col_s2: st.session_state.speech_enabled = st.toggle("음성 ON", value=st.session_state.speech_enabled)

    # 강제 한 줄 배치 구역 (들숨/멈춤1)
    c1, c2 = st.columns(2)
    with c1:
        row1 = st.columns([1, 2])
        row1[0].markdown("<p style='margin-top:10px; font-size:13px;'>들숨</p>", unsafe_allow_html=True)
        st.session_state.inhale = row1[1].number_input("inh", 1, 20, st.session_state.inhale, label_visibility="collapsed")
    with c2:
        row2 = st.columns([1, 2])
        row2[0].markdown("<p style='margin-top:10px; font-size:13px;'>멈춤1</p>", unsafe_allow_html=True)
        st.session_state.hold1 = row2[1].number_input("h1", 0, 20, st.session_state.hold1, label_visibility="collapsed")

    # 강제 한 줄 배치 구역 (날숨/멈춤2)
    c3, c4 = st.columns(2)
    with c3:
        row3 = st.columns([1, 2])
        row3[0].markdown("<p style='margin-top:10px; font-size:13px;'>날숨</p>", unsafe_allow_html=True)
        st.session_state.exhale = row3[1].number_input("exh", 1, 20, st.session_state.exhale, label_visibility="collapsed")
    with c4:
        row4 = st.columns([1, 2])
        row4[0].markdown("<p style='margin-top:10px; font-size:13px;'>멈춤2</p>", unsafe_allow_html=True)
        st.session_state.hold2 = row4[1].number_input("h2", 0, 20, st.session_state.hold2, label_visibility="collapsed")

    # 최근 기록 상시 노출
    st.markdown("<p style='margin-top:20px; font-weight:bold;'>📊 최근 기록</p>", unsafe_allow_html=True)
    df = load_data()
    if not df.empty:
        st.dataframe(df.tail(5).iloc[::-1], use_container_width=True, hide_index=True)

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
                        <div style='width:100%; text-align:right; font-size:11px; color:#999;'>⏱ {mins:02d}:{secs:02d} | 🔄 {st.session_state.cycles}회</div>
                        <p style='color:{color}; font-size:20px; font-weight:bold; margin:5px 0;'>{name}</p>
                        <div style='font-size:65px; font-weight:bold; color:{color}; line-height:1;'>{remaining}</div>
                        <p style='font-size:13px; color:#888; margin-top:5px;'>{speech_text}</p>
                    </div>
                    """, unsafe_allow_html=True)
                time.sleep(1)
            if idx == 3 and st.session_state.running:
                st.session_state.cycles += 1

st.markdown('<div class="footer">Lim의 첫 모바일 작품 with Gemini</div>', unsafe_allow_html=True)

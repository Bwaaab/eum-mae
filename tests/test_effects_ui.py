"""
이펙트 모듈(modules/effects.py) 독립 시각 테스트 플레이그라운드
실행 명령: py -m streamlit run tests/test_effects_ui.py
"""
from pathlib import Path
import sys
import streamlit as st

# 프로젝트 루트 경로를 sys.path에 추가하여 modules 직접 임포트 보장
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules import effects
from modules.effects import EffectType, EFFECT_PRESETS

st.set_page_config(page_title="음메 - 이펙트 테스트", page_icon="✨", layout="centered")

st.title("✨ 이펙트 독립 테스트")
st.caption("modules/effects.py 시각 연출 검증용 테스트 도구")

st.divider()

# --- 1. 단일 이펙트(Atomic Effects) 테스트 ---
st.subheader("1. 단일 이펙트 테스트")
col1, col2 = st.columns([2, 1])

with col1:
    selected_atomic = st.selectbox(
        "이펙트 선택",
        options=[e.value for e in EffectType],
        format_func=lambda x: f"{x.upper()} ({x})"
    )
    duration_slider = st.slider("재생 시간 (초)", min_value=0.5, max_value=4.0, value=1.5, step=0.1)

with col2:
    st.write(" ")
    st.write(" ")
    trigger_atomic = st.button("단일 효과 실행", use_container_width=True)

if trigger_atomic:
    st.info(f"실행 중: `{selected_atomic}` ({duration_slider}초)")
    success = effects.play_atomic_effect(
        EffectType(selected_atomic),
        options={"duration": duration_slider}
    )
    if success:
        st.success("실행 완료!")
    else:
        st.warning("실행 실패 또는 미지원 연출")

st.divider()

# --- 2. 프리셋(세트) 테스트 ---
st.subheader("2. 프리셋 세트 테스트")
col3, col4 = st.columns([2, 1])

with col3:
    preset_keys = list(EFFECT_PRESETS.keys())
    selected_preset = st.selectbox("프리셋 선택", options=preset_keys)

with col4:
    st.write(" ")
    st.write(" ")
    trigger_preset = st.button("프리셋 실행", use_container_width=True)

if trigger_preset:
    st.info(f"프리셋 실행 중: `{selected_preset}`")
    success = effects.play_preset(selected_preset)
    if success:
        st.success("프리셋 완료!")

st.divider()

# --- 3. 기본 play() 인터페이스 테스트 ---
st.subheader("3. 기본 play() 테스트")
if st.button("effects.play() 호출", use_container_width=True):
    effects.play()
    st.success("play() 호출 완료!")

"""
이펙트 및 시각 연출 모듈 (modules/effects.py)
기능적 비즈니스 로직에 영향을 주지 않으며, 독립적으로 시각 연출을 렌더링합니다.
"""
from enum import Enum
import time
from typing import Any, Dict, List, Optional
import streamlit as st


# 1. 단일 이펙트 타입 정의
class EffectType(str, Enum):
    ROLLING = "rolling"       # 메뉴 추천 슬롯머신 셔플 / 긴장감 연출
    CONFETTI = "confetti"     # 축하 폭죽 파티클 (#17 구현 예정)
    GLOW = "glow"             # 카드 반짝임 CSS 효과 (#18 구현 예정)


# 2. 조합형 세트(프리셋) 정의
EFFECT_PRESETS: Dict[str, List[Dict[str, Any]]] = {
    "preset_draw": [
        {"type": EffectType.ROLLING, "options": {"duration": 1.5}}
    ],
}


def play_atomic_effect(effect: EffectType, options: Optional[Dict[str, Any]] = None) -> bool:
    """[단일 이펙트] 개별 효과를 독립적으로 화면에 출력합니다."""
    if options is None:
        options = {}

    try:
        if effect == EffectType.ROLLING:
            duration = options.get("duration", 1.5)
            # Streamlit empty placeholder를 활용한 슬롯머신 셔플 연출
            food_emojis = ["🍕", "🍔", "🍜", "🍣", "🍱", "🥘", "🍛", "🥩", "🥗", "🍲"]
            loading_texts = [
                "🐮 음메가 메뉴를 고르는 중...",
                "🎲 오늘의 운명을 결정하는 중...",
                "✨ 맛있는 선택을 탐색하는 중..."
            ]

            slot_placeholder = st.empty()
            start_time = time.time()
            idx = 0

            while time.time() - start_time < duration:
                emoji = food_emojis[idx % len(food_emojis)]
                text = loading_texts[(idx // 3) % len(loading_texts)]
                slot_placeholder.markdown(
                    f"<h3 style='text-align: center; color: #FF4B4B;'>{emoji} {text}</h3>",
                    unsafe_allow_html=True
                )
                time.sleep(0.12)
                idx += 1

            # 연출 종료 후 placeholder 정리
            slot_placeholder.empty()
            return True

        elif effect == EffectType.CONFETTI:
            # #17 이슈에서 canvas-confetti 연동 예정
            return True

        elif effect == EffectType.GLOW:
            # #18 이슈에서 CSS 글로우 주입 예정
            return True

        return False
    except Exception:
        # 이펙트 실행 중 오류가 발생하더라도 메인 기능이 멈추지 않도록 안전 방어
        return False


def play_preset(preset_name: str, options: Optional[Dict[str, Any]] = None) -> bool:
    """[세트 이펙트] 사전 정의된 연출 파이프라인을 순차 실행합니다."""
    if preset_name not in EFFECT_PRESETS:
        return False
    for step in EFFECT_PRESETS[preset_name]:
        step_opts = step.get("options", {}).copy()
        if options:
            step_opts.update(options)
        play_atomic_effect(step["type"], step_opts)
    return True


def play_effect(target: str, is_preset: bool = False, options: Optional[Dict[str, Any]] = None) -> bool:
    """[통합 엔트리포인트] 팀원용 간편 호출 함수"""
    if is_preset or target.startswith("preset_"):
        return play_preset(target, options)
    try:
        return play_atomic_effect(EffectType(target), options)
    except ValueError:
        return False


def play() -> None:
    """
    기존 app.py 연동용 기본 추첨 연출 함수
    뽑기 버튼 클릭 시 호출되어 기본 롤링 연출을 실행합니다.
    """
    play_preset("preset_draw")

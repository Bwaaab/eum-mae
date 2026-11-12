"""
이펙트 및 시각 연출 모듈 (modules/effects.py)
기능적 비즈니스 로직에 영향을 주지 않으며, 독립적으로 시각 연출을 렌더링합니다.
"""
from enum import Enum
import time
from typing import Any, Dict, List, Optional
import streamlit as st
import streamlit.components.v1 as components


# 1. 단일 이펙트 타입 정의
class EffectType(str, Enum):
    ROLLING = "rolling"       # 메뉴 추천 슬롯머신 셔플 / 긴장감 연출
    CONFETTI = "confetti"     # 축하 폭죽 파티클 (#17)
    GLOW = "glow"             # 카드 반짝임 및 등장 CSS 효과 (#18)


# 2. 조합형 세트(프리셋) 정의
EFFECT_PRESETS: Dict[str, List[Dict[str, Any]]] = {
    "preset_draw": [
        {"type": EffectType.ROLLING, "options": {"duration": 1.5}}
    ],
    "preset_celebration": [
        {"type": EffectType.GLOW, "options": {}},
        {"type": EffectType.CONFETTI, "options": {}}
    ],
    "preset_jackpot": [
        {"type": EffectType.ROLLING, "options": {"duration": 1.5}},
        {"type": EffectType.GLOW, "options": {}},
        {"type": EffectType.CONFETTI, "options": {}}
    ],
}



_CARD_GLOW_CSS = """<style>
@keyframes cardPopIn {
    0% {
        opacity: 0;
        transform: scale(0.85) translateY(16px);
    }
    60% {
        opacity: 1;
        transform: scale(1.03) translateY(-3px);
    }
    100% {
        opacity: 1;
        transform: scale(1.0) translateY(0);
    }
}

@keyframes glowPulse {
    0% {
        box-shadow: 0 0 15px rgba(255, 180, 0, 0.4), 0 0 30px rgba(255, 120, 0, 0.2);
        border-color: rgba(255, 180, 0, 0.7);
    }
    50% {
        box-shadow: 0 0 30px rgba(255, 200, 50, 0.85), 0 0 60px rgba(255, 140, 0, 0.55), 0 0 85px rgba(255, 100, 0, 0.35);
        border-color: rgba(255, 215, 0, 1.0);
    }
    100% {
        box-shadow: 0 0 15px rgba(255, 180, 0, 0.4), 0 0 30px rgba(255, 120, 0, 0.2);
        border-color: rgba(255, 180, 0, 0.7);
    }
}

.eum-mae-glow-card {
    background: linear-gradient(135deg, rgba(255, 250, 240, 0.96) 0%, rgba(255, 255, 255, 0.98) 100%);
    border: 2.5px solid rgba(255, 180, 0, 0.85);
    border-radius: 20px;
    padding: 26px 20px 22px 20px;
    text-align: center;
    margin: 16px auto;
    max-width: 480px;
    animation: cardPopIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards, glowPulse 2.2s infinite ease-in-out;
    color: #262730;
    box-sizing: border-box;
}

.eum-mae-glow-badge {
    display: inline-block;
    background: linear-gradient(90deg, #FF6B6B, #FFA07A);
    color: #FFFFFF !important;
    font-size: 0.85rem;
    font-weight: 700;
    padding: 4px 14px;
    border-radius: 999px;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
}

.eum-mae-food-name {
    font-size: 2.1rem;
    font-weight: 800;
    margin: 8px 0 10px 0;
    color: #FF4B4B;
    letter-spacing: -0.5px;
    word-break: keep-all;
}

.eum-mae-glow-desc {
    font-size: 1.05rem;
    color: #555555;
    margin: 8px 0 0 0;
    font-weight: 500;
}

.eum-mae-glow-category {
    display: inline-block;
    background: rgba(255, 180, 0, 0.15);
    color: #D97706;
    padding: 3px 10px;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 600;
    margin-top: 6px;
}

@media (prefers-color-scheme: dark) {
    .eum-mae-glow-card {
        background: linear-gradient(135deg, rgba(38, 39, 48, 0.96) 0%, rgba(28, 29, 36, 0.98) 100%);
        color: #FAFAFA;
    }
    .eum-mae-glow-desc {
        color: #DDDDDD;
    }
}
</style>
"""


def _build_confetti_html() -> str:
    """매 호출 시 고유 타임스탬프를 포함하여 부모 창(window.parent)에서 직접 폭죽을 발사하는 HTML 생성"""
    nonce = time.time()
    return f"""<!-- confetti-run-{nonce} -->
<script>
(function() {{
    var pWin = window.parent || window;
    var pDoc = pWin.document;

    function fire() {{
        if (!pWin.confetti) return;
        pWin.confetti({{
            particleCount: 80,
            spread: 70,
            origin: {{ y: 0.6 }}
        }});
        setTimeout(function() {{
            pWin.confetti({{
                particleCount: 50,
                angle: 60,
                spread: 60,
                origin: {{ x: 0.05, y: 0.7 }}
            }});
            pWin.confetti({{
                particleCount: 50,
                angle: 120,
                spread: 60,
                origin: {{ x: 0.95, y: 0.7 }}
            }});
        }}, 200);
    }}

    if (pWin.confetti) {{
        fire();
    }} else {{
        var existing = pDoc.getElementById('eum-mae-confetti-lib');
        if (!existing) {{
            var s = pDoc.createElement('script');
            s.id = 'eum-mae-confetti-lib';
            s.src = 'https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js';
            s.onload = fire;
            pDoc.head.appendChild(s);
        }} else {{
            existing.addEventListener('load', fire);
        }}
    }}
}})();
</script>
"""


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
            # 부모 창(window.parent)에 직접 canvas-confetti 파티클 발사
            components.html(_build_confetti_html(), height=1)
            return True

        elif effect == EffectType.GLOW:
            inject_card_glow_css()
            food_name = options.get("food_name")
            if food_name:
                render_glow_card(
                    food_name=food_name,
                    category=options.get("category"),
                    badge_text=options.get("badge_text", "🎉 오늘의 추천 메뉴!"),
                    subtitle=options.get("subtitle")
                )
            return True

        return False
    except Exception:
        # 이펙트 실행 중 오류가 발생하더라도 메인 기능이 멈추지 않도록 안전 방어
        return False


def inject_card_glow_css() -> None:
    """당첨 카드 강조용 CSS 스타일 및 키프레임 애니메이션 주입 (#18)"""
    st.markdown(_CARD_GLOW_CSS, unsafe_allow_html=True)


def render_glow_card(
    food_name: str,
    category: Optional[str] = None,
    badge_text: str = "🎉 오늘의 추천 메뉴!",
    subtitle: Optional[str] = None,
) -> None:
    """
    당첨 메뉴 카드 강조 CSS 글로우 및 등장 이펙트가 적용된 카드 렌더링 (#18)
    
    :param food_name: 당첨된 음식 이름
    :param category: 음식 카테고리 (선택 사항)
    :param badge_text: 상단 강조 뱃지 텍스트
    :param subtitle: 하단 설명 안내문구 (선택 사항)
    """
    inject_card_glow_css()
    category_html = f'<div class="eum-mae-glow-category">🏷️ {category}</div>' if category else ""
    desc_text = subtitle or "오늘 드실 가장 맛있는 한 끼! 🐮✨"
    card_html = f"""
<div class="eum-mae-glow-card">
    <div class="eum-mae-glow-badge">{badge_text}</div>
    <div class="eum-mae-food-name">{food_name}</div>
    {category_html}
    <p class="eum-mae-glow-desc">{desc_text}</p>
</div>
"""
    st.markdown(card_html, unsafe_allow_html=True)


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


def show_celebration_effect() -> None:
    """
    메뉴 추첨 완료 시 호출하는 축하 폭죽(컨페티) 연출 함수 (#17)
    결과창 모듈 또는 추첨 완료 시점에서 간편하게 호출할 수 있습니다.
    """
    play_atomic_effect(EffectType.CONFETTI)


def play() -> None:
    """
    기존 app.py 연동용 기본 추첨 연출 함수
    뽑기 버튼 클릭 시 호출되어 기본 롤링 연출을 실행합니다.
    """
    play_preset("preset_draw")

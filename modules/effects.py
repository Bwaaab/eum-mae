"""
이펙트 및 시각 연출 모듈 (modules/effects.py)
기능적 비즈니스 로직에 영향을 주지 않으며, 독립적으로 시각 연출을 렌더링합니다.
"""
import base64
from enum import Enum
from functools import lru_cache
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parents[1]
COW_ASSETS_DIR = ROOT / "assets" / "images"


# 1. 단일 이펙트 타입 정의
class EffectType(str, Enum):
    ROLLING = "rolling"               # 메뉴 추천 슬롯머신 셔플 / 긴장감 연출
    CONFETTI = "confetti"             # 축하 폭죽 파티클 (#17)
    GLOW = "glow"                     # 카드 반짝임 및 등장 CSS 효과 (#18)
    COW_ANIMATION = "cow_animation"   # 젖소 캐릭터 인터랙션 및 입에서 카드 등장 연출 (#71)


# 2. 조합형 세트(프리셋) 정의
EFFECT_PRESETS: Dict[str, List[Dict[str, Any]]] = {
    "preset_draw": [
        {"type": EffectType.ROLLING, "options": {"duration": 0.8, "fullscreen": True}},
        {"type": EffectType.COW_ANIMATION, "options": {"state": "open", "fullscreen": True, "duration": 2.3}},
    ],
    "preset_celebration": [
        {"type": EffectType.GLOW, "options": {}},
        {"type": EffectType.CONFETTI, "options": {}}
    ],
    "preset_jackpot": [
        {"type": EffectType.ROLLING, "options": {"duration": 0.8, "fullscreen": True}},
        {"type": EffectType.COW_ANIMATION, "options": {"state": "open", "fullscreen": True, "duration": 2.3}},
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


_COW_SCENE_CSS = """<style>
@keyframes eumMaeFadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
@keyframes eumMaeEmojiBounce {
    0%, 100% { transform: scale(1) translateY(0); }
    50% { transform: scale(1.16) translateY(-6px); }
}
@keyframes cowBreathe {
    0%, 100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(-5px) scale(1.015); }
}
@keyframes cowShake {
    0%, 100% { transform: translate(0, 0) rotate(0deg); }
    20% { transform: translate(-4px, -2px) rotate(-2deg); }
    40% { transform: translate(4px, 1px) rotate(2deg); }
    60% { transform: translate(-3px, 2px) rotate(-1.5deg); }
    80% { transform: translate(3px, -1px) rotate(1.5deg); }
}
@keyframes cowPopOpen {
    0% { transform: scale(0.52) translateY(18px); opacity: 0.2; }
    12% { opacity: 1; }
    48% { transform: scale(1.22) translateY(0); }
    54% { transform: scale(1.30) translateY(-6px); }
    66% { transform: scale(1.18) translateY(0); }
    100% { transform: scale(1.18) translateY(0); }
}
@keyframes cowEyeBlinkOpen {
    0%, 88%, 100% { opacity: 1; }
    92%, 96% { opacity: 0; }
}
@keyframes cowEyeBlinkClose {
    0%, 88%, 100% { opacity: 0; }
    92%, 96% { opacity: 1; }
}
@keyframes cowMouthClosedPhase {
    0%, 50% { opacity: 1; }
    53%, 100% { opacity: 0; }
}
@keyframes cowMouthOpenPhase {
    0%, 50% { opacity: 0; }
    53%, 100% { opacity: 1; }
}
@keyframes cardEmergeFromMouth {
    0%, 52% {
        opacity: 0;
        transform: translate(-50%, -45%) scale(0.05);
    }
    66% {
        opacity: 1;
        transform: translate(-50%, 15%) scale(0.7);
    }
    84% {
        opacity: 1;
        transform: translate(-50%, 58%) scale(1.14);
    }
    100% {
        opacity: 1;
        transform: translate(-50%, 60%) scale(1.16);
    }
}
.eum-mae-scene-overlay {
    position: fixed;
    inset: 0;
    z-index: 999999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(17, 19, 28, 0.88);
    backdrop-filter: blur(10px);
    animation: eumMaeFadeIn 0.2s ease-out;
    padding: 24px;
    box-sizing: border-box;
}
.eum-mae-rolling-card {
    background: linear-gradient(135deg, rgba(38, 41, 56, 0.96), rgba(25, 27, 38, 0.98));
    border: 2.5px solid rgba(255, 180, 0, 0.85);
    border-radius: 24px;
    padding: 36px 44px;
    text-align: center;
    box-shadow: 0 0 36px rgba(255, 180, 0, 0.35);
    max-width: 420px;
    width: 90%;
}
.eum-mae-rolling-emoji {
    font-size: 3.6rem;
    line-height: 1.2;
    animation: eumMaeEmojiBounce 0.24s infinite ease-in-out;
}
.eum-mae-rolling-text {
    margin-top: 14px;
    font-size: 1.25rem;
    font-weight: 700;
    color: #FFD166;
    letter-spacing: -0.3px;
}
.eum-mae-cow-inline {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 12px auto;
}
.eum-mae-cow-speech {
    background: #FFFFFF;
    color: #222222;
    font-weight: 700;
    font-size: 1rem;
    padding: 8px 18px;
    border-radius: 999px;
    margin-bottom: 10px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.22);
    border: 2px solid rgba(255, 180, 0, 0.8);
}
.eum-mae-cow-stage {
    position: relative;
    margin: 0 auto;
}
.eum-mae-cow-stage.is-idle {
    animation: cowBreathe 2.8s infinite ease-in-out;
}
.eum-mae-cow-stage.is-rolling {
    animation: cowShake 0.32s infinite ease-in-out;
}
.eum-mae-cow-stage.is-open {
    animation: cowPopOpen 2.2s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}
.eum-mae-cow-layer {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: contain;
    pointer-events: none;
    user-select: none;
}
.eum-mae-eye-open {
    animation: cowEyeBlinkOpen 3.6s infinite;
}
.eum-mae-eye-close {
    opacity: 0;
    animation: cowEyeBlinkClose 3.6s infinite;
}
.eum-mae-mouth-preopen {
    animation: cowMouthClosedPhase 2.2s forwards;
}
.eum-mae-mouth-open-delay {
    opacity: 0;
    animation: cowMouthOpenPhase 2.2s forwards;
}
.eum-mae-emerge-card {
    position: absolute;
    top: 62%;
    left: 50%;
    z-index: 20;
    min-width: 220px;
    padding: 14px 22px;
    border-radius: 16px;
    background: linear-gradient(135deg, #FFF7E0 0%, #FFFFFF 100%);
    border: 2.5px solid #FFB400;
    box-shadow: 0 12px 32px rgba(255, 180, 0, 0.55), 0 0 24px rgba(255, 215, 0, 0.45);
    text-align: center;
    color: #262730;
    animation: cardEmergeFromMouth 2.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.eum-mae-emerge-badge {
    display: inline-block;
    background: linear-gradient(90deg, #FF6B6B, #FFA07A);
    color: #FFFFFF;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 3px 12px;
    border-radius: 999px;
    margin-bottom: 6px;
}
.eum-mae-emerge-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #FF4B4B;
    word-break: keep-all;
}
</style>"""


@lru_cache(maxsize=8)
def _load_cow_asset_b64(filename: str) -> str:
    """assets/images 내 젖소 파츠 PNG 파일을 Base64 data URI로 캐싱 로드합니다."""
    asset_path = COW_ASSETS_DIR / filename
    raw_bytes = asset_path.read_bytes()
    encoded = base64.b64encode(raw_bytes).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _build_fullscreen_rolling_html(emoji: str, text: str) -> str:
    """풀스크린 중앙 롤링 씬 HTML 생성"""
    return (
        f'{_COW_SCENE_CSS}'
        f'<div class="eum-mae-scene-overlay">'
        f'<div class="eum-mae-rolling-card">'
        f'<div class="eum-mae-rolling-emoji">{emoji}</div>'
        f'<div class="eum-mae-rolling-text">{text}</div>'
        f'</div>'
        f'</div>'
    )


def _build_cow_character_html(
    state: str = "idle",
    size: int = 200,
    speech: Optional[str] = None,
    fullscreen: bool = False,
    card_title: str = "🎉 오늘의 추천 메뉴! ✨",
    show_emerge_card: bool = True,
) -> str:
    """
    상태(idle / rolling / open)에 맞는 젖소 파츠 레이어링 HTML을 생성합니다.
    Markdown 코드 블록 오인 방지를 위해 들여쓰기/빈 줄 없이 단일 연결 문자열로 생성합니다.
    """
    face_uri = _load_cow_asset_b64("cow_face.png")
    eye_uri = _load_cow_asset_b64("cow_eye.png")
    close_eye_uri = _load_cow_asset_b64("cow_close_eye.png")
    mouth_uri = _load_cow_asset_b64("cow_mouth.png")
    open_mouth_uri = _load_cow_asset_b64("cow_open_mouth.png")

    normalized_state = state if state in {"idle", "rolling", "open"} else "idle"
    stage_cls = f"eum-mae-cow-stage is-{normalized_state}"

    if normalized_state == "idle":
        eye_html = (
            f'<img class="eum-mae-cow-layer eum-mae-eye-open" src="{eye_uri}" alt="cow eye">'
            f'<img class="eum-mae-cow-layer eum-mae-eye-close" src="{close_eye_uri}" alt="cow closed eye">'
        )
        mouth_html = f'<img class="eum-mae-cow-layer" src="{mouth_uri}" alt="cow mouth">'
        emerge_html = ""
        default_speech = "오늘 뭐 먹지? 음메~ 🐮"
    elif normalized_state == "rolling":
        eye_html = f'<img class="eum-mae-cow-layer" src="{eye_uri}" alt="cow eye">'
        mouth_html = f'<img class="eum-mae-cow-layer" src="{mouth_uri}" alt="cow mouth">'
        emerge_html = ""
        default_speech = "두근두근... 고르는 중! 🎲"
    else:
        eye_html = f'<img class="eum-mae-cow-layer" src="{eye_uri}" alt="cow eye">'
        mouth_html = (
            f'<img class="eum-mae-cow-layer eum-mae-mouth-preopen" src="{mouth_uri}" alt="cow mouth">'
            f'<img class="eum-mae-cow-layer eum-mae-mouth-open-delay" src="{open_mouth_uri}" alt="cow open mouth">'
        )
        emerge_html = (
            f'<div class="eum-mae-emerge-card">'
            f'<div class="eum-mae-emerge-badge">🐮 음메 추천!</div>'
            f'<div class="eum-mae-emerge-title">{card_title}</div>'
            f'</div>'
        ) if show_emerge_card else ""
        default_speech = "음메~! 맛있는 메뉴 나왔다! ✨"

    speech_text = speech if speech is not None else default_speech
    speech_html = f'<div class="eum-mae-cow-speech">{speech_text}</div>' if speech_text else ""
    wrapper_cls = "eum-mae-scene-overlay" if fullscreen else "eum-mae-cow-inline"

    return (
        f'{_COW_SCENE_CSS}'
        f'<div class="{wrapper_cls}">'
        f'{speech_html}'
        f'<div class="{stage_cls}" style="width: {size}px; height: {size}px;">'
        f'<img class="eum-mae-cow-layer" src="{face_uri}" alt="cow face">'
        f'{eye_html}'
        f'{mouth_html}'
        f'{emerge_html}'
        f'</div>'
        f'</div>'
    )


def render_cow_character(
    state: str = "idle",
    size: int = 200,
    speech: Optional[str] = None,
    fullscreen: bool = False,
    card_title: str = "🎉 오늘의 추천 메뉴! ✨",
    show_emerge_card: bool = True,
    target: Optional[Any] = None,
) -> None:
    """젖소 캐릭터 인터랙션 애니메이션을 지정된 컨테이너 또는 현재 위치에 렌더링합니다 (#71)."""
    html = _build_cow_character_html(
        state=state,
        size=size,
        speech=speech,
        fullscreen=fullscreen,
        card_title=card_title,
        show_emerge_card=show_emerge_card,
    )
    renderer = target if target is not None else st
    renderer.markdown(html, unsafe_allow_html=True)


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
            fullscreen = options.get("fullscreen", False)
            keep_placeholder = options.get("_keep_placeholder", False)
            # Streamlit empty placeholder를 활용한 슬롯머신 셔플 연출
            food_emojis = ["🍕", "🍔", "🍜", "🍣", "🍱", "🥘", "🍛", "🥩", "🥗", "🍲"]
            loading_texts = [
                "🐮 음메가 메뉴를 고르는 중...",
                "🎲 오늘의 운명을 결정하는 중...",
                "✨ 맛있는 선택을 탐색하는 중..."
            ]

            slot_placeholder = options.get("_placeholder") or st.empty()
            start_time = time.time()
            idx = 0

            while time.time() - start_time < duration:
                emoji = food_emojis[idx % len(food_emojis)]
                text = loading_texts[(idx // 3) % len(loading_texts)]
                if fullscreen:
                    slot_placeholder.markdown(
                        _build_fullscreen_rolling_html(emoji, text),
                        unsafe_allow_html=True,
                    )
                else:
                    slot_placeholder.markdown(
                        f"<h3 style='text-align: center; color: #FF4B4B;'>{emoji} {text}</h3>",
                        unsafe_allow_html=True
                    )
                time.sleep(0.12)
                idx += 1

            # 연출 종료 후 placeholder 정리 (프리셋에서 다음 씬과 공유 중이면 유지)
            if not keep_placeholder:
                slot_placeholder.empty()
            return True

        elif effect == EffectType.COW_ANIMATION:
            state = options.get("state", "idle")
            size = options.get("size", 210)
            speech = options.get("speech")
            fullscreen = options.get("fullscreen", False)
            card_title = options.get("card_title", "🎉 오늘의 추천 메뉴! ✨")
            show_emerge_card = options.get("show_emerge_card", True)
            duration = options.get("duration", 2.3)
            keep_placeholder = options.get("_keep_placeholder", False)

            if fullscreen:
                scene_placeholder = options.get("_placeholder") or st.empty()
                render_cow_character(
                    state=state,
                    size=size,
                    speech=speech,
                    fullscreen=True,
                    card_title=card_title,
                    show_emerge_card=show_emerge_card,
                    target=scene_placeholder,
                )
                time.sleep(duration)
                if not keep_placeholder:
                    scene_placeholder.empty()
            else:
                render_cow_character(
                    state=state,
                    size=size,
                    speech=speech,
                    fullscreen=False,
                    card_title=card_title,
                    show_emerge_card=show_emerge_card,
                )
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
    card_html = (
        f'<div class="eum-mae-glow-card">'
        f'<div class="eum-mae-glow-badge">{badge_text}</div>'
        f'<div class="eum-mae-food-name">{food_name}</div>'
        f'{category_html}'
        f'<p class="eum-mae-glow-desc">{desc_text}</p>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


def play_preset(preset_name: str, options: Optional[Dict[str, Any]] = None) -> bool:
    """[세트 이펙트] 사전 정의된 연출 파이프라인을 순차 실행합니다."""
    if preset_name not in EFFECT_PRESETS:
        return False

    steps = EFFECT_PRESETS[preset_name]
    has_fullscreen_scene = any(
        step.get("options", {}).get("fullscreen", False) for step in steps
    )
    shared_placeholder = st.empty() if has_fullscreen_scene else None

    try:
        for step in steps:
            step_opts = step.get("options", {}).copy()
            if options:
                step_opts.update(options)
            if shared_placeholder is not None and step_opts.get("fullscreen", False):
                step_opts["_placeholder"] = shared_placeholder
                step_opts["_keep_placeholder"] = True
            play_atomic_effect(step["type"], step_opts)
    finally:
        if shared_placeholder is not None:
            shared_placeholder.empty()
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

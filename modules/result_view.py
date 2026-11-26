import base64
import io
import os
from pathlib import Path
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from models import Food
from modules import effects

DEFAULT_IMAGE_PATH = "assets/images/default.png"


def _load_food_image_b64(image_path: str) -> str:
    """음식 대표 이미지를 Base64 data URI로 변환 (파일 누락 시 기본 이미지 폴백)"""
    target_path = Path(image_path) if image_path else Path(DEFAULT_IMAGE_PATH)
    if not target_path.exists():
        target_path = Path(DEFAULT_IMAGE_PATH)
    if not target_path.exists():
        return ""

    raw_bytes = target_path.read_bytes()
    encoded = base64.b64encode(raw_bytes).decode("ascii")
    ext = target_path.suffix.lower().lstrip(".") or "png"
    mime = "jpeg" if ext in {"jpg", "jpeg"} else ext
    return f"data:image/{mime};base64,{encoded}"


def _build_share_text(selected_food: Food) -> str:
    """메신저 공유용 당첨 결과 텍스트 생성"""
    food_name = getattr(selected_food, "name", str(selected_food))
    category = getattr(selected_food, "category", "")
    description = getattr(selected_food, "description", "")

    lines = [
        "🐮 [음매 - 오늘의 메뉴 추천 결과]",
        f"🍽️ 추천 메뉴: {food_name}",
    ]
    if category:
        lines.append(f"📂 카테고리: {category}")
    if description:
        lines.append(f"💬 메뉴 설명: {description}")
    lines.append("👉 오늘 이 메뉴 어때요?")
    return "\n".join(lines)


def _load_korean_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Windows/Linux/Cloud 환경에서 한글 깨짐을 방지하기 위한 폰트 로더"""
    font_candidates = [
        "C:/Windows/Fonts/malgunbd.ttf",
        "C:/Windows/Fonts/malgun.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    ]
    for path in font_candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _create_result_card_image(selected_food: Food) -> bytes:
    """당첨 메뉴 정보가 담긴 PNG 결과 카드 이미지 바이트 생성"""
    food_name = getattr(selected_food, "name", str(selected_food))
    category = getattr(selected_food, "category", "")

    width, height = 720, 420
    img = Image.new("RGB", (width, height), color=(255, 251, 242))
    draw = ImageDraw.Draw(img)

    draw.rectangle([20, 20, width - 20, height - 20], outline=(235, 180, 90), width=4)
    draw.rectangle([24, 24, width - 24, 105], fill=(255, 232, 185))

    title_font = _load_korean_font(30)
    category_font = _load_korean_font(24)
    menu_font = _load_korean_font(54)
    footer_font = _load_korean_font(20)

    draw.text((width // 2, 65), "EUM-MAE 오늘의 추천 메뉴", fill=(90, 55, 20), font=title_font, anchor="mm")

    if category:
        draw.text((width // 2, 165), f"[ {category} ]", fill=(150, 100, 45), font=category_font, anchor="mm")

    draw.text((width // 2, 240), food_name, fill=(35, 35, 35), font=menu_font, anchor="mm")
    draw.text((width // 2, 345), "맛있는 식사 시간 되세요!", fill=(120, 120, 120), font=footer_font, anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def show_result_card(selected_food: Food) -> None:
    """당첨 메뉴(메뉴명, 대표 이미지, 카테고리) 중앙 강조 카드 팝업 UI 렌더링 (#23)"""
    food_name = getattr(selected_food, "name", str(selected_food))
    category = getattr(selected_food, "category", None)
    image_path = getattr(selected_food, "image_path", DEFAULT_IMAGE_PATH)

    effects.inject_card_glow_css()

    img_uri = _load_food_image_b64(image_path)
    if img_uri:
        image_html = (
            f'<div style="margin: 14px auto; width: 200px; height: 200px; border-radius: 16px; '
            f'overflow: hidden; border: 2px solid rgba(255, 180, 0, 0.45); background: #FFFDF7;">'
            f'<img src="{img_uri}" alt="{food_name}" style="width: 100%; height: 100%; object-fit: cover;">'
            f'</div>'
        )
    else:
        # 이미지 리소스가 없는 메뉴일 경우 기본 음식 카드 플레이스홀더 표시
        image_html = (
            f'<div style="margin: 14px auto; width: 140px; height: 140px; border-radius: 20px; '
            f'border: 2px dashed rgba(255, 180, 0, 0.65); background: rgba(255, 243, 214, 0.7); '
            f'display: flex; align-items: center; justify-content: center; font-size: 4rem;">'
            f'🍽️</div>'
        )

    category_html = f'<div class="eum-mae-glow-category">🏷️ {category}</div>' if category else ""

    card_html = (
        f'<div class="eum-mae-glow-card" style="width: 100%; max-width: 460px; margin: 16px auto;">'
        f'<div class="eum-mae-glow-badge">🎉 오늘의 추천 메뉴!</div>'
        f'{image_html}'
        f'<div class="eum-mae-food-name">{food_name}</div>'
        f'{category_html}'
        f'<p class="eum-mae-glow-desc">오늘 드실 가장 맛있는 한 끼! 🐮✨</p>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

def render_result(selected_food: Food) -> None:
    """당첨 결과 표시 및 저장"""
    if not selected_food:
        return

    # #23: 당첨 메뉴 카드(대표 이미지, 메뉴명, 카테고리) 중앙 렌더링
    show_result_card(selected_food)

    # #17: 축하 폭죽(컨페티) 발사
    effects.show_celebration_effect()

    st.divider()
    st.caption("📋 우측 상단 복사 아이콘을 눌러 카카오톡 등에 바로 공유해 보세요!")
    share_text = _build_share_text(selected_food)
    st.code(share_text, language="text")

    img_bytes = _create_result_card_image(selected_food)
    st.download_button(
        label="🖼️ 결과 카드 이미지 다운로드 (PNG)",
        data=img_bytes,
        file_name="result_menu.png",
        mime="image/png",
        use_container_width=True,
    )
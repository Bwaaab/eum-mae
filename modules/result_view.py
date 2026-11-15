import io
import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from models import Food
from modules import effects


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
        "C:/Windows/Fonts/malgunbd.ttf",  # Windows 맑은 고딕 Bold
        "C:/Windows/Fonts/malgun.ttf",    # Windows 맑은 고딕
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",  # Linux/Streamlit Cloud
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

    # 카드 테두리 및 상단 배너 영역
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


def render_result(selected_food: Food) -> None:
    """당첨 결과 표시 및 저장"""
    if not selected_food:
        return

    food_name = getattr(selected_food, "name", str(selected_food))

    st.subheader("🎉 오늘의 추천 메뉴!")
    st.markdown(f"### 오늘 드실 메뉴는 **{food_name}** 입니다!")

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
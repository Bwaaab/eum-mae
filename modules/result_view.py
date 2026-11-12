import streamlit as st
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
import streamlit as st
from models import Food
from modules import effects

def render_result(selected_food: Food) -> None:
    """당첨 결과 표시 및 저장"""
    if not selected_food:
        return

    # Food 객체의 name 속성이 있으면 가져오고, 없으면 객체 자체를 문자열로 표시
    food_name = getattr(selected_food, "name", str(selected_food))

    st.subheader("🎉 오늘의 추천 메뉴!")
    st.markdown(f"### 오늘 드실 메뉴는 **{food_name}** 입니다!")

    effects.show_celebration_effect()
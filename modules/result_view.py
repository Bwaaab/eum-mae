import streamlit as st
from models import Food
from modules import effects

def render_result(selected_food: Food) -> None:
    """당첨 결과 표시 및 저장"""
    if not selected_food:
        return

    # Food 객체의 name 속성이 있으면 가져오고, 없으면 객체 자체를 문자열로 표시
    food_name = getattr(selected_food, "name", str(selected_food))
    category = getattr(selected_food, "category", None)

    # #18: 당첨 메뉴 카드 강조 CSS 글로우 및 등장 이펙트 렌더링
    effects.render_glow_card(food_name=food_name, category=category)

    # #17: 축하 폭죽(컨페티) 발사
    effects.show_celebration_effect()
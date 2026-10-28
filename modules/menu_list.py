import streamlit as st
from pathlib import Path

from models import Food

Default_image = "assets/images/default.png"
Root = Path(__file__).resolve().parents[1]

# (id, name). 한식/중식/일식/양식은 주석으로만 구분하고 Food 필드에는 넣지 않는다.
# 지금은 구분당 예시 3개만 둔다. 나머지 메뉴는 별도 이슈에서 채운다.
Seed: tuple[tuple[str, str], ...] = (
    # 한식
    ("bibimbap", "비빔밥"),
    ("kimchijjigae", "김치찌개"),
    ("doenjangjjigae", "된장찌개"),
    # 중식
    ("jajangmyeon", "짜장면"),
    ("jjamppong", "짬뽕"),
    ("tangsuyuk", "탕수육"),
    # 일식
    ("sushi", "초밥"),
    ("ramen", "라멘"),
    ("donkatsu", "돈카츠"),
    # 양식
    ("steak", "스테이크"),
    ("pasta", "파스타"),
    ("pizza", "피자"),
)


def _existing_image(image_path: str) -> str | None:
    """파일이 있으면 그 경로, 없으면 default.png, 둘 다 없으면 None."""
    candidate = Root / image_path
    if candidate.is_file():
        return str(candidate)
    if image_path != Default_image:
        fallback = Root / Default_image
        if fallback.is_file():
            return str(fallback)
    return None


def load_default_foods() -> dict[str, Food]:
    """기본 음식 목록 로드."""
    foods: dict[str, Food] = {}
    for food_id, name in Seed:
        foods[food_id] = Food(food_id, name, Default_image)
    return foods


def render_menu(all_foods: list[Food]) -> list[str]:
    """메뉴 목록 UI 렌더링 및 선택된 ID 반환."""
    if not all_foods:
        st.write("메뉴가 없습니다")
        return []

    selected_ids: list[str] = []
    for food in all_foods:
        image = _existing_image(food.image_path)
        if image is not None:
            try:
                st.image(image, width=160)
            except OSError:
                pass
        if st.checkbox(food.name, key=food.id):
            selected_ids.append(food.id)
    return selected_ids

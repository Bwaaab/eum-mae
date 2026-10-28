from pathlib import Path

import streamlit as st

from models import Food

DEFAULT_IMAGE = "assets/images/default.png"
ROOT = Path(__file__).resolve().parents[1]

# 키는 id. 한식/중식/일식/양식은 주석으로만 구분하고 Food 필드에는 넣지 않는다.
# 지금은 구분당 예시 3개만 둔다. 나머지 메뉴는 별도 이슈에서 채운다.
SEED: dict[str, Food] = {
    # 한식
    "bibimbap": Food("bibimbap", "비빔밥", DEFAULT_IMAGE),
    "kimchijjigae": Food("kimchijjigae", "김치찌개", DEFAULT_IMAGE),
    "doenjangjjigae": Food("doenjangjjigae", "된장찌개", DEFAULT_IMAGE),
    # 중식
    "jajangmyeon": Food("jajangmyeon", "짜장면", DEFAULT_IMAGE),
    "jjamppong": Food("jjamppong", "짬뽕", DEFAULT_IMAGE),
    "tangsuyuk": Food("tangsuyuk", "탕수육", DEFAULT_IMAGE),
    # 일식
    "sushi": Food("sushi", "초밥", DEFAULT_IMAGE),
    "ramen": Food("ramen", "라멘", DEFAULT_IMAGE),
    "donkatsu": Food("donkatsu", "돈카츠", DEFAULT_IMAGE),
    # 양식
    "steak": Food("steak", "스테이크", DEFAULT_IMAGE),
    "pasta": Food("pasta", "파스타", DEFAULT_IMAGE),
    "pizza": Food("pizza", "피자", DEFAULT_IMAGE),
}


def _existing_image(image_path: str):
    """파일이 있으면 그 경로, 없으면 default.png, 둘 다 없으면 None."""
    candidate = ROOT / image_path
    if candidate.is_file():
        return str(candidate)
    if image_path != DEFAULT_IMAGE:
        fallback = ROOT / DEFAULT_IMAGE
        if fallback.is_file():
            return str(fallback)
    return None


def load_default_foods() -> dict[str, Food]:
    """기본 음식 목록 로드."""
    return dict(SEED)


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

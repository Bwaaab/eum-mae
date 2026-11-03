import shutil
import uuid
from pathlib import Path

import streamlit as st

from models import Food

DEFAULT_IMAGE = "assets/images/default.png"
ROOT = Path(__file__).resolve().parents[1]
ALLOWED_EXT = {".png", ".jpg", ".jpeg"}

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


def add_food(registry: dict[str, Food], name: str, image_path: str):
    """이름과 사진을 받아 메뉴를 추가한다. 거절되면 None이고 registry는 그대로다."""
    cleaned = name.strip()
    if not cleaned:
        st.warning("이름을 입력하세요")
        return None

    source = Path(image_path)
    if not image_path or not source.is_file():
        st.warning("사진을 넣어 주세요")
        return None
    if source.resolve() == (ROOT / DEFAULT_IMAGE).resolve():
        st.warning("사진을 넣어 주세요")
        return None

    ext = source.suffix.lower()
    if ext not in ALLOWED_EXT:
        st.warning("png, jpg, jpeg만 추가할 수 있습니다")
        return None
    if any(food.name == cleaned for food in registry.values()):
        st.warning("같은 이름이 이미 있습니다")
        return None

    food_id = uuid.uuid4().hex
    while food_id in registry:
        food_id = uuid.uuid4().hex

    dest_rel = f"assets/images/{food_id}{ext}"
    dest = ROOT / dest_rel
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
    except OSError:
        st.warning("사진을 저장하지 못했습니다")
        return None

    food = Food(food_id, cleaned, dest_rel)
    registry[food_id] = food
    return food


def remove_food(registry: dict[str, Food], food_id: str) -> None:
    """있는 항목 하나만 지운다. 없는 id면 목록을 바꾸지 않는다."""
    registry.pop(food_id, None)


def _render_add_form(registry: dict[str, Food]) -> None:
    """이름과 사진을 받아 registry에 메뉴를 넣는다."""
    name = st.text_input("메뉴 이름", key="new-food-name")
    uploaded = st.file_uploader("사진", type=["png", "jpg", "jpeg"], key="new-food-image")
    if not st.button("메뉴 추가", key="add-food"):
        return
    if uploaded is None:
        st.warning("사진을 넣어 주세요")
        return

    ext = Path(uploaded.name).suffix.lower()
    tmp = ROOT / "assets" / "images" / f".upload-{uuid.uuid4().hex}{ext}"
    try:
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_bytes(uploaded.getvalue())
        added = add_food(registry, name, str(tmp))
    finally:
        tmp.unlink(missing_ok=True)
    if added is not None:
        st.rerun()


def render_menu(all_foods: list[Food]) -> list[str]:
    """메뉴 목록 UI 렌더링 및 선택된 ID 반환."""
    registry = st.session_state.get("registry")
    if isinstance(registry, dict):
        _render_add_form(registry)

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
        checked = st.checkbox(food.name, key=food.id)
        if isinstance(registry, dict) and st.button("삭제", key=f"delete-{food.id}"):
            remove_food(registry, food.id)
            st.rerun()
        if checked:
            selected_ids.append(food.id)
    return selected_ids

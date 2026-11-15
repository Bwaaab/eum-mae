import csv
import shutil
import uuid
from pathlib import Path

import streamlit as st

from models import Food

DEFAULT_IMAGE = "assets/images/default.png"
ROOT = Path(__file__).resolve().parents[1]
SEED_CSV = ROOT / "docs" / "default_foods.csv"
DEFAULT_IMAGE_PATH = (ROOT / DEFAULT_IMAGE).resolve()
ALLOWED_EXT = {".png", ".jpg", ".jpeg"}


def _existing_image(image_path: str) -> str | None:
    """Return a usable image path, falling back to default.png when needed."""
    candidate = ROOT / image_path
    if candidate.is_file():
        return str(candidate)
    if image_path != DEFAULT_IMAGE and DEFAULT_IMAGE_PATH.is_file():
        return str(DEFAULT_IMAGE_PATH)
    return None


def load_default_foods() -> dict[str, Food]:
    """Load default foods from docs/default_foods.csv as id -> Food."""
    foods: dict[str, Food] = {}
    with SEED_CSV.open(encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            food_id = (row.get("id") or "").strip()
            name = (row.get("name") or "").strip()
            if not food_id or not name:
                continue
            image_path = (row.get("image_path") or "").strip() or DEFAULT_IMAGE
            foods[food_id] = Food(food_id, name, image_path)
    return foods


def add_food(registry: dict[str, Food], name: str, image_path: str):
    """Add a food with name and photo. Return None and leave registry unchanged on reject."""
    cleaned = name.strip()
    if not cleaned:
        st.warning("이름을 입력하세요")
        return None

    source = Path(image_path) if image_path else None
    if source is None or not source.is_file() or source.resolve() == DEFAULT_IMAGE_PATH:
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
    """Remove one food by id. Missing ids leave the registry unchanged."""
    registry.pop(food_id, None)


def _render_add_form(registry: dict[str, Food]) -> None:
    """Render name/photo inputs and append a food on submit."""
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
    """Render the menu list and return checked food ids."""
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

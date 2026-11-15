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
CATEGORIES = ("한식", "중식", "일식", "양식")

# id -> category, filled when defaults load; kept in session for user-added foods
_FOOD_CATEGORY: dict[str, str] = {}


def _existing_image(image_path: str) -> str | None:
    """Return a usable image path, falling back to default.png when needed."""
    candidate = ROOT / image_path
    if candidate.is_file():
        return str(candidate)
    if image_path != DEFAULT_IMAGE and DEFAULT_IMAGE_PATH.is_file():
        return str(DEFAULT_IMAGE_PATH)
    return None


def _category_map() -> dict[str, str]:
    """Session category map, seeded from CSV ids."""
    if "food_categories" not in st.session_state:
        st.session_state.food_categories = dict(_FOOD_CATEGORY)
    return st.session_state.food_categories


def load_default_foods() -> dict[str, Food]:
    """Load default foods from docs/default_foods.csv as id -> Food."""
    foods: dict[str, Food] = {}
    _FOOD_CATEGORY.clear()
    with SEED_CSV.open(encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            food_id = (row.get("id") or "").strip()
            name = (row.get("name") or "").strip()
            if not food_id or not name:
                continue
            image_path = (row.get("image_path") or "").strip() or DEFAULT_IMAGE
            category = (row.get("category") or "").strip() or "한식"
            foods[food_id] = Food(food_id, name, image_path)
            _FOOD_CATEGORY[food_id] = category
    return foods


def add_food(registry: dict[str, Food], name: str, image_path: str, category: str = "한식"):
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
    cat = category if category in CATEGORIES else "한식"
    _category_map()[food_id] = cat
    return food


def remove_food(registry: dict[str, Food], food_id: str) -> None:
    """Remove one food by id. Missing ids leave the registry unchanged."""
    registry.pop(food_id, None)
    _category_map().pop(food_id, None)


def _render_add_form(registry: dict[str, Food]) -> None:
    """Render name/photo/category inputs and append a food on submit."""
    name = st.text_input("메뉴 이름", key="new-food-name")
    category = st.selectbox("카테고리", options=list(CATEGORIES), key="new-food-category")
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
        added = add_food(registry, name, str(tmp), category)
    finally:
        tmp.unlink(missing_ok=True)
    if added is not None:
        st.rerun()


def _foods_in_category(all_foods: list[Food], category: str) -> list[Food]:
    cats = _category_map()
    return [food for food in all_foods if cats.get(food.id, "한식") == category]


def _all_selected(foods: list[Food]) -> bool:
    """True when every food in the list is currently checked."""
    return bool(foods) and all(st.session_state.get(food.id, False) for food in foods)


def _toggle_select_all(foods: list[Food]) -> None:
    """Toggle all checkboxes for the given foods."""
    turn_on = not _all_selected(foods)
    for food in foods:
        st.session_state[food.id] = turn_on
    st.rerun()


def _render_food_cell(food: Food, registry) -> bool:
    """Render one food in a cell: image, then checkbox and delete on one row."""
    image = _existing_image(food.image_path)
    if image is not None:
        try:
            st.image(image, width=120)
        except OSError:
            pass

    check_col, delete_col = st.columns([4, 1])
    with check_col:
        checked = st.checkbox(food.name, key=food.id)
    with delete_col:
        if isinstance(registry, dict) and st.button("삭제", key=f"delete-{food.id}"):
            remove_food(registry, food.id)
            st.rerun()
    return checked


def _render_category_pool(foods: list[Food], registry) -> list[str]:
    """Render foods in two columns and return checked ids."""
    if not foods:
        st.caption("이 카테고리에 메뉴가 없습니다.")
        return []

    selected_ids: list[str] = []
    for i in range(0, len(foods), 2):
        left, right = st.columns(2)
        pair = foods[i : i + 2]
        with left:
            if _render_food_cell(pair[0], registry):
                selected_ids.append(pair[0].id)
        if len(pair) > 1:
            with right:
                if _render_food_cell(pair[1], registry):
                    selected_ids.append(pair[1].id)
    return selected_ids


def render_menu(all_foods: list[Food]) -> list[str]:
    """Render category tabs and return checked food ids for the open category."""
    registry = st.session_state.get("registry")
    if isinstance(registry, dict):
        _render_add_form(registry)

    # Sync CSV categories into session once registry exists
    cats = _category_map()
    for food_id, category in _FOOD_CATEGORY.items():
        cats.setdefault(food_id, category)

    if not all_foods:
        st.write("메뉴가 없습니다")
        return []

    if "open_category" not in st.session_state:
        st.session_state.open_category = "한식"

    cat_cols = st.columns(4)
    for col, category in zip(cat_cols, CATEGORIES):
        with col:
            is_open = st.session_state.open_category == category
            label = f"[{category}]" if is_open else category
            if st.button(label, key=f"open-{category}", use_container_width=True):
                st.session_state.open_category = category
                st.rerun()
            foods = _foods_in_category(all_foods, category)
            all_on = _all_selected(foods)
            toggle_label = (
                f"전체 해제 ({len(foods)})" if all_on else f"전체 선택 ({len(foods)})"
            )
            if st.button(toggle_label, key=f"all-{category}", use_container_width=True):
                _toggle_select_all(foods)

    open_cat = st.session_state.open_category
    st.subheader(f"{open_cat} 메뉴")
    return _render_category_pool(_foods_in_category(all_foods, open_cat), registry)

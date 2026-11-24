import csv
import html
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
POOL_COLUMNS = 4

# Selectable blocks sized for a future thumbnail + name (no list image in this issue)
_CARD_CSS = """
<style>
div[class*="st-key-pick-"] {
  margin-bottom: 0.2rem;
}
div[class*="st-key-pick-"] button {
  border: 1px solid transparent !important;
  border-radius: 14px !important;
  font-weight: 700 !important;
  color: #ffffff !important;
  width: 100% !important;
  min-height: 9.5rem !important;
  height: 9.5rem !important;
  padding: 0.75rem 0.6rem !important;
  white-space: normal !important;
  line-height: 1.25 !important;
  display: flex !important;
  align-items: flex-end !important;
  justify-content: center !important;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.12) !important;
}
div[class*="st-key-pick-"] button[data-testid="baseButton-secondary"],
div[class*="st-key-pick-"] button[kind="secondary"] {
  background-color: #2F80ED !important;
}
div[class*="st-key-pick-"] button[data-testid="baseButton-primary"],
div[class*="st-key-pick-"] button[kind="primary"] {
  background-color: #E53935 !important;
}
div[class*="st-key-delete-"] {
  margin-bottom: 0.7rem;
}
div[class*="st-key-delete-"] button {
  min-height: 1.9rem !important;
  font-size: 0.8rem !important;
}
</style>
"""

_FLOAT_CSS = """
<style>
/* Leave room on the left so the float panel does not cover the list */
section.main .block-container {
  padding-left: 9.5rem !important;
}
.eum-float-panel {
  position: fixed;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1000;
  width: 8rem;
  max-height: 72vh;
  overflow-y: auto;
  padding: 0.55rem 0.45rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(15, 23, 42, 0.12);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.14);
}
.eum-float-title {
  font-size: 0.78rem;
  font-weight: 700;
  color: #334155;
  margin: 0 0 0.45rem 0;
  text-align: center;
}
.eum-float-chip {
  margin: 0 0 0.15rem 0;
  padding: 0;
  background: transparent;
  border: none;
  color: #334155;
  font-size: 0.8rem;
  font-weight: 500;
  text-align: left;
  line-height: 1.35;
  word-break: keep-all;
}
.eum-float-empty {
  font-size: 0.72rem;
  color: #64748b;
  text-align: center;
  line-height: 1.35;
  padding: 0.35rem 0.15rem;
}
</style>
"""


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
    if "checked_map" in st.session_state:
        checked = dict(st.session_state.checked_map)
        checked.pop(food_id, None)
        st.session_state.checked_map = checked


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


def _checked_map() -> dict[str, bool]:
    """Persistent selection store so hidden categories keep their checks."""
    if "checked_map" not in st.session_state:
        st.session_state.checked_map = {}
    return st.session_state.checked_map


def _set_checked_map(checked: dict[str, bool]) -> None:
    """Replace selection map so Streamlit keeps it across reruns."""
    st.session_state.checked_map = dict(checked)


def _clear_previous_result() -> None:
    """Drop a prior draw result so celebration does not replay while picking."""
    if st.session_state.get("selected") is not None:
        st.session_state.selected = None


def _all_selected(foods: list[Food]) -> bool:
    """True when every food in the list is currently checked."""
    checked = _checked_map()
    return bool(foods) and all(checked.get(food.id, False) for food in foods)


def _toggle_food(food_id: str) -> None:
    """Flip one food's selection; leave every other food unchanged."""
    checked = _checked_map()
    checked[food_id] = not checked.get(food_id, False)
    _set_checked_map(checked)
    _clear_previous_result()


def _toggle_select_all(foods: list[Food]) -> None:
    """Toggle only this category's foods; leave other categories unchanged."""
    checked = _checked_map()
    turn_on = not _all_selected(foods)
    for food in foods:
        checked[food.id] = turn_on
    _set_checked_map(checked)
    _clear_previous_result()


def _selected_ids(valid_ids: set[str]) -> list[str]:
    """Checked food ids that still exist in the current registry list."""
    checked = _checked_map()
    for food_id in list(checked):
        if food_id not in valid_ids:
            checked.pop(food_id, None)
    _set_checked_map(checked)
    return [food_id for food_id, on in checked.items() if on and food_id in valid_ids]


def _foods_by_ids(all_foods: list[Food], selected_ids: list[str]) -> list[Food]:
    """Preserve selection order while mapping ids back to Food objects."""
    by_id = {food.id: food for food in all_foods}
    return [by_id[food_id] for food_id in selected_ids if food_id in by_id]


def _render_selected_float(selected_foods: list[Food]) -> None:
    """Fixed left panel listing currently selected menus as float blocks."""
    if selected_foods:
        chips = "".join(
            f'<div class="eum-float-chip">{html.escape(food.name)}</div>'
            for food in selected_foods
        )
        body = (
            f'<div class="eum-float-title">선택 {len(selected_foods)}</div>{chips}'
        )
    else:
        body = (
            '<div class="eum-float-title">선택 0</div>'
            '<div class="eum-float-empty">메뉴를 고르면<br/>여기에 표시됩니다</div>'
        )
    st.markdown(
        f"{_FLOAT_CSS}<div class=\"eum-float-panel\">{body}</div>",
        unsafe_allow_html=True,
    )


def _render_food_cell(food: Food, registry) -> None:
    """Render one selectable name block (image slot reserved by block size only)."""
    selected = bool(_checked_map().get(food.id, False))

    if st.button(
        f"{'✓ ' if selected else ''}{food.name}",
        key=f"pick-{food.id}",
        use_container_width=True,
        type="primary" if selected else "secondary",
    ):
        _toggle_food(food.id)
        st.rerun()

    if isinstance(registry, dict) and st.button(
        "삭제", key=f"delete-{food.id}", use_container_width=True
    ):
        remove_food(registry, food.id)
        _clear_previous_result()
        st.rerun()


def _render_category_pool(foods: list[Food], registry) -> None:
    """Render foods in a four-column selectable block grid."""
    st.markdown(_CARD_CSS, unsafe_allow_html=True)
    if not foods:
        st.caption("이 카테고리에 메뉴가 없습니다.")
        return

    for i in range(0, len(foods), POOL_COLUMNS):
        cols = st.columns(POOL_COLUMNS)
        chunk = foods[i : i + POOL_COLUMNS]
        for col, food in zip(cols, chunk):
            with col:
                _render_food_cell(food, registry)


def render_menu(all_foods: list[Food]) -> list[str]:
    """Show category pick UI and return selected food ids for the draw button."""
    registry = st.session_state.get("registry")
    if isinstance(registry, dict):
        _render_add_form(registry)

    cats = _category_map()
    for food_id, category in _FOOD_CATEGORY.items():
        cats.setdefault(food_id, category)

    if not all_foods:
        st.write("메뉴가 없습니다")
        return []

    valid_ids = {food.id for food in all_foods}

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
                st.rerun()

    open_cat = st.session_state.open_category
    st.subheader(f"{open_cat} 메뉴")
    _render_category_pool(_foods_in_category(all_foods, open_cat), registry)

    # app.py: selected_ids = render_menu(...); draw uses this list only
    selected_ids = _selected_ids(valid_ids)
    _render_selected_float(_foods_by_ids(all_foods, selected_ids))
    return selected_ids

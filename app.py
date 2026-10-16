import streamlit as st
from models import Food
from modules import menu_list, draw_engine, effects, result_view

# 중앙 데이터 저장소 최초 초기화 (세션 유지)
if "registry" not in st.session_state:
    st.session_state.registry = menu_list.load_default_foods()
if "selected" not in st.session_state:
    st.session_state.selected = None

st.title("🐮 음메 - 오늘 뭐 먹지?")

# 메뉴 목록을 출력할 스크롤 박스 및 메뉴 목록 UI 표시
# 선택된 ID 수집
with st.container(height=450):
    selected_ids = menu_list.render_menu(list(st.session_state.registry.values()))

# [뽑기] 버튼 우측 하단 배치
col_empty, col_btn = st.columns([3, 1])
with col_btn:
    clicked = st.button("🎲 오늘의 메뉴 뽑기!", disabled=(len(selected_ids) == 0), use_container_width=True)

# [뽑기] 버튼 클릭 시 동작 시퀀스
if clicked:
    # 순수 추첨
    selected_id = draw_engine.draw(selected_ids)
    selected_food = st.session_state.registry[selected_id]
    
    # 연출 재생
    effects.play()
    
    # 당첨 결과 세션에 보관 (이후 다운로드 클릭 시에도 결과 유지)
    st.session_state.selected = selected_food

# 결과 출력 (세션에 당첨 데이터가 있으면 항상 표시)
if st.session_state.selected is not None:
    result_view.render_result(st.session_state.selected)
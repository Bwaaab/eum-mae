import streamlit as st
from models import Food

def load_default_foods() -> dict[str, Food]:
    """기본 음식 목록 로드 (구현 예정)"""
    return {}  # 현재 빈 딕셔너리 반환

def render_menu(all_foods: list[Food]) -> list[str]:
    """메뉴 목록 UI 렌더링 및 선택된 ID 반환 (구현 예정)"""
    return []  # 현재 빈 리스트 반환
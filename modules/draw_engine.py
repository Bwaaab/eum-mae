import random

def draw(selected_ids: list[str]) -> str:
    if not isinstance(selected_ids, list) or any(
        not isinstance(food_id, str) for food_id in selected_ids
    ):
        raise TypeError("selected_ids must be a list of strings")
    return random.choice(selected_ids)
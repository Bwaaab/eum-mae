from dataclasses import dataclass

@dataclass(frozen=True)
class Food:
    id: str                                        # 고유 식별자
    name: str                                      # 음식 이름
    image_path: str = "assets/images/default.png"  # 음식 사진 경로
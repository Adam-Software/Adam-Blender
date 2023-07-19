from typing import Any


class Motor:
    name: str
    JointController: Any
    target_position: float
    present_position: int

    def __init__(self, name: str, JointController: Any) -> None:
        self.name = name
        self.JointController = JointController
        self.target_position = 0
        self.present_position = 0
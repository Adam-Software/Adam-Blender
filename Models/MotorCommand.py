class MotorCommand:
    name: str
    goal_position: float
    speed: int

    def __init__(self, name: str, goal_position: float, speed: int = 0) -> None:
        self.name = name
        self.goal_position = goal_position
        self.speed = speed

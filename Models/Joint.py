class Joint:
    lover_limit: int
    upper_limit: int
    speed: int
    servo_Id: int
    id: int
    
    def __init__(self, lover_limit: int, upper_limit: int, speed: int, id: int) -> None:
        self.lover_limit = lover_limit
        self.upper_limit = upper_limit
        self.speed = speed
        self.id = id

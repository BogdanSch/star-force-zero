from units.unit import Unit
from enums.direction import Direction

class Bullet(Unit):
    BULLET_SYMBOL: str = '◈'
    BULLET_NAME: str = "Bullet"

    def __init__(self, startLocation: tuple = (0, 0)):
        super().__init__(self.BULLET_NAME, self.BULLET_SYMBOL, startLocation)

    def getNextLocation(self, direction: Direction = Direction.UP) -> tuple:
        if direction == Direction.UP:
            return (self.location[0], self.location[1] - 1)
        return self.location
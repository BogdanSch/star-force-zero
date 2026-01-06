from data.enums.entity import Entity
from units.unit import Unit
from data.enums.direction import Direction
from typing import Final

class Bullet(Unit):
    BULLET_SYMBOL: Final[str] = '◈'
    BULLET_SPEED: Final[int] = 20
    BULLET_NAME: Final[str] = "Bullet"

    def __init__(self, startLocation: tuple = (0, 0)):
        super().__init__(self.BULLET_NAME, self.BULLET_SYMBOL, Entity.BULLET, startLocation, self.BULLET_SPEED)

    def getNextLocation(self, direction: Direction = Direction.UP) -> tuple:
        if direction == Direction.UP:
            return (self.location[0], self.location[1] - 1)
        return self.location
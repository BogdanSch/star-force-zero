import random
from data.enums.entity import Entity
from helpers.location import Location
from units.unitWithHealth import UnitWithHealth
from data.enums.direction import Direction

class Enemy(UnitWithHealth):
    def __init__(self, location: Location, speed: int, name: str = "Normal", symbol: str = '!', health: int = 1, damage: int = 1):
        super().__init__(name, symbol, Entity.ENEMY, location, speed, health)
        self._damage = damage
    def getNextLocation(self, direction: Direction = Direction.DOWN) -> Location:
        nextLocation = Location(self.location.x, self.location.y + (1 if direction == Direction.DOWN else -1))
        chance = random.random()
        if 0.34 < chance < 0.4:
            nextLocation.x -= 1
        elif 0.54 < chance < 0.6:
            nextLocation.x += 1
        return nextLocation
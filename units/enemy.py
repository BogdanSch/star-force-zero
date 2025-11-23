import random
from typing import Final
from units.unitWithHealth import UnitWithHealth
from enums.direction import Direction

class Enemy(UnitWithHealth):
    def __init__(self, name: str, location: tuple, symbol: str = '!', health: int = 1, damage: int = 1):
        super().__init__(name, symbol, location, health)
        self.__damage = damage
    def getNextLocation(self, direction: Direction = Direction.DOWN) -> tuple:
        nextLocation = [self.location[0], self.location[1] + 1]
        
        chance = random.random()
        if 0.35 < chance < 0.4:
            nextLocation[0] = nextLocation[0] - 1
        elif 0.55 < chance < 0.6:
            nextLocation[0] = nextLocation[0] + 1
        return tuple(nextLocation)
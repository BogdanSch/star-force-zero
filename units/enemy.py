import random
from typing import Final
from units.unitWithHealth import UnitWithHealth
from enums.direction import Direction

class Enemy(UnitWithHealth):
    def __init__(self, name: str, location: tuple, symbol: str = '!', health: int = 1, damage: int = 1):
        super().__init__(name, symbol, location, health)
        self.__damage = damage
    def getNextLocation(self, direction: Direction = Direction.DOWN) -> tuple:
        if direction == Direction.DOWN:
            return (self.location[0], self.location[1] + 1)
        
        chance = random.random()
        if chance < 0.3:
            return (self.location[0] - 1, self.location[1])
        elif chance < 0.6:
            return (self.location[0] + 1, self.location[1])
        
        return self.location
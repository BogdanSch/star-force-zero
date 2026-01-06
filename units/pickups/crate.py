import random
from data.enums.entity import Entity
from units.pickups.megabomb import Megabomb
from units.unitWithHealth import UnitWithHealth
from units.pickups.extraScore import ExtraScore
from units.pickups.heart import Heart
from data.enums.direction import Direction

class Crate(UnitWithHealth):
    def __init__(self, location: tuple, name: str = "Crate", speed: int = 4, health: int = 1, symbol: str = 'X'):
        super().__init__(name, symbol, Entity.CRATE, location, speed, health)
        self.pickup = random.choice([
            Heart,
            ExtraScore,
            Megabomb
        ])
        self._isRemoved = False
    def spawnPickup(self):
        return self.pickup(self.location)
    def getNextLocation(self, direction: Direction = Direction.DOWN) -> tuple:
        nextLocation = [self.location[0], self.location[1] + (1 if direction == Direction.DOWN else -1)]
        return tuple(nextLocation)
    @property
    def isRemoved(self) -> bool:
        return self._isRemoved
    def remove(self):
        self._isRemoved = True
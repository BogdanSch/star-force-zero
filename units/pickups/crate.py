import random
from units.unitWithHealth import UnitWithHealth
from units.pickups.pickup import Pickup
from data.enums.direction import Direction
from data.enums.pickupType import PickupType

class Crate(UnitWithHealth):
    pickupSymbols: dict[PickupType, str] = {
        PickupType.HEAL: '♥',
        PickupType.MEGABOMB: '♦',
        PickupType.EXTRA_SCORE: '•'
    }
    def __init__(self, name: str, location: tuple, speed: int = 4, health: int = 1, symbol: str = 'X'):
        super().__init__(name, symbol, location, speed, health)
        self.pickupType = random.choice([
            PickupType.HEAL,
            PickupType.MEGABOMB,
            PickupType.EXTRA_SCORE
        ])
        self._isRemoved = False
    def spawnPickup(self):
        return Pickup(self.pickupType, self.pickupSymbols[self.pickupType], self.location)
    def getNextLocation(self, direction: Direction = Direction.DOWN) -> tuple:
        nextLocation = [self.location[0], self.location[1] + (1 if direction == Direction.DOWN else -1)]
        return tuple(nextLocation)
    @property
    def isRemoved(self) -> bool:
        return self._isRemoved
    def remove(self):
        self._isRemoved = True
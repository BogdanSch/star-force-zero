import time
from typing import Final, TYPE_CHECKING # <--- Import TYPE_CHECKING
from data.enums.entity import Entity
from data.enums.direction import Direction
from units.unitWithHealth import UnitWithHealth

# FIX: Only import Pickup for static analysis, not at runtime
if TYPE_CHECKING:
    from units.pickups.pickup import Pickup

class Player(UnitWithHealth):
    PLAYER_SYMBOL: Final[str] = '▲'
    FIRE_COOLDOWN: Final[float] = .5
    INVENTORY_MAX_SIZE: Final[int] = 10

    def __init__(self, name: str, location: tuple, health: int, speed: int = 1, damage: int = 1, score: int = 0):
        super().__init__(name, self.PLAYER_SYMBOL, Entity.PLAYER, location, speed, health)
        self.score: int = score
        self.damage: int = damage
        self.lastFireTime: float = time.time()
        self.inventory: list['Pickup'] = [] 

    def incrementScore(self, value: int = 1) -> None:
        self.score += value

    def getNextLocation(self, direction: Direction) -> tuple:
        if direction == Direction.UP:
            return (self.location[0], self.location[1] - 1)
        elif direction == Direction.DOWN:
            return (self.location[0], self.location[1] + 1)
        elif direction == Direction.LEFT:
            return (self.location[0] - 1, self.location[1])
        elif direction == Direction.RIGHT:
            return (self.location[0] + 1, self.location[1])
        return self.location

    def canFire(self) -> bool:
        """Checks if the player can attack"""
        return time.time() - self.lastFireTime > self.FIRE_COOLDOWN

    def fire(self):
        """Update last fire time when the player shoots."""
        self.lastFireTime = time.time()

    def isInventoryFull(self) -> bool:
        return len(self.inventory) >= self.INVENTORY_MAX_SIZE

    def addItem(self, item: 'Pickup') -> None:
        """Add an item to the inventory."""
        if self.isInventoryFull():
            raise RuntimeError(f"Can't add {item.name}. The inventory is full.")
        self.inventory.append(item)

    def getItemByIndex(self, itemIndex: int) -> 'Pickup':
        """Try to find an item by its index."""
        if itemIndex < 1 or itemIndex > len(self.inventory):
            raise IndexError("Cannot activate this pickup.")
        return self.inventory[itemIndex - 1]
import time
from typing import Final
from data.enums.direction import Direction
from units.unitWithHealth import UnitWithHealth

class Player(UnitWithHealth):
    PLAYER_SYMBOL: Final[str] = '▲'
    PLAYER_MAX_HEALTH: Final[int] = 3
    fireCountdown: float = .5

    def __init__(self, name: str, location: tuple, speed: int = 1, damage: int = 1, score: int = 0):
        super().__init__(name, self.PLAYER_SYMBOL, location, speed, self.PLAYER_MAX_HEALTH)
        self.score = score
        self.damage = damage
        self.lastFireTime = time.time()

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
        return time.time() - self.lastFireTime > self.fireCountdown

    def fire(self):
        """Update last fire time when the player shoots."""
        self.lastFireTime = time.time()
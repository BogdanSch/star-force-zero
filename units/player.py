import time
from units.unit import Unit
from enums.direction import Direction

class Player(Unit):
    PLAYER_SYMBOL: str = '▲'
    PLAYER_MAX_HEALTH: int = 3
    fireCountdown: float = .5

    def __init__(self, name: str = "Main", location: tuple = (0, 0), score: int = 0):
        self.score = score
        self.health = self.PLAYER_MAX_HEALTH
        self.lastFireTime = time.time()
        super().__init__(name, self.PLAYER_SYMBOL, location)

    def incrementScore(self, value: int) -> None:
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
        return time.time() - self.lastFireTime > self.fireCountdown

    def fire(self):
        """Update last fire time when the player shoots."""
        self.lastFireTime = time.time()
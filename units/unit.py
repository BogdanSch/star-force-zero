from data.enums.entity import Entity

class Unit:
    def __init__(self, name: str, symbol: str, entityType: Entity, location: tuple = (0, 0), speed: int = 0):
        self.name = name
        self.symbol = symbol
        self.entityType = entityType
        self.location = location
        self.speed = speed
        self._frameCounter = 0
    def __str__(self):
        return f"{self.symbol}"
    def shouldMove(self) -> bool:
        self._frameCounter += 1
        return self._frameCounter % max(1, (30 // self.speed)) == 0
class Unit:
    def __init__(self, name: str, symbol: str, location: tuple = (0, 0), speed: int = 0):
        self.name = name
        self.symbol = symbol
        self.location = location
        self.speed = speed
        self._frameCounter = 0
    def __str__(self):
        return f"{self.symbol}"
    def shouldMove(self) -> bool:
        self._frameCounter += 1
        return self._frameCounter % max(1, (30 // self.speed)) == 0
from units.unit import Unit

class UnitWithHealth(Unit):
    def __init__(self, name: str, symbol: str, location: tuple, speed: int, health: int):
        super().__init__(name, symbol, location, speed)
        self.health = health
    def takeDamage(self, damage: int) -> None:
        self.health -= damage
    def isAlive(self) -> bool:
        return self.health > 0

from units.unit import Unit

class UnitWithHealth(Unit):
    def __init__(self, name: str, symbol: str, location: tuple, health: int):
        super().__init__(name, symbol, location)
        self.health = health
    def takeDamage(self, damage: int) -> None:
        self.health -= damage
    def isAlive(self) -> bool:
        return self.health > 0

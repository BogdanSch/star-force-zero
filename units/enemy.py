from units.unitWithHealth import UnitWithHealth

class Enemy(UnitWithHealth):
    def __init__(self, name: str, symbol: str, location: tuple, health: int = 1, damage: int = 1):
        super().__init__(self, name, symbol, location, health)
        self.__damage = damage
    def takeDamage(self, damage: int) -> None:
        self.health -= damage
    def isAlive(self) -> bool:
        return self.health > 0
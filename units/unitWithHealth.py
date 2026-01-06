from data.enums.entity import Entity
from helpers.location import Location
from units.unit import Unit

class UnitWithHealth(Unit):
    def __init__(self, name: str, symbol: str, entityType: Entity, location: Location = Location(0, 0), speed: int = 1, health: int = 1) -> None:
        super().__init__(name, symbol, entityType, location, speed)
        self.health = health
    def takeDamage(self, damage: int) -> None:
        self.health -= damage
    def heal(self, amount) -> None:
        self.health += amount
    def isAlive(self) -> bool:
        return self.health > 0

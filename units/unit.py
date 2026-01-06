from typing import TYPE_CHECKING
from data.enums.entity import Entity
from helpers.location import Location
from units.collision.disposable import Disposable

if TYPE_CHECKING:
    from logic.game import Game
    from units.enemy import Enemy
    from units.bullet import Bullet
    from units.pickups.crate import Crate

class Unit:
    def __init__(self, name: str, symbol: str, entityType: Entity, location: Location = Location(0, 0), speed: int = 0):
        self.name = name
        self.symbol = symbol
        self.entityType = entityType
        self.location = location
        self.speed = speed
        self._frameCounter = 0
        
    def shouldMove(self) -> bool:
        self._frameCounter += 1
        return self._frameCounter % max(1, (30 // self.speed)) == 0
    
    def __str__(self):
        return f"{self.symbol}"
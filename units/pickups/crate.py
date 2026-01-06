import random
from typing import TYPE_CHECKING
from data.enums.entity import Entity
from helpers.location import Location
from units.collision.disposable import Disposable
from units.unitWithHealth import UnitWithHealth
from units.pickups.megabomb import Megabomb
from units.pickups.extraScore import ExtraScore
from units.pickups.heart import Heart
from data.enums.direction import Direction
if TYPE_CHECKING:
    from units.pickups.pickup import Pickup
    from logic.game import Game
    from units.bullet import Bullet
    from units.enemy import Enemy

class Crate(UnitWithHealth, Disposable):
    def __init__(self, location: Location, name: str = "Crate", speed: int = 4, health: int = 1, symbol: str = 'X'):
        super().__init__(name, symbol, Entity.CRATE, location, speed, health)
        self.pickup = random.choice([
            Heart,
            ExtraScore,
            Megabomb
        ])
        self._isRemoved = False

    def spawnPickup(self) -> "Pickup":
        return self.pickup(self.location)
    
    def getNextLocation(self, direction: Direction = Direction.DOWN) -> Location:
        nextLocation = Location(self.location.x, self.location.y + (1 if direction == Direction.DOWN else -1))
        return nextLocation
    
    @property
    def isRemoved(self) -> bool:
        return self._isRemoved
    
    def remove(self):
        self._isRemoved = True
    
    def onHitByPlayer(self, game: 'Game') -> bool:
        game.addNotification("Player rammed a crate!", 2)
        game.player.takeDamage(1)
        game.killUnit(self, False)
        return False

    def onHitByBullet(self, bullet: 'Bullet', game: 'Game') -> bool:
        self.takeDamage(1)

        game.killUnit(bullet)
        if not self.isAlive():
            game.killUnit(self)
        return False
    
    def onHitByEnemy(self, enemy: 'Enemy', game: 'Game') -> bool:
        return super().onHitByEnemy(enemy, game)
    
    def onHitByCrate(self, crate: 'Crate', game: 'Game') -> bool:
        return super().onHitByCrate(crate, game)
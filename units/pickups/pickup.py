from typing import TYPE_CHECKING
from data.enums.entity import Entity
from helpers.location import Location
from units.collision.disposable import Disposable
from units.unit import Unit

if TYPE_CHECKING:
    from logic.game import Game
    from units.bullet import Bullet
    from units.enemy import Enemy
    from units.pickups.crate import Crate

class Pickup(Unit, Disposable):
    def __init__(self, name: str, pickupSymbol: str, location: Location, pickupType: Entity) -> None:
        super().__init__(name, pickupSymbol, pickupType, location, 0)
    def pick(self, game: 'Game') -> None:
        pass
    def activate(self, game: "Game") -> None:
        pass

    def onHitByPlayer(self, game: 'Game') -> bool:
        game.handlePickupCollection(self)
        return True

    def onHitByBullet(self, bullet: 'Bullet', game: 'Game') -> bool:
        return super().onHitByBullet(bullet, game)
    
    def onHitByEnemy(self, enemy: 'Enemy', game: 'Game') -> bool:
        return super().onHitByEnemy(enemy, game)
    
    def onHitByCrate(self, crate: 'Crate', game: 'Game') -> bool:
        game.killUnit(crate)
        return False
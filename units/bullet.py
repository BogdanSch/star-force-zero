from typing import TYPE_CHECKING, Final
from data.enums.entity import Entity
from helpers.location import Location
from units.collision.disposable import Disposable
from units.unit import Unit
from data.enums.direction import Direction

if TYPE_CHECKING:
    from logic.game import Game
    from units.enemy import Enemy
    from units.pickups.crate import Crate

class Bullet(Unit, Disposable):
    BULLET_SYMBOL: Final[str] = '◈'
    BULLET_SPEED: Final[int] = 20
    BULLET_NAME: Final[str] = "Bullet"

    def __init__(self, startLocation: Location = Location(0, 0)):
        super().__init__(self.BULLET_NAME, self.BULLET_SYMBOL, Entity.BULLET, startLocation, self.BULLET_SPEED)

    def getNextLocation(self, direction: Direction = Direction.UP) -> Location:
        if direction == Direction.UP: 
            return Location(self.location.x, self.location.y - 1)
        return self.location
    
    def onHitByPlayer(self, game: 'Game') -> bool:
        return super().onHitByPlayer(game)

    def onHitByBullet(self, bullet: 'Bullet', game: 'Game') -> bool:
        return super().onHitByBullet(bullet, game)
    
    def onHitByEnemy(self, enemy: 'Enemy', game: 'Game') -> bool:
        enemy.takeDamage(1)
        game.player.incrementScore(game.SCORE_INCREMENT)
        
        game.killUnit(self) 
        if not enemy.isAlive():
            game.killUnit(enemy)
        return False
    
    def onHitByCrate(self, crate: 'Crate', game: 'Game') -> bool:
        crate.takeDamage(1)
        
        game.killUnit(self) 
        if not crate.isAlive():
            game.killUnit(crate)
        return False
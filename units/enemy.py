import random
from typing import TYPE_CHECKING
from data.enums.entity import Entity
from helpers.location import Location
from units.collision.disposable import Disposable
from units.unitWithHealth import UnitWithHealth
from data.enums.direction import Direction

if TYPE_CHECKING:
    from logic.game import Game
    from units.bullet import Bullet
    from units.pickups.crate import Crate

class Enemy(UnitWithHealth, Disposable):
    def __init__(self, location: Location, speed: int, name: str = "Normal", symbol: str = '!', health: int = 1, damage: int = 1):
        super().__init__(name, symbol, Entity.ENEMY, location, speed, health)
        self._damage = damage

    def getNextLocation(self, direction: Direction = Direction.DOWN) -> Location:
        nextLocation = Location(self.location.x, self.location.y + (1 if direction == Direction.DOWN else -1))
        chance = random.random()
        if 0.34 < chance < 0.4:
            nextLocation.x -= 1
        elif 0.54 < chance < 0.6:
            nextLocation.x += 1
        return nextLocation
    
    def onHitByPlayer(self, game: 'Game') -> bool:
        game.addNotification("Player rammed Enemy!")
        game.player.takeDamage(1)
        game.player.incrementScore(game.SCORE_INCREMENT)
        self.takeDamage(self.health)
        if not self.isAlive():
            game.killUnit(self)
        return False

    def onHitByBullet(self, bullet: 'Bullet', game: 'Game') -> bool:
        self.takeDamage(1)
        game.player.incrementScore(game.SCORE_INCREMENT)
        
        game.killUnit(bullet) 
        if not self.isAlive():
            game.killUnit(self)
        return False
    
    def onHitByEnemy(self, enemy: 'Enemy', game: 'Game') -> bool:
        return super().onHitByEnemy(enemy, game)
    
    def onHitByCrate(self, crate: 'Crate', game: 'Game') -> bool:
        return super().onHitByCrate(crate, game)
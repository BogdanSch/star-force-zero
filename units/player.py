import time
from typing import Final, TYPE_CHECKING
from data.enums.entity import Entity
from data.enums.direction import Direction
from helpers.location import Location
from units.collision.disposable import Disposable
from units.unitWithHealth import UnitWithHealth

if TYPE_CHECKING:
    from units.pickups.pickup import Pickup
    from logic.game import Game
    from units.bullet import Bullet
    from units.enemy import Enemy
    from units.pickups.crate import Crate

class Player(UnitWithHealth, Disposable):
    PLAYER_SYMBOL: Final[str] = '▲'
    FIRE_COOLDOWN: Final[float] = .5
    INVENTORY_MAX_SIZE: Final[int] = 10

    def __init__(self, name: str, location: Location, health: int, speed: int = 1, damage: int = 1, score: int = 0):
        super().__init__(name, self.PLAYER_SYMBOL, Entity.PLAYER, location, speed, health)
        self.score: int = score
        self.damage: int = damage
        self.lastFireTime: float = time.time()
        self.inventory: list['Pickup'] = [] 

    def incrementScore(self, value: int = 1) -> None:
        self.score += value

    def getNextLocation(self, direction: Direction) -> Location:
        if direction == Direction.UP:
            return Location(self.location.x, self.location.y - 1)
        elif direction == Direction.DOWN:
            return Location(self.location.x, self.location.y + 1)
        elif direction == Direction.LEFT:
            return Location(self.location.x - 1, self.location.y)
        elif direction == Direction.RIGHT:
            return Location(self.location.x + 1, self.location.y)
        return self.location

    def canFire(self) -> bool:
        """Checks if the player can attack"""
        return time.time() - self.lastFireTime > self.FIRE_COOLDOWN

    def fire(self):
        """Update last fire time when the player shoots."""
        self.lastFireTime = time.time()

    def isInventoryFull(self) -> bool:
        return len(self.inventory) >= self.INVENTORY_MAX_SIZE

    def addItem(self, item: 'Pickup') -> None:
        """Add an item to the inventory."""
        if self.isInventoryFull():
            raise RuntimeError(f"Can't add {item.name}. The inventory is full.")
        self.inventory.append(item)

    def getItemByIndex(self, itemIndex: int) -> 'Pickup':
        """Try to find an item by its index."""
        if itemIndex < 1 or itemIndex > len(self.inventory):
            raise IndexError("Cannot activate this pickup.")
        return self.inventory[itemIndex - 1]
    
    def onHitByPlayer(self, game: 'Game') -> bool:
        return super().onHitByPlayer(game)

    def onHitByBullet(self, bullet: 'Bullet', game: 'Game') -> bool:
        return super().onHitByBullet(bullet, game)
    
    def onHitByEnemy(self, enemy: 'Enemy', game: 'Game') -> bool:
        game.addNotification("Player was hit by an enemy", 3)
        enemy.takeDamage(1)
        game.player.incrementScore(game.SCORE_INCREMENT)
        
        game.killUnit(self) 
        if not enemy.isAlive():
            game.killUnit(enemy)
        return True
    
    def onHitByCrate(self, crate: 'Crate', game: 'Game') -> bool:
        game.addNotification("Player rammed a crate!")
        crate.takeDamage(1)
        self.takeDamage(1)
        
        if not crate.isAlive():
            game.killUnit(crate)
            return True
        return False
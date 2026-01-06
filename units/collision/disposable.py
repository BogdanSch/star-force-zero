from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from logic.game import Game
    from units.bullet import Bullet
    from units.enemy import Enemy
    from units.pickups.crate import Crate

class Disposable(ABC):
    @abstractmethod
    def onHitByPlayer(self, game: 'Game') -> bool:
        """
        Called when a Player tries to move into this unit.
        Return True if the Player can enter the cell (unit removed/collected).
        Return False if the Player is blocked.
        """
        return False

    @abstractmethod
    def onHitByBullet(self, bullet: 'Bullet', game: 'Game') -> bool:
        """
        Called when a Bullet hits this unit.
        Return True if the Bullet should continue moving (rare).
        Return False if the Bullet is destroyed/blocked.
        """
        return False

    @abstractmethod
    def onHitByEnemy(self, enemy: 'Enemy', game: 'Game') -> bool:
        """
        Called when an Enemy runs into this unit.
        """
        return False
    
    @abstractmethod
    def onHitByCrate(self, crate: 'Crate', game: 'Game') -> bool:
        """
        Called when a Crate runs into this unit.
        """
        return False
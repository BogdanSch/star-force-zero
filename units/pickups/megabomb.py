from typing import TYPE_CHECKING
from data.enums.entity import Entity
from units.pickups.pickup import Pickup

if TYPE_CHECKING:
    from logic.game import Game
    
class Megabomb(Pickup):
    def __init__(self, position: tuple[int, int]):
        super().__init__("Megabomb", '♦', position, Entity.MEGABOMB)
    def pick(self, game: "Game") -> None:
        try:
            game.player.addItem(self)
            game.addNotification("Collected a megabomb.")
        except RuntimeError as e:
            game.addNotification(str(e))
    def activate(self, game: "Game") -> None:
        game.addNotification("Megabomb activated!")
        enemiesDestroyed = len(game._enemies)
        game.player.incrementScore(enemiesDestroyed * game.SCORE_INCREMENT)
        for enemy in game._enemies:
            game._grid[enemy.location[1]][enemy.location[0]] = game.EMPTY_CELL_SYMBOL
            game._enemies.clear()
        game.player.inventory.remove(self)
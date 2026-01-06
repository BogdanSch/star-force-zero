from typing import TYPE_CHECKING
from data.enums.entity import Entity
from units.pickups.pickup import Pickup

if TYPE_CHECKING:
    from logic.game import Game

class ExtraScore(Pickup):
    def __init__(self, position: tuple[int, int]):
        super().__init__("Extra Score", '★', position, Entity.EXTRA_SCORE)
    def pick(self, game: "Game") -> None:
        self.activate(game)
    def activate(self, game: "Game") -> None:
        game.player.incrementScore(game.EXTRA_SCORE_INCREMENT)
from typing import TYPE_CHECKING
from data.enums.entity import Entity
from helpers.location import Location
from units.pickups.pickup import Pickup

if TYPE_CHECKING:
    from logic.game import Game

class Heart(Pickup):
    def __init__(self, position: Location):
        super().__init__("Heart", '♥', position, Entity.HEART)
    def pick(self, game: "Game") -> None:
        self.activate(game)
    def activate(self, game: "Game") -> None:
        game.player.heal(1)
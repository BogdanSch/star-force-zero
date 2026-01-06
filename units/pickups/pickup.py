from typing import TYPE_CHECKING
from data.enums.entity import Entity
from units.unit import Unit

if TYPE_CHECKING:
    from logic.game import Game

class Pickup(Unit):
    def __init__(self, name: str, pickupSymbol: str, location: tuple[int, int], pickupType: Entity) -> None:
        super().__init__(name, pickupSymbol, pickupType, location, 0)
    def pick(self, game: "Game") -> None:
        pass
    def activate(self, game: "Game") -> None:
        pass
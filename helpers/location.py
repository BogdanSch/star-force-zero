from logic import game
from logic.game import Game
from units.unit import Unit

class Location:
    __slots__ = ["x", "y"]
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    def getOccupyingUnit(self, grid: list[list[Unit | str]]) -> Unit | None:
        cell = grid[self.y][self.x]
        return cell if isinstance(cell, Unit) else None
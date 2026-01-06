from typing import TYPE_CHECKING, Iterator
from helpers.location import Location
from units.unit import Unit
from units.wall import Wall
if TYPE_CHECKING:
    from logic.game import Game

class Grid:
    def __init__(self, gridSize: tuple[int, int], game: "Game") -> None:
        self.gridSize = gridSize
        self.game = game
        self._grid: list[list[Unit | str]] = []
        self.initializeGrid()
    
    def initializeGrid(self):
        for y in range(self.gridSize[1]):
            row = []
            for x in range(self.gridSize[0]):
                if y == 0 or y == self.gridSize[1] - 1 or x == 0 or x == self.gridSize[0] - 1:
                    row.append(Wall(Location(x, y)))
                elif Location(x, y) == self.game.player.location:
                    row.append(self.game.player)
                else:
                    row.append(self.game.EMPTY_CELL_SYMBOL)
            self._grid.append(row)
    
    def isLocationValid(self, location: Location) -> bool:
        if location.x <= 0 or location.x >= self.gridSize[0] - 1: return False
        elif location.y <= 0 or location.y >= self.gridSize[1] - 1: return False
        return True
    
    def isLocationAtLowerBorder(self, location: Location) -> bool:
        return location.y >= self.gridSize[1] - 1
    
    def isBlocked(self, location: Location) -> bool:
        return self.getOccupyingUnit(location) is not None

    def getOccupyingUnit(self, location: Location) -> Unit | None:
        if self.isLocationValid(location) is False: return None

        cell = self._grid[location.y][location.x]
        return cell if isinstance(cell, Unit) else None
    
    def setOccupyingUnit(self, location: Location, unit: Unit | str) -> None:
        if self.isLocationValid(location) is False: return
        self._grid[location.y][location.x] = unit
    
    @property
    def grid(self) -> Iterator[list]:
        for row in self._grid:
            yield row
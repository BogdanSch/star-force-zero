import time
from units.player import Player
from units.wall import Wall
from units.enemy import Enemy
from units.bullet import Bullet
from enums.direction import Direction

class Game:
    EMPTY_CELL_SYMBOL: str = ' '
    __slots__ = ["player", "gridSize", "gameDurationInSeconds", "__grid", "__gameState", "__bullets", "__enemies", "startTime"]

    def __init__(self, player: Player, gridSize: tuple, gameDurationInSeconds: int):
        self.player = player
        self.gridSize = gridSize

        self.__grid = []
        self.initializeGrid()

        self.__enemies = []
        self.__bullets = []

        self.__gameState = "The round has started"
        self.startTime = time.time()
        self.gameDurationInSeconds = gameDurationInSeconds

    def initializeGrid(self):
        for y in range(self.gridSize[1]):
            row = []
            for x in range(self.gridSize[0]):
                if y == 0 or y == self.gridSize[1] - 1 or x == 0 or x == self.gridSize[0] - 1:
                    row.append(Wall((x, y)))
                elif (x, y) == self.player.location:
                    row.append(self.player)
                else:
                    row.append(self.EMPTY_CELL_SYMBOL)
            self.__grid.append(row)

    @property
    def grid(self) -> list:
        for row in self.__grid:
            yield row

    @property
    def gameState(self) -> str:
        return self.__gameState

    def getTimeLeft(self) -> float:
        return time.time() - self.startTime

    def isGameOver(self) -> bool:
        if time.time() - self.startTime > self.gameDurationInSeconds or self.player.health <= 0:
            self.__gameState = "Game Over"
            return True
        return False

    def isLocationValid(self, location: tuple) -> bool:
        if location[0] <= 0 or location[0] >= self.gridSize[0]: return False
        elif location[1] <= 0 or location[1] >= self.gridSize[1]: return False
        elif (isinstance(self.__grid[location[1]][location[0]], Wall)
                or isinstance(self.__grid[location[1]][location[0]], Enemy)
                or isinstance(self.__grid[location[1]][location[0]], Bullet)): return False
        return True

    def isLocationAtBorder(self, location: tuple) -> bool:
        return (location[0] <= 0 or location[0] >= self.gridSize[0]) or (location[1] <= 0 or location[1] >= self.gridSize[1])

    def moveEnemies(self):
        pass

    def movePlayer(self, direction: Direction) -> None:
        nextLocation = self.player.getNextLocation(direction)

        if self.isLocationValid(nextLocation):
            self.__grid[self.player.location[1]][self.player.location[0]] = self.EMPTY_CELL_SYMBOL
            self.player.location = nextLocation
            self.__grid[self.player.location[1]][self.player.location[0]] = self.player

    def moveBullets(self) -> None:
        bulletsToRemove = []
        for bullet in self.__bullets:
            targetLocation = bullet.getNextLocation()
            targetUnit = self.__grid[targetLocation[1]][targetLocation[0]]

            if targetUnit and isinstance(targetUnit, Enemy):
                bulletsToRemove.append(bullet)
                self.__enemies.remove(targetUnit)
                self.__grid[targetLocation[1]][targetLocation[0]] = self.EMPTY_CELL_SYMBOL
            elif targetUnit and isinstance(targetUnit, Wall):
                bulletsToRemove.append(bullet)
            else:
                if self.isLocationValid(targetLocation):
                    self.__grid[bullet.location[1]][bullet.location[0]] = self.EMPTY_CELL_SYMBOL
                    bullet.location = targetLocation
                    self.__grid[bullet.location[1]][bullet.location[0]] = bullet

        for bullet in bulletsToRemove:
            self.__bullets.remove(bullet)
            self.__grid[bullet.location[1]][bullet.location[0]] = self.EMPTY_CELL_SYMBOL

    def update(self) -> None:
        self.moveBullets()
        self.moveEnemies()

    def spawnBullet(self) -> None:
        if not self.player.canFire():
            self.__gameState = "Reloading"
            return;

        bulletLocation = self.player.getNextLocation(Direction.UP)

        if self.isLocationValid(bulletLocation):
            self.__gameState = "Fired"

            self.player.fire()
            bullet = Bullet(bulletLocation)
            self.__bullets.append(bullet)
            self.__grid[bullet.location[1]][bullet.location[0]] = bullet
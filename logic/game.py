import datetime
import random
import time

from typing import Final, Iterator
from repositories.scoreRepository import ScoreRepository
from data.score import Score
from units.player import Player
from units.wall import Wall
from units.enemy import Enemy
from units.bullet import Bullet
from enums.direction import Direction

class Game:
    EMPTY_CELL_SYMBOL: Final[str] = ' '
    ENEMY_SPAWN_INTERVAL_DECREMENT: Final[float] = 0.1
    MIN_ENEMY_SPAWN_INTERVAL: Final[float] = 0.5
    ENEMY_MOVE_EVERY_N_FRAMES: Final[int] = 8
    SCORE_INCREMENT: Final[int] = 20
    SCORE_REWARD_FRAMES_INTERVAL: Final[int] = 40
    # __slots__ = ["player", "gridSize", "gameDurationInSeconds", "__grid", "__gameState", "__bullets", "__enemies", "startTime"]

    def __init__(self, player: Player, gridSize: tuple, gameDurationInSeconds: int):
        self.player = player
        self.gridSize = gridSize

        self.__grid = []
        self.initializeGrid()

        self.__enemies: list[Enemy] = []
        self.__bullets: list[Bullet] = []

        self.__gameState = "The round has started"
        self.startTime = time.time()
        self.gameDurationInSeconds = gameDurationInSeconds

        self.__enemySpawnInterval = 5.0
        self.__lastEnemySpawnTime = time.time()
        self.__frameCounter = 0

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
    def grid(self) -> Iterator[list]:
        for row in self.__grid:
            yield row

    @property
    def gameState(self) -> str:
        return self.__gameState

    def getTimeLeft(self) -> float:
        return self.startTime + self.gameDurationInSeconds - time.time()

    def isGameOver(self) -> bool:
        if time.time() - self.startTime > self.gameDurationInSeconds or self.player.health <= 0:
            self.__gameState = "Game Over"
            return True
        return False

    def isLocationValid(self, location: tuple) -> bool:
        if location[0] <= 0 or location[0] >= self.gridSize[0]: return False
        elif location[1] <= 0 or location[1] >= self.gridSize[1]: return False
        elif (isinstance(self.__grid[location[1]][location[0]], Wall)
                or isinstance(self.__grid[location[1]][location[0]], Bullet)): return False
        return True

    def isLocationAtLowerBorder(self, location: tuple) -> bool:
        return location[1] == self.gridSize[1] - 1

    def moveEnemies(self):
        enemiesToRemove = []
        for enemy in self.__enemies:
            if not enemy.isAlive():
                enemiesToRemove.append(enemy)
                continue

            targetLocation = enemy.getNextLocation()
            targetUnit = self.__grid[targetLocation[1]][targetLocation[0]]

            if targetUnit and isinstance(targetUnit, Player):
                self.__gameState = "Player was hit by enemy"
                enemiesToRemove.append(enemy)
                self.player.takeDamage(1)
            elif targetUnit and isinstance(targetUnit, Wall) and self.isLocationAtLowerBorder(targetLocation):
                self.__gameState = "Enemy reached the base"
                enemiesToRemove.append(enemy)
                self.player.takeDamage(1)
            else:
                if self.isLocationValid(targetLocation):
                    self.__grid[enemy.location[1]][enemy.location[0]] = self.EMPTY_CELL_SYMBOL
                    enemy.location = targetLocation
                    self.__grid[enemy.location[1]][enemy.location[0]] = enemy

        for enemy in enemiesToRemove:
            self.__enemies.remove(enemy)
            self.__grid[enemy.location[1]][enemy.location[0]] = self.EMPTY_CELL_SYMBOL

    def movePlayer(self, direction: Direction) -> None:
        nextLocation = self.player.getNextLocation(direction)
        if not self.isLocationValid(nextLocation): return

        targetUnit = self.__grid[nextLocation[1]][nextLocation[0]]
        if isinstance(targetUnit, Enemy) and targetUnit.isAlive():
            self.__gameState = "Player was hit by enemy"
            self.__enemies.remove(targetUnit)
            self.player.takeDamage(1)

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
                targetUnit.takeDamage(1)
                self.player.incrementScore(self.SCORE_INCREMENT)
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
        self.__frameCounter += 1
        if self.__frameCounter % self.SCORE_REWARD_FRAMES_INTERVAL == 0:
            self.player.incrementScore()

        self.trySpawnEnemy()
        self.moveBullets()
        if self.__frameCounter % self.ENEMY_MOVE_EVERY_N_FRAMES == 0:
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

    def trySpawnEnemy(self) -> None:
        if time.time() - self.__lastEnemySpawnTime < self.__enemySpawnInterval:
            return
        self.__lastEnemySpawnTime = time.time()

        if self.__enemySpawnInterval > self.MIN_ENEMY_SPAWN_INTERVAL:
            self.__enemySpawnInterval -= self.ENEMY_SPAWN_INTERVAL_DECREMENT

        enemy = Enemy("Normal", (random.randint(1, len(self.__grid[0]) - 2), 1))
        self.__enemies.append(enemy)

    def getScore(self) -> Score:
        return Score(self.player.name, self.player.score, datetime.datetime.now().isoformat())

    def saveProgress(self, scoreRepository: ScoreRepository) -> None:
        scoreRepository.addScore(self.getScore())
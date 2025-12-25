import datetime
import random
import time

from typing import Final, Iterator
from repositories.scoreRepository import ScoreRepository
from data.score import Score
from units.unit import Unit
from units.player import Player
from units.wall import Wall
from units.enemy import Enemy
from units.bullet import Bullet
from units.pickups.crate import Crate
from units.pickups.pickup import Pickup
from data.enums.direction import Direction

class Game:
    EMPTY_CELL_SYMBOL: Final[str] = ' '

    ENEMY_SPAWN_INTERVAL_DECREMENT: Final[float] = 0.04
    MIN_ENEMY_SPAWN_INTERVAL: Final[float] = 0.5
    MAX_NUMBER_OF_ENEMIES_TO_SPAWN: Final[int] = 4

    SCORE_INCREMENT: Final[int] = 20
    SCORE_REWARD_FRAMES_INTERVAL: Final[int] = 40

    def __init__(self, player: Player, gridSize: tuple, gameDurationInSeconds: int):
        self.player = player
        self.gridSize = gridSize

        self._grid: list[Unit | str] = []
        self.initializeGrid()

        self._enemies: list[Enemy] = []
        self._bullets: list[Bullet] = []
        self._crates: list[Crate] = []
        self._pickups: list[Pickup] = []

        self._gameStatus: str = "Running"
        self._notifications: list[dict] = []
        self.startTime = time.time()
        self.gameDurationInSeconds = gameDurationInSeconds

        self._enemySpawnInterval = 9.0
        self._lastEnemySpawnTime = time.time()
        self._frameCounter = 0

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
            self._grid.append(row)

    @property
    def grid(self) -> Iterator[list]:
        for row in self._grid:
            yield row

    @property
    def gameState(self) -> str:
        return self._gameState

    def getTimeLeft(self) -> float:
        return self.startTime + self.gameDurationInSeconds - time.time()

    def isGameOver(self) -> bool:
        if time.time() - self.startTime > self.gameDurationInSeconds or self.player.health <= 0:
            self._gameStatus = "Game Over"
            self.addNotification("Game Over", 999)
            return True
        return False

    def isLocationValid(self, location: tuple) -> bool:
        if location[0] <= 0 or location[0] >= self.gridSize[0]: return False
        elif location[1] <= 0 or location[1] >= self.gridSize[1]: return False
        return True

    def isBlocked(self, location: tuple) -> bool:
        unit: Unit | str = self._grid[location[1]][location[0]]
        return isinstance(unit, (Wall, Bullet, Enemy, Crate))

    def isLocationAtLowerBorder(self, location: tuple) -> bool:
        return location[1] == self.gridSize[1] - 1
        
    def addNotification(self, text: str, duration: float = 1.5) -> None:
        self._notifications.append({
            "text": text,
            "expiresAt": time.time() + duration
        })
        
    def moveEnemies(self):
        enemiesToRemove = []
        for enemy in self._enemies:
            if not enemy.shouldMove():
                continue
            if not enemy.isAlive():
                enemiesToRemove.append(enemy)
                continue

            targetLocation = enemy.getNextLocation()
            targetUnit = self._grid[targetLocation[1]][targetLocation[0]]

            if targetUnit and isinstance(targetUnit, Player):
                self.addNotification("Player was hit by enemy")
                enemiesToRemove.append(enemy)
                self.player.takeDamage(1)
            elif self.isLocationAtLowerBorder(targetLocation):
                self.addNotification("Enemy reached the base")
                enemiesToRemove.append(enemy)
                self.player.takeDamage(1)
            else:
                if self.isLocationValid(targetLocation) and not self.isBlocked(targetLocation):
                    self._grid[enemy.location[1]][enemy.location[0]] = self.EMPTY_CELL_SYMBOL
                    enemy.location = targetLocation
                    self._grid[enemy.location[1]][enemy.location[0]] = enemy

        for enemy in enemiesToRemove:
            self._enemies.remove(enemy)
            self._grid[enemy.location[1]][enemy.location[0]] = self.EMPTY_CELL_SYMBOL

    def movePlayer(self, direction: Direction) -> None:
        nextLocation = self.player.getNextLocation(direction)
        if not self.isLocationValid(nextLocation): return
        targetUnit = self._grid[nextLocation[1]][nextLocation[0]]

        if isinstance(targetUnit, Enemy) and targetUnit.isAlive():
            self.addNotification("Player was hit by enemy")
            self._enemies.remove(targetUnit)
            self.player.takeDamage(1)
        elif isinstance(targetUnit, Pickup):
            self.addNotification(f"Picked up {targetUnit.type.value}")
            self.player.inventory.append(targetUnit)
            self._pickups.remove(targetUnit)

        if self.isBlocked(nextLocation): return

        self._grid[self.player.location[1]][self.player.location[0]] = self.EMPTY_CELL_SYMBOL
        self.player.location = nextLocation
        self._grid[self.player.location[1]][self.player.location[0]] = self.player

    def moveBullets(self) -> None:
        bulletsToRemove = []
        for bullet in self._bullets:
            targetLocation = bullet.getNextLocation()
            if not self.isLocationValid(targetLocation):
                bulletsToRemove.append(bullet)
                continue
            if not bullet.shouldMove(): continue

            targetUnit = self._grid[targetLocation[1]][targetLocation[0]]

            if targetUnit and isinstance(targetUnit, Enemy):
                bulletsToRemove.append(bullet)
                targetUnit.takeDamage(1)
                self.player.incrementScore(self.SCORE_INCREMENT)
            elif targetUnit and isinstance(targetUnit, Crate):
                bulletsToRemove.append(bullet)
                targetUnit.takeDamage(1)
                if targetUnit.isAlive():
                    continue

                pickup: Pickup = targetUnit.spawnPickup()
                pickup.location = targetLocation

                self._pickups.append(pickup)
                self._crates.remove(targetUnit)
                self._grid[bullet.location[1]][bullet.location[0]] = self.EMPTY_CELL_SYMBOL
                self._grid[targetLocation[1]][targetLocation[0]] = pickup
            elif targetUnit and isinstance(targetUnit, Pickup):
                bulletsToRemove.append(bullet)
            else:
                self._grid[bullet.location[1]][bullet.location[0]] = self.EMPTY_CELL_SYMBOL
                bullet.location = targetLocation
                self._grid[bullet.location[1]][bullet.location[0]] = bullet

        for bullet in bulletsToRemove:
            self._bullets.remove(bullet)
            self._grid[bullet.location[1]][bullet.location[0]] = self.EMPTY_CELL_SYMBOL

    def moveCrates(self) -> None:
        cratesToRemove = []

        for crate in self._crates:
            if not crate.shouldMove(): continue
            targetLocation = crate.getNextLocation()
            if self.isLocationAtLowerBorder(targetLocation):
                cratesToRemove.append(crate)
                continue
            if not self.isLocationValid(targetLocation):
                continue

            self._grid[crate.location[1]][crate.location[0]] = self.EMPTY_CELL_SYMBOL
            crate.location = targetLocation
            self._grid[targetLocation[1]][targetLocation[0]] = crate

        for crate in cratesToRemove:
            self._crates.remove(crate)
            self._grid[crate.location[1]][crate.location[0]] = self.EMPTY_CELL_SYMBOL

    def update(self) -> None:
        self._frameCounter += 1
        if self._frameCounter % self.SCORE_REWARD_FRAMES_INTERVAL == 0:
            self.player.incrementScore()
        if self.player.canFire():
            self.addNotification("Ready to fire", 0.45)
        else:
            self.addNotification("Reloading", 0.5)

        self.trySpawnCrate()
        self.trySpawnEnemies()
        self.moveBullets()
        self.moveCrates()
        self.moveEnemies()

    def spawnBullet(self) -> None:
        if not self.player.canFire():
            return

        bulletLocation = self.player.getNextLocation(Direction.UP)
        if not self.isLocationValid(bulletLocation) or self.isBlocked(bulletLocation):
            return

        self.player.fire()
        bullet = Bullet(bulletLocation)
        self._bullets.append(bullet)
        self._grid[bullet.location[1]][bullet.location[0]] = bullet

    def trySpawnEnemies(self) -> None:
        if time.time() - self._lastEnemySpawnTime < self._enemySpawnInterval: return

        self._lastEnemySpawnTime = time.time()
        if self._enemySpawnInterval > self.MIN_ENEMY_SPAWN_INTERVAL:
            self._enemySpawnInterval -= self.ENEMY_SPAWN_INTERVAL_DECREMENT

        anchorX = random.randint(1, self.gridSize[0] - 2)
        count = random.randint(1, self.MAX_NUMBER_OF_ENEMIES_TO_SPAWN)
        possibleOffsets = [-3, -1, 0, 1, 3]

        xPositions = []
        for offset in possibleOffsets:
            x = anchorX + offset
            if self.isLocationValid((x, 1)) and not self.isBlocked((x, 1)):
                xPositions.append(x)
            if len(xPositions) == count: break
        for x in xPositions:
            enemy = Enemy("Normal", (x, 1), 4)
            self._enemies.append(enemy)
            self._grid[1][x] = enemy

    def trySpawnCrate(self):
        if random.random() > 10e-4 / 1.5: return

        x = random.randint(1, self.gridSize[0] - 2)
        if not self.isLocationValid((x, 1)) or self.isBlocked((x, 1)): return

        crate = Crate("Crate", (x, 1))
        self._crates.append(crate)
        self._grid[1][x] = crate

    def getScore(self) -> Score:
        return Score(self.player.name, self.player.score, datetime.datetime.now().isoformat())

    def saveProgress(self, scoreRepository: ScoreRepository) -> None:
        scoreRepository.addScore(self.getScore())
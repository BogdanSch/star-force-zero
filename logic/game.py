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
from data.enums.pickupType import PickupType
from data.enums.direction import Direction

class Game:
    EMPTY_CELL_SYMBOL: Final[str] = ' '

    ENEMY_SPAWN_INTERVAL_DECREMENT: Final[float] = 0.04
    MIN_ENEMY_SPAWN_INTERVAL: Final[float] = 0.5
    MAX_NUMBER_OF_ENEMIES_TO_SPAWN: Final[int] = 4

    SCORE_INCREMENT: Final[int] = 20
    EXTRA_SCORE_INCREMENT: Final[int] = 100
    SCORE_REWARD_FRAMES_INTERVAL: Final[int] = 30

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

        self._enemySpawnInterval = 8.0
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
    def gameStatus(self) -> str:
        return self._gameStatus

    @property
    def notifications(self) -> list[dict]:
        return [n["text"] for n in self._notifications if n["expiresAt"] > time.time()]

    def getTimeLeft(self) -> float:
        return self.startTime + self.gameDurationInSeconds - time.time()

    def isGameOver(self) -> bool:
        if self.player.health <= 0:
            self._gameStatus = "Game Over"
            self.addNotification("Game Over", 999)
            return True
        elif time.time() - self.startTime > self.gameDurationInSeconds:
            self._gameStatus = "Victory"
            self.addNotification("Victory!", 999)
            return True
        return False

    def isLocationValid(self, location: tuple) -> bool:
        if location[0] <= 0 or location[0] >= self.gridSize[0]: return False
        elif location[1] <= 0 or location[1] >= self.gridSize[1]: return False
        return True

    def isBlocked(self, location: tuple) -> bool:
        unit: Unit | str = self._grid[location[1]][location[0]]
        return isinstance(unit, (Wall, Bullet, Enemy, Crate, Pickup, Player))

    def isLocationAtLowerBorder(self, location: tuple) -> bool:
        return location[1] == self.gridSize[1] - 1
        
    def addNotification(self, text: str, duration: float = 1.5) -> None:
        if any(n["text"] == text and n["expiresAt"] > time.time() for n in self._notifications):
            return
        self._notifications.append({
            "text": text,
            "expiresAt": time.time() + duration
        })

    def _updateUnitPosition(self, unit: Unit, nextLocation: tuple) -> None:
        currentOccupant = self._grid[unit.location[1]][unit.location[0]]
        if currentOccupant == unit:
            self._grid[unit.location[1]][unit.location[0]] = self.EMPTY_CELL_SYMBOL
        unit.location = nextLocation
        self._grid[nextLocation[1]][nextLocation[0]] = unit
        
    def moveEnemies(self):
        enemiesToRemove = []
        for enemy in self._enemies:
            if not enemy.shouldMove():
                continue
            if not enemy.isAlive():
                enemiesToRemove.append(enemy)
                continue

            targetLocation = enemy.getNextLocation()
            if not self.isLocationValid(targetLocation):
                continue

            if self.isBlocked(targetLocation):
                targetUnit = self._grid[targetLocation[1]][targetLocation[0]]
                
                if targetUnit and isinstance(targetUnit, Player):
                    self.addNotification("Player was hit by an enemy", 3)
                    enemiesToRemove.append(enemy)
                    self.player.takeDamage(1)
                elif self.isLocationAtLowerBorder(targetLocation):
                    self.addNotification("Enemy reached the base", 3)
                    enemiesToRemove.append(enemy)
                    self.player.takeDamage(1)
                elif targetUnit and isinstance(targetUnit, Bullet):
                    enemy.takeDamage(1)
                    self.player.incrementScore(self.SCORE_INCREMENT)
                    self._bullets.remove(targetUnit)
                elif targetUnit and (isinstance(targetUnit, (Crate, Pickup, Enemy))):
                    continue
                else:
                    enemiesToRemove.append(enemy)
            else:
                self._updateUnitPosition(enemy, targetLocation)

        for enemy in enemiesToRemove:
            self._enemies.remove(enemy)
            self._grid[enemy.location[1]][enemy.location[0]] = self.EMPTY_CELL_SYMBOL

    def handlePickupCollection(self, pickup: Pickup) -> None:
        self.addNotification(f"Picked up {pickup.type.value}")
        self._pickups.remove(pickup)

        match pickup.type:
            case PickupType.HEAL:
                self.player.heal(1)
            case PickupType.EXTRA_SCORE:
                self.player.incrementScore(self.EXTRA_SCORE_INCREMENT)
            case _:
                self.player.inventory.append(pickup)

        self._updateUnitPosition(self.player, pickup.location)

    def movePlayer(self, direction: Direction) -> None:
        nextLocation = self.player.getNextLocation(direction)
        if not self.isLocationValid(nextLocation): return

        if self.isBlocked(nextLocation):
            targetUnit = self._grid[nextLocation[1]][nextLocation[0]]
            if targetUnit and isinstance(targetUnit, Enemy):
                self.addNotification("Player rammed an enemy!")
                self.player.takeDamage(1)
                self.player.incrementScore(self.SCORE_INCREMENT)

                if targetUnit in self._enemies: self._enemies.remove(targetUnit)
                self._updateUnitPosition(self.player, nextLocation)
            elif targetUnit and isinstance(targetUnit, Crate):
                self.addNotification("Player rammed a crate!")
                self.player.takeDamage(1)

                if targetUnit in self._crates: self._crates.remove(targetUnit)
                self._updateUnitPosition(self.player, nextLocation)
            elif targetUnit and isinstance(targetUnit, Pickup):
                self.handlePickupCollection(targetUnit)
        else:
            self._updateUnitPosition(self.player, nextLocation)

    def moveBullets(self) -> None:
        bulletsToRemove = []
        for bullet in self._bullets:
            if not bullet.shouldMove(): continue

            targetLocation = bullet.getNextLocation()
            if not self.isLocationValid(targetLocation):
                bulletsToRemove.append(bullet)
                continue

            if self.isBlocked(targetLocation):
                targetUnit = self._grid[targetLocation[1]][targetLocation[0]]

                if targetUnit and isinstance(targetUnit, Enemy):
                    bulletsToRemove.append(bullet)
                    targetUnit.takeDamage(1)
                    self.player.incrementScore(self.SCORE_INCREMENT)
                elif targetUnit and isinstance(targetUnit, Crate):
                    bulletsToRemove.append(bullet)
                    targetUnit.takeDamage(1)
                else:
                    bulletsToRemove.append(bullet)
            else:
                self._updateUnitPosition(bullet, targetLocation)

        for bullet in bulletsToRemove:
            self._bullets.remove(bullet)
            self._grid[bullet.location[1]][bullet.location[0]] = self.EMPTY_CELL_SYMBOL

    def moveCrates(self) -> None:
        cratesToRemove = []

        for crate in self._crates:
            if not crate.shouldMove(): continue

            targetLocation = crate.getNextLocation()
            if self.isLocationAtLowerBorder(targetLocation) or not self.isLocationValid(targetLocation):
                cratesToRemove.append(crate)
                continue
            if not crate.isAlive():
                pickup: Pickup = crate.spawnPickup()
                self._pickups.append(pickup)
                self._grid[pickup.location[1]][pickup.location[0]] = pickup
                cratesToRemove.append(crate)
                continue
            
            if self.isBlocked(targetLocation):
                targetUnit = self._grid[targetLocation[1]][targetLocation[0]]
                if isinstance(targetUnit, Player):
                    self.addNotification("Player was hit by a crate")
                    cratesToRemove.append(crate)
                    self.player.takeDamage(1)
                else:
                    cratesToRemove.append(crate)
            else:
                self._updateUnitPosition(crate, targetLocation)

        for crate in cratesToRemove:
            self._crates.remove(crate)
            self._grid[crate.location[1]][crate.location[0]] = self.EMPTY_CELL_SYMBOL

    def update(self) -> None:
        self._frameCounter += 1
        if self._frameCounter % self.SCORE_REWARD_FRAMES_INTERVAL == 0:
            self.player.incrementScore()

        if self.player.canFire():
            self.addNotification("Ready to fire", 0.6)
        else:
            self.addNotification("Reloading", 0.5)

        self.trySpawnCrate()
        self.trySpawnEnemies()
        self.moveBullets()
        self.moveEnemies()
        self.moveCrates()

    def spawnBullet(self) -> None:
        if not self.player.canFire(): return

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
        possibleOffsets = [-7, -5, -3, -1, 0, 1, 3, 5, 7]

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
    
    def tryActivatePickup(self, pickupIndex: int) -> None:
        if pickupIndex < 0 or pickupIndex >= len(self.player.inventory):
            self.addNotification("Invalid pickup index")
            return

        pickup = self.player.inventory[pickupIndex]
        match pickup.type:
            case PickupType.MEGABOMB:
                self.addNotification("Megabomb activated!")
                enemiesDestroyed = len(self._enemies)
                self.player.incrementScore(enemiesDestroyed * self.SCORE_INCREMENT)
                for enemy in self._enemies:
                    self._grid[enemy.location[1]][enemy.location[0]] = self.EMPTY_CELL_SYMBOL
                self._enemies.clear()
                self.player.inventory.remove(pickup)
            case _:
                self.addNotification(f"Cannot activate {pickup.type.value}")

    def getScore(self) -> Score:
        return Score(self.player.name, self.player.score, datetime.datetime.now().isoformat())

    def saveProgress(self, scoreRepository: ScoreRepository) -> None:
        scoreRepository.addScore(self.getScore())
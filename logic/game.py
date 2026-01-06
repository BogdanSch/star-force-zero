import datetime
import random
import time

from typing import TYPE_CHECKING, Final, Iterator
from helpers.grid import Grid
from helpers.location import Location
from repositories.scoreRepository import ScoreRepository
from data.score import Score
from units.unit import Unit
from units.enemy import Enemy
from units.bullet import Bullet
from units.pickups.crate import Crate
from units.pickups.pickup import Pickup
from data.enums.direction import Direction

if TYPE_CHECKING:
    from units.player import Player

class Game:
    EMPTY_CELL_SYMBOL: Final[str] = ' '

    ENEMY_SPAWN_INTERVAL_DECREMENT: Final[float] = 0.04
    MIN_ENEMY_SPAWN_INTERVAL: Final[float] = 0.5
    MAX_NUMBER_OF_ENEMIES_TO_SPAWN: Final[int] = 4

    SCORE_INCREMENT: Final[int] = 20
    EXTRA_SCORE_INCREMENT: Final[int] = 100
    SCORE_REWARD_FRAMES_INTERVAL: Final[int] = 30

    __slots__ = ["player", "gridSize", "_grid", "_enemies", "_bullets", "_crates", "_pickups", "_gameStatus", "_notifications", "startTime", "gameDurationInSeconds", "_enemySpawnInterval", "_lastEnemySpawnTime", "_frameCounter"]

    def __init__(self, player: "Player", gridSize: tuple[int, int], gameDurationInSeconds: int):
        self.player = player
        self.gridSize = gridSize

        self._grid: Grid = Grid(gridSize, self)
        # self.initializeGrid()

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

    @property
    def grid(self) -> Iterator[list]:
        return self._grid.grid

    @property
    def gameStatus(self) -> str:
        return self._gameStatus

    @property
    def notifications(self) -> list[str]:
        return [
            n["text"] 
            for n in self._notifications 
            if n["expiresAt"] > time.time()
        ]

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

    def addNotification(self, text: str, duration: float = 1.5) -> None:
        if any(n["text"] == text and n["expiresAt"] > time.time() for n in self._notifications):
            return
        self._notifications.append({
            "text": text,
            "expiresAt": time.time() + duration
        })

    def _updateUnitPosition(self, unit: Unit, nextLocation: Location) -> None:
        currentOccupant = self._grid.getOccupyingUnit(unit.location)
        if currentOccupant == unit:
            self._grid.setOccupyingUnit(unit.location, self.EMPTY_CELL_SYMBOL)
        unit.location = nextLocation
        self._grid.setOccupyingUnit(nextLocation, unit)
    
    def killUnit(self, unit: Unit, spawnPickup: bool = True) -> None:
        """
        Permanently removes a unit from the game.
        Handles list removal, grid clearing, and death effects (like Crate drops).
        """
        currentOccupant = self._grid.getOccupyingUnit(unit.location)
        if currentOccupant == unit:
            self._grid.setOccupyingUnit(unit.location, self.EMPTY_CELL_SYMBOL)

        if isinstance(unit, Enemy):
            if unit in self._enemies:
                self._enemies.remove(unit)
        elif isinstance(unit, Bullet):
            if unit in self._bullets:
                self._bullets.remove(unit)
        elif isinstance(unit, Pickup):
            if unit in self._pickups:
                self._pickups.remove(unit)
        elif isinstance(unit, Crate):
            if unit in self._crates:
                self._crates.remove(unit)
                pickup: Pickup = unit.spawnPickup()
                self._pickups.append(pickup)
                self._grid.setOccupyingUnit(pickup.location, pickup)
        
    def moveEnemies(self):
        enemiesToRemove = []
        for enemy in self._enemies:
            if not enemy.shouldMove():
                continue
            if not enemy.isAlive():
                enemiesToRemove.append(enemy)
                continue

            targetLocation = enemy.getNextLocation()
            if self._grid.isLocationAtLowerBorder(targetLocation):
                self.addNotification("Enemy reached the base", 3)
                enemiesToRemove.append(enemy)
                self.player.takeDamage(1)
                continue
            if not self._grid.isLocationValid(targetLocation):
                continue
            
            targetUnit = self._grid.getOccupyingUnit(targetLocation)
            if targetUnit and hasattr(targetUnit, "onHitByEnemy"):
                canMoveIn: bool = targetUnit.onHitByEnemy(enemy, self)
                if canMoveIn:
                    self._updateUnitPosition(enemy, targetLocation)
            else:
                self._updateUnitPosition(enemy, targetLocation)
            # if self._grid.isBlocked(targetLocation):
            #     targetUnit = self._grid.getOccupyingUnit(targetLocation)

            #     if targetUnit and isinstance(targetUnit, Player):
            #         self.addNotification("Player was hit by an enemy", 3)
            #         enemiesToRemove.append(enemy)
            #         self.player.takeDamage(1)
            #     elif self._grid.isLocationAtLowerBorder(targetLocation):
            #         self.addNotification("Enemy reached the base", 3)
            #         enemiesToRemove.append(enemy)
            #         self.player.takeDamage(1)
            #     elif targetUnit and isinstance(targetUnit, Bullet):
            #         enemy.takeDamage(1)
            #         self.player.incrementScore(self.SCORE_INCREMENT)
            #         self._bullets.remove(targetUnit)
            #         self._grid.setOccupyingUnit(targetLocation, self.EMPTY_CELL_SYMBOL)
            #     elif targetUnit and (isinstance(targetUnit, (Crate, Pickup, Enemy))):
            #         continue
            #     else:
            #         enemiesToRemove.append(enemy)
            # else:
            #     self._updateUnitPosition(enemy, targetLocation)

        for enemy in enemiesToRemove:
            if enemy in self._enemies:
                self._enemies.remove(enemy)
            self._grid.setOccupyingUnit(enemy.location, self.EMPTY_CELL_SYMBOL)

    def handlePickupCollection(self, pickup: Pickup) -> None:
        self._pickups.remove(pickup)
        if self.player.isInventoryFull():
            self.addNotification(f"Can't add {pickup.name}. The inventory is full.")
            return

        pickup.pick(self)
        self._updateUnitPosition(self.player, pickup.location)

    def movePlayer(self, direction: Direction) -> None:
        if self.isGameOver(): return

        nextLocation = self.player.getNextLocation(direction)
        if not self._grid.isLocationValid(nextLocation): return

        targetUnit: Unit | None = self._grid.getOccupyingUnit(nextLocation)

        if targetUnit and hasattr(targetUnit, 'onHitByPlayer'): 
            canMoveIn: bool = targetUnit.onHitByPlayer(self)
            if canMoveIn:
                self._updateUnitPosition(self.player, nextLocation)
        else:
            self._updateUnitPosition(self.player, nextLocation)

            # if targetUnit and isinstance(targetUnit, Enemy):
            #     self.addNotification("Player rammed an enemy!")
            #     self.player.takeDamage(1)
            #     self.player.incrementScore(self.SCORE_INCREMENT)
            #     self._enemies.remove(targetUnit)
            #     self._updateUnitPosition(self.player, nextLocation)
            # elif targetUnit and isinstance(targetUnit, Crate):
            #     self.addNotification("Player rammed a crate!")
            #     self.player.takeDamage(1)
            #     self._crates.remove(targetUnit)
            #     self._updateUnitPosition(self.player, nextLocation)
            # elif targetUnit and isinstance(targetUnit, Pickup):
            #     self.handlePickupCollection(targetUnit)
        # else:
        #     self._updateUnitPosition(self.player, nextLocation)

    def moveBullets(self) -> None:
        bulletsToRemove = []
        for bullet in self._bullets:
            if not bullet.shouldMove(): 
                continue

            targetLocation = bullet.getNextLocation()
            if not self._grid.isLocationValid(targetLocation):
                bulletsToRemove.append(bullet)
                continue
            
            targetUnit = self._grid.getOccupyingUnit(targetLocation)
            if targetUnit and hasattr(targetUnit, 'onHitByBullet'):
                canMoveIn: bool = targetUnit.onHitByBullet(bullet, self)
                if canMoveIn:
                    self._updateUnitPosition(bullet, targetLocation)
                else:
                    bulletsToRemove.append(bullet)
            else:
                self._updateUnitPosition(bullet, targetLocation)
                
            # if self._grid.isBlocked(targetLocation):

            #     if targetUnit and isinstance(targetUnit, Enemy):
            #         bulletsToRemove.append(bullet)
            #         targetUnit.takeDamage(1)
            #         self.player.incrementScore(self.SCORE_INCREMENT)
            #     elif targetUnit and isinstance(targetUnit, Crate):
            #         bulletsToRemove.append(bullet)
            #         targetUnit.takeDamage(1)
            #     else:
            #         bulletsToRemove.append(bullet)
            # else:
            #     self._updateUnitPosition(bullet, targetLocation)

        for bullet in bulletsToRemove:
            if bullet in self._bullets:
                self._bullets.remove(bullet)
            self._grid.setOccupyingUnit(bullet.location, self.EMPTY_CELL_SYMBOL)

    def moveCrates(self) -> None:
        cratesToRemove = []

        for crate in self._crates:
            if not crate.shouldMove(): continue
            if not crate.isAlive():
                pickup: Pickup = crate.spawnPickup()
                self._pickups.append(pickup)
                self._grid.setOccupyingUnit(pickup.location, pickup)
                cratesToRemove.append(crate)
                crate.remove()
                continue

            targetLocation = crate.getNextLocation()
            if self._grid.isLocationAtLowerBorder(targetLocation) or not self._grid.isLocationValid(targetLocation):
                cratesToRemove.append(crate)
                continue

            targetUnit = self._grid.getOccupyingUnit(targetLocation)
            if targetUnit and hasattr(targetUnit, "onHitByCrate"):
                canMoveIn: bool = targetUnit.onHitByCrate(crate, self)
                if canMoveIn:
                    self._updateUnitPosition(crate, targetLocation)
            else:
                self._updateUnitPosition(crate, targetLocation)
            # if self._grid.isBlocked(targetLocation):
            #     targetUnit = self._grid.getOccupyingUnit(targetLocation)
            #     if isinstance(targetUnit, Player):
            #         self.addNotification("Player was hit by a crate")
            #         cratesToRemove.append(crate)
            #         self.player.takeDamage(1)
            #     elif isinstance(targetUnit, Bullet):
            #         crate.takeDamage(1)
            #         self._bullets.remove(targetUnit)
            #         self._grid.setOccupyingUnit(targetLocation, self.EMPTY_CELL_SYMBOL)
            #     else:
            #         cratesToRemove.append(crate)
            # else:
            #     self._updateUnitPosition(crate, targetLocation)

        for crate in cratesToRemove:
            if crate in self._crates:
                self._crates.remove(crate)
            if not crate.isRemoved:
                self._grid.setOccupyingUnit(crate.location, self.EMPTY_CELL_SYMBOL)

    def update(self) -> None:
        self._frameCounter += 1
        if self._frameCounter % self.SCORE_REWARD_FRAMES_INTERVAL == 0:
            self.player.incrementScore()

        if self.player.canFire():
            self.addNotification("Ready to fire", 1)
        else:
            self.addNotification("Reloading", 0.4)

        self.trySpawnCrate()
        self.trySpawnEnemies()
        self.moveBullets()
        self.moveEnemies()
        self.moveCrates()

    def spawnBullet(self) -> None:
        if not self.player.canFire(): return

        bulletLocation = self.player.getNextLocation(Direction.UP)
        if not self._grid.isLocationValid(bulletLocation) or self._grid.isBlocked(bulletLocation):
            self.addNotification("Cannot fire: Path blocked", 2)
            return

        self.player.fire()
        bullet = Bullet(bulletLocation)
        self._bullets.append(bullet)
        self._grid.setOccupyingUnit(bulletLocation, bullet)

    def trySpawnEnemies(self) -> None:
        if time.time() - self._lastEnemySpawnTime < self._enemySpawnInterval: return

        self._lastEnemySpawnTime = time.time()
        if self._enemySpawnInterval > self.MIN_ENEMY_SPAWN_INTERVAL:
            self._enemySpawnInterval -= self.ENEMY_SPAWN_INTERVAL_DECREMENT

        anchorX = random.randint(1, self.gridSize[0] - 2)
        count = random.randint(1, self.MAX_NUMBER_OF_ENEMIES_TO_SPAWN)
        possibleOffsets = [-7, -5, -3, -1, 0, 1, 3, 5, 7]

        locations: list[Location] = []
        for offset in possibleOffsets:
            x: int = anchorX + offset
            currentLocation = Location(x, 1)

            if self._grid.isLocationValid(currentLocation) and not self._grid.isBlocked(currentLocation):
                locations.append(currentLocation)
            if len(locations) == count: break

        for location in locations:
            enemy = Enemy(location, 4)
            self._enemies.append(enemy)
            self._grid.setOccupyingUnit(location, enemy)

    def trySpawnCrate(self):
        if random.random() > 0.0025: return

        x = random.randint(1, self.gridSize[0] - 2)
        targetLocation = Location(x, 1)

        if not self._grid.isLocationValid(targetLocation) or self._grid.isBlocked(targetLocation): return

        crate = Crate(targetLocation)
        self._crates.append(crate)
        self._grid.setOccupyingUnit(targetLocation, crate)

    def tryActivatePickup(self, pickupIndex: int) -> None:
        try:
            pickup = self.player.getItemByIndex(pickupIndex)
        except IndexError as e:
            self.addNotification(str(e))
            return

        pickup.activate(self)

    def getScore(self) -> Score:
        return Score(self.player.name, self.player.score, datetime.datetime.now().isoformat())

    def saveProgress(self, scoreRepository: ScoreRepository) -> None:
        scoreRepository.addScore(self.getScore())
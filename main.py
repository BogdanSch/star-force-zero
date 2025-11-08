# import keyboard
import pyfiglet
import time
import pygame

from typing import Iterator, Final
from units.player import Player
from units.enemy import Enemy
from units.bullet import Bullet
from units.wall import Wall
from logic.game import Game
from enums.direction import Direction
from rich.console import Console

FRAME_RATE: Final[int] = 30
GAME_DURATION_IN_SECONDS: Final[int] = 240
CELL_SIZE: int = 24

def parseUserInput(event: pygame.Event) -> Direction | None:
    if event.key == pygame.K_UP or event.key == pygame.K_w:
        return Direction.UP
    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
        return Direction.DOWN
    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
        return Direction.LEFT
    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
        return Direction.RIGHT
    return None

def displayGameStats(game: Game) -> None:
    pass
    # console.print(f"State: {game.gameState}", style="orange1", justify="center")
    # console.print(f"Time left: {game.getTimeLeft()}", style="medium_violet_red", justify="center")
    # console.print(f"Score: {game.player.score}\t\tHealth: {game.player.health}", style="blue", justify="center")

def displayGrid(screen: pygame.Surface, grid: Iterator[list]) -> None:
    matrix = list(grid)

    for y in range(len(matrix)):
        for x in range(len(matrix[y])):
            cell = matrix[y][x]
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if isinstance(cell, Player):
                pygame.draw.rect(screen, (0, 255, 0), rect)
            elif isinstance(cell, Enemy):
                pygame.draw.rect(screen, (255, 0, 0), rect)
            elif isinstance(cell, Bullet):
                pygame.draw.rect(screen, (255, 255, 0), rect)
            elif isinstance(cell, Wall):
                pygame.draw.rect(screen, (100, 100, 100), rect)

def displayWelcomeMessage() -> None:
    pass
    # console.print(pyfiglet.figlet_format("Star Force Zero", font = "isometric1" ))
    # console.print("Welcome to Star Force Zero! Use W/A/S/D or Arrow keys to move. Press 'Esc' to exit the game.")

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    player = Player("Starkiller", (10, 20))
    game = Game(player, (20, 24), GAME_DURATION_IN_SECONDS)

    displayWelcomeMessage()
    displayGrid(screen, game.grid)

    running: bool = True
    while running and not game.isGameOver():
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.KEYDOWN:
                direction = parseUserInput(event)
                if direction:
                    game.movePlayer(direction)
                if event.key == pygame.K_SPACE:
                    game.spawnBullet()

        game.update()

        displayGameStats(game)
        displayGrid(screen, game.grid)

        pygame.display.flip()
        clock.tick(FRAME_RATE)

    pygame.quit()

if __name__ == "__main__":
    main()
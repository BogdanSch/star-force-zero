import time
import pygame

from typing import Iterator, Final
from config import DB_PATH
from repositories.scoreRepository import ScoreRepository
from units.player import Player
from units.enemy import Enemy
from units.bullet import Bullet
from units.wall import Wall
from logic.game import Game
from enums.direction import Direction
from helpers.timeHelper import formatTimeInSeconds

FRAME_RATE: Final[int] = 30
GAME_DURATION_IN_SECONDS: Final[int] = 180
CELL_SIZE: Final[int] = 24
IMAGE_SCALE_COEFFICIENT: Final[float] = 1.5

SCREEN_WIDTH: Final[int] = 860
SCREEN_HEIGHT: Final[int] = 620

DARK_COLOR: Final[tuple[int, int, int]] = (20, 20, 20)
LIGHT_COLOR: Final[tuple[int, int, int]] = (200, 200, 200)

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

def displayMainMenu(screen: pygame.Surface, titleFont: pygame.font.Font, paragraphFont: pygame.font.Font) -> None:
# def displayWelcomeMessage(screen: pygame.Surface) -> None:
    text = titleFont.render("Star Force Zero", True, LIGHT_COLOR)
    text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, 8))
    screen.blit(text, text_rect)

    text = paragraphFont.render("Welcome to Star Force Zero! Use W/A/S/D or Arrow keys to move. Press Close to exit the game.", True, LIGHT_COLOR)
    text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, 40))
    screen.blit(text, text_rect)

def displayGameStats(screen: pygame.Surface, game: Game, paragraphFont: pygame.font.Font) -> None:
    PADDING_X = 20
    START_Y = 60
    LINE_SPACING = 30

    stats = [
        f"State: {game.gameState}",
        f"Time left: {formatTimeInSeconds(game.getTimeLeft())}",
        f"Score: {game.player.score}\tHealth: {game.player.health}"
    ]

    for i, line in enumerate(stats):
        text = paragraphFont.render(line, True, LIGHT_COLOR)
        text_rect = text.get_rect()
        text_rect.topright = (SCREEN_WIDTH - PADDING_X, START_Y + i * LINE_SPACING)
        screen.blit(text, text_rect)

def displayGrid(screen: pygame.Surface, grid: Iterator[list], playerImage: pygame.Surface, enemyImage: pygame.Surface) -> None:
    matrix = list(grid)
    for y in range(len(matrix)):
        for x in range(len(matrix[y])):
            cell = matrix[y][x]
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if isinstance(cell, Player):
                screen.blit(playerImage, rect)
            elif isinstance(cell, Enemy):
                screen.blit(enemyImage, rect)
            elif isinstance(cell, Bullet):
                pygame.draw.rect(screen, (255, 255, 0), rect)
            elif isinstance(cell, Wall):
                pygame.draw.rect(screen, (100, 100, 100), rect)

def createImage(path: str):
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(image, (CELL_SIZE * IMAGE_SCALE_COEFFICIENT, CELL_SIZE * IMAGE_SCALE_COEFFICIENT))

def main() -> None:
    scoreRepository = ScoreRepository(DB_PATH)
    pygame.init()
    pygame.font.init()

    titleFont = pygame.font.Font(None, 40)
    paragraphFont = pygame.font.Font(None, 20)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Sky Force Zero")
    clock = pygame.time.Clock()

    player = Player("Starkiller", (10, 20))
    game = Game(player, (26, 26), GAME_DURATION_IN_SECONDS)

    playerImage = createImage("./assets/player-ship.png")
    enemyImage = createImage("./assets/enemy-ship.png")

    displayMainMenu(screen, titleFont, paragraphFont)
    displayGrid(screen, game.grid, playerImage, enemyImage)

    running: bool = True
    while running and not game.isGameOver():
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.KEYDOWN:
                direction = parseUserInput(event)
                if direction: game.movePlayer(direction)
                if event.key == pygame.K_SPACE: game.spawnBullet()

        game.update()

        displayGameStats(screen, game, paragraphFont)
        displayGrid(screen, game.grid, playerImage, enemyImage)

        pygame.display.flip()
        clock.tick(FRAME_RATE)

    game.saveProgress(scoreRepository)
    pygame.quit()

if __name__ == "__main__":
    main()
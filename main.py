import sys
import pygame

from typing import Iterator, Final
from config import DB_PATH
from helpers.button import Button
from repositories.scoreRepository import ScoreRepository
from data.score import Score
from units.player import Player
from units.enemy import Enemy
from units.bullet import Bullet
from units.wall import Wall
from logic.game import Game
from enums.direction import Direction
from helpers.timeHelper import formatTimeInSeconds

FRAME_RATE: Final[int] = 30
GAME_DURATION_IN_SECONDS: Final[int] = 180
CELL_SIZE: Final[int] = 28

SCREEN_WIDTH: Final[int] = 1060
SCREEN_HEIGHT: Final[int] = 760

DARK_COLOR: Final[tuple[int, int, int]] = (20, 20, 20)
GREY_COLOR: Final[tuple[int, int, int]] = (20, 50, 40)
LIGHT_COLOR: Final[tuple[int, int, int]] = (200, 200, 200)

def parseUserInput(event: pygame.event.Event) -> Direction | None:
    if event.key == pygame.K_UP or event.key == pygame.K_w:
        return Direction.UP
    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
        return Direction.DOWN
    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
        return Direction.LEFT
    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
        return Direction.RIGHT
    return None

def displayMainMenu(screen: pygame.Surface, buttonPlaceholderImage: pygame.Surface, titleFont: pygame.font.Font, paragraphFont: pygame.font.Font) -> None:
    pygame.display.set_caption("Star Force Zero - Main Menu")

    running: bool = True
    while running:
        screen.fill(DARK_COLOR)
        playerMousePosition = pygame.mouse.get_pos()

        title = titleFont.render("Star Force Zero", True, LIGHT_COLOR)
        titleRect = title.get_rect(center=(SCREEN_WIDTH / 2, 120))
        screen.blit(title, titleRect)

        text = paragraphFont.render("Welcome to Star Force Zero! Use W/A/S/D or Arrow keys to move. Press Close to exit the game.", True, LIGHT_COLOR)
        textRect = text.get_rect(center=(SCREEN_WIDTH / 2, 200))
        screen.blit(text, textRect)

        playButton = Button(image=buttonPlaceholderImage, position=(SCREEN_WIDTH // 2, 260), 
                            textValue="Play", font=paragraphFont, baseColor=DARK_COLOR, hoveringColor=GREY_COLOR)
        playButton.changeColor(playerMousePosition)
        playButton.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if playButton.checkForInput(playerMousePosition):
                    running = False
        pygame.display.update()

def displayGameOverModal(screen: pygame.Surface, game: Game, scoreRepository: ScoreRepository, buttonPlaceholderImage: pygame.Surface, titleFont: pygame.font.Font, paragraphFont: pygame.font.Font) -> bool:
    pygame.display.set_caption("Star Force Zero - Game Over")

    running: bool = True
    userText: str = ""

    score = game.getScore()

    while running:
        screen.fill(DARK_COLOR)
        playerMousePosition = pygame.mouse.get_pos()

        title = titleFont.render("Game Over", True, LIGHT_COLOR)
        titleRect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        screen.blit(title, titleRect)

        text = paragraphFont.render(f"Your score: {score.score} points", True, LIGHT_COLOR)
        textRect = text.get_rect(center=(SCREEN_WIDTH // 2, 160))
        screen.blit(text, textRect)

        text = paragraphFont.render("Enter your name to save the results", True, LIGHT_COLOR)
        textRect = text.get_rect(center=(SCREEN_WIDTH // 2, 240))
        screen.blit(text, textRect)

        inputSurface = paragraphFont.render(userText, True, LIGHT_COLOR)
        inputSurfaceRect = text.get_rect(center=(SCREEN_WIDTH // 2, 280))
        screen.blit(inputSurface, inputSurfaceRect)

        saveResultButton = Button(image=buttonPlaceholderImage, position=(SCREEN_WIDTH // 2 + 200, 280),
            textValue="Save", font=paragraphFont, baseColor=DARK_COLOR,
            hoveringColor=GREY_COLOR)
        saveResultButton.changeColor(playerMousePosition)
        saveResultButton.update(screen)

        text = paragraphFont.render("Would you like to try again?", True, LIGHT_COLOR)
        textRect = text.get_rect(center=(SCREEN_WIDTH // 2, 360))
        screen.blit(text, textRect)

        playAgainButton = Button(image=buttonPlaceholderImage, position=(SCREEN_WIDTH // 2, 400),
            textValue="Play Again", font=paragraphFont, baseColor=DARK_COLOR, hoveringColor=GREY_COLOR)
        playAgainButton.changeColor(playerMousePosition)
        playAgainButton.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    userText = userText[:-1]
                else:
                    userText += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if playAgainButton.checkForInput(playerMousePosition):
                    running = False
                    return True
                elif saveResultButton.checkForInput(playerMousePosition):
                    saveResultButton.isEnabled = False
                    game.player.name = userText
                    game.saveProgress(scoreRepository)

        pygame.display.update()

    return False

def displayGame(game, screen, playerImage, enemyImage, paragraphFont):
    pygame.display.set_caption("Sky Force Zero - Game")

    displayGrid(screen, game.grid, playerImage, enemyImage)
    running: bool = True
    clock = pygame.time.Clock()

    while running and not game.isGameOver():
        screen.fill(DARK_COLOR)

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

def displayGameStats(screen: pygame.Surface, game: Game, paragraphFont: pygame.font.Font) -> None:
    PADDING_X: Final[int] = 20
    START_Y: Final[int] = 60
    LINE_SPACING: Final[int] = 30

    stats = [
        f"{game.gameState}",
        f"Time left: {formatTimeInSeconds(game.getTimeLeft())}",
        f"Score: {game.player.score}",
        f"Health: {game.player.health}",
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

def createImage(path: str, size: tuple[int, int] = (CELL_SIZE, CELL_SIZE)) -> pygame.Surface:
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(image, size)

def createFont(size: int) -> pygame.font.Font:
    return  pygame.font.Font(None, size)

def main() -> None:
    scoreRepository = ScoreRepository(DB_PATH)
    pygame.init()
    pygame.font.init()

    titleFont = createFont(60)
    paragraphFont = createFont(28)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    buttonPlaceholderImage = createImage("./assets/button-placeholder.png", (280, 160))
    playerImage = createImage("./assets/player-ship.png")
    enemyImage = createImage("./assets/enemy-ship.png")

    displayMainMenu(screen, buttonPlaceholderImage, titleFont, paragraphFont)

    player = Player("", (10, 20))
    game = Game(player, (26, 26), GAME_DURATION_IN_SECONDS)

    while True:
        # displayGame(game, screen, playerImage, enemyImage, paragraphFont)
        isGameContinued = displayGameOverModal(screen, game, scoreRepository, buttonPlaceholderImage, titleFont, paragraphFont)

        if not isGameContinued: break

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
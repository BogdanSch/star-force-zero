import sys
import pygame
import os

from typing import Iterator, Final
from config import DB_PATH
from helpers.button import Button
from helpers.textInput import TextInput
from repositories.scoreRepository import ScoreRepository
from data.score import Score
from units.player import Player
from units.enemy import Enemy
from units.bullet import Bullet
from units.wall import Wall
from logic.game import Game
from data.enums.direction import Direction
from helpers.timeHelper import formatTimeInSeconds

USERNAME_FILE_PATH: Final[str] = "username.txt"

FRAME_RATE: Final[int] = 30
GAME_DURATION_IN_SECONDS: Final[int] = 180
CELL_SIZE: Final[int] = 28
TOP_SCORES_COUNT: Final[int] = 6

SCREEN_WIDTH: Final[int] = 1060
SCREEN_HEIGHT: Final[int] = 760

DARK_COLOR: Final[tuple[int, int, int]] = (20, 20, 20)
GREY_COLOR: Final[tuple[int, int, int]] = (20, 50, 40)
LIGHT_COLOR: Final[tuple[int, int, int]] = (200, 200, 200)
RED_COLOR: Final[tuple[int, int, int]] = (251, 1, 2)

def displayMainMenuScreen(screen: pygame.Surface, buttonPlaceholderImage: pygame.Surface, titleFont: pygame.font.Font, paragraphFont: pygame.font.Font) -> None:
    pygame.display.set_caption("Star Force Zero - Main Menu")

    running: bool = True
    while running:
        screen.fill(DARK_COLOR)
        playerMousePosition = pygame.mouse.get_pos()

        title = titleFont.render("Star Force Zero", True, LIGHT_COLOR)
        titleRect = title.get_rect(center=(SCREEN_WIDTH / 2, 160))
        screen.blit(title, titleRect)

        text = paragraphFont.render("Welcome to Star Force Zero! Use W/A/S/D or Arrow keys to move. Press Close to exit the game.", True, LIGHT_COLOR)
        textRect = text.get_rect(center=(SCREEN_WIDTH / 2, 240))
        screen.blit(text, textRect)

        playButton = Button(image=buttonPlaceholderImage, position=(SCREEN_WIDTH // 2, 320), 
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

def displayGameOverModal(screen: pygame.Surface, game: Game, scoreRepository: ScoreRepository, buttonPlaceholderImage: pygame.Surface, inputPlaceholderImage: pygame.Surface, titleFont: pygame.font.Font, paragraphFont: pygame.font.Font) -> bool:
    pygame.display.set_caption("Star Force Zero - Game Over")

    running: bool = True
    userText: str = getUsername()
    userTextError: str = ""
    saveButtonText: str = "Save"

    score = game.getScore()

    while running:
        screen.fill(DARK_COLOR)
        playerMousePosition = pygame.mouse.get_pos()

        title = titleFont.render("Game Over", True, LIGHT_COLOR)
        titleRect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title, titleRect)

        text = paragraphFont.render(f"Your score: {score.score} points", True, LIGHT_COLOR)
        textRect = text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        screen.blit(text, textRect)

        text = paragraphFont.render("Enter your name to save the results", True, LIGHT_COLOR)
        textRect = text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(text, textRect)

        usernameInput = TextInput((SCREEN_WIDTH // 2 - 120, 260), userText, "Enter your username", paragraphFont, DARK_COLOR, inputPlaceholderImage)
        usernameInput.update(screen)
        if userTextError:
            errorText = paragraphFont.render(userTextError, True, RED_COLOR)
            errorTextRect = errorText.get_rect(center=(SCREEN_WIDTH // 2 - 120, 300))
            screen.blit(errorText, errorTextRect)
        saveResultButton = Button(image=buttonPlaceholderImage, position=(SCREEN_WIDTH // 2 + 148, 260),
            textValue=saveButtonText, font=paragraphFont, baseColor=DARK_COLOR,
            hoveringColor=GREY_COLOR)
        saveResultButton.changeColor(playerMousePosition)
        saveResultButton.update(screen)

        text = paragraphFont.render("Would you like to try again?", True, LIGHT_COLOR)
        textRect = text.get_rect(center=(SCREEN_WIDTH // 2, 360))
        screen.blit(text, textRect)

        playAgainButton = Button(image=buttonPlaceholderImage, position=(SCREEN_WIDTH // 2, 408),
            textValue="Play Again", font=paragraphFont, baseColor=DARK_COLOR, hoveringColor=GREY_COLOR)
        playAgainButton.changeColor(playerMousePosition)
        playAgainButton.update(screen)

        displayTopScoresTable(scoreRepository.getTop(TOP_SCORES_COUNT), screen, paragraphFont, (SCREEN_WIDTH // 2, 480))

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
                    if usernameInput.isEmpty(): 
                        userTextError = "Username cannot be empty!"
                        continue
                    saveResultButton.isEnabled = False

                    saveButtonText = "Saving..."
                    userTextError = ""
                    saveUsername(userText)

                    game.player.name = userText
                    game.saveProgress(scoreRepository)
                    saveButtonText = "Saved"

        pygame.display.update()

    return False

def displayGameScreen(game, screen, playerImage, enemyImage, paragraphFont):
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

def displayTopScoresTable(topScores: list[Score], screen: pygame.Surface, paragraphFont: pygame.font.Font, position: tuple[int, int]) -> None:
    header = paragraphFont.render("Top 10 Scores", True, LIGHT_COLOR)
    headerRect = header.get_rect(center=(position[0], position[1]))
    screen.blit(header, headerRect)

    startY = position[1] + 28
    rowHeight = 28

    nameText = paragraphFont.render("Name", True, LIGHT_COLOR)
    scoreText = paragraphFont.render("Score", True, LIGHT_COLOR)

    screen.blit(nameText, (SCREEN_WIDTH // 2 - 200, startY))
    screen.blit(scoreText, (SCREEN_WIDTH // 2 + 100, startY))

    pygame.draw.line(screen, LIGHT_COLOR, (SCREEN_WIDTH // 2 - 240, startY + 25),
                     (SCREEN_WIDTH // 2 + 240, startY + 25), 2)

    for i, score in enumerate(topScores):
        y = startY + 35 + i * rowHeight

        name_surface = paragraphFont.render(score.playerName, True, LIGHT_COLOR)
        score_surface = paragraphFont.render(str(score.score), True, LIGHT_COLOR)

        screen.blit(name_surface, (SCREEN_WIDTH // 2 - 200, y))
        screen.blit(score_surface, (SCREEN_WIDTH // 2 + 100, y))

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

def saveUsername(name: str) -> None:
    with open(USERNAME_FILE_PATH, 'w') as f:
        f.write(name)
def getUsername() -> str:
    if not os.path.exists(USERNAME_FILE_PATH): return ""
    if os.path.getsize(USERNAME_FILE_PATH) == 0: return ""
    with open(USERNAME_FILE_PATH, 'r') as f:
        return f.readline().strip()

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
    inputPlaceholderImage = createImage("./assets/input-placeholder.png", (320, 180))
    playerImage = createImage("./assets/player-ship.png")
    enemyImage = createImage("./assets/enemy-ship.png")

    displayMainMenuScreen(screen, buttonPlaceholderImage, titleFont, paragraphFont)

    player = Player("", (10, 20))
    game = Game(player, (26, 26), GAME_DURATION_IN_SECONDS)

    while True:
        displayGameScreen(game, screen, playerImage, enemyImage, paragraphFont)
        isGameContinued = displayGameOverModal(screen, game, scoreRepository, buttonPlaceholderImage, inputPlaceholderImage, titleFont, paragraphFont)

        if not isGameContinued: break

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
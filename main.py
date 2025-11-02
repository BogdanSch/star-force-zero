import keyboard
import pyfiglet
import time

from units.player import Player
from logic.game import Game
from enums.direction import Direction
from rich.console import Console

TIMER_INTERVAL: float = 0.1
GAME_DURATION_IN_SECONDS: int = 240

def parseUserInput() -> Direction | None:
    if keyboard.is_pressed('w') or keyboard.is_pressed('up'):
        return Direction.UP
    elif keyboard.is_pressed('s') or keyboard.is_pressed('down'):
        return Direction.DOWN
    elif keyboard.is_pressed('a') or keyboard.is_pressed('left'):
        return Direction.LEFT
    elif keyboard.is_pressed('d') or keyboard.is_pressed('right'):
        return Direction.RIGHT
    return None
def displayGameStats(console: Console, game: Game) -> None:
    console.print(f"State: {game.gameState}")
    console.print(f"Time left: {game.getTimeLeft()}")
    console.print(f"Score: {game.score}\t\tHealth: {game.player.health}")

def displayGrid(console: Console, grid: list) -> None:
    for row in grid:
        console.print(''.join(f"{str(cell)}" for cell in row))

def displayWelcomeMessage(console: Console) -> None:
    console.print(pyfiglet.figlet_format("Star Force Zero", font = "isometric1" ))
    console.print("Welcome to Star Force Zero! Use W/A/S/D or Arrow keys to move. Press 'Esc' to exit the game.")

def main() -> None:
    console = Console()

    player = Player("Starkiller", (10, 20))
    game = Game(player, (20, 24), GAME_DURATION_IN_SECONDS)

    displayWelcomeMessage(console)
    input("Press any key to start...")

    console.print(game.gameState)
    displayGrid(console, game.grid)

    while not game.isGameOver() and not keyboard.is_pressed('esc'):
        direction = parseUserInput()

        if direction:
            game.movePlayer(direction)
        if keyboard.is_pressed('space'):
            game.spawnBullet()
            console.print(game._Game__bullets)

        game.update()
        console.clear()

        console.print(game.gameState)
        displayGrid(console, game.grid)
        time.sleep(TIMER_INTERVAL)

if __name__ == "__main__":
    main()
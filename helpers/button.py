import pygame
from colors import GREY_COLOR


class Button:
    def __init__(
        self,
        position: tuple[int, int],
        textValue: str,
        font: pygame.font.Font,
        /,
        baseColor,
        hoveringColor,
        *,
        image: pygame.Surface | None = None
    ):
        self.image = image
        self.position = position
        self.font = font
        self.baseColor = baseColor
        self.hoveringColor = hoveringColor
        self.textValue = textValue

        self.text = self.font.render(self.textValue, True, self.baseColor)

        if self.image is None:
            self.image = self.text

        self.rect = self.image.get_rect(center=self.position)
        self.textRect = self.text.get_rect(center=self.position)
        self._isEnabled = True

    def update(self, screen: pygame.Surface) -> None:
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.textRect)

    def checkForInput(self, position: tuple[int, int]) -> bool:
        if not self._isEnabled:
            return False

        return (
            self.rect.left <= position[0] <= self.rect.right
            and self.rect.top <= position[1] <= self.rect.bottom
        )

    def changeColor(self, position: tuple[int, int]) -> None:
        if not self._isEnabled:
            self.text = self.font.render(self.textValue, True, GREY_COLOR)
            return

        if (
            self.rect.left <= position[0] <= self.rect.right
            and self.rect.top <= position[1] <= self.rect.bottom
        ):
            self.text = self.font.render(self.textValue, True, self.hoveringColor)
        else:
            self.text = self.font.render(self.textValue, True, self.baseColor)

    @property
    def isEnabled(self) -> bool:
        return self._isEnabled

    @isEnabled.setter
    def isEnabled(self, isEnabled: bool) -> None:
        self._isEnabled = bool(isEnabled)
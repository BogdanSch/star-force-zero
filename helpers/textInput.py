import pygame

class TextInput():
	def __init__(self, position: tuple[int, int], value: str, placeholder: str, font: pygame.font.Font, baseColor: tuple[int, int, int], image: pygame.Surface | None = None):
		self.image = image
		self.position = position
		self.font = font
		self.value = value
		self.placeholder = placeholder
		self.baseColor = baseColor

		self.label = self.font.render(self.value if self.value else self.placeholder, True, self.baseColor)
		if self.image is None:
			self.image = self.label

		self.rect = self.image.get_rect(center=(self.position[0], self.position[1]))
		self.labelRect = self.label.get_rect(center=(self.position[0], self.position[1]))
		self._isEnabled = True

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.label, self.labelRect)

	def inputValue(self, key: int, character: str):
		if not self._isEnabled: return
		if key == pygame.K_BACKSPACE:
			self.value = self.value[:-1]
		else:
			self.value += character

		display_text = self.value if self.value else self.placeholder
		self.label = self.font.render(display_text, True, self.baseColor)
		self.labelRect = self.label.get_rect(center=(self.position[0], self.position[1]))
	
	def isEmpty(self) -> bool:
		return len(self.value.strip()) == 0

	@property
	def isEnabled(self) -> bool:
		return self._isEnabled

	@isEnabled.setter
	def isEnabled(self, isEnabled: bool):
		self._isEnabled = bool(isEnabled)


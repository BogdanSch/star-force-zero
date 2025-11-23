import pygame

class Button():
	def __init__(self, position: tuple[int, int], textValue: str, font: pygame.font.Font, baseColor, hoveringColor, image: pygame.Surface | None = None ):
		self.image = image
		self.position = position
		self.font = font
		self.baseColor, self.hoveringColor = baseColor, hoveringColor
		self.textValue = textValue
		self.text = self.font.render(self.textValue, True, self.baseColor)
		
		if self.image is None: self.image = self.text
			
		self.rect = self.image.get_rect(center=(self.position[0], self.position[1]))
		self.textRect = self.text.get_rect(center=(self.position[0], self.position[1]))
		self._isEnabled = True

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.textRect)

	def checkForInput(self, position):
		if not self._isEnabled: return False
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.textValue, True, self.hoveringColor)
		else:
			self.text = self.font.render(self.textValue, True, self.baseColor)
	
	@property
	def isEnabled(self) -> bool: return self._isEnabled
	@isEnabled.setter
	def isEnabled(self, isEnabled: bool):
		self._isEnabled = bool(isEnabled)


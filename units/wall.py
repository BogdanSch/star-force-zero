from units.unit import Unit

class Wall(Unit):
    WALL_SYMBOL: str = '■'
    WALL_NAME: str = "Wall"

    def __init__(self, location: tuple = (0, 0)):
        super().__init__(self.WALL_NAME, self.WALL_SYMBOL, location, 0)
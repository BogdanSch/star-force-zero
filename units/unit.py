class Unit:
    def __init__(self, name: str, symbol: str, location: tuple = (0, 0)):
        self.name = name
        self.symbol = symbol
        self.location = location

    def __str__(self):
        return f"{self.symbol}"
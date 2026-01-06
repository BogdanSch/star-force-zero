class Location:
    __slots__ = ["x", "y"]
    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y
    def _isValidOperand(self, other: object) -> bool:
        return (hasattr(other, "x") and
                hasattr(other, "y"))
    def __eq__(self, other):
        if not self._isValidOperand(other):
            return NotImplemented
        return ((self.x, self.y) == (other.x, other.y))
from data.enums.pickupType import PickupType
from units.unit import Unit

class Pickup(Unit):
    def __init__(self, pickupType: PickupType, pickupSymbol: str, location: tuple[int, int]) -> None:
        super().__init__(pickupType.value, pickupSymbol, location, 0)
        self.type = pickupType
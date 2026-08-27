# Character should not need to know which system supplied a modifier. This Protocol lets
# regions, equipment, or future systems provide the needed attribute without inheritance.


from typing import Protocol 

# Define the interface for anything that can modify a character's movement speed.
class SpeedModifier(Protocol):
    percent_change: float

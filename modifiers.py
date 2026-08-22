from typing import Protocol 

# Define the interface for anything that can modify a character's movement speed.
class SpeedModifier(Protocol):
    percent_change: float
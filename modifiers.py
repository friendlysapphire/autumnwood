# Player doesn't need to know about RegionEffects classes or other ways it can be asked to modify itself,
# try to keep Player's input params for modifiers (eg speed) based on protocols


from typing import Protocol 

# Define the interface for anything that can modify a character's movement speed.
class SpeedModifier(Protocol):
    percent_change: float
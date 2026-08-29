from enum import StrEnum


# Define the animation states shared by characters and sprite configurations.
class AnimationState(StrEnum):
    IDLE = "idle"
    WALKING = "walking"
    TALKING = "talking"
    ATTACK_PREP = "attack_prep"
    ATTACK = "attack"
    DYING = "dying"
    DEAD = "dead"

from dataclasses import dataclass
from enum import StrEnum


# Identify exact NPCs through the name field authored in Tiled.
class ExactNPC(StrEnum):
    TRAVELING_VENDOR_01 = "traveling_vendor_01"

@dataclass(frozen=True)
# Describe the static ordered statements for one conversation. DialogPanel owns
# the runtime state that selects which statement is currently displayed.
class DialogueScript:
    id: str
    statements: tuple[str, ...]


# the scripts

tv_01_statements: tuple[str, ...] = (
    "Welcome to my Shop!",
    "Statement 2"
)

tv_01 = DialogueScript(id=ExactNPC.TRAVELING_VENDOR_01,
                       statements=tv_01_statements)


# Exact-NPC entries are custom dialogue overrides. NPCType-based default dialogue
# will later be used as a fallback when an NPC has no entry in this registry.
# TODO: when switch to python 3.15, make this a frozendict
DIALOGUE_SCRIPTS: dict[ExactNPC: DialogueScript] = {
    ExactNPC.TRAVELING_VENDOR_01: tv_01
}

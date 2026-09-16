from dataclasses import dataclass
from enum import StrEnum

from characters.npc_type import NPCType


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

# CUSTOM SCRIPTS BY CHARACTER INTERNAL NAME
tv_01_statements: tuple[str, ...] = (
    "Welcome to my Shop!! Welcome to my Shop!! Welcome to my Shop!! Welcome to my Shop!! Welcome to my Shop!! Welcome to my Shop!!",
    "Statement 2"
)

tv_01 = DialogueScript(id=ExactNPC.TRAVELING_VENDOR_01,
                       statements=tv_01_statements)


# DEFAULT SCRIPTS BY CHARACTER NPC TYPE (FALLBACKS WHEN NO CUSTOM DIALOG IS NEEDED)

generic_map1_vendor_statements: tuple[str, ...] = (
    "Welcome to my Shop!",
    "Statement 2"
)

generic_map01_vendor = DialogueScript(id=NPCType.TRAVELING_VENDOR,
                       statements=generic_map1_vendor_statements)



# Exact-NPC entries override the default dialogue for their NPCType. NPCs with
# no named entry resolve through DEFAULT_DIALOG_SCRIPTS_BY_TYPE.
# TODO: when switch to python 3.15, make this a frozendict
DIALOGUE_SCRIPTS_BY_NAME: dict[ExactNPC: DialogueScript] = {
    ExactNPC.TRAVELING_VENDOR_01: tv_01
}

DEFAULT_DIALOG_SCRIPTS_BY_TYPE: dict[NPCType: DialogueScript] = {
    NPCType.TRAVELING_VENDOR : generic_map01_vendor
}

from dataclasses import dataclass
from enum import StrEnum

from characters.npc_type import NPCType
from ui.post_dialogue_menu import PostDialogueMenuType


# Identify exact NPCs through the name field authored in Tiled.
class ExactNPC(StrEnum):
    TRAVELING_VENDOR_01 = "traveling_vendor_01"

@dataclass(frozen=True)
# Describe the static text and optional post-dialogue menu for one NPC interaction.
# DialoguePanel owns the runtime state that selects what is currently displayed.
class NPCInteractionDefinition:
    id: str
    statements: tuple[str, ...]
    post_dialogue_menu: PostDialogueMenuType | None = None


# CUSTOM INTERACTIONS BY CHARACTER INTERNAL NAME
tv_01_statements: tuple[str, ...] = (
    "Hi Ashley, welcome to my shop!",
    "Here you will find food, weapons, spells, armor, and other sundry items on sale at fair prices."
)

tv_01 = NPCInteractionDefinition(id=ExactNPC.TRAVELING_VENDOR_01,
                       statements=tv_01_statements,
                       post_dialogue_menu=PostDialogueMenuType.GENERAL_VENDOR_MENU)


# DEFAULT NPC INTERACTIONS BY CHARACTER TYPE (FALLBACKS WHEN NO CUSTOM ONE IS NEEDED)

generic_map1_vendor_statements: tuple[str, ...] = (
    "Welcome to my Shop!",
    "Statement 2"
)

generic_map01_vendor = NPCInteractionDefinition(id=NPCType.TRAVELING_VENDOR,
                       statements=generic_map1_vendor_statements,
                       post_dialogue_menu=PostDialogueMenuType.GENERAL_VENDOR_MENU)



# Exact-NPC entries override the default interaction for their NPCType. NPCs with
# no named entry resolve through DEFAULT_NPC_INTERACTIONS_BY_TYPE.
# TODO: when switch to python 3.15, make this a frozendict
NPC_INTERACTIONS_BY_NAME: dict[ExactNPC: NPCInteractionDefinition] = {
    ExactNPC.TRAVELING_VENDOR_01: tv_01
}

DEFAULT_NPC_INTERACTIONS_BY_TYPE: dict[NPCType: NPCInteractionDefinition] = {
    NPCType.TRAVELING_VENDOR : generic_map01_vendor
}

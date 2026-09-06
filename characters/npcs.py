from enum import StrEnum

import pygame

from characters.character import Character, DirectionValue, AnimationState
from characters.character_scaffolds import CharacterScaffold


# Define the NPC types that map authors may select through the character_type property.
class NPCType(StrEnum):
    TRAVELING_VENDOR = "traveling_vendor"


# NPC adds map-authored identity and initial-placement data to Character.
# It does not decide when it should appear; the game loop applies that map-load policy.
class NPC(Character):

    def __init__(self,
                 *, 
                 name: str,
                 display_name: str,
                 scaffold: CharacterScaffold,
                 npc_type: NPCType,
                 supports_interaction: bool,
                 is_interactable_on_spawn: bool,
                 spawn_on_map_load: bool,
                 initial_x_spawn: float,
                 initial_y_spawn: float,
                 initial_x_direction: DirectionValue = 0,
                 initial_y_direction: DirectionValue = 0
                 ):

        super().__init__(name=name,
                         display_name=display_name,
                         scaffold=scaffold)

        # Store the feet-center location authored by this NPC's point object in Tiled.
        self.initial_x_spawn_loc = initial_x_spawn
        self.initial_y_spawn_loc = initial_y_spawn

        self.direction_x = initial_x_direction
        self.direction_y = initial_y_direction

        self.npc_type = npc_type

        self.spawn_on_map_load = spawn_on_map_load

        # An NPC cannot become interactable on spawn unless it supports interaction at all.
        if supports_interaction is False and is_interactable_on_spawn is True:
            raise ValueError(f" NPC: {name}, {display_name} can't NOT support interaction and also be interactable on spawn.")

        # Set the capability before using the interaction-state setter, which validates against it.
        self.supports_interaction = supports_interaction
        self.is_interactable_on_spawn = is_interactable_on_spawn
        # leading _ because we're using property getter and setter below for validation
        self._is_currently_interactable = False

    # Place this NPC at its authored initial location. Callers may override the initial
    # direction, but deciding whether to spawn now remains outside this method.
    def spawn_from_initial_map_placement(self, 
                                         direction_x: DirectionValue | None = None,
                                         direction_y: DirectionValue | None = None,
                                         ):
        
        if direction_x is not None:
            self.direction_x = direction_x

        if direction_y is not None:
            self.direction_y = direction_y

        # Each spawn restores this NPC's map-authored initial interaction state.
        self.is_currently_interactable = self.is_interactable_on_spawn

        super().spawn(self.initial_x_spawn_loc,
                      self.initial_y_spawn_loc,
                      self.direction_x,
                      self.direction_y)

    @property
    def is_currently_interactable(self) -> bool:
        return self._is_currently_interactable

    @is_currently_interactable.setter
    def is_currently_interactable(self, interactable_val: bool) -> None:

        if self.supports_interaction is False and interactable_val is True:
            raise ValueError(f"NPC {self.display_name}, {self.name} does not support interaction;"
                             " can't set self.is_currently_interactable to true.")

        self._is_currently_interactable = interactable_val

    # returns interaction rect for NPCs that support interaction (whether or not the NPC is currently interactable)
    # returns None if NPC does not support interaction at all
    @property
    def interaction_rect(self) -> pygame.Rect | None:

        if self.supports_interaction is False:
            return None
        
        if not self.spawned:
            raise ValueError(f"NPC {self.name}, {self.display_name} has no interaction rect beccause it's not spawned.")

        # calculate the actual visible sillouette of the sprite 
        top = self.world_y + self.scaffold.visible_top_offset
        left = self.world_x + self.scaffold.visible_left_offset

        # Derive each visible dimensions
        npc_current_frame = self.scaffold.sprite_animation_rects.get(self._current_animation_state)[self._current_frame_index]
        npc_sprite_full_width = npc_current_frame.width
        npc_sprite_full_height = npc_current_frame.height

        width = npc_sprite_full_width - self.scaffold.visible_left_offset - self.scaffold.visible_right_offset
        height = npc_sprite_full_height - self.scaffold.visible_top_offset - self.scaffold.visible_bottom_offset

        # Pad the visible bounds evenly to create a talk range, not a physical collision box.
        # TODO: make customizable?
        return pygame.Rect(left - 30, top - 30, width + 60, height + 60)

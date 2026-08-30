from enum import StrEnum

from characters.character import Character, DirectionValue
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

        super().spawn(self.initial_x_spawn_loc,
                      self.initial_y_spawn_loc,
                      self.direction_x,
                      self.direction_y)

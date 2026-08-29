# Autumnwood Design Overview

This document summarizes the current code and map-design architecture
for Autumnwood. It is intended as a quick reference for remembering what
the major pieces are responsible for and how data flows through the
game.

A separate guide, [Regions and Region Effects](regions-and-region-effects.md),
covers the detailed checklist for adding new regions and region effects.

## Core design principles

-   Tiled defines world layout, visible map art, and map-authored
    gameplay metadata.
-   Python converts Tiled gameplay metadata into runtime objects.
-   Visual map art and gameplay metadata are often represented
    separately.
-   `Character` owns character state, animation, and character-specific
    movement math.
-   `GameMap` owns the currently loaded Tiled map and map-derived
    runtime data.
-   Regions describe areas of the map.
-   Region effects describe what those areas imply for gameplay.
-   World objects represent discrete interactable things authored in
    Tiled.
-   The main game loop coordinates systems rather than putting every
    behavior inside `Character`.
-   Prefer small, explicit abstractions over building large generalized
    systems before they are needed.
-   Prefer readable Python, including comprehensions and generator
    expressions where they make intent clearer, but not concision for
    its own sake.

## Tiled map structure

### `Ground`

Base terrain art: grass, sand, water tiles, paths, and similar
ground-level terrain.

These are primarily visual unless a separate region or collision object
gives them gameplay meaning.

### `Scenery`

Complete visible props and environmental scenery such as trees, rocks,
houses, tents, and decorative structures.

A tree painted here is only map art. Tiled does not automatically treat
it as a discrete gameplay object. Large props should remain complete
rather than being manually split between visual layers.
Player-behind-prop rendering can be handled by the engine later.

### `walls`

A lowercase visual layer used by the Epic RPG World Automapping rules.
The lowercase name is intentional because the Automapping rules target
that layer.

### `World Objects`

Discrete gameplay objects that Python should load and reason about. This
is the foundation of the object/interaction system.

Example apple tree:

-   built-in Tiled Name: `apple_tree_01` (the runtime name may be
    optional)
-   custom property: `world_object_type = apple_tree`

General convention:

-   **Name** identifies one specific object when an individual identity
    is useful.
-   **Custom properties** describe what kind of object it is or how it
    behaves.

The visible tree art can remain on `Scenery`; the `World Objects` layer
provides the invisible gameplay representation used by Python.

The current objects are static. Runtime state such as a door becoming
unlocked, changing art, or becoming passable should be added when a real
object requires it rather than pre-built as a generic system.

### `NPCs`

Point objects describing non-player characters that belong to this map.
Each requires a `character_type` custom property so Python can select the
appropriate character scaffold. `spawn_on_map_load` defaults to `true`;
set it to `false` for an NPC that a future trigger should place later.

The point is the NPC's initial position. It does not need a separate
entry on the `Spawns` layer.

### `Spawns`

Named locations where characters can be placed, such as `player_start`,
entrances, and return points for map transitions.

Map transitions refer to destination spawn names rather than hard-coded
coordinates.

### `Regions`

Rectangular gameplay areas with explicit meaning. Every object on this
layer requires a `region_type` custom property.

Examples include `map_transition`, `quicksand`, and navigable water.
Some region types use the base `Region` class; others use subclasses
when they need extra runtime data.

See [Regions and Region Effects](regions-and-region-effects.md) for the full
region workflow.

### `Collisions`

Plain impassable map areas. Objects on this layer are automatically
loaded as `RegionType.SOLID`.

They intentionally require no `region_type` metadata. This keeps
ordinary collision authoring cheap because maps may contain many
collision rectangles.

## `GameMap`

`GameMap` is the runtime representation of one loaded Tiled map.

Constructing a `GameMap` from a `.tmx` path currently:

-   loads the Tiled map and referenced tile images
-   converts Tiled gameplay metadata into runtime regions and world
    objects, and NPCs
-   calculates the map's pixel width and height

Important public state currently includes:

-   `tiled_map`
-   `regions`
-   `world_objects`
-   `npcs`
-   `width`
-   `height`

### Map queries

`GameMap` owns queries that depend directly on the contents of a
particular map.

Current examples:

-   `get_player_spawn_coords()`
-   `get_regions_intersecting_character()`
-   `get_world_objs_intersecting_character()`

This is an important refactoring boundary: `GameMap` answers questions
about the map, but does not need to interpret every gameplay consequence
of the answer.

``` text
GameMap:
Which regions intersect this character?

region_effects:
What effects do these intersecting regions produce?

main:
When and how should those effects be applied?
```

This separation also avoids circular dependencies between `game_map.py`
and `region_effects.py`.

### Internal Tiled conversion

`GameMap._load_map_elements()` converts Tiled object
layers into Python runtime objects.

``` text
Collisions object
-> Region(type=SOLID)

Regions / map_transition
-> MapTransitionRegion

Regions / quicksand
-> QuicksandRegion

World Objects / apple_tree
-> AppleTree

NPCs / traveling_vendor
-> NPC(scaffold=TRAVELING_VENDOR)
```

The leading underscore marks this loader as an internal implementation
detail of `GameMap`.

## Character

`Character` represents a character's own runtime state and
movement/animation behavior.

Current responsibilities include:

-   name
-   sprite sheet and animation frames
-   world position
-   movement direction
-   character-owned speed
-   spawn offsets
-   collision rectangle configuration
-   visible sprite bounds
-   animation state and animation timing
-   calculating proposed movement
-   character-specific visible-sprite bounds calculations used by movement

### Position and spawning

A `Character` is constructed before it exists in the world. `spawn()`
places it at a map spawn location and establishes its world coordinates.

Position-dependent methods should not be used before the character has
been spawned.

### Character scaffolds and NPCs

`CharacterScaffold` holds the reusable, static configuration for one
kind of character: its sprite source, frame rectangles, collision and
visible bounds, spawn offsets, and default speed. It is keyword-only so
each value remains clear at the definition site.

`NPC` is a `Character` with map-authored placement information such as
its NPC type, initial location, and whether it should spawn when the map
loads. `GameMap` loads that data; `main.py` applies the spawn policy when
the initial map or a transition destination becomes current.

### Collision rectangle

Character collision uses a small rectangle around the character's feet
rather than the full sprite.

`get_collision_rect()` can return the current collision rectangle or
calculate one at a proposed position without actually moving the
character.

### Movement speed

`default_speed` is the character's configured base speed. `speed` is its
persistent runtime speed.

Temporary environmental effects such as quicksand do **not** overwrite
either stored value.

`get_proposed_new_position()` accepts speed modifiers and calculates a
temporary effective speed for that movement only.

This leaves room for future persistent speed influences such as
equipment, buffs/debuffs, injuries, mounts, and abilities.

## `SpeedModifier`

`SpeedModifier` is a `Protocol`.

``` python
class SpeedModifier(Protocol):
    percent_change: float
```

Anything exposing a compatible `percent_change` attribute can be used as
a speed modifier without explicitly inheriting from `SpeedModifier`.

This lets unrelated systems contribute speed changes without forcing
them into one inheritance hierarchy. Examples could eventually include
`SpeedRegionEffect`, equipment modifiers, status modifiers, and mount
modifiers.

Multiple percentage modifiers are currently combined additively, then
applied to the character's stored speed for the current movement
calculation.

## Regions

`Region` is the base runtime representation of a rectangular gameplay
area. It contains `rect` and `type`.

`RegionType` is a `StrEnum` whose string values match values authored in
Tiled.

Current region types include:

-   `SOLID`
-   `NAVIGABLE_DEEP_WATER`
-   `NAVIGABLE_SHALLOW_WATER`
-   `MAP_TRANSITION`
-   `QUICKSAND`

### Specialized region subclasses

A specialized subclass is used only when that region needs additional
runtime data.

#### `MapTransitionRegion`

Adds `destination_map` and `destination_spawn`. Its type is fixed
automatically to `RegionType.MAP_TRANSITION`.

#### `QuicksandRegion`

Adds `percent_change`. Its type is fixed automatically to
`RegionType.QUICKSAND`.

A region type that requires no additional runtime data can remain a
plain `Region`.

## Region effects

A `Region` describes an area. A `RegionEffect` describes an effect
produced by occupying that area.

Current concrete effects:

-   `MapTransitionRegionEffect`
-   `SpeedRegionEffect`

`ActiveRegionEffects` collects discovered effects into:

-   `pre_move_effects`
-   `post_move_effects`

### `get_active_region_effects()`

`get_active_region_effects()` is now a plain function rather than a
`GameMap` method.

Its responsibility is:

``` text
intersecting regions
-> gameplay effects implied by those regions
```

Conceptually:

``` python
def get_active_region_effects(
    intersecting_regions: Sequence[Region],
) -> ActiveRegionEffects:
```

It deliberately does not receive a `GameMap` or a `Character`. The
caller first asks the map which regions intersect the character, then
passes those regions into the effect function.

This keeps the dependency boundary clean and prevents `game_map.py` and
`region_effects.py` from importing each other.

### Pre-move effects

These affect the upcoming movement. Current example: quicksand produces
a `SpeedRegionEffect`.

### Post-move effects

These react to the player's location after movement resolves. Current
example: map transition produces a `MapTransitionRegionEffect`.

The game currently does not explicitly model `ON_ENTER` or `ON_EXIT`
region events. Add that only when a real gameplay feature requires it.

## Region data flow

``` text
Tiled region
-> GameMap loads Region / specialized Region subclass
-> GameMap determines which regions intersect the player
-> get_active_region_effects(intersecting_regions)
-> ActiveRegionEffects
-> game loop processes pre- or post-move effects
```

### Quicksand example

``` text
Tiled: region_type = quicksand
-> QuicksandRegion(percent_change=-0.50)
-> GameMap reports that player intersects quicksand
-> get_active_region_effects()
-> SpeedRegionEffect(percent_change=-0.50)
-> pre_move_effects
-> passed as a SpeedModifier
-> Character calculates temporary effective speed
-> movement occurs at reduced speed
```

Leaving quicksand requires no cleanup because the player's stored speed
was never changed.

### Map transition example

``` text
Tiled map-transition region
-> MapTransitionRegion
-> player intersects region after movement
-> get_active_region_effects()
-> MapTransitionRegionEffect
-> post_move_effects
-> main loop constructs destination GameMap
-> destination spawn is looked up by name
-> existing player is spawned there
```

Round-trip transitions between maps are working.

## World objects and interaction

`WorldObject` is the runtime foundation for discrete interactable things
in the world.

Current first concrete object:

-   `AppleTree`

`WorldObjectType` identifies the type authored in Tiled.

Current interaction flow:

``` text
Tiled World Objects object
-> GameMap loads WorldObject / AppleTree
-> player presses E
-> GameMap finds world objects intersecting the player's collision rectangle
-> main loop dispatches based on runtime object type
-> interaction creates a GameNotification
```

The current apple-tree interaction is intentionally simple. It proves
that Tiled-authored world objects can become runtime objects and
participate in player interaction.

### Current interaction range

Interaction currently uses overlap between the player's collision
rectangle and the world object's rectangle.

This is sufficient for the first milestone. A later interaction system
may use facing direction, a small interaction rectangle, or
nearby-object selection rather than literal collision overlap.

### Large prop rendering note

A large apple-tree sprite currently looks somewhat odd when the player
walks upward into its leaves because only the base is blocked by
collision while the complete tree is rendered as scenery.

This is a known presentation issue, not a reason to enlarge the
collision box. The likely later solution is Y/depth-aware rendering so
the player can appear behind the upper portion of large props while
still colliding only with their base.

## Game notifications

The game has a basic on-screen notification system for transient gameplay
feedback, such as an object interaction. This is intentionally separate
from future NPC dialogue.

`GameNotification` stores:

-   `text`
-   `dismiss_policy`
-   optional `timeout_secs`

`NotificationPanel` owns the active notification, remaining time for a
timed notification, and panel rendering.

Current dismissal policies:

-   `ON_MOVE_ATTEMPT`
-   `TIMED`

### `ON_MOVE_ATTEMPT`

The notification remains visible until the player attempts movement.

The policy is deliberately named `ON_MOVE_ATTEMPT`, rather than
`ON_MOVE`, because the notification should disappear when the player tries to
move even if collision prevents an actual position change.

### `TIMED`

The notification remains visible for a configured number of seconds.

If a timed notification receives no valid positive timeout, it uses a
default timeout of 3 seconds. `NotificationPanel` decrements its remaining
time using frame `delta_secs`.

### Notification panel

The current implementation uses:

-   a `pygame.Surface` created with `pygame.SRCALPHA`
-   a semi-transparent black panel
-   rendered font text blitted onto that panel
-   the panel blitted near the bottom of the game window

The panel is only drawn when an active notification exists.

The current Pygame default font is temporary. Autumnwood should
eventually ship its own suitable game font rather than depend on fonts
installed on the player's system.

The notification system is deliberately small. NPC dialogue will need its
own advance behavior rather than being forced into notification policies.

## Map loading and transitions

The old collection of separate active-map variables has been
consolidated into `GameMap`.

The main loop now owns:

``` text
current_map: GameMap
```

A map transition replaces it with a destination `GameMap`. The existing
player object is then respawned at the requested named spawn in the new
map.

Map names stored in Tiled are logical names such as `special_forest`;
Python resolves them to `.tmx` files under the maps/resources path.

## Movement and collision flow

The current frame flow is approximately:

``` text
1. Read discrete Pygame events such as quit, debug toggle, and E interaction.
2. Read held movement keys and set player direction / movement-attempt flags.
3. Ask GameMap which regions intersect the player's current position.
4. Translate those regions into active region effects.
5. Collect pre-move effects such as SpeedModifiers.
6. Calculate and validate proposed movement.
7. Move the player when the proposed position is valid.
8. Ask GameMap which regions intersect the new player position.
9. Translate those regions into active region effects again.
10. Process post-move effects such as map transitions.
11. Select the animation state and apply notification dismissal tied to movement attempts.
12. Calculate camera position.
13. Draw the map.
14. Advance and draw the player and any spawned NPCs.
15. Update/draw any active game notification.
16. Draw optional debug overlays.
17. Flip the completed frame to the display.
```

### Movement validation

`is_proposed_player_move_valid()` checks map bounds and intersections
with regions that are not walkable by default.

The current rule is intentionally based on
`Region.is_walkable_by_default()`.

Later this will need to become more contextual for cases such as locked
door + key, deep water + boat, and other conditionally passable terrain
or objects.

That contextual traversal system is deliberately deferred until a real
gameplay feature requires it.

## Camera

The camera stores the world coordinate shown at the screen's top-left.

After player movement:

-   calculate the camera position that would center the player
-   clamp it to the current `GameMap` bounds
-   subtract the camera position from world coordinates when drawing

Debug rectangles are shifted into screen coordinates with the same
camera offset.

Camera positioning currently lives in the focused `camera.py` function. A
dedicated `Camera` object remains a possible later refactor only if the
camera gains enough state or behavior to justify one.

## Animation

`AnimationState` is a `StrEnum`.

Current states include idle, walking, attack preparation, attack, dying,
and dead.

Each character is configured with sprite-sheet rectangles for the
animation states it supports. If a requested animation is unavailable,
the character currently falls back to idle.

## Debug overlay

The backquote key toggles map-debug rendering.

The overlay currently shows:

-   map region rectangles
-   different colors by region type
-   world-object rectangles
-   the player's collision rectangle

When a new `RegionType` is added, update the debug-color match so it can
be visually verified on the map.

## Current refactor

The game began with much of its map/runtime logic in `main.py`.
Refactoring is now happening incrementally rather than as a rewrite.

Completed extractions so far are:

- `GameMap` for loaded map state and spatial queries
- `camera.py` for clamped camera-position calculation
- `movement.py` for world movement validation and collision sliding
- `map_render.py` for Tiled tile-layer drawing
- `debug_rendering.py` for optional diagnostic overlays
- `notifications.py` for active-notification lifecycle and presentation
- `npcs.py` for NPC-specific map placement state

The main-loop refactor continues: `main.py` should coordinate these systems
rather than own their internal state or rendering details.

The guiding question is not simply "how can `main.py` become shorter?"
It is:

> Which object or module has enough information and responsibility to
> own this behavior?

Current direction:

``` text
GameMap
    loaded map data
    dimensions
    regions
    world objects
    NPCs
    spawn lookup
    map-specific intersection queries

region_effects.py
    translate intersecting regions into effects

Character
    character-owned state and movement/animation calculations

NPC
    a Character with map-authored initial placement and spawn policy

main.py
    game-loop orchestration
    input
    sequencing systems
    applying effects
    map replacement
```

Future extractions should remain focused responsibilities, rather than parts
of a premature large-engine architecture.

## Development roadmap

``` text
movement / maps / camera
-> regions / effects / transitions
-> object + interaction foundation
-> basic notification UI
-> refactor main into clearer runtime responsibilities
-> first NPC map loading / spawning / rendering
-> NPC interaction + dialogue
-> inventory as real interactions require it
-> health / damage
-> contextual traversal and blocking
-> combat / enemies
-> quests / story state
-> content creation and final overworld
-> presentation / polish
```

Important roadmap notes:

-   Quicksand is working.
-   Map transitions work in both directions.
-   `GameMap` now encapsulates loaded map state and map-specific
    queries.
-   The first `WorldObject` (`AppleTree`) loads from Tiled and can be
    interacted with using E.
-   A basic on-screen `GameNotification` pipeline works, including
    `ON_MOVE_ATTEMPT` and `TIMED` dismissal policies.
-   The main loop now loads and renders map-authored NPCs. The first
    NPC's interaction and dialogue are the next content feature.
-   A fade-to-black / fade-in map transition effect is planned, but is
    not urgent.
-   Y/depth-aware rendering for large props such as trees is a known
    later presentation task.
-   Window resizing and resolution handling are not implemented yet; the
    current window is fixed-size.
-   The game should eventually ship its own font rather than depend on
    system fonts.
-   Do not build NPC AI, pathfinding, or a generalized dialogue engine
    before the first NPC interaction shows what is actually needed.
-   Do not build inventory, harvesting, respawn, or a generalized item
    system merely because the apple tree exists; add those when an
    actual interaction requires them.
-   When an object first needs to change state (for example, an
    unlocked door or collected item), add the smallest runtime-state
    model that supports that real interaction.
-   Do not build the final large overworld yet.
-   Near the content phase, prototype overworld scale with crude maps
    and actual travel time before committing to final dimensions.
-   The target feeling is a substantial exploratory world in the
    tradition of older Ultima-style RPGs, not necessarily a compact
    modern indie map.

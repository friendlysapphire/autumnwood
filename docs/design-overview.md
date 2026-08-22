# Autumnwood Design Overview

This document summarizes the current code and map-design architecture for Autumnwood. It is intended as a quick reference for remembering what the major pieces are responsible for and how data flows through the game.

A separate guide, `regions_and_region_effects.m`, covers the detailed checklist for adding new regions and region effects.

## Core design principles

The project currently follows a few simple rules:

- Tiled defines the world layout and metadata.
- Python converts Tiled data into runtime objects.
- Visual map art and gameplay metadata are often represented separately.
- `Character` owns character state and movement math.
- Regions describe areas of the map.
- Region effects describe what those areas imply for the player.
- The main game loop coordinates systems rather than putting every behavior inside `Character`.
- Prefer small, explicit abstractions over building large generalized systems before they are needed.

## Tiled map structure

Current map layers have distinct responsibilities.

### `Ground`

The base terrain art.

Examples:

- grass
- sand
- water tiles
- paths

These are primarily visual unless a separate region or collision object gives them gameplay meaning.

### `Objects on Ground`

Visual scenery placed above the ground.

Examples:

- trees
- rocks
- decorative structures

A tree painted here is only map art. Tiled does not automatically treat it as a discrete gameplay object.

### `World Objects`

Discrete gameplay objects that Python should load and reason about.

This layer is new and is the foundation for the object/interaction system.

Example apple tree:

- built-in Tiled Name: `apple_tree_01`
- custom property: `object_type = apple_tree`

General convention:

- **Name** identifies one specific object.
- **Custom properties** describe what kind of object it is or how it behaves.

The visible art can remain on `Objects on Ground`; the `World Objects` layer provides the invisible gameplay representation.

### `Spawns`

Named locations where characters can be placed.

Examples:

- `player_start`
- `entrance`
- return points for map transitions

Map transitions refer to destination spawn names rather than hard-coded coordinates.

### `Regions`

Rectangular gameplay areas with explicit meaning.

Every object on this layer requires a `region_type` custom property.

Examples:

- `map_transition`
- `quicksand`
- navigable water

Some region types use the base `Region` class; others use subclasses when they need extra runtime data.

See `REGIONS_AND_REGION_EFFECTS.md` for the full region workflow.

### `Collisions`

Plain impassable map areas.

Objects on this layer are automatically loaded as `RegionType.SOLID`.

They intentionally require no `region_type` metadata. This keeps ordinary collision authoring cheap because maps may contain many collision rectangles.

## Character

`Character` represents a character's own runtime state and movement/animation behavior.

Current responsibilities include:

- name
- sprite sheet and animation frames
- world position
- movement direction
- character-owned speed
- spawn offsets
- collision rectangle configuration
- visible sprite bounds
- animation state and animation timing
- calculating proposed movement
- checking map bounds

### Position and spawning

A `Character` is constructed before it exists in the world.

`spawn()` places it at a named map location and establishes its world coordinates.

Position-dependent methods should not be used before the character has been spawned.

### Collision rectangle

Character collision uses a small rectangle around the character's feet rather than the full sprite.

`get_collision_rect()` can return the current collision rectangle or calculate one at a proposed position without actually moving the character.

### Movement speed

The character remains the source of truth for its normal/current speed.

Temporary environmental effects such as quicksand do **not** overwrite that stored speed.

`get_proposed_new_position()` accepts speed modifiers and calculates a temporary effective speed for that movement only.

This leaves room for future persistent speed influences such as:

- equipment
- buffs/debuffs
- injuries
- mounts
- abilities

## `SpeedModifier`

`SpeedModifier` is a `Protocol`.

Its current interface is simply:

```python
class SpeedModifier(Protocol):
    percent_change: float
```

Anything exposing a compatible `percent_change` attribute can be used as a speed modifier without explicitly inheriting from `SpeedModifier`.

This lets unrelated systems contribute speed changes without forcing them into one inheritance hierarchy.

Examples could eventually include:

- `SpeedRegionEffect`
- equipment modifiers
- status modifiers
- mount modifiers

Multiple percentage modifiers are currently combined additively, then applied to the character's stored speed for the current movement calculation.

## Regions

`Region` is the base runtime representation of a rectangular gameplay area.

It contains:

- `rect`
- `type`

`RegionType` is a `StrEnum` whose string values match the values authored in Tiled.

Current region types include:

- `SOLID`
- `NAVIGABLE_DEEP_WATER`
- `NAVIGABLE_SHALLOW_WATER`
- `MAP_TRANSITION`
- `QUICKSAND`

### Specialized region subclasses

A specialized subclass is used only when that region needs additional runtime data.

#### `MapTransitionRegion`

Adds:

- `destination_map`
- `destination_spawn`

Its type is fixed automatically to `RegionType.MAP_TRANSITION`.

#### `QuicksandRegion`

Adds:

- `percent_change`

Its type is fixed automatically to `RegionType.QUICKSAND`.

A region type that requires no additional runtime data can remain a plain `Region`.

## Region effects

A `Region` describes an area. A `RegionEffect` describes an effect produced by occupying that area.

The effect system is intentionally separate from the region classes themselves.

Current base class:

```python
RegionEffect
```

Current concrete effects:

- `MapTransitionRegionEffect`
- `SpeedRegionEffect`

`ActiveRegionEffects` collects discovered effects into:

- `pre_move_effects`
- `post_move_effects`

### Pre-move effects

These affect the upcoming movement.

Current example:

- quicksand produces a `SpeedRegionEffect`

### Post-move effects

These react to the player's location after movement resolves.

Current example:

- map transition produces a `MapTransitionRegionEffect`

The game currently does not explicitly model `ON_ENTER` or `ON_EXIT` region events. Add that only when a real gameplay feature requires it.

## Region data flow

The general flow is:

```text
Tiled region
-> get_map_regions()
-> Region / specialized Region subclass
-> player intersects region
-> get_region_effects()
-> ActiveRegionEffects
-> game loop processes pre- or post-move effect
```

### Quicksand example

```text
Tiled: region_type = quicksand
-> QuicksandRegion(percent_change=-0.50)
-> player currently intersects quicksand
-> SpeedRegionEffect(percent_change=-0.50)
-> pre_move_effects
-> passed as a SpeedModifier
-> Character calculates temporary effective speed
-> movement occurs at reduced speed
```

Leaving quicksand requires no cleanup because the player's stored speed was never changed.

### Map transition example

```text
Tiled map-transition region
-> MapTransitionRegion
-> player enters region
-> MapTransitionRegionEffect
-> post_move_effects
-> main loop loads destination map
-> destination spawn is looked up by name
-> existing player is spawned there
```

Round-trip transitions between maps are working.

## Map loading

`load_map_and_regions()` currently loads the map-dependent runtime state:

- `tiled_map`
- `map_regions`
- `map_height`
- `map_width`

The main loop owns the active versions of those values.

A map transition replaces that active map state and then respawns the existing player at the requested named spawn.

Map names stored in Tiled are logical names such as:

```text
special_forest
```

Python resolves those to `.tmx` files under the maps/resources path.

## Movement and collision flow

The current frame flow is approximately:

```text
1. Read input and set player direction.
2. Determine region effects at the player's current position.
3. Process pre-move effects and derive movement inputs such as SpeedModifiers.
4. Calculate and validate proposed movement.
5. Move the player.
6. Determine region effects at the new position.
7. Process post-move effects such as map transitions.
8. Calculate camera position.
9. Update animation.
10. Draw map, character, and optional debug overlays.
```

### Movement validation

`is_proposed_player_move_valid()` checks:

- map bounds
- intersections with regions that are not walkable by default

The current rule is intentionally based on `Region.is_walkable_by_default()`.

Later this will need to become more contextual for cases such as:

- locked door + key
- deep water + boat
- other conditionally passable terrain or objects

That contextual traversal system has been deliberately deferred until a real gameplay feature requires it.

## Camera

The camera stores the world coordinate shown at the screen's top-left.

After player movement:

- calculate the camera position that would center the player
- clamp it to the map bounds
- subtract the camera position from world coordinates when drawing

Debug rectangles are shifted into screen coordinates with the same camera offset.

## Animation

`AnimationState` is a `StrEnum`.

Current states include values such as:

- idle
- walking
- attack preparation
- attack
- dying
- dead

Each character is configured with sprite-sheet rectangles for the animation states it supports.

If a requested animation is unavailable, the character currently falls back to idle.

## Debug overlay

The backquote key toggles map-debug rendering.

The overlay currently shows:

- map region rectangles
- different colors by region type
- the player's collision rectangle

When a new `RegionType` is added, update the debug-color match so it can be visually verified on the map.

## Object / interaction system: current next step

The next major system is the world-object foundation.

The first test object is an apple tree.

Current Tiled setup:

```text
Visible art:
    Objects on Ground layer

Gameplay representation:
    World Objects layer
    Name = apple_tree_01
    object_type = apple_tree
```

The intended first milestone is deliberately small:

```text
Tiled World Object
-> Python runtime WorldObject
-> player gets close enough
-> player presses interaction key
-> game identifies the object
-> simple interaction/message
```

Do not build inventory, harvesting, respawn, or a generalized item system until the first basic interaction works.

## Development roadmap

Current broad roadmap:

```text
movement / maps / camera
-> regions / effects / transitions
-> object + interaction foundation
-> first simple NPC + dialogue
-> inventory as real interactions require it
-> health / damage
-> contextual traversal and blocking
-> combat / enemies
-> quests / story state
-> content creation and final overworld
-> presentation / polish
```

Important roadmap notes:

- Quicksand is working.
- Map transitions work in both directions.
- A fade-to-black / fade-in map transition effect is planned, but is not urgent.
- NPC/dialogue should arrive relatively early after the object/interaction foundation so the project begins to feel like a game rather than only an environmental engine.
- Do not build the final large overworld yet.
- Near the content phase, prototype overworld scale with crude maps and actual travel time before committing to final dimensions.
- The target feeling is a substantial exploratory world in the tradition of older Ultima-style RPGs, not necessarily a compact modern indie map.

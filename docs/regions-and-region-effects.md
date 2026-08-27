# Regions and Region Effects

This is the checklist for adding a new gameplay region and wiring up any effects it should produce.

The current design separates several ideas:

- **GameMap**: owns the currently loaded Tiled map and the runtime map data derived from it, including regions and world objects.
- **Region**: an area on the map with gameplay meaning.
- **RegionEffect**: one effect implied by occupying a region.
- **ActiveRegionEffects**: groups effects implied by one set of intersecting regions into pre-move and post-move buckets.
- **Game loop processing**: coordinates intersection queries, effect discovery, and application of those effects.

Ordinary impassable scenery stays on Tiled's **Collisions** layer and requires no custom metadata. Special gameplay areas go on the **Regions** layer.

## 1. Add the region in Tiled

For a normal gameplay region:

1. Draw a rectangle on the **Regions** object layer.
2. Add the custom string property `region_type = <value>`.
3. Add any additional custom properties required by that region type.

Examples:

- Quicksand: `region_type = quicksand`
- Map transition:
  - `region_type = map_transition`
  - `destination_map = special_forest`
  - `destination_spawn = entrance`

Use Tiled's built-in **Name** field only when a particular region needs its own identity. Use custom properties to describe what kind of region it is and how it behaves.

Ordinary collision rectangles belong on the **Collisions** layer. They are automatically treated as `SOLID` and do not need `region_type`.

## 2. Add the region type in `region.py`

Add the Tiled string value to `RegionType`.

Example:

```python
QUICKSAND = "quicksand"
```

The string must match the `region_type` value authored in Tiled.

Then update `Region.is_walkable_by_default()` so the new type has an explicit default movement rule.

## 3. Decide whether the region needs its own subclass

A plain `Region` is enough when the region only needs:

- `rect`
- `type`

Create a subclass when the region needs additional runtime data.

Examples:

- `MapTransitionRegion`: `destination_map`, `destination_spawn`
- `QuicksandRegion`: `percent_change`

When a subclass always represents one `RegionType`, fix its type automatically:

```python
type: RegionType = field(init=False, default=RegionType.QUICKSAND)
```

This prevents inconsistent objects.

### Why some region types use subclasses and others do not

Not every `RegionType` needs its own Python class.

Use a plain `Region(rect=..., type=...)` when the region's type alone contains everything the game needs to know. For example, a navigable-water region may only need its rectangle and `RegionType`.

Create a specialized subclass only when that region needs additional runtime data or behavior that a plain `Region` does not have.

Examples:

- `MapTransitionRegion` needs `destination_map` and `destination_spawn`.
- `QuicksandRegion` carries its `percent_change`.
- A simple navigable-water region can remain a plain `Region` because its `RegionType` is enough to describe it.

## 4. Teach `GameMap` how to load it

`GameMap` owns the active Tiled map and converts its authored metadata into runtime map objects when the map is constructed.

Its internal map-loading code currently creates both:

- regions
- world objects

The current quicksand percentage is a Python-defined shared value rather
than per-region Tiled metadata. A Tiled quicksand object therefore needs
only `region_type = quicksand` today.

For a new region type:

1. Read `obj.properties["region_type"]`.
2. Match the value to the appropriate `RegionType`.
3. Read any required custom properties.
4. Validate required properties and fail clearly if they are missing.
5. Construct the correct `Region` subclass.
6. Append it to the region collection.

Keep the authoring contract:

- **Collisions layer** -> always `RegionType.SOLID`
- **Regions layer** -> explicit `region_type` required

If the region requires no special runtime data, a plain `Region` may be enough.

The general loading branch:

```python
elif r_type:
    region_list.append(Region(rect=region_rect, type=RegionType(r_type)))
```

means that the map supplied a `region_type` that does not require a specialized subclass. Python attempts to convert it to a `RegionType` and represents it with the base `Region` class.

`RegionType(r_type)` will reject an unknown value.

The final `else` is different: it means the Tiled object did not supply a `region_type` at all, which is an authoring error on the **Regions** layer.

## 5. Understand region intersection

`GameMap` owns the regions belonging to the current map, so it also provides the map-specific intersection query:

```python
current_map.get_regions_intersecting_character(character)
```

This compares the character's collision rectangle with the map's regions and returns the regions currently intersecting the character.

This step deliberately remains separate from region-effect discovery.

Conceptually:

```text
Character + GameMap
-> GameMap determines intersecting Regions
-> intersecting Regions are passed to the effect system
-> effect system determines what those Regions imply
```

This separation prevents the region-effect module from needing to know about `GameMap` and avoids circular dependencies between map and effect modules.

## 6. Decide whether the region produces an effect

Not every region needs a `RegionEffect`.

Examples:

- `SOLID` affects movement validity directly and needs no separate effect.
- Navigable water may initially need no effect.
- Quicksand produces a speed effect.
- A map-transition region produces a transition effect.

If the region produces a new kind of effect, add a small dataclass in `region_effects.py`.

Existing examples:

- `SpeedRegionEffect`
- `MapTransitionRegionEffect`

Each effect dataclass should contain only the data needed to apply that effect.

All concrete region-effect classes inherit from the common `RegionEffect` base class.

## 7. Make the new effect a `RegionEffect`

All region effects inherit from the common `RegionEffect` base class.

Example:

```python
@dataclass(kw_only=True)
class NewRegionEffect(RegionEffect):
    ...
```

`ActiveRegionEffects` collects effects into two mutable lists:

- `pre_move_effects`
- `post_move_effects`

These use `field(default_factory=list)`.

Add the effect to the appropriate list when `get_active_region_effects()` discovers the corresponding region.

## 8. Update `get_active_region_effects()`

`get_active_region_effects()` operates only on regions that have already been identified as intersecting the player.

Its responsibility is:

1. Receive a sequence of intersecting `Region` objects.
2. Determine what effects those regions imply.
3. Return an `ActiveRegionEffects` object.
4. **Not** apply those effects itself.

Its input therefore looks conceptually like:

```python
def get_active_region_effects(
    intersecting_regions: Sequence[Region],
) -> ActiveRegionEffects:
```

The function does not need the `Character` or `GameMap`. Those responsibilities belong elsewhere.

The game loop first asks the current map for intersecting regions:

```text
current_map.get_regions_intersecting_character(player)
```

and then passes those regions into:

```text
get_active_region_effects(intersecting_regions)
```

Use `isinstance()` when effect creation depends on data that exists only on a region subclass.

Examples:

```python
isinstance(region, MapTransitionRegion)
isinstance(region, QuicksandRegion)
```

Then create the appropriate effect and append it to the correct bucket.

The region subclass and the effect class remain separate concepts:

```text
Region
= what exists on the map

RegionEffect
= what occupying that region currently implies
```

### Pre-move effects

Use for effects that need to influence the upcoming movement.

Example: quicksand speed reduction.

### Post-move effects

Use for effects that react to the player's position after movement resolves.

Example: map transition.

The current model intentionally does not track explicit enter/exit events yet. Add that only when a real gameplay feature needs it.

## 9. Process region effects in the game loop

The frame currently follows this pattern:

```text
1. Read player input.
2. Ask GameMap which regions intersect the player at the current position.
3. Convert those regions into ActiveRegionEffects.
4. Process pre-move effects.
5. Resolve player movement.
6. Ask GameMap which regions intersect the player at the new position.
7. Convert those regions into ActiveRegionEffects.
8. Process post-move effects.
9. Calculate camera and animation state.
10. Draw the frame.
```

The important separation is:

```text
GameMap
-> knows where Regions are

get_active_region_effects()
-> knows what intersecting Regions imply

game loop
-> knows when those effects should be processed

Character / other subsystems
-> perform the actual relevant behavior
```

Before movement, the game loop gets the currently intersecting regions and derives `pre_move_effects`.

After movement, it performs the intersection query again because the player's position may have changed, then derives and processes `post_move_effects`.

Use `isinstance()` to narrow a general `RegionEffect` to the specific effect dataclass before accessing effect-specific fields.

Do not pass an arbitrary collection of unrelated region effects into a subsystem. Process the effects first and pass that subsystem only the inputs relevant to it.

For example, movement receives speed modifiers rather than every possible pre-move region effect.

## 10. Speed effects and `SpeedModifier`

Temporary terrain effects must not overwrite the character's stored speed.

The character remains the source of truth for its normal speed. Temporary movement changes are represented through the `SpeedModifier` protocol:

```python
class SpeedModifier(Protocol):
    percent_change: float
```

Anything with a compatible `percent_change` attribute can satisfy this protocol. `SpeedRegionEffect` therefore works as a `SpeedModifier` without needing to inherit from it or explicitly declare that it implements the protocol.

Before movement:

1. Get the regions currently intersecting the player.
2. Convert them into `ActiveRegionEffects`.
3. Collect applicable `SpeedRegionEffect`s from `pre_move_effects`.
4. Pass them to the movement code as `SpeedModifier`s.
5. The character sums their percentage changes.
6. It calculates a temporary effective speed for this movement only.
7. The character's stored speed is not changed.

Conceptually:

```text
stored character speed
+ active SpeedModifiers
-> effective speed for this movement
-> proposed position
```

Multiple percentage modifiers are currently additive.

For example:

```text
quicksand: -50%
boots:     +10%
----------------
total:     -40%
```

The character calculates:

```python
aggregate_pct_change = sum(
    modifier.percent_change
    for modifier in speed_modifiers
)

effective_speed = self.speed * (1 + aggregate_pct_change)
```

This leaves room for future non-region speed modifiers such as:

- equipment
- buffs/debuffs
- injuries
- mounts
- abilities

Those systems can provide objects satisfying `SpeedModifier` without needing to know anything about regions.

## 11. Map transitions

Map transitions are post-move effects.

The current path is:

```text
Tiled map-transition object
-> GameMap loads MapTransitionRegion
-> player moves into its rectangle
-> GameMap reports the region as intersecting
-> get_active_region_effects()
-> MapTransitionRegionEffect
-> post_move_effects
-> game loop creates destination GameMap
-> destination spawn is looked up
-> existing player is spawned there
```

Creating a new `GameMap` replaces the active map state as one object rather than requiring the game loop to separately replace:

- Tiled map
- region collection
- world-object collection
- map width
- map height

The destination spawn is obtained through:

```python
current_map.get_spawn_coords(...)
```

## 12. Update debug rendering

Add a distinct debug color for the new `RegionType` in the debug-overlay `match` statement.

The debug overlay reads the regions from the current `GameMap`.

This helps verify that:

- Tiled metadata loaded correctly
- the correct runtime region subclass was created
- the rectangle is in the expected location

## 13. Test the full path

Verify the whole chain:

```text
Tiled region
-> region_type/custom properties
-> GameMap loading
-> Region or Region subclass
-> GameMap intersection query
-> get_active_region_effects() if applicable
-> ActiveRegionEffects pre/post bucket
-> game-loop processing
-> subsystem-specific input if applicable
-> visible gameplay result
```

Also test:

- entering the region
- remaining inside the region
- leaving the region
- collision interaction, if relevant
- overlap with other regions/effects, if possible

For temporary effects such as quicksand, specifically verify that leaving the region restores normal behavior without requiring cleanup of stored player state.

## Current examples

### `SOLID`

- Authored on: **Collisions** layer
- Metadata: none
- Runtime: `Region(type=SOLID)`
- Owned by: `GameMap`
- Default walkability: false
- Region effect: none

### `MAP_TRANSITION`

- Authored on: **Regions** layer
- Properties: `region_type`, `destination_map`, `destination_spawn`
- Runtime: `MapTransitionRegion`
- Owned by: `GameMap`
- Default walkability: true
- Effect: `MapTransitionRegionEffect`
- Processing: post-move

### `QUICKSAND`

- Authored on: **Regions** layer
- Property: `region_type = quicksand`
- Runtime: `QuicksandRegion`
- Owned by: `GameMap`
- Default walkability: true
- Effect: `SpeedRegionEffect`
- Processing: pre-move
- Speed handling: contributes a `SpeedModifier` to the current movement calculation without changing the player's stored speed

## Quick checklist

When adding a region, check:

- Tiled **Regions** layer and custom properties
- `RegionType` in `region.py`
- `Region.is_walkable_by_default()`
- optional new `Region` subclass in `region.py`
- `GameMap` loading logic in `game_map.py`
- optional new effect dataclass in `region_effects.py`
- new effect subclass of `RegionEffect`, if needed
- `get_active_region_effects()` in `region_effects.py`
- `GameMap.get_regions_intersecting_character()`
- pre-move or post-move processing in the main loop
- `SpeedModifier` compatibility if the effect changes movement speed
- debug-overlay color
- gameplay test

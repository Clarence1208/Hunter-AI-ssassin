# Apartment Layout Documentation

## Overview

The game now features a **fixed apartment-style map** instead of random obstacle generation. This provides a consistent, strategic environment with defined rooms, corridors, and cover points.

## Map Structure

### Rooms

1. **Bedroom** (Top-Left)
   - Enclosed room with one entrance
   - Enemy patrol area
   - Strategic cover points

2. **Kitchen** (Top-Right)
   - Open area with counter/island
   - Enemy spawn location
   - Connected to main area

3. **Living Room** (Center)
   - Large open space
   - Furniture for cover (couch, table)
   - Main combat area

4. **Bathroom** (Bottom-Right)
   - Small enclosed room
   - Single entrance
   - Enemy patrol zone

5. **Corridors**
   - Connect different rooms
   - Narrow passages
   - Strategic chokepoints

### Layout Dimensions
- **Screen Size**: 1280 x 720 pixels
- **Wall Thickness**: 20 pixels
- **Room Sizes**: Vary from 200-400 pixels
- **Grid Pattern**: 80x80 pixel floor tiles

## Spawn Locations

### Player Spawn
- **Position**: Bottom-left corner (100, 100)
- **Area**: Entrance/safe zone
- **Strategy**: Far from all enemies, good starting position

### Enemy Spawns

All enemies spawn **far from the player** in strategic locations:

1. **Enemy 1**: Bedroom (200, 620)
2. **Enemy 2**: Kitchen (1080, 470)
3. **Enemy 3**: Bathroom (1130, 100)
4. **Enemy 4**: Living Room Center (700, 400)
5. **Enemy 5**: Hallway (900, 200)

**Distance from Player**: All enemies spawn 400-1000 pixels away from player start.

## Patrol Routes

Each enemy has a predefined patrol route within their area:

### Enemy 1 - Bedroom Patrol
```
(150, 620) → (250, 620) → (250, 470) → (150, 470) → repeat
```
Small square patrol in bedroom area.

### Enemy 2 - Kitchen Patrol
```
(1080, 570) → (1180, 570) → (1180, 420) → (1080, 420) → repeat
```
Patrols kitchen area near counter.

### Enemy 3 - Bathroom Patrol
```
(1130, 80) → (1030, 80) → (1030, 150) → (1130, 150) → repeat
```
Small patrol in bathroom.

### Enemy 4 - Living Room Patrol
```
(600, 300) → (800, 300) → (800, 450) → (600, 450) → repeat
```
Large patrol through living room.

### Enemy 5 - Corridor Patrol
```
(450, 200) → (650, 200) → (650, 350) → (450, 350) → repeat
```
Patrols hallway connecting areas.

## Visual Design

### Color Scheme

**Floor**:
- Base: Dark gray `(40, 40, 45)`
- Grid: Slightly lighter `(45, 45, 50)`
- Pattern: 80px grid for tile effect

**Walls**:
- Main walls: Blue-gray `(60, 60, 70)`
- Accent walls: Purple-gray `(70, 50, 60)`
- Furniture/Doors: Brown `(80, 60, 50)`

**Borders**:
- All walls have subtle darker borders (-20 RGB)
- Creates depth and 3D effect

### Textures

1. **Floor Grid**: Subtle lines every 80 pixels
2. **Wall Borders**: 2-pixel outline around each wall
3. **Color Variation**: Different wall types for visual interest

## Strategic Elements

### Cover Points

Strategic furniture and obstacles for tactical gameplay:

1. **Living Room Couch** (500, 300) - 120x60
2. **Living Room Table** (700, 450) - 80x80
3. **Kitchen Counter** (1080, 470) - 80x60
4. **Hallway Cover** (450, 150) - 70x50
5. **Bedroom Cover** (400, 370) - 60x70

### Chokepoints

Narrow passages that control enemy movement:
- Bedroom doorway
- Bathroom entrance
- Kitchen corridor
- Central hallway

### Open Areas

Large spaces for maneuvering:
- Living room center
- Kitchen open space
- Main corridor

## Gameplay Strategy

### For Players

**Early Game**:
1. Start at entrance (bottom-left)
2. Survey the map (game pauses until first move)
3. Plan route to nearest enemy
4. Use corridors for cover

**Mid Game**:
1. Clear enemies room by room
2. Use furniture for cover from bullets
3. Avoid open areas when spotted
4. Learn patrol patterns

**Late Game**:
1. Hunt remaining enemies
2. Use map knowledge to ambush
3. Corner enemies in rooms

### For RL Agents

**Advantages**:
- **Consistent environment**: Same map every episode
- **Learnable patterns**: Fixed enemy patrols
- **Strategic depth**: Room-by-room tactics
- **Clear objectives**: Defined areas to clear

**Challenges**:
- **Long-range engagement**: Enemies far from start
- **Multiple rooms**: Must navigate complex layout
- **Patrol coordination**: Multiple enemies to track
- **Cover usage**: Must learn to use furniture

## Configuration

### Toggle Layout Mode

In `config.py`:
```python
USE_APARTMENT_LAYOUT = True   # Use fixed apartment
# or
USE_APARTMENT_LAYOUT = False  # Use random generation
```

### Customize Colors

```python
WALL_COLOR = (60, 60, 70)         # Main walls
FLOOR_COLOR = (40, 40, 45)        # Floor
DOOR_COLOR = (80, 60, 50)         # Furniture
ACCENT_WALL_COLOR = (70, 50, 60) # Accent walls
```

### Modify Layout

Edit `map_layouts.py`:
- `get_walls()`: Change room structure
- `get_player_spawn()`: Change player start
- `get_enemy_spawns()`: Modify enemy positions
- `get_enemy_patrol_routes()`: Adjust patrol paths

## Future Enhancements

Potential improvements to the layout system:

1. **Multiple Maps**: Add more apartment layouts
2. **Dynamic Elements**: Doors that open/close
3. **Hazards**: Environmental dangers
4. **Objectives**: Keys, items to collect
5. **Destructible Cover**: Cover that breaks when shot
6. **Lighting**: Room-based lighting zones
7. **Map Editor**: Tool to create custom layouts

## Performance

Layout rendering performance:
- **16 walls**: Minimal draw calls
- **Floor grid**: Simple line drawing
- **No impact**: Same FPS as random generation
- **Memory**: Fixed overhead, no random generation cost

## Comparison

### Fixed Layout vs Random

| Feature | Fixed Apartment | Random Generation |
|---------|----------------|-------------------|
| Consistency | ✅ Same every time | ❌ Different each reset |
| Learning | ✅ Agent can memorize | ❌ Must generalize |
| Visual Appeal | ✅ Designed, themed | ⚠️ Generic obstacles |
| Strategic Depth | ✅ Rooms and tactics | ⚠️ Random placement |
| Development | ⚠️ Manual design | ✅ Automatic |

---

The apartment layout provides a professional, learnable environment perfect for both human play and RL training!

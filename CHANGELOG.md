# Changelog

## v2.2 - Apartment Layout & Textures

### Major Changes

#### 🏠 Fixed Apartment Layout
- **Replaced random generation** with a designed apartment map
- **Multiple rooms**: Living room, bedroom, kitchen, bathroom
- **Corridors and doorways**: Realistic apartment structure
- **Strategic cover points**: Furniture, counters, and obstacles
- **Fixed spawn points**: Consistent starting positions

#### 🎨 Visual Textures
- **Floor texture**: Grid pattern for visual depth
- **Colored walls**: Different colors for variety (walls, accents, doors)
- **Borders**: Subtle borders on walls for 3D effect
- **Dark theme**: Professional dark color scheme

#### 🎯 Improved Enemy Placement
- **Far from player**: Enemies spawn at defined positions far from entrance
- **Strategic locations**: Each enemy in different room/area
- **Patrol routes**: Defined patrol paths for each enemy position
- **Balanced difficulty**: Better-spaced encounters

### Configuration
New settings in `config.py`:
```python
USE_APARTMENT_LAYOUT = True  # Toggle fixed vs random maps
WALL_COLOR = (60, 60, 70)   # Wall color
FLOOR_COLOR = (40, 40, 45)   # Floor color
DOOR_COLOR = (80, 60, 50)    # Accent/furniture color
ACCENT_WALL_COLOR = (70, 50, 60)  # Accent walls
```

### Technical Changes

#### New Files
- `map_layouts.py` - Apartment layout definition class
  - `ApartmentLayout` class with room structure
  - Fixed spawn points for player and enemies
  - Patrol route definitions

#### Files Modified
- `config.py` - Added layout and color settings
- `entities.py` - Obstacle now accepts custom colors, added borders
- `game_env.py` - Added apartment layout support, floor rendering
  - `_generate_apartment_layout()` method
  - `_generate_random_layout()` method (backward compatible)
  - Floor grid pattern rendering

### Gameplay Impact

**Before**:
- Random obstacle placement
- Random spawn positions  
- No defined structure
- Generic gray obstacles

**After**:
- Designed apartment layout
- Fixed, balanced spawns
- Room-based structure
- Textured, colored environment
- Strategic cover placement

### Benefits

**For Players**:
- **Learnable map**: Can develop strategies for specific layout
- **Visual clarity**: Colors help identify different areas
- **Strategic depth**: Use rooms and corridors tactically
- **Better pacing**: Enemies spread out for progressive difficulty

**For RL Training**:
- **Consistent environment**: Same map every episode
- **Faster learning**: Agent can learn optimal paths
- **Better evaluation**: Fair comparison between training runs
- **Strategic AI**: Agent must learn room-by-room tactics

### Backward Compatibility

Set `USE_APARTMENT_LAYOUT = False` in `config.py` to use original random generation.

---

## v2.1 - Visual & UX Improvements

### Visual Enhancements

#### 🎨 Improved Enemy Vision Cone Rendering
- **Gradient effect**: Vision cones now have a 3-layer gradient (tamed light effect)
- **Better visibility**: Easier to see the full cone from the enemy
- **Color coding**: Vision line changes color when enemy sees player
- **Smoother rendering**: Filled wedge shape instead of just outline

#### ⏸️ Game Start Pause
- **Wait for player**: Game now pauses until player makes first movement
- **Clear indication**: "MOVE TO START" message displayed on screen
- **Better control**: Player can survey the level before starting
- **Strategic advantage**: Time to plan approach before enemies activate

### Configuration
New setting in `config.py`:
- `PAUSE_UNTIL_FIRST_MOVE = True` - Enable/disable start pause

### Technical Changes

#### Files Modified
- `config.py` - Added pause configuration
- `game_env.py` - Added game_started flag, improved vision rendering
  - New `_draw_vision_cone()` method for gradient cones
  - Start screen with instructions
  - Enemies freeze until player moves

### User Experience Impact

**Before**:
- Game started immediately
- Vision cones hard to see (outline only)
- No time to assess the situation

**After**:
- Player controls when game starts
- Vision cones clearly visible with gradient
- Can plan strategy before moving

---

## v2.0 - Shooting Mechanics Update

### Major Changes

#### 🎯 Enemy Shooting System
- **Enemies now shoot bullets** when they detect the player
- Replaced touch-based death with projectile-based combat
- Added shooting delay (0.5s) when first detecting player
- Added shooting cooldown (1s) between shots

#### 💥 Bullet System
- New `Bullet` class with physics and collision detection
- Bullets travel at 8 pixels/frame
- Bullets blocked by obstacles
- Bullets have 2-second lifetime
- Visual trail effect for bullet motion

#### 🎨 Visual Effects
- Muzzle flash animation when enemies shoot
- Bullet trail showing direction of travel
- Bullet count display in UI

#### ⚙️ Configuration
Added new configuration parameters in `config.py`:
- `ENEMY_SHOOT_COOLDOWN`
- `ENEMY_SHOOT_DELAY`
- `BULLET_SPEED`
- `BULLET_SIZE`
- `BULLET_COLOR`
- `BULLET_LIFETIME`

### Gameplay Impact

**Before**: 
- Player died when enemies touched them
- Stealth was about avoiding enemy proximity

**After**:
- Player dies when shot by bullets
- Stealth is about avoiding enemy line of sight
- Cover and obstacles are crucial for survival
- More strategic and challenging gameplay

### Technical Changes

#### Files Modified
- `config.py` - Added shooting configuration
- `entities.py` - Added `Bullet` class, updated `Enemy` AI
- `game_env.py` - Added bullet management, updated collision detection
- `README.md` - Updated game mechanics description
- `QUICKSTART.md` - Updated objective description

#### New Files
- `SHOOTING_MECHANICS.md` - Detailed shooting system documentation
- `CHANGELOG.md` - This file

### For RL Training

The shooting mechanic makes the task more challenging:
- **Time pressure**: Must act quickly when spotted
- **Cover usage**: Learning to use obstacles strategically
- **Prediction**: Anticipating enemy behavior and bullet trajectories
- **Risk-reward**: Balancing aggressive vs. cautious approaches

### Backward Compatibility

- Old `check_collision_with_player()` method deprecated but kept
- API remains the same (same observation/action spaces)
- Existing RL code should work without modification
- Reward structure unchanged

---

## v1.0 - Initial Release

- Basic Hunter Assassin game with arcade library
- Ray casting for enemy vision
- Player stealth movement
- Enemy AI with patrol/chase/alert states
- RL-ready environment interface
- Clean architecture with modular design

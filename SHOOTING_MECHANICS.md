# Shooting Mechanics

## Overview

Enemies now **shoot bullets** at the player when they have line of sight, making the game more challenging and strategic. This replaces the old "touch to kill" mechanic.

## How It Works

### Enemy Shooting Behavior

1. **Detection**: Enemy detects player within vision cone using ray casting
2. **Delay**: 0.5 second delay (30 frames) before first shot after detecting player
3. **Shooting**: Enemy fires bullet aimed at player's current position
4. **Cooldown**: 1 second cooldown (60 frames) between shots
5. **Visual Feedback**: Bright muzzle flash when shooting

### Bullet Properties

- **Speed**: 8.0 pixels/frame (configurable in `config.py`)
- **Size**: 4 pixel radius
- **Color**: Yellow
- **Lifetime**: 2 seconds (120 frames) before despawning
- **Collisions**: 
  - Bullets stop when hitting obstacles
  - Bullets kill player on contact
  - Bullets despawn when hitting screen boundaries

### Visual Effects

- **Bullet Trail**: Yellow streak showing bullet motion direction
- **Muzzle Flash**: Bright white/yellow flash at enemy position when shooting
- **Bullet Count**: Displayed in UI for debugging

## Configuration

All shooting parameters can be adjusted in `config.py`:

```python
# Enemy shooting settings
ENEMY_SHOOT_COOLDOWN = 60        # Frames between shots
ENEMY_SHOOT_DELAY = 30           # Delay before first shot
BULLET_SPEED = 8.0               # Bullet movement speed
BULLET_SIZE = 4                  # Bullet radius
BULLET_COLOR = (255, 255, 0)     # Yellow bullets
BULLET_LIFETIME = 120            # Frames before despawn
```

## Gameplay Impact

### For Players

- **Take Cover**: Use obstacles to block bullets and break line of sight
- **Move Strategically**: Avoid open areas where enemies can shoot you
- **Quick Eliminations**: Eliminate enemies quickly before they can shoot
- **Dodge**: Keep moving to avoid bullets (they aim at current position)

### For RL Agents

The shooting mechanic adds several challenges:
- **Time Pressure**: Must eliminate enemies before being shot
- **Cover Usage**: Learning to use obstacles for protection
- **Risk Assessment**: Balancing aggressive play vs. cautious approach
- **Prediction**: Predicting bullet trajectories and enemy shooting patterns

## Reward Structure

The reward structure remains similar, but death is now caused by bullets:

- **Get Shot**: -100 reward (same as before)
- **Kill Enemy**: +100 reward
- **Win**: +500 reward
- **Step Penalty**: -0.1 per step

## Technical Implementation

### Bullet Class

Located in `entities.py`, the `Bullet` class handles:
- Position and velocity updates
- Collision detection with obstacles
- Collision detection with player
- Rendering with trail effect

### Enemy AI Updates

The `Enemy` class now includes:
- Shooting cooldown tracking
- Shooting delay timer
- `_shoot_at_player()` method
- Returns `Bullet` object from `update_ai()` when shooting

### Game Environment Integration

The `HunterAssassinEnv` class manages:
- Bullet list tracking
- Bullet updates each frame
- Bullet-player collision checking
- Bullet rendering
- Bullet cleanup

## Tips for RL Training

1. **Observation Space**: The current observation includes enemy positions and alert states, which helps agents learn to avoid being shot

2. **Reward Shaping**: Consider adding:
   - Small penalty for being in enemy line of sight
   - Reward for breaking line of sight after being spotted
   - Reward for using cover effectively

3. **Curriculum Learning**: Start training with:
   - Fewer enemies
   - Slower bullet speed
   - Longer shooting delay
   - Gradually increase difficulty

4. **Action Space**: The 8-directional movement helps agents dodge bullets

## Future Enhancements

Potential improvements to consider:
- Player shooting ability
- Different bullet types (faster, slower, homing)
- Limited ammo for enemies
- Bullet spread/accuracy system
- Ricocheting bullets
- Explosive projectiles

---

**Note**: Enemies no longer need to touch the player to kill them. The old `check_collision_with_player()` method is deprecated but kept for backward compatibility.

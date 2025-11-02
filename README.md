# Hunter Assassin - RL Ready

A clean implementation of the Hunter Assassin game using Python Arcade with ray casting for enemy vision. Designed with a modular architecture ready for reinforcement learning agent integration.

## Features

- **Apartment Layout**: Fixed apartment-style map with rooms, corridors, and strategic cover
- **Textured Environment**: Floor grid pattern, colored walls, visual depth
- **Ray Casting**: Enemies use ray casting for realistic line-of-sight detection
- **Enemy Shooting**: Enemies fire bullets when they see the player (use cover!)
- **Visual Effects**: Gradient vision cones, muzzle flashes, bullet trails
- **Strategic Start**: Game pauses until first movement - plan your approach
- **Smart Enemy Placement**: Enemies spawn far from player with defined patrol routes
- **Clean Architecture**: Modular design with separate concerns (entities, game logic, utilities)
- **RL-Ready Interface**: Gym-like environment with well-defined state/action/reward structure
- **Smooth Gameplay**: Built with the latest Arcade library
- **Configurable**: Easy-to-modify configuration file for all game parameters

## Game Mechanics

- **Player**: Stealth-based movement, eliminate enemies by getting close
- **Enemies**: AI-controlled with patrol routes, cone-based vision, chase behavior, and **shooting**
  - Enemies **shoot bullets** when they see the player
  - Short delay before first shot when detecting player
  - Cooldown between shots
  - Bullets travel through the air and can be blocked by obstacles
- **Obstacles**: Strategic cover that blocks line of sight and bullets
- **Stealth**: Avoid enemy vision cones to stay undetected - if spotted, you'll be shot!

## Project Structure

```
Hunter-AI-ssassin/
├── config.py          # Game configuration and parameters
├── entities.py        # Player, Enemy, Obstacle, and Bullet classes
├── map_layouts.py     # Fixed apartment layout definition
├── utils.py           # Ray casting and collision detection utilities
├── game_env.py        # Main game environment (RL-ready)
├── main.py            # Entry point for running the game
└── requirements.txt
```

## Installation

1. **Clone or navigate to the repository**

2. **Create a virtual environment** (recommended):
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the game**:
```bash
python main.py
```

**Note**: This project is tested with arcade 3.3.2. The rendering uses custom draw methods compatible with arcade 3.x API.

## Usage

### Manual Play Mode
Play the game yourself with keyboard controls:
```bash
python main.py --mode play
```

**Controls:**
- `WASD` or `Arrow Keys` or Click - Move player
- `SPACE` - Toggle vision rays display
- `V` - Toggle enemy vision cones
- `R` - Reset game
- `ESC` - Quit

### Headless Mode
Run without rendering (useful for training):
```bash
python main.py --mode play --no-render

```
### Training RL Mode
Run with rendering :
```bash
python agent.py train 100 
```

## Reinforcement Learning Integration

The game environment is designed to be easily integrated with RL frameworks.

### State Space

The observation is a continuous vector containing:
- **Ray cast distances** (16 rays, 360° coverage): Normalized distances to obstacles
- **Player info**: Position (x, y normalized), alive status
- **Enemy info** (for each enemy): Relative position, distance, alive status, alert status

**Total observation size**: `16 (rays) + 3 (player) + 5×NUM_ENEMIES (enemy info)`

### Action Space

Discrete action space with 9 actions:
- 1: Move up
- 2: Move down
- 3: Move left
- 4: Move right

### Reward Structure

- **Kill enemy**: +100
- **Get killed**: -100
- **Win (all enemies eliminated)**: +500
- **Step penalty**: -0.1 (encourages efficiency)
- **Distance reward**: Small positive reward for getting closer to enemies

## Configuration

All game parameters can be easily modified in `config.py`:

- Window settings (resolution, title)
- Player settings (speed, size, attack range)
- Enemy settings (speed, vision range, vision angle, number of enemies)
- Obstacle settings (number, sizes)
- RL settings (max steps, rewards, penalties)
- Ray casting settings (number of rays, max distance)

## Architecture Highlights

### Clean Separation of Concerns
- **config.py**: All configuration in one place
- **entities.py**: Game entities with their own logic
- **utils.py**: Reusable utility functions
- **game_env.py**: Game logic and RL interface
- **main.py**: Entry points and demo modes

### Ray Casting System
The game implements proper ray casting for:
- Enemy vision detection
- Obstacle occlusion
- Player distance sensing (for RL observations)

### Modular Enemy AI
Enemy behavior is state-based:
- **Random**: When no player detected with influence to follow the current direction
- **Chase**: Pursue player when in line of sight
- **Alert**: Investigate last known player position

## Development
## Performance

- Runs at 60 FPS with rendering
- Can run much faster in headless mode for training
- Supports adjustable game speed via `config.GAME_SPEED`


## License

This project is open source and available for educational and research purposes.

## Credits

Built with:
- [Python Arcade](https://api.arcade.academy/) - 2D game framework
- NumPy - Numerical computing
- Inspired by the mobile game "Hunter Assassin"


### TO DO : 
- Amélirorer le QT agent
- La mort de l'agent ne relance pas toujours un épisode.
- Les ennemis ne démarent si on est en mode click pour bouger le joueur (mais on s'en fiche pour le RL)
- Trouver des beaux sprites ennemis
- Voir pourquoi ça prend autant de cpu (wtf) - optimisation (J'ai plus le comportement ?)
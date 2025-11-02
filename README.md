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

### Demo Mode
Watch random actions being executed:
```bash
python main.py --mode demo --episodes 5
```

### Test RL Interface
Test the environment's RL interface:
```bash
python main.py --mode test
```

### Headless Mode
Run without rendering (useful for training):
```bash
python main.py --mode play --no-render
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
- 0: Stay still
- 1: Move up
- 2: Move down
- 3: Move left
- 4: Move right
- 5: Move up-left
- 6: Move up-right
- 7: Move down-left
- 8: Move down-right

### Reward Structure

- **Kill enemy**: +100
- **Get killed**: -100
- **Win (all enemies eliminated)**: +500
- **Step penalty**: -0.1 (encourages efficiency)
- **Distance reward**: Small positive reward for getting closer to enemies

### Example RL Integration

```python
from game_env import HunterAssassinEnv
import numpy as np

# Create environment
env = HunterAssassinEnv(render_mode=False)  # Set to True for visualization

# Training loop example
for episode in range(1000):
    obs = env.reset()
    done = False
    episode_reward = 0
    
    while not done:
        # Your RL agent selects action here
        action = your_agent.select_action(obs)
        
        # Take action
        obs, reward, done, info = env.step(action)
        episode_reward += reward
        
        # Train your agent here
        your_agent.learn(obs, action, reward, done)
    
    print(f"Episode {episode}: Reward = {episode_reward}, Kills = {info['kills']}")
```

### Integration with Popular RL Frameworks

#### Stable-Baselines3
Create a Gym wrapper:
```python
import gymnasium as gym
from gymnasium import spaces

class GymHunterEnv(gym.Env):
    def __init__(self):
        self.env = HunterAssassinEnv(render_mode=False)
        self.observation_space = spaces.Box(
            low=0, high=1, 
            shape=(self.env.get_observation_space_size(),), 
            dtype=np.float32
        )
        self.action_space = spaces.Discrete(self.env.get_action_space_size())
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        obs = self.env.reset()
        return obs, {}
    
    def step(self, action):
        obs, reward, done, info = self.env.step(action)
        return obs, reward, done, False, info
```

#### PyTorch/Custom RL
The environment can be used directly with custom implementations:
```python
# The env.step() and env.reset() methods follow standard conventions
obs = env.reset()
action = model.forward(obs)
next_obs, reward, done, info = env.step(action)
```

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
- **Patrol**: Follow waypoints when no player detected
- **Chase**: Pursue player when in line of sight
- **Alert**: Investigate last known player position

### RL-Ready Design
- Clear observation/action/reward structure
- Episode management with proper reset
- Info dictionary for debugging and metrics
- Configurable rendering (can run headless)

## Development

### Adding New Features

**New Enemy Behavior**:
Edit the `Enemy` class in `entities.py` and add new states to the AI.

**Different Observation Types**:
Modify `_get_observation()` in `game_env.py` to add or change observations.

**New Reward Shaping**:
Adjust reward calculations in the `step()` method of `game_env.py`.

**Different Map Layouts**:
Modify `_generate_obstacles()` in `game_env.py` for custom level designs.

## Performance

- Runs at 60 FPS with rendering
- Can run much faster in headless mode for training
- Supports adjustable game speed via `config.GAME_SPEED`

## Future Extensions

Some ideas for extending the game:
- Save/load trained agents
- Multiple difficulty levels
- Procedural level generation
- Different enemy types with varied behaviors
- Power-ups and special abilities
- Multiplayer support
- Level editor

## License

This project is open source and available for educational and research purposes.

## Credits

Built with:
- [Python Arcade](https://api.arcade.academy/) - 2D game framework
- NumPy - Numerical computing
- Inspired by the mobile game "Hunter Assassin"


### TO DO : 
- Remove le ray autour du joueur
- Améliorer le comportement des ennemis (chemin aléatoire ++)
- Fix ray des ennemis (comme pour le joueur)
- Fix le path du joueur quand on repasse en manuel
- Trouver des beaux sprites ennemis
- Voir pourquoi ça prend autant de cpu (wtf) - optimisation
- Vitesse du jeu
- Prototype d'IA
- Tej les fichiers d'IA qui servent à rien
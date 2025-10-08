# Quick Start Guide

## Installation & Setup

```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

## Running the Game

### Play Manually
```bash
python main.py --mode play
```

**Game Start:**
- Game is **PAUSED** when it starts
- Move in any direction to begin
- Use this time to plan your strategy!

**Controls:**
- `W/A/S/D` or `Arrow Keys` - Move (and start game)
- `SPACE` - Toggle vision rays
- `V` - Toggle enemy vision cones  
- `R` - Reset game
- `ESC` - Quit

### Watch Demo (Random Actions)
```bash
python main.py --mode demo --episodes 5
```

### Test RL Interface (Headless)
```bash
python main.py --mode test
```

### Visualize Observations
```bash
python visualize_observations.py
```

### Run Training Example
```bash
python example_rl_training.py
```

## Game Objective

- **Eliminate all enemies** without being shot
- **Stealth**: Stay out of enemy vision cones (yellow) - enemies will **shoot** if they see you!
- **Attack**: Get close to enemies to eliminate them
- **Survive**: Avoid bullets and use obstacles as cover
- **Take Cover**: Obstacles block both vision and bullets

## For RL Training

```python
from game_env import HunterAssassinEnv

# Create environment
env = HunterAssassinEnv(render_mode=False)  # Set True for visualization

# Training loop
obs = env.reset()
done = False

while not done:
    action = your_agent.select_action(obs)
    obs, reward, done, info = env.step(action)
    your_agent.learn(obs, action, reward, done)
```

### Key Information
- **Observation size**: 44 (16 rays + player info + 5 enemies × 5 values)
- **Action space**: 9 discrete actions
- **Rewards**: 
  - Kill: +100
  - Win: +500  
  - Death: -100
  - Step: -0.1

## Troubleshooting

### Game won't start
- Make sure virtual environment is activated
- Run: `pip install -r requirements.txt`

### Performance issues
- Use `--no-render` flag for faster training
- Adjust `config.GAME_SPEED` in `config.py`

### Want to modify game?
- **Game parameters**: Edit `config.py`
- **Rewards**: Modify `game_env.py` step() method
- **Enemy behavior**: Edit `entities.py` Enemy class
- **Observations**: Modify `game_env.py` _get_observation() method

## Next Steps

1. **Play the game** to understand mechanics
2. **Run visualize_observations.py** to see what the agent observes
3. **Check example_rl_training.py** for training template
4. **Integrate your RL algorithm** (DQN, PPO, A3C, etc.)
5. **Tune rewards** in `config.py` for better learning

Enjoy! 🎮🤖

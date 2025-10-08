"""
Game configuration settings for Hunter Assassin
"""

# Window settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Hunter Assassin - RL Ready"

# Game settings
GAME_SPEED = 1.0  # Multiplier for game speed (useful for RL training)

# Grid and map settings
GRID_SIZE = 40
MAP_WIDTH = SCREEN_WIDTH
MAP_HEIGHT = SCREEN_HEIGHT

# Player settings
PLAYER_MOVEMENT_SPEED = 3.0
PLAYER_SIZE = 15
PLAYER_COLOR = (0, 255, 100)  # Green
PLAYER_ATTACK_RANGE = 30
PLAYER_KILL_REWARD = 100.0

# Enemy settings
ENEMY_MOVEMENT_SPEED = 1.0  # Reduced from 2.0
ENEMY_SIZE = 15
ENEMY_COLOR = (255, 50, 50)  # Red
ENEMY_VISION_RANGE = 200
ENEMY_VISION_ANGLE = 60  # Degrees (cone of vision)
ENEMY_CHASE_SPEED = 1.5  # Reduced from 2.5
ENEMY_PATROL_PAUSE_TIME = 60  # Frames
ENEMY_ALERT_COLOR = (255, 150, 0)  # Orange when alerted
NUM_ENEMIES = 5

# Enemy shooting settings
ENEMY_SHOOT_COOLDOWN = 60  # Frames between shots (1 second at 60fps)
ENEMY_SHOOT_DELAY = 30  # Frames delay before first shot when seeing player
BULLET_SPEED = 8.0
BULLET_SIZE = 4
BULLET_COLOR = (255, 255, 0)  # Yellow
BULLET_LIFETIME = 120  # Frames before bullet disappears

# Obstacle settings
OBSTACLE_COLOR = (80, 80, 100)  # Dark gray
NUM_OBSTACLES = 15  # Not used when USE_APARTMENT_LAYOUT is True
OBSTACLE_MIN_SIZE = 40
OBSTACLE_MAX_SIZE = 120

# Map layout settings
USE_APARTMENT_LAYOUT = True  # Use fixed apartment map instead of random
WALL_COLOR = (60, 60, 70)  # Dark blue-gray for walls
FLOOR_COLOR = (40, 40, 45)  # Very dark gray for floor
DOOR_COLOR = (80, 60, 50)  # Brown for doors/openings
ACCENT_WALL_COLOR = (70, 50, 60)  # Accent color for some walls

# Ray casting settings
RAY_COLOR = (255, 255, 0, 50)  # Yellow with transparency
RAY_THICKNESS = 1

# Game behavior settings
PAUSE_UNTIL_FIRST_MOVE = True  # Don't start game until player moves

# RL-specific settings
MAX_STEPS_PER_EPISODE = 2000
STEP_PENALTY = -0.1  # Small penalty per step to encourage efficiency
DEATH_PENALTY = -100.0
WIN_REWARD = 500.0
DISTANCE_REWARD_SCALE = 0.5  # Reward for getting closer to enemies

# Action space (discrete)
ACTIONS = {
    0: (0, 0),      # Stay still
    1: (0, 1),      # Up
    2: (0, -1),     # Down
    3: (-1, 0),     # Left
    4: (1, 0),      # Right
    5: (-1, 1),     # Up-Left
    6: (1, 1),      # Up-Right
    7: (-1, -1),    # Down-Left
    8: (1, -1),     # Down-Right
}
NUM_ACTIONS = len(ACTIONS)

# State observation settings
NUM_RAYS = 16  # Number of ray casts for distance sensing
RAY_MAX_DISTANCE = 300

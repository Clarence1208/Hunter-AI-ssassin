"""
Game configuration settings for Hunter Assassin
"""

# Window settings
TILE_SIZE = 64  # Pixels per tile
MAP_TILES_WIDTH = 16
MAP_TILES_HEIGHT = 16
SCREEN_WIDTH = TILE_SIZE * MAP_TILES_WIDTH  # 1024
SCREEN_HEIGHT = TILE_SIZE * MAP_TILES_HEIGHT  # 1024
SCREEN_TITLE = "Hunter Assassin - Stealth Edition"

# Game settings
GAME_SPEED = 1.0  # Multiplier for game speed (useful for RL training)

# Grid and map settings
GRID_SIZE = 40
MAP_WIDTH = SCREEN_WIDTH
MAP_HEIGHT = SCREEN_HEIGHT

# Player settings
PLAYER_MOVEMENT_SPEED = 2.5
PLAYER_SIZE = 20
PLAYER_COLOR = (0, 255, 100)  # Green
PLAYER_HEALTH = 1  # 1 HP - one hit and you lose
PLAYER_MELEE_RANGE = 40  # Melee attack range in pixels
PLAYER_MELEE_WINDUP = 0.3  # Seconds before attack executes
PLAYER_MELEE_ANGLE = 120  # Degrees - attack from behind/side
PLAYER_KILL_REWARD = 100.0

# Guard settings (renamed from Enemy)
GUARD_MOVEMENT_SPEED = 1.0
GUARD_SIZE = 20
GUARD_COLOR = (255, 50, 50)  # Red
GUARD_VISION_RANGE = TILE_SIZE * 8  # 8 tiles = 512 pixels
GUARD_VISION_ANGLE = 60  # Degrees (cone of vision)
GUARD_CHASE_SPEED = 1.5
GUARD_PATROL_PAUSE_TIME = 60  # Frames
GUARD_ALERT_COLOR = (255, 150, 0)  # Orange when alerted
GUARD_DETECTION_TIME = 0.3  # Seconds to full detection
GUARD_SHOOT_RANGE = TILE_SIZE * 6  # Can shoot within 6 tiles
NUM_GUARDS = 4  # Will be overridden by JSON map

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
USE_JSON_MAP = True  # Use JSON map loader
JSON_MAP_PATH = "data/level1.json"
WALL_COLOR = (60, 60, 70)  # Dark blue-gray for walls
FLOOR_COLOR = (40, 40, 45)  # Very dark gray for floor
OBJECTIVE_COLOR = (255, 215, 0)  # Gold for objectives
HIDE_SPOT_COLOR = (100, 100, 150)  # Blue-ish for hide spots

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

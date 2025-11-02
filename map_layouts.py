"""
Predefined map layouts for Hunter Assassin game.
"""
import config
from typing import List, Tuple, Dict


class ApartmentLayout:

    def __init__(self):
        self.width = config.SCREEN_WIDTH
        self.height = config.SCREEN_HEIGHT
        
    def get_walls(self) -> List[Dict]:
        """
        Get wall/obstacle definitions for the apartment.
        Creates a maze-like layout with corridors and turnable passages.
        
        Returns:
            List of wall dictionaries with 'x', 'y', 'width', 'height', 'color'
        """
        walls = []
        
        # Outer walls (perimeter)
        wall_thickness = 15
        
        # Top wall
        walls.append({
            'x': self.width / 2,
            'y': self.height - wall_thickness / 2,
            'width': self.width,
            'height': wall_thickness,
            'color': config.WALL_COLOR
        })
        
        # Bottom wall
        walls.append({
            'x': self.width / 2,
            'y': wall_thickness / 2,
            'width': self.width,
            'height': wall_thickness,
            'color': config.WALL_COLOR
        })
        
        # Left wall
        walls.append({
            'x': wall_thickness / 2,
            'y': self.height / 2,
            'width': wall_thickness,
            'height': self.height,
            'color': config.WALL_COLOR
        })
        
        # Right wall
        walls.append({
            'x': self.width - wall_thickness / 2,
            'y': self.height / 2,
            'width': wall_thickness,
            'height': self.height,
            'color': config.WALL_COLOR
        })
        
        # Interior walls creating maze-like corridors
        # This creates L-shaped corridors and passages where you can turn
        
        # === LEFT SIDE MAZE ===
        # Vertical wall 1 (left area)
        walls.append({
            'x': 200,
            'y': self.height - 200,
            'width': wall_thickness,
            'height': 300,
            'color': config.WALL_COLOR
        })
        
        # Horizontal wall connecting (creates L-turn)
        walls.append({
            'x': 300,
            'y': self.height - 350,
            'width': 220,
            'height': wall_thickness,
            'color': config.WALL_COLOR
        })
        
        # Vertical wall 2 (creates corridor)
        walls.append({
            'x': 400,
            'y': self.height - 480,
            'width': wall_thickness,
            'height': 280,
            'color': config.ACCENT_WALL_COLOR
        })
        
        # Bottom left maze section
        walls.append({
            'x': 250,
            'y': 200,
            'width': wall_thickness,
            'height': 250,
            'color': config.WALL_COLOR
        })
        
        # Horizontal connector (bottom left)
        walls.append({
            'x': 150,
            'y': 325,
            'width': 220,
            'height': wall_thickness,
            'color': config.ACCENT_WALL_COLOR
        })
        
        # === CENTER MAZE ===
        # Central vertical divider
        walls.append({
            'x': self.width / 2,
            'y': 300,
            'width': wall_thickness,
            'height': 400,
            'color': config.WALL_COLOR
        })
        
        # Upper horizontal passage
        walls.append({
            'x': 750,
            'y': self.height - 200,
            'width': 300,
            'height': wall_thickness,
            'color': config.WALL_COLOR
        })
        
        # Middle horizontal wall (creates turn)
        walls.append({
            'x': 550,
            'y': 400,
            'width': 200,
            'height': wall_thickness,
            'color': config.ACCENT_WALL_COLOR
        })
        
        # Lower middle connector
        walls.append({
            'x': 750,
            'y': 200,
            'width': 300,
            'height': wall_thickness,
            'color': config.WALL_COLOR
        })
        
        # === RIGHT SIDE MAZE ===
        # Right vertical wall 1
        walls.append({
            'x': self.width - 250,
            'y': self.height - 300,
            'width': wall_thickness,
            'height': 400,
            'color': config.WALL_COLOR
        })
        
        # Right corridor connector
        walls.append({
            'x': self.width - 150,
            'y': self.height - 450,
            'width': 220,
            'height': wall_thickness,
            'color': config.ACCENT_WALL_COLOR
        })
        
        # Bottom right maze
        walls.append({
            'x': self.width - 200,
            'y': 300,
            'width': wall_thickness,
            'height': 380,
            'color': config.WALL_COLOR
        })
        
        # === STRATEGIC COVER (smaller walls to hide behind) ===
        # Cover 1 (center-left)
        walls.append({
            'x': 350,
            'y': 450,
            'width': 80,
            'height': 50,
            'color': config.DOOR_COLOR
        })
        
        # Cover 2 (center-right)
        walls.append({
            'x': 850,
            'y': 450,
            'width': 80,
            'height': 50,
            'color': config.DOOR_COLOR
        })
        
        # Cover 3 (top area)
        walls.append({
            'x': 550,
            'y': self.height - 100,
            'width': 60,
            'height': 80,
            'color': config.DOOR_COLOR
        })
        
        # Cover 4 (bottom area)
        walls.append({
            'x': 550,
            'y': 100,
            'width': 70,
            'height': 60,
            'color': config.DOOR_COLOR
        })
        
        return walls
    
    def get_player_spawn(self) -> Tuple[float, float]:
        """
        Get fixed player spawn position (near entrance/safe area).
        
        Returns:
            (x, y) coordinates
        """
        # Spawn player in bottom left (entrance area)
        return (80, 80)
    
    def get_enemy_spawns(self, num_enemies: int = 5) -> List[Tuple[float, float]]:
        """
        Get fixed enemy spawn positions spread throughout maze.
        
        Args:
            num_enemies: Number of enemies to spawn
        
        Returns:
            List of (x, y) coordinates
        """
        # Predefined spawn points in different corridors (far from player)
        spawn_points = [
            (300, self.height - 200),      # Top left corridor
            (700, self.height - 350),      # Top center area
            (self.width - 300, self.height - 300),  # Top right corridor
            (900, 300),                    # Right center corridor
            (450, 200),                    # Bottom center
            (self.width - 100, 450),      # Right side
            (150, 450),                    # Left side
        ]
        
        # Return requested number of spawns
        return spawn_points[:num_enemies]
    
    def get_enemy_patrol_routes(self, enemy_index: int) -> List[Tuple[float, float]]:
        """
        Get patrol waypoints for a specific enemy in the maze.
        
        Args:
            enemy_index: Index of the enemy (0-based)
        
        Returns:
            List of (x, y) waypoints for patrol route
        """
        # Define patrol routes for each enemy in the maze corridors
        patrol_routes = [
            # Enemy 0: Top left corridor (L-shaped patrol)
            [
                (280, self.height - 150),
                (280, self.height - 280),
                (350, self.height - 280),
                (350, self.height - 150),
            ],
            
            # Enemy 1: Top center area
            [
                (600, self.height - 300),
                (800, self.height - 300),
                (800, self.height - 400),
                (600, self.height - 400),
            ],
            
            # Enemy 2: Top right corridor
            [
                (self.width - 300, self.height - 250),
                (self.width - 120, self.height - 250),
                (self.width - 120, self.height - 400),
                (self.width - 300, self.height - 400),
            ],
            
            # Enemy 3: Right center (vertical patrol)
            [
                (900, 250),
                (900, 350),
                (800, 350),
                (800, 250),
            ],
            
            # Enemy 4: Bottom center
            [
                (400, 150),
                (600, 150),
                (600, 250),
                (400, 250),
            ],
            
            # Enemy 5: Right side corridor
            [
                (self.width - 100, 400),
                (self.width - 100, 500),
                (self.width - 180, 500),
                (self.width - 180, 400),
            ],
            
            # Enemy 6: Left side corridor
            [
                (120, 400),
                (180, 400),
                (180, 480),
                (120, 480),
            ],
        ]
        
        # Return patrol route for this enemy (or default if out of range)
        if enemy_index < len(patrol_routes):
            return patrol_routes[enemy_index]
        else:
            # Default patrol (small square)
            spawn = self.get_enemy_spawns(enemy_index + 1)[enemy_index]
            return [
                (spawn[0] - 50, spawn[1] - 50),
                (spawn[0] + 50, spawn[1] - 50),
                (spawn[0] + 50, spawn[1] + 50),
                (spawn[0] - 50, spawn[1] + 50),
            ]


def get_apartment_layout() -> ApartmentLayout:
    """Get the apartment layout instance."""
    return ApartmentLayout()

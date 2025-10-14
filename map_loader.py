"""
JSON Map Loader for tile-based stealth game
"""
import json
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass


@dataclass
class GuardData:
    """Guard configuration from JSON"""
    pos: Tuple[int, int]
    patrol: List[Tuple[int, int]]
    fov_deg: float = 60.0
    range_tiles: float = 8.0
    speed: float = 1.0
    detection_time: float = 0.3


@dataclass
class ObjectiveData:
    """Objective marker"""
    pos: Tuple[int, int]
    collected: bool = False


@dataclass
class LightData:
    """Light source"""
    center: Tuple[int, int]
    radius: float


class MapData:
    """Parsed map data"""
    
    def __init__(self, json_path: str):
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        self.size = tuple(data['size'])  # (width, height)
        self.tiles = data['tiles']  # 2D array [row][col]
        self.player_start = tuple(data['player_start'])  # (x, y) in tile coords
        
        # Parse guards
        self.guards = []
        for g in data.get('guards', []):
            patrol_points = [tuple(p) for p in g['patrol']]
            guard = GuardData(
                pos=tuple(g['pos']),
                patrol=patrol_points,
                fov_deg=g.get('fov_deg', 60.0),
                range_tiles=g.get('range_tiles', 8.0),
                speed=g.get('speed', 1.0),
                detection_time=g.get('detection_time', 0.3)
            )
            self.guards.append(guard)
        
        # Parse objectives
        self.objectives = []
        for obj in data.get('objectives', []):
            self.objectives.append(ObjectiveData(pos=tuple(obj['pos'])))
        
        # Parse hide spots
        self.hide_spots = [tuple(spot) for spot in data.get('hide_spots', [])]
        
        # Parse lights
        self.lights = []
        for light in data.get('lights', []):
            self.lights.append(LightData(
                center=tuple(light['center']),
                radius=light['radius']
            ))
    
    def get_tile(self, x: int, y: int) -> str:
        """Get tile at grid position (x, y)"""
        if 0 <= y < len(self.tiles) and 0 <= x < len(self.tiles[0]):
            return self.tiles[y][x]
        return 'W'  # Out of bounds = wall
    
    def is_wall(self, x: int, y: int) -> bool:
        """Check if position is a wall"""
        return self.get_tile(x, y) == 'W'
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if position is walkable"""
        return not self.is_wall(x, y)
    
    def tile_to_world(self, tile_x: int, tile_y: int, tile_size: int = 64) -> Tuple[float, float]:
        """Convert tile coordinates to world pixel coordinates (center of tile)"""
        world_x = tile_x * tile_size + tile_size / 2
        world_y = tile_y * tile_size + tile_size / 2
        return (world_x, world_y)
    
    def world_to_tile(self, world_x: float, world_y: float, tile_size: int = 64) -> Tuple[int, int]:
        """Convert world pixel coordinates to tile coordinates"""
        tile_x = int(world_x / tile_size)
        tile_y = int(world_y / tile_size)
        return (tile_x, tile_y)


def load_map(json_path: str) -> MapData:
    """Load and parse a JSON map file"""
    return MapData(json_path)


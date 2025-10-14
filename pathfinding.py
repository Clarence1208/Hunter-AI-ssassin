"""
A* Pathfinding for Hunter Assassin game
Finds optimal path through tile-based maze
"""
import math
from typing import List, Tuple, Optional, Set
import heapq


class Node:
    """Node for A* pathfinding"""
    def __init__(self, x: int, y: int, g: float = 0, h: float = 0, parent: Optional['Node'] = None):
        self.x = x
        self.y = y
        self.g = g  # Cost from start
        self.h = h  # Heuristic to goal
        self.f = g + h  # Total cost
        self.parent = parent
    
    def __lt__(self, other):
        return self.f < other.f
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))


def heuristic(x1: int, y1: int, x2: int, y2: int) -> float:
    """Manhattan distance heuristic"""
    return abs(x2 - x1) + abs(y2 - y1)


def world_to_grid(world_x: float, world_y: float, tile_size: int) -> Tuple[int, int]:
    """Convert world coordinates to grid coordinates"""
    grid_x = int(world_x / tile_size)
    grid_y = int(world_y / tile_size)
    return (grid_x, grid_y)


def grid_to_world(grid_x: int, grid_y: int, tile_size: int) -> Tuple[float, float]:
    """Convert grid coordinates to world center of tile"""
    world_x = grid_x * tile_size + tile_size / 2
    world_y = grid_y * tile_size + tile_size / 2
    return (world_x, world_y)


def is_walkable_grid(grid_x: int, grid_y: int, obstacles: List, tile_size: int, player_radius: float) -> bool:
    """
    Check if a grid position is walkable (no obstacles).
    Takes into account the player's size by checking multiple points around the tile center.
    
    Args:
        grid_x, grid_y: Grid coordinates
        obstacles: List of Obstacle sprites
        tile_size: Size of each tile in pixels
        player_radius: Radius of the player character
    """
    # Convert grid to world coordinates (center of tile)
    world_x, world_y = grid_to_world(grid_x, grid_y, tile_size)
    
    # Use player's actual radius plus a buffer for safety
    check_radius = player_radius + 4  # 4px buffer to prevent tight squeezes
    
    # Check multiple points around the player's body to ensure the whole body fits
    # Check center + 8 points around the perimeter at player's radius
    check_points = [
        (world_x, world_y),  # Center
        (world_x + check_radius, world_y),  # Right
        (world_x - check_radius, world_y),  # Left
        (world_x, world_y + check_radius),  # Top
        (world_x, world_y - check_radius),  # Bottom
        (world_x + check_radius * 0.707, world_y + check_radius * 0.707),  # Top-right
        (world_x - check_radius * 0.707, world_y + check_radius * 0.707),  # Top-left
        (world_x + check_radius * 0.707, world_y - check_radius * 0.707),  # Bottom-right
        (world_x - check_radius * 0.707, world_y - check_radius * 0.707),  # Bottom-left
    ]
    
    # Check if any point of the player's body would collide with obstacles
    for check_x, check_y in check_points:
        for obstacle in obstacles:
            # Check if this point is inside the obstacle
            if (obstacle.left <= check_x <= obstacle.right and
                obstacle.bottom <= check_y <= obstacle.top):
                return False
    
    return True


def get_neighbors(x: int, y: int, grid_width: int, grid_height: int, 
                  obstacles: List = None, tile_size: int = None, 
                  player_radius: float = None) -> List[Tuple[int, int, float]]:
    """
    Get walkable neighbors for a grid position.
    Returns list of (x, y, cost) tuples.
    Includes diagonal movement with proper collision checking.
    
    For diagonal moves, both adjacent cardinal tiles must be walkable
    to prevent cutting corners through walls.
    """
    neighbors = []
    
    # Cardinal directions (always allowed if in bounds and walkable)
    cardinal_directions = [
        (0, 1, 1.0),    # Up
        (0, -1, 1.0),   # Down
        (1, 0, 1.0),    # Right
        (-1, 0, 1.0),   # Left
    ]
    
    # Diagonal directions (need both adjacent cardinals to be walkable)
    diagonal_directions = [
        (1, 1, 1.4, [(1, 0), (0, 1)]),      # Up-Right (needs Right and Up)
        (1, -1, 1.4, [(1, 0), (0, -1)]),    # Down-Right (needs Right and Down)
        (-1, 1, 1.4, [(-1, 0), (0, 1)]),    # Up-Left (needs Left and Up)
        (-1, -1, 1.4, [(-1, 0), (0, -1)]),  # Down-Left (needs Left and Down)
    ]
    
    # Check cardinal directions
    walkable_cardinals = set()
    for dx, dy, cost in cardinal_directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid_width and 0 <= ny < grid_height:
            neighbors.append((nx, ny, cost))
            walkable_cardinals.add((dx, dy))
    
    # Check diagonal directions (only if adjacent cardinals are walkable)
    if obstacles is not None and tile_size is not None and player_radius is not None:
        for dx, dy, cost, required_cardinals in diagonal_directions:
            nx, ny = x + dx, y + dy
            
            # Check bounds
            if not (0 <= nx < grid_width and 0 <= ny < grid_height):
                continue
            
            # Check if both adjacent cardinal directions are walkable
            both_cardinals_walkable = all(
                (cdx, cdy) in walkable_cardinals and
                is_walkable_grid(x + cdx, y + cdy, obstacles, tile_size, player_radius)
                for cdx, cdy in required_cardinals
            )
            
            if both_cardinals_walkable:
                neighbors.append((nx, ny, cost))
    else:
        # Fallback: allow all diagonal moves (for backward compatibility)
        for dx, dy, cost, _ in diagonal_directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_width and 0 <= ny < grid_height:
                neighbors.append((nx, ny, cost))
    
    return neighbors


def find_path(start_x: float, start_y: float, 
              goal_x: float, goal_y: float,
              obstacles: List, 
              tile_size: int,
              grid_width: int, 
              grid_height: int,
              player_radius: float,
              max_distance: Optional[float] = None) -> Optional[List[Tuple[float, float]]]:
    """
    Find path from start to goal using A* algorithm.
    
    Args:
        start_x, start_y: Starting world coordinates
        goal_x, goal_y: Goal world coordinates
        obstacles: List of obstacle sprites
        tile_size: Size of each tile in pixels
        grid_width, grid_height: Grid dimensions
        player_radius: Radius of the player character
        max_distance: Optional maximum path length (in tiles)
    
    Returns:
        List of (world_x, world_y) waypoints, or None if no path found
    """
    # Convert to grid coordinates
    start_grid = world_to_grid(start_x, start_y, tile_size)
    goal_grid = world_to_grid(goal_x, goal_y, tile_size)
    
    # Check if start and goal are valid
    if not is_walkable_grid(start_grid[0], start_grid[1], obstacles, tile_size, player_radius):
        return None
    
    if not is_walkable_grid(goal_grid[0], goal_grid[1], obstacles, tile_size, player_radius):
        # Try to find nearest walkable tile near goal
        goal_grid = find_nearest_walkable(goal_grid[0], goal_grid[1], obstacles, tile_size, 
                                         grid_width, grid_height, player_radius)
        if goal_grid is None:
            return None
    
    # A* algorithm
    open_set = []
    start_node = Node(start_grid[0], start_grid[1], 0, 
                     heuristic(start_grid[0], start_grid[1], goal_grid[0], goal_grid[1]))
    heapq.heappush(open_set, start_node)
    
    closed_set: Set[Tuple[int, int]] = set()
    g_scores = {(start_grid[0], start_grid[1]): 0}
    
    while open_set:
        current = heapq.heappop(open_set)
        
        # Reached goal
        if current.x == goal_grid[0] and current.y == goal_grid[1]:
            # Reconstruct path
            path = []
            node = current
            while node is not None:
                world_pos = grid_to_world(node.x, node.y, tile_size)
                path.append(world_pos)
                node = node.parent
            path.reverse()
            
            # Simplify path (remove unnecessary waypoints)
            path = simplify_path(path, obstacles, tile_size)
            
            return path
        
        closed_set.add((current.x, current.y))
        
        # Check neighbors (pass obstacles and player_radius for diagonal blocking)
        for nx, ny, move_cost in get_neighbors(current.x, current.y, grid_width, grid_height,
                                               obstacles, tile_size, player_radius):
            if (nx, ny) in closed_set:
                continue
            
            # Check if walkable
            if not is_walkable_grid(nx, ny, obstacles, tile_size, player_radius):
                continue
            
            # Calculate costs
            tentative_g = current.g + move_cost
            
            # Optional: distance limit
            if max_distance and tentative_g > max_distance:
                continue
            
            # Check if this path is better
            if (nx, ny) not in g_scores or tentative_g < g_scores[(nx, ny)]:
                g_scores[(nx, ny)] = tentative_g
                h = heuristic(nx, ny, goal_grid[0], goal_grid[1])
                neighbor = Node(nx, ny, tentative_g, h, current)
                heapq.heappush(open_set, neighbor)
    
    # No path found
    return None


def find_nearest_walkable(x: int, y: int, obstacles: List, tile_size: int,
                          grid_width: int, grid_height: int, player_radius: float,
                          max_radius: int = 5) -> Optional[Tuple[int, int]]:
    """Find nearest walkable tile to given position"""
    for radius in range(1, max_radius + 1):
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if abs(dx) == radius or abs(dy) == radius:  # Check perimeter only
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < grid_width and 0 <= ny < grid_height:
                        if is_walkable_grid(nx, ny, obstacles, tile_size, player_radius):
                            return (nx, ny)
    return None


def simplify_path(path: List[Tuple[float, float]], obstacles: List, tile_size: int) -> List[Tuple[float, float]]:
    """
    Simplify path by removing unnecessary waypoints.
    Uses line-of-sight checks to skip intermediate points.
    """
    if len(path) <= 2:
        return path
    
    simplified = [path[0]]
    current_idx = 0
    
    while current_idx < len(path) - 1:
        # Try to skip as many waypoints as possible
        furthest_idx = current_idx + 1
        
        for test_idx in range(current_idx + 2, len(path)):
            if has_clear_path(path[current_idx], path[test_idx], obstacles, tile_size):
                furthest_idx = test_idx
            else:
                break
        
        simplified.append(path[furthest_idx])
        current_idx = furthest_idx
    
    return simplified


def has_clear_path(start: Tuple[float, float], end: Tuple[float, float], 
                   obstacles: List, tile_size: int) -> bool:
    """
    Check if there's a clear straight line between two points.
    Samples points along the line and checks for obstacles.
    """
    x1, y1 = start
    x2, y2 = end
    
    # Calculate number of samples based on distance
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    num_samples = int(distance / (tile_size / 2)) + 1
    
    for i in range(num_samples + 1):
        t = i / max(num_samples, 1)
        test_x = x1 + (x2 - x1) * t
        test_y = y1 + (y2 - y1) * t
        
        # Check if this point is in an obstacle
        radius = tile_size / 4
        for obstacle in obstacles:
            if (obstacle.left - radius <= test_x <= obstacle.right + radius and
                obstacle.bottom - radius <= test_y <= obstacle.top + radius):
                return False
    
    return True

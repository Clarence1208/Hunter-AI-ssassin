"""
Utility functions for ray casting, collision detection, and game mechanics
"""
import math
import arcade
from typing import List, Tuple, Optional


def cast_ray(start_x: float, start_y: float, angle: float, max_distance: float, 
             obstacles: List['Obstacle']) -> Tuple[float, Optional['Obstacle']]:
    """
    Cast a ray from start position at given angle and find the first intersection.
    
    Args:
        start_x, start_y: Starting position
        angle: Angle in degrees
        max_distance: Maximum ray distance
        obstacles: List of obstacles to check collision
    
    Returns:
        Tuple of (distance, obstacle) where obstacle is None if no hit
    """
    angle_rad = math.radians(angle)
    end_x = start_x + math.cos(angle_rad) * max_distance
    end_y = start_y + math.sin(angle_rad) * max_distance
    
    closest_distance = max_distance
    hit_obstacle = None
    
    for obstacle in obstacles:
        intersection = line_rectangle_intersection(
            start_x, start_y, end_x, end_y,
            obstacle.center_x, obstacle.center_y,
            obstacle.width, obstacle.height
        )
        
        if intersection:
            dist = math.sqrt((intersection[0] - start_x)**2 + (intersection[1] - start_y)**2)
            if dist < closest_distance:
                closest_distance = dist
                hit_obstacle = obstacle
    
    return closest_distance, hit_obstacle


def line_rectangle_intersection(x1: float, y1: float, x2: float, y2: float,
                                rect_x: float, rect_y: float, 
                                rect_width: float, rect_height: float) -> Optional[Tuple[float, float]]:
    """
    Check if a line segment intersects with a rectangle and return the intersection point.
    
    Args:
        x1, y1: Line start
        x2, y2: Line end
        rect_x, rect_y: Rectangle center
        rect_width, rect_height: Rectangle dimensions
    
    Returns:
        Closest intersection point (x, y) or None
    """
    # Rectangle edges
    left = rect_x - rect_width / 2
    right = rect_x + rect_width / 2
    bottom = rect_y - rect_height / 2
    top = rect_y + rect_height / 2
    
    # Check intersection with all four edges
    intersections = []
    
    # Top edge
    point = line_segment_intersection(x1, y1, x2, y2, left, top, right, top)
    if point:
        intersections.append(point)
    
    # Bottom edge
    point = line_segment_intersection(x1, y1, x2, y2, left, bottom, right, bottom)
    if point:
        intersections.append(point)
    
    # Left edge
    point = line_segment_intersection(x1, y1, x2, y2, left, bottom, left, top)
    if point:
        intersections.append(point)
    
    # Right edge
    point = line_segment_intersection(x1, y1, x2, y2, right, bottom, right, top)
    if point:
        intersections.append(point)
    
    if not intersections:
        return None
    
    # Return closest intersection
    closest = min(intersections, key=lambda p: (p[0] - x1)**2 + (p[1] - y1)**2)
    return closest


def line_segment_intersection(x1: float, y1: float, x2: float, y2: float,
                              x3: float, y3: float, x4: float, y4: float) -> Optional[Tuple[float, float]]:
    """
    Find intersection point between two line segments.
    
    Returns:
        Intersection point (x, y) or None if no intersection
    """
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    
    if abs(denom) < 1e-10:  # Parallel lines
        return None
    
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    
    if 0 <= t <= 1 and 0 <= u <= 1:
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return (x, y)
    
    return None


def has_line_of_sight(x1: float, y1: float, x2: float, y2: float,
                      obstacles: List['Obstacle']) -> bool:
    """
    Check if there's a clear line of sight between two points.
    
    Args:
        x1, y1: First point
        x2, y2: Second point
        obstacles: List of obstacles that block sight
    
    Returns:
        True if line of sight is clear, False otherwise
    """
    for obstacle in obstacles:
        if line_rectangle_intersection(x1, y1, x2, y2,
                                      obstacle.center_x, obstacle.center_y,
                                      obstacle.width, obstacle.height):
            return False
    return True


def get_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def get_angle_to_point(from_x: float, from_y: float, to_x: float, to_y: float) -> float:
    """
    Get angle in degrees from one point to another.
    
    Returns:
        Angle in degrees (0-360)
    """
    angle = math.degrees(math.atan2(to_y - from_y, to_x - from_x))
    return angle


def normalize_angle(angle: float) -> float:
    """Normalize angle to 0-360 range."""
    while angle < 0:
        angle += 360
    while angle >= 360:
        angle -= 360
    return angle


def angle_difference(angle1: float, angle2: float) -> float:
    """
    Calculate the smallest difference between two angles.
    
    Returns:
        Difference in degrees (-180 to 180)
    """
    diff = angle2 - angle1
    while diff > 180:
        diff -= 360
    while diff < -180:
        diff += 360
    return diff


def is_point_in_cone(point_x: float, point_y: float, 
                     cone_x: float, cone_y: float,
                     cone_angle: float, cone_fov: float, 
                     max_distance: float) -> bool:
    """
    Check if a point is within a cone of vision.
    
    Args:
        point_x, point_y: Point to check
        cone_x, cone_y: Cone origin
        cone_angle: Direction the cone is facing (degrees)
        cone_fov: Field of view angle (degrees)
        max_distance: Maximum vision distance
    
    Returns:
        True if point is in cone
    """
    distance = get_distance(cone_x, cone_y, point_x, point_y)
    if distance > max_distance:
        return False
    
    angle_to_point = get_angle_to_point(cone_x, cone_y, point_x, point_y)
    angle_diff = abs(angle_difference(cone_angle, angle_to_point))
    
    return angle_diff <= cone_fov / 2


def check_collision_circles(x1: float, y1: float, r1: float,
                           x2: float, y2: float, r2: float) -> bool:
    """Check collision between two circles."""
    distance = get_distance(x1, y1, x2, y2)
    return distance < (r1 + r2)

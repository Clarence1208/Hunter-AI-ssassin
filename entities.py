"""
Game entity classes: Player, Enemy, Obstacle, and Bullet
"""
import arcade
import random
import math
from typing import List, Tuple, Optional
import config
from utils import (has_line_of_sight, get_distance, get_angle_to_point, 
                   is_point_in_cone, check_collision_circles, cast_ray)
from pathfinding import find_path
from player_animation import AnimatedPlayerSprite


class Obstacle(arcade.SpriteSolidColor):
    """Represents a wall/obstacle in the game."""
    
    def __init__(self, x: float, y: float, width: float, height: float, color=None):
        if color is None:
            color = config.OBSTACLE_COLOR
        super().__init__(int(width), int(height), color)
        self.center_x = x
        self.center_y = y
        self.width = width
        self.height = height
        self.custom_color = color
    
    def draw_colored(self):
        """Draw the obstacle as a colored rectangle with subtle border."""
        # Draw main filled rectangle
        arcade.draw_lrbt_rectangle_filled(
            self.center_x - self.width / 2,  # left
            self.center_x + self.width / 2,  # right
            self.center_y - self.height / 2, # bottom
            self.center_y + self.height / 2, # top
            self.custom_color
        )
        
        # Draw subtle border for depth
        border_color = tuple(max(0, c - 20) for c in self.custom_color[:3])
        arcade.draw_lrbt_rectangle_outline(
            self.center_x - self.width / 2,
            self.center_x + self.width / 2,
            self.center_y - self.height / 2,
            self.center_y + self.height / 2,
            border_color, 2
        )


class Bullet:
    """
    Bullet/projectile fired by enemies.
    """
    
    def __init__(self, x: float, y: float, angle: float, shooter_id: int):
        self.center_x = x
        self.center_y = y
        self.angle = angle  # Direction in degrees
        self.speed = config.BULLET_SPEED
        self.radius = config.BULLET_SIZE
        self.color = config.BULLET_COLOR
        self.lifetime = config.BULLET_LIFETIME
        self.age = 0
        self.active = True
        self.shooter_id = shooter_id  # ID of enemy that shot this
        
        # Calculate velocity
        angle_rad = math.radians(angle)
        self.velocity_x = math.cos(angle_rad) * self.speed
        self.velocity_y = math.sin(angle_rad) * self.speed
    
    def update(self, obstacles: List['Obstacle']) -> bool:
        """
        Update bullet position and check for collisions.
        
        Returns:
            True if bullet should be removed
        """
        if not self.active:
            return True
        
        self.age += 1
        if self.age >= self.lifetime:
            self.active = False
            return True
        
        # Move bullet
        new_x = self.center_x + self.velocity_x
        new_y = self.center_y + self.velocity_y
        
        # Check screen boundaries
        if (new_x < 0 or new_x > config.SCREEN_WIDTH or 
            new_y < 0 or new_y > config.SCREEN_HEIGHT):
            self.active = False
            return True
        
        # Check obstacle collisions
        for obstacle in obstacles:
            closest_x = max(obstacle.left, min(new_x, obstacle.right))
            closest_y = max(obstacle.bottom, min(new_y, obstacle.top))
            
            dist = get_distance(new_x, new_y, closest_x, closest_y)
            if dist < self.radius:
                self.active = False
                return True
        
        self.center_x = new_x
        self.center_y = new_y
        return False
    
    def check_hit_player(self, player: 'Player') -> bool:
        """Check if bullet hit the player."""
        if not self.active or not player.alive:
            return False
        
        distance = get_distance(self.center_x, self.center_y,
                               player.center_x, player.center_y)
        return distance < (self.radius + player.radius)
    
    def draw_colored(self):
        """Draw the bullet."""
        if self.active:
            # Draw bullet as a circle with a trail
            arcade.draw_circle_filled(
                self.center_x, self.center_y,
                self.radius,
                self.color
            )
            
            # Draw motion trail
            trail_length = 10
            trail_x = self.center_x - self.velocity_x / self.speed * trail_length
            trail_y = self.center_y - self.velocity_y / self.speed * trail_length
            arcade.draw_line(
                self.center_x, self.center_y,
                trail_x, trail_y,
                (*self.color[:3], 100), 2
            )


class Player(arcade.SpriteSolidColor):
    """
    Player character controlled by user or RL agent.
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(config.PLAYER_SIZE * 2, config.PLAYER_SIZE * 2, config.PLAYER_COLOR)
        self.center_x = x
        self.center_y = y
        self.radius = config.PLAYER_SIZE
        self.speed = config.PLAYER_MOVEMENT_SPEED
        self.alive = True
        self.kills = 0
        
        # Animated sprite for visual representation
        self.animated_sprite = AnimatedPlayerSprite(x, y)
        
        # Attack state
        self.is_attacking = False
        self.attack_target = None
        self.damage_dealt = False  # Track if damage was dealt in current attack
        
        # Movement tracking for animation
        self.last_move_dx = 0
        self.last_move_dy = 0
        
        # Point-and-click movement with pathfinding
        self.target_position = None  # Final destination (x, y) or None
        self.path_waypoints = []  # List of waypoints to follow
        self.current_waypoint_idx = 0  # Index of current waypoint
        self.movement_threshold = 8.0  # Stop when within 8 pixels of waypoint
        
    def set_target(self, target_x: float, target_y: float, obstacles: List[Obstacle], 
                   grid_width: int, grid_height: int, tile_size: int):
        """
        Set target position and calculate path using A* pathfinding.
        
        Args:
            target_x, target_y: Desired destination in world coordinates
            obstacles: List of obstacles to avoid
            grid_width, grid_height: Grid dimensions
            tile_size: Size of each tile
        """
        self.target_position = (target_x, target_y)
        
        # Calculate path using A* with player's radius
        path = find_path(
            self.center_x, self.center_y,
            target_x, target_y,
            obstacles, tile_size,
            grid_width, grid_height,
            self.radius  # Pass player radius for collision checking
        )
        
        if path:
            self.path_waypoints = path
            self.current_waypoint_idx = 0
        else:
            # No path found, clear target
            self.target_position = None
            self.path_waypoints = []
            self.current_waypoint_idx = 0
    
    def clear_target(self):
        """Clear movement target and path."""
        self.target_position = None
        self.path_waypoints = []
        self.current_waypoint_idx = 0
    
    def update_movement(self, obstacles: List[Obstacle], screen_width: float, screen_height: float):
        """
        Update pathfinding-based movement toward target.
        Follows waypoints from A* pathfinding algorithm.
        Called each frame to move player along calculated path.
        """
        if not self.alive or not self.path_waypoints or self.is_attacking:
            # Update animation even if not moving
            if not self.is_attacking:
                self.animated_sprite.update_animation(0, 0)
            return
        
        # Get current waypoint
        if self.current_waypoint_idx >= len(self.path_waypoints):
            # Reached end of path
            self.clear_target()
            self.animated_sprite.update_animation(0, 0)
            return
        
        waypoint_x, waypoint_y = self.path_waypoints[self.current_waypoint_idx]
        
        # Calculate distance to current waypoint
        distance = get_distance(self.center_x, self.center_y, waypoint_x, waypoint_y)
        
        # If close enough to waypoint, move to next one
        if distance < self.movement_threshold:
            self.current_waypoint_idx += 1
            if self.current_waypoint_idx >= len(self.path_waypoints):
                # Reached final destination
                self.clear_target()
                self.animated_sprite.update_animation(0, 0)
                return
            waypoint_x, waypoint_y = self.path_waypoints[self.current_waypoint_idx]
            distance = get_distance(self.center_x, self.center_y, waypoint_x, waypoint_y)
        
        # Calculate direction vector toward waypoint
        dx = waypoint_x - self.center_x
        dy = waypoint_y - self.center_y
        
        # Normalize and scale by speed
        magnitude = math.sqrt(dx * dx + dy * dy)
        norm_dx = 0
        norm_dy = 0
        if magnitude > 0:
            norm_dx = dx / magnitude
            norm_dy = dy / magnitude
            dx = norm_dx * self.speed
            dy = norm_dy * self.speed
        
        # Calculate new position
        new_x = self.center_x + dx
        new_y = self.center_y + dy
        
        # Check screen boundaries
        new_x = max(self.radius, min(screen_width - self.radius, new_x))
        new_y = max(self.radius, min(screen_height - self.radius, new_y))
        
        # Check obstacle collisions
        collision = False
        for obstacle in obstacles:
            closest_x = max(obstacle.left, min(new_x, obstacle.right))
            closest_y = max(obstacle.bottom, min(new_y, obstacle.top))
            
            dist = get_distance(new_x, new_y, closest_x, closest_y)
            if dist < self.radius + 2:  # Small buffer
                collision = True
                break
        
        if not collision:
            # Move to new position
            self.center_x = new_x
            self.center_y = new_y
            # Update animated sprite
            self.animated_sprite.center_x = new_x
            self.animated_sprite.center_y = new_y
            # Update animation with normalized direction
            self.animated_sprite.update_animation(norm_dx, norm_dy)
        else:
            # Path is blocked, try to recalculate
            # For now, just clear target (player can click again)
            self.clear_target()
            self.animated_sprite.update_animation(0, 0)
    
    def move(self, dx: float, dy: float, obstacles: List[Obstacle], 
             screen_width: float, screen_height: float) -> bool:
        """
        Move player with arrow keys (overrides point-and-click).
        
        Args:
            dx, dy: Movement direction (-1, 0, 1)
            obstacles: List of obstacles to check collision
            screen_width, screen_height: Screen boundaries
        
        Returns:
            True if movement was successful
        """
        if not self.alive or self.is_attacking:
            return False
        
        # Arrow key movement cancels point-and-click target
        if dx != 0 or dy != 0:
            self.target_position = None
        
        # Track movement for animation
        self.last_move_dx = dx
        self.last_move_dy = dy
        
        # Calculate new position
        new_x = self.center_x + dx * self.speed
        new_y = self.center_y + dy * self.speed
        
        # Check screen boundaries
        new_x = max(self.radius, min(screen_width - self.radius, new_x))
        new_y = max(self.radius, min(screen_height - self.radius, new_y))
        
        # Check obstacle collisions
        collision = False
        for obstacle in obstacles:
            # Simple AABB collision check with circle
            closest_x = max(obstacle.left, min(new_x, obstacle.right))
            closest_y = max(obstacle.bottom, min(new_y, obstacle.top))
            
            dist = get_distance(new_x, new_y, closest_x, closest_y)
            if dist < self.radius:
                collision = True
                break
        
        if not collision:
            self.center_x = new_x
            self.center_y = new_y
            # Update animated sprite position
            self.animated_sprite.center_x = new_x
            self.animated_sprite.center_y = new_y
            # Update animation with movement direction
            self.animated_sprite.update_animation(dx, dy)
            return True
        else:
            # Still update animation even if blocked
            self.animated_sprite.update_animation(0, 0)
        
        return False
    
    def can_attack(self, enemy: 'Enemy') -> bool:
        """Check if player is close enough to attack enemy."""
        if not self.alive or not enemy.alive or self.is_attacking:
            return False
        distance = get_distance(self.center_x, self.center_y, 
                               enemy.center_x, enemy.center_y)
        attack_range = getattr(config, 'PLAYER_MELEE_RANGE', getattr(config, 'PLAYER_ATTACK_RANGE', 30))
        return distance < attack_range
    
    def start_attack(self, enemy: 'Enemy'):
        """
        Start an attack animation against an enemy.
        
        Args:
            enemy: The enemy being attacked
        """
        if not self.alive or not enemy.alive or self.is_attacking:
            return
        
        self.is_attacking = True
        self.attack_target = enemy
        self.damage_dealt = False
        
        # Start the attack animation on the sprite
        self.animated_sprite.start_attack_animation(enemy)
    
    def update_attack(self) -> bool:
        """
        Update attack state. Called each frame.
        
        Returns:
            True if damage should be dealt this frame, False otherwise
        """
        if not self.is_attacking:
            return False
        
        # Update the attack animation frames
        self.animated_sprite.update_animation(0, 0)
        
        # Check if we should deal damage
        if not self.damage_dealt and self.animated_sprite.should_deal_damage():
            self.damage_dealt = True
            return True
        
        # Check if attack animation is complete
        if not self.animated_sprite.is_attacking():
            self.is_attacking = False
            self.attack_target = None
            self.damage_dealt = False
        
        return False
    
    def die(self):
        """Kill the player."""
        self.alive = False
        self.color = (100, 100, 100)  # Gray when dead
    
    def draw_colored(self):
        """Draw the player using animated sprite."""
        if self.alive:
            # Draw the animated sprite using arcade's texture drawing
            if self.animated_sprite.texture:
                # Use the sprite's width and height properties (which include scale)
                width = self.animated_sprite.width
                height = self.animated_sprite.height
                half_width = width / 2
                half_height = height / 2
                
                # Create a Rect for the sprite position
                rect = arcade.LRBT(
                    left=self.animated_sprite.center_x - half_width,
                    right=self.animated_sprite.center_x + half_width,
                    bottom=self.animated_sprite.center_y - half_height,
                    top=self.animated_sprite.center_y + half_height
                )
                
                # Draw the texture
                arcade.draw_texture_rect(
                    texture=self.animated_sprite.texture,
                    rect=rect,
                    angle=self.animated_sprite.angle
                )
        else:
            # Draw gray circle when dead
            arcade.draw_circle_filled(
                self.center_x, self.center_y,
                self.radius,
                (100, 100, 100)
            )


class Enemy(arcade.SpriteSolidColor):
    """
    Enemy AI with patrol and chase behavior, using ray casting for vision.
    """
    
    def __init__(self, x: float, y: float, patrol_points: Optional[List[Tuple[float, float]]] = None):
        # Use GUARD config if available, fall back to ENEMY for compatibility
        size = getattr(config, 'GUARD_SIZE', getattr(config, 'ENEMY_SIZE', 20))
        color = getattr(config, 'GUARD_COLOR', getattr(config, 'ENEMY_COLOR', (255, 50, 50)))
        
        super().__init__(size * 2, size * 2, color)
        self.center_x = x
        self.center_y = y
        self.radius = size
        self.speed = getattr(config, 'GUARD_MOVEMENT_SPEED', getattr(config, 'ENEMY_MOVEMENT_SPEED', 1.0))
        self.chase_speed = getattr(config, 'GUARD_CHASE_SPEED', getattr(config, 'ENEMY_CHASE_SPEED', 1.5))
        self.alive = True
        
        # Vision properties
        self.vision_range = getattr(config, 'GUARD_VISION_RANGE', getattr(config, 'ENEMY_VISION_RANGE', 200))
        self.vision_angle = 0  # Direction enemy is facing
        self.fov = getattr(config, 'GUARD_VISION_ANGLE', getattr(config, 'ENEMY_VISION_ANGLE', 60))
        self.can_see_player = False
        
        # AI state
        self.state = "patrol"  # patrol, chase, alert
        self.patrol_points = patrol_points if patrol_points else []
        self.current_patrol_index = 0
        self.patrol_pause_counter = 0
        self.last_known_player_pos = None
        
        # Alert state
        self.alert_timer = 0
        self.alert_duration = 180  # Frames to stay alert
        
        # Shooting
        self.shoot_cooldown = 0
        self.shoot_delay_timer = 0  # Delay before shooting when first seeing player
        self.is_shooting = False
        
        # Pathfinding (like player)
        self.target_position = None  # Current navigation target
        self.path_waypoints = []  # Waypoints from A* pathfinding
        self.current_waypoint_idx = 0
        self.movement_threshold = 8.0  # Distance to consider waypoint reached
        self.path_recalc_timer = 0  # Timer to avoid recalculating path every frame
        
    def update_ai(self, player: Player, obstacles: List[Obstacle], delta_time: float = 1.0,
                  grid_width: int = 16, grid_height: int = 16, tile_size: int = 50) -> Optional[Bullet]:
        """
        Update enemy AI behavior.
        
        Args:
            player: Player entity
            obstacles: List of obstacles
            delta_time: Time multiplier for speed
            grid_width, grid_height: Grid dimensions for pathfinding
            tile_size: Tile size for pathfinding
        
        Returns:
            Bullet object if enemy shoots, None otherwise
        """
        if not self.alive:
            return None
        
        # Update cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Check if can see player
        self.can_see_player = self._check_player_vision(player, obstacles)
        
        bullet = None
        if self.can_see_player:
            self.state = "chase"
            self.last_known_player_pos = (player.center_x, player.center_y)
            self.alert_timer = self.alert_duration
            self.color = getattr(config, 'GUARD_ALERT_COLOR', getattr(config, 'ENEMY_ALERT_COLOR', (255, 150, 0)))
            
            # Handle shooting
            delay = getattr(config, 'ENEMY_SHOOT_DELAY', 30)
            if self.shoot_delay_timer < delay:
                self.shoot_delay_timer += 1
            elif self.shoot_cooldown == 0:
                # Shoot at player
                bullet = self._shoot_at_player(player)
                cooldown = getattr(config, 'ENEMY_SHOOT_COOLDOWN', 60)
                self.shoot_cooldown = cooldown
                self.is_shooting = True
        else:
            # Reset shoot delay when losing sight of player
            self.shoot_delay_timer = 0
            self.is_shooting = False
            
            if self.alert_timer > 0:
                self.state = "alert"
                self.alert_timer -= 1
                self.color = getattr(config, 'GUARD_ALERT_COLOR', getattr(config, 'ENEMY_ALERT_COLOR', (255, 150, 0)))
            else:
                self.state = "patrol"
                color = getattr(config, 'GUARD_COLOR', getattr(config, 'ENEMY_COLOR', (255, 50, 50)))
                self.color = color
        
        # Update path recalc timer
        if self.path_recalc_timer > 0:
            self.path_recalc_timer -= 1
        
        # Execute behavior based on state
        if self.state == "chase":
            self._chase_player(player, obstacles, delta_time, grid_width, grid_height, tile_size)
        elif self.state == "alert" and self.last_known_player_pos:
            self._investigate_position(self.last_known_player_pos, obstacles, delta_time, 
                                      grid_width, grid_height, tile_size)
        else:
            self._patrol(obstacles, delta_time, grid_width, grid_height, tile_size)
        
        return bullet
    
    def _check_player_vision(self, player: Player, obstacles: List[Obstacle]) -> bool:
        """Check if enemy can see the player using ray casting."""
        if not player.alive:
            return False
        
        # Check if player is in vision cone
        in_cone = is_point_in_cone(
            player.center_x, player.center_y,
            self.center_x, self.center_y,
            self.vision_angle, self.fov, self.vision_range
        )
        
        if not in_cone:
            return False
        
        # Check line of sight (not blocked by obstacles)
        return has_line_of_sight(self.center_x, self.center_y,
                                player.center_x, player.center_y,
                                obstacles)
    
    def _shoot_at_player(self, player: Player) -> Bullet:
        """
        Create a bullet aimed at the player.
        
        Returns:
            Bullet object
        """
        # Calculate angle to player
        angle = get_angle_to_point(self.center_x, self.center_y,
                                   player.center_x, player.center_y)
        
        # Create bullet at enemy position
        bullet = Bullet(self.center_x, self.center_y, angle, id(self))
        return bullet
    
    def _set_pathfinding_target(self, target_x: float, target_y: float, obstacles: List[Obstacle],
                                grid_width: int, grid_height: int, tile_size: int):
        """
        Calculate A* path to target position.
        
        Args:
            target_x, target_y: Destination coordinates
            obstacles: List of obstacles to avoid
            grid_width, grid_height: Grid dimensions
            tile_size: Size of each tile
        """
        self.target_position = (target_x, target_y)
        
        # Calculate path using A*
        path = find_path(
            self.center_x, self.center_y,
            target_x, target_y,
            obstacles, tile_size,
            grid_width, grid_height,
            self.radius  # Enemy's radius for collision checking
        )
        
        if path:
            self.path_waypoints = path
            self.current_waypoint_idx = 0
        else:
            # No path found, clear everything
            self.target_position = None
            self.path_waypoints = []
            self.current_waypoint_idx = 0
    
    def _clear_path(self):
        """Clear current pathfinding target and waypoints."""
        self.target_position = None
        self.path_waypoints = []
        self.current_waypoint_idx = 0
    
    def _follow_path(self, speed_multiplier: float = 1.0) -> bool:
        """
        Follow current pathfinding waypoints.
        
        Args:
            speed_multiplier: Multiplier for movement speed
        
        Returns:
            True if reached destination, False if still moving
        """
        if not self.path_waypoints:
            return True
        
        # Get current waypoint
        if self.current_waypoint_idx >= len(self.path_waypoints):
            self._clear_path()
            return True
        
        waypoint_x, waypoint_y = self.path_waypoints[self.current_waypoint_idx]
        
        # Calculate distance to current waypoint
        distance = get_distance(self.center_x, self.center_y, waypoint_x, waypoint_y)
        
        # If close enough to waypoint, move to next one
        if distance < self.movement_threshold:
            self.current_waypoint_idx += 1
            if self.current_waypoint_idx >= len(self.path_waypoints):
                self._clear_path()
                return True
            waypoint_x, waypoint_y = self.path_waypoints[self.current_waypoint_idx]
        
        # Calculate angle to waypoint and update vision direction
        angle = get_angle_to_point(self.center_x, self.center_y, waypoint_x, waypoint_y)
        self.vision_angle = angle
        
        # Move toward waypoint
        angle_rad = math.radians(angle)
        move_speed = self.speed * speed_multiplier
        dx = math.cos(angle_rad) * move_speed
        dy = math.sin(angle_rad) * move_speed
        
        # Direct movement (pathfinding already avoids obstacles)
        self.center_x += dx
        self.center_y += dy
        
        return False
    
    def _chase_player(self, player: Player, obstacles: List[Obstacle], delta_time: float,
                     grid_width: int, grid_height: int, tile_size: int):
        """Chase the player using pathfinding."""
        # Recalculate path periodically or when target changed significantly
        should_recalc = False
        if self.path_recalc_timer == 0:
            should_recalc = True
            self.path_recalc_timer = 30  # Recalculate every 30 frames (about 0.5 seconds)
        
        # Also recalculate if target moved significantly
        if self.target_position:
            dist_to_old_target = get_distance(player.center_x, player.center_y,
                                              self.target_position[0], self.target_position[1])
            if dist_to_old_target > 30:  # Player moved more than 30 pixels
                should_recalc = True
        else:
            should_recalc = True
        
        if should_recalc:
            self._set_pathfinding_target(player.center_x, player.center_y, obstacles,
                                        grid_width, grid_height, tile_size)
        
        # Follow the path
        self._follow_path(self.chase_speed * delta_time)
    
    def _investigate_position(self, position: Tuple[float, float], 
                            obstacles: List[Obstacle], delta_time: float,
                            grid_width: int, grid_height: int, tile_size: int):
        """Move to last known player position using pathfinding."""
        target_x, target_y = position
        distance = get_distance(self.center_x, self.center_y, target_x, target_y)
        
        if distance < 10:  # Reached position
            self.last_known_player_pos = None
            self.alert_timer = 0
            self._clear_path()
            return
        
        # Set path to investigation position if not already set
        if not self.target_position or get_distance(target_x, target_y, 
                                                    self.target_position[0], 
                                                    self.target_position[1]) > 5:
            self._set_pathfinding_target(target_x, target_y, obstacles,
                                        grid_width, grid_height, tile_size)
        
        # Follow the path
        reached = self._follow_path(self.speed * delta_time)
        if reached:
            self.last_known_player_pos = None
            self.alert_timer = 0
    
    def _patrol(self, obstacles: List[Obstacle], delta_time: float,
                grid_width: int, grid_height: int, tile_size: int):
        """Patrol between waypoints using pathfinding."""
        if not self.patrol_points:
            # Random wandering if no patrol points (keep simple direct movement)
            if random.random() < 0.02:  # 2% chance to change direction each frame
                self.vision_angle = random.uniform(0, 360)
            
            angle_rad = math.radians(self.vision_angle)
            dx = math.cos(angle_rad) * self.speed * delta_time
            dy = math.sin(angle_rad) * self.speed * delta_time
            
            self._move_with_collision(dx, dy, obstacles)
            return
        
        # Patrol with waypoints
        if self.patrol_pause_counter > 0:
            self.patrol_pause_counter -= 1
            self._clear_path()  # Clear path while paused
            return
        
        target = self.patrol_points[self.current_patrol_index]
        distance = get_distance(self.center_x, self.center_y, target[0], target[1])
        
        if distance < 10:  # Reached waypoint
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
            pause_time = getattr(config, 'GUARD_PATROL_PAUSE_TIME', getattr(config, 'ENEMY_PATROL_PAUSE_TIME', 60))
            self.patrol_pause_counter = pause_time
            self._clear_path()
            return
        
        # Set path to patrol target if not already set or changed
        if not self.target_position or get_distance(target[0], target[1],
                                                    self.target_position[0],
                                                    self.target_position[1]) > 5:
            self._set_pathfinding_target(target[0], target[1], obstacles,
                                        grid_width, grid_height, tile_size)
        
        # Follow the path
        self._follow_path(self.speed * delta_time)
    
    def _move_with_collision(self, dx: float, dy: float, obstacles: List[Obstacle]) -> bool:
        """Move with obstacle collision detection."""
        # Add a small buffer to prevent clipping into walls
        buffer = 2.0
        
        new_x = self.center_x + dx
        new_y = self.center_y + dy
        
        # Check boundaries with buffer
        new_x = max(self.radius + buffer, min(config.SCREEN_WIDTH - self.radius - buffer, new_x))
        new_y = max(self.radius + buffer, min(config.SCREEN_HEIGHT - self.radius - buffer, new_y))
        
        # Check obstacle collisions with expanded collision radius
        collision = False
        collision_radius = self.radius + buffer
        
        for obstacle in obstacles:
            # Calculate closest point on rectangle to circle
            closest_x = max(obstacle.left, min(new_x, obstacle.right))
            closest_y = max(obstacle.bottom, min(new_y, obstacle.top))
            
            # Calculate distance from center of enemy to closest point
            dist = get_distance(new_x, new_y, closest_x, closest_y)
            
            if dist < collision_radius:
                collision = True
                break
        
        if not collision:
            self.center_x = new_x
            self.center_y = new_y
            return True
        else:
            # If collision, try sliding along the wall
            # Try moving only in x direction
            test_x = self.center_x + dx
            test_x = max(self.radius + buffer, min(config.SCREEN_WIDTH - self.radius - buffer, test_x))
            
            x_collision = False
            for obstacle in obstacles:
                closest_x = max(obstacle.left, min(test_x, obstacle.right))
                closest_y = max(obstacle.bottom, min(self.center_y, obstacle.top))
                dist = get_distance(test_x, self.center_y, closest_x, closest_y)
                if dist < collision_radius:
                    x_collision = True
                    break
            
            if not x_collision:
                self.center_x = test_x
                return True
            
            # Try moving only in y direction
            test_y = self.center_y + dy
            test_y = max(self.radius + buffer, min(config.SCREEN_HEIGHT - self.radius - buffer, test_y))
            
            y_collision = False
            for obstacle in obstacles:
                closest_x = max(obstacle.left, min(self.center_x, obstacle.right))
                closest_y = max(obstacle.bottom, min(test_y, obstacle.top))
                dist = get_distance(self.center_x, test_y, closest_x, closest_y)
                if dist < collision_radius:
                    y_collision = True
                    break
            
            if not y_collision:
                self.center_y = test_y
                return True
            
            # If both failed, rotate vision angle
            self.vision_angle = (self.vision_angle + random.uniform(45, 135)) % 360
        
        return False
    
    def die(self):
        """Kill the enemy."""
        self.alive = False
        self.color = (50, 50, 50)  # Dark gray when dead
    
    def check_collision_with_player(self, player: Player) -> bool:
        """
        Check if enemy caught the player (deprecated - now enemies shoot).
        Kept for backward compatibility but not used for death.
        """
        if not self.alive or not player.alive:
            return False
        return check_collision_circles(
            self.center_x, self.center_y, self.radius,
            player.center_x, player.center_y, player.radius
        )
    
    def draw_colored(self):
        """Draw the enemy as a colored circle."""
        if self.alive:
            arcade.draw_circle_filled(
                self.center_x, self.center_y,
                self.radius,
                self.color
            )
            
            # Draw muzzle flash when shooting
            cooldown = getattr(config, 'ENEMY_SHOOT_COOLDOWN', 60)
            if self.is_shooting and self.shoot_cooldown > cooldown - 5:
                # Flash at the front of the enemy
                angle_rad = math.radians(self.vision_angle)
                flash_distance = self.radius + 5
                flash_x = self.center_x + math.cos(angle_rad) * flash_distance
                flash_y = self.center_y + math.sin(angle_rad) * flash_distance
                
                # Draw bright flash
                arcade.draw_circle_filled(flash_x, flash_y, 8, (255, 255, 200))
                arcade.draw_circle_filled(flash_x, flash_y, 5, (255, 255, 100))

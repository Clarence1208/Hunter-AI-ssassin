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
        
    def move(self, dx: float, dy: float, obstacles: List[Obstacle], 
             screen_width: float, screen_height: float) -> bool:
        """
        Move player and check for collisions.
        
        Args:
            dx, dy: Movement direction (-1, 0, 1)
            obstacles: List of obstacles to check collision
            screen_width, screen_height: Screen boundaries
        
        Returns:
            True if movement was successful
        """
        if not self.alive:
            return False
        
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
            return True
        
        return False
    
    def can_attack(self, enemy: 'Enemy') -> bool:
        """Check if player is close enough to attack enemy."""
        if not self.alive or not enemy.alive:
            return False
        distance = get_distance(self.center_x, self.center_y, 
                               enemy.center_x, enemy.center_y)
        return distance < config.PLAYER_ATTACK_RANGE
    
    def die(self):
        """Kill the player."""
        self.alive = False
        self.color = (100, 100, 100)  # Gray when dead
    
    def draw_colored(self):
        """Draw the player as a colored circle."""
        color = self.color if self.alive else (100, 100, 100)
        arcade.draw_circle_filled(
            self.center_x, self.center_y,
            self.radius,
            color
        )


class Enemy(arcade.SpriteSolidColor):
    """
    Enemy AI with patrol and chase behavior, using ray casting for vision.
    """
    
    def __init__(self, x: float, y: float, patrol_points: Optional[List[Tuple[float, float]]] = None):
        super().__init__(config.ENEMY_SIZE * 2, config.ENEMY_SIZE * 2, config.ENEMY_COLOR)
        self.center_x = x
        self.center_y = y
        self.radius = config.ENEMY_SIZE
        self.speed = config.ENEMY_MOVEMENT_SPEED
        self.chase_speed = config.ENEMY_CHASE_SPEED
        self.alive = True
        
        # Vision properties
        self.vision_range = config.ENEMY_VISION_RANGE
        self.vision_angle = 0  # Direction enemy is facing
        self.fov = config.ENEMY_VISION_ANGLE
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
        
    def update_ai(self, player: Player, obstacles: List[Obstacle], delta_time: float = 1.0) -> Optional[Bullet]:
        """
        Update enemy AI behavior.
        
        Args:
            player: Player entity
            obstacles: List of obstacles
            delta_time: Time multiplier for speed
        
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
            self.color = config.ENEMY_ALERT_COLOR
            
            # Handle shooting
            if self.shoot_delay_timer < config.ENEMY_SHOOT_DELAY:
                self.shoot_delay_timer += 1
            elif self.shoot_cooldown == 0:
                # Shoot at player
                bullet = self._shoot_at_player(player)
                self.shoot_cooldown = config.ENEMY_SHOOT_COOLDOWN
                self.is_shooting = True
        else:
            # Reset shoot delay when losing sight of player
            self.shoot_delay_timer = 0
            self.is_shooting = False
            
            if self.alert_timer > 0:
                self.state = "alert"
                self.alert_timer -= 1
                self.color = config.ENEMY_ALERT_COLOR
            else:
                self.state = "patrol"
                self.color = config.ENEMY_COLOR
        
        # Execute behavior based on state
        if self.state == "chase":
            self._chase_player(player, obstacles, delta_time)
        elif self.state == "alert" and self.last_known_player_pos:
            self._investigate_position(self.last_known_player_pos, obstacles, delta_time)
        else:
            self._patrol(obstacles, delta_time)
        
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
    
    def _chase_player(self, player: Player, obstacles: List[Obstacle], delta_time: float):
        """Chase the player."""
        angle = get_angle_to_point(self.center_x, self.center_y,
                                   player.center_x, player.center_y)
        self.vision_angle = angle
        
        # Move towards player
        angle_rad = math.radians(angle)
        dx = math.cos(angle_rad) * self.chase_speed * delta_time
        dy = math.sin(angle_rad) * self.chase_speed * delta_time
        
        self._move_with_collision(dx, dy, obstacles)
    
    def _investigate_position(self, position: Tuple[float, float], 
                            obstacles: List[Obstacle], delta_time: float):
        """Move to last known player position."""
        target_x, target_y = position
        distance = get_distance(self.center_x, self.center_y, target_x, target_y)
        
        if distance < 10:  # Reached position
            self.last_known_player_pos = None
            self.alert_timer = 0
            return
        
        angle = get_angle_to_point(self.center_x, self.center_y, target_x, target_y)
        self.vision_angle = angle
        
        angle_rad = math.radians(angle)
        dx = math.cos(angle_rad) * self.speed * delta_time
        dy = math.sin(angle_rad) * self.speed * delta_time
        
        self._move_with_collision(dx, dy, obstacles)
    
    def _patrol(self, obstacles: List[Obstacle], delta_time: float):
        """Patrol between waypoints."""
        if not self.patrol_points:
            # Random wandering if no patrol points
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
            return
        
        target = self.patrol_points[self.current_patrol_index]
        distance = get_distance(self.center_x, self.center_y, target[0], target[1])
        
        if distance < 10:  # Reached waypoint
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
            self.patrol_pause_counter = config.ENEMY_PATROL_PAUSE_TIME
            return
        
        angle = get_angle_to_point(self.center_x, self.center_y, target[0], target[1])
        self.vision_angle = angle
        
        angle_rad = math.radians(angle)
        dx = math.cos(angle_rad) * self.speed * delta_time
        dy = math.sin(angle_rad) * self.speed * delta_time
        
        self._move_with_collision(dx, dy, obstacles)
    
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
            if self.is_shooting and self.shoot_cooldown > config.ENEMY_SHOOT_COOLDOWN - 5:
                # Flash at the front of the enemy
                angle_rad = math.radians(self.vision_angle)
                flash_distance = self.radius + 5
                flash_x = self.center_x + math.cos(angle_rad) * flash_distance
                flash_y = self.center_y + math.sin(angle_rad) * flash_distance
                
                # Draw bright flash
                arcade.draw_circle_filled(flash_x, flash_y, 8, (255, 255, 200))
                arcade.draw_circle_filled(flash_x, flash_y, 5, (255, 255, 100))

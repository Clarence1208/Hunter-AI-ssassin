"""
Hunter Assassin Game Environment - RL Ready
Provides Gym-like interface for reinforcement learning
"""
import arcade
import numpy as np
import random
import math
from typing import Tuple, Dict, Optional, List
import config
from entities import Player, Enemy, Obstacle, Bullet
from utils import cast_ray, get_distance, check_collision_circles
from map_layouts import get_apartment_layout


class HunterAssassinEnv(arcade.Window):
    """
    Main game environment with RL-compatible interface.
    
    State space: Continuous observations including:
        - Ray cast distances (NUM_RAYS floats)
        - Player position (x, y normalized)
        - Player velocity (dx, dy)
        - Enemy positions and states (relative to player)
        - Health status
    
    Action space: Discrete (9 actions - 8 directions + stay)
    
    Reward structure:
        - Kill enemy: +100
        - Get killed: -100
        - Win (all enemies killed): +500
        - Step penalty: -0.1
        - Distance to nearest enemy: small positive reward for getting closer
    """
    
    def __init__(self, render_mode: bool = True):
        """
        Initialize the game environment.
        
        Args:
            render_mode: If True, render the game. If False, run headless for training.
        """
        super().__init__(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, 
                        config.SCREEN_TITLE, visible=render_mode)
        self.render_mode = render_mode
        
        # Set background color
        arcade.set_background_color(arcade.color.BLACK)
        
        # Game entities
        self.player: Optional[Player] = None
        self.enemies: arcade.SpriteList = arcade.SpriteList()
        self.obstacles: arcade.SpriteList = arcade.SpriteList()
        self.bullets: List[Bullet] = []
        
        # Map dimensions for pathfinding
        self.grid_width = config.MAP_TILES_WIDTH if hasattr(config, 'MAP_TILES_WIDTH') else 16
        self.grid_height = config.MAP_TILES_HEIGHT if hasattr(config, 'MAP_TILES_HEIGHT') else 16
        self.tile_size = config.TILE_SIZE if hasattr(config, 'TILE_SIZE') else 50
        
        # Game state
        self.episode_step = 0
        self.total_reward = 0.0
        self.previous_min_enemy_distance = None
        self.game_started = True
        
        # Input tracking for manual control
        self.key_state = {
            arcade.key.W: False,
            arcade.key.S: False,
            arcade.key.A: False,
            arcade.key.D: False,
            arcade.key.UP: False,
            arcade.key.DOWN: False,
            arcade.key.LEFT: False,
            arcade.key.RIGHT: False,
            arcade.key.SPACE: False,
        }
        
        # Visual settings
        self.show_enemy_vision = True
        
        # UI Text objects (for performance)
        self.text_start = arcade.Text(
            "MOVE TO START",
            config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2 + 50,
            arcade.color.YELLOW, 36, font_name="Arial",
            anchor_x="center", anchor_y="center", bold=True
        )
        self.text_start_hint = arcade.Text(
            "(Press WASD or Arrow Keys)",
            config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2 + 10,
            arcade.color.WHITE, 18, font_name="Arial",
            anchor_x="center", anchor_y="center"
        )
        self.text_kills = arcade.Text(
            f"Kills: 0",
            10, config.SCREEN_HEIGHT - 30,
            arcade.color.WHITE, 16, font_name="Arial"
        )
        self.text_guards = arcade.Text(
            f"Guards: 0/0",
            10, config.SCREEN_HEIGHT - 55,
            arcade.color.WHITE, 16, font_name="Arial"
        )
        self.text_step = arcade.Text(
            f"Step: 0/{config.MAX_STEPS_PER_EPISODE}",
            10, config.SCREEN_HEIGHT - 80,
            arcade.color.WHITE, 16, font_name="Arial"
        )
        self.text_reward = arcade.Text(
            f"Reward: 0.0",
            10, config.SCREEN_HEIGHT - 105,
            arcade.color.WHITE, 16, font_name="Arial"
        )
        self.text_bullets = arcade.Text(
            f"Bullets: 0",
            10, config.SCREEN_HEIGHT - 130,
            arcade.color.YELLOW, 12, font_name="Arial"
        )
        self.text_controls = arcade.Text(
            "LEFT CLICK: Move | WASD/Arrows: Move | V: Vision | R: Reset",
            10, 10,
            arcade.color.WHITE, 11, font_name="Arial"
        )
        
        # Initialize game
        self.reset()
    
    def reset(self) -> np.ndarray:
        """
        Reset the game to initial state.
        
        Returns:
            Initial observation
        """
        # Clear existing entities
        self.enemies.clear()
        self.obstacles.clear()
        self.bullets.clear()
        
        # Reset counters
        self.episode_step = 0
        self.total_reward = 0.0
        self.previous_min_enemy_distance = None
        self.game_started = True
        
        # Create obstacles and entities based on layout mode
        if config.USE_JSON_MAP:
            self._generate_json_map()
        elif hasattr(config, 'USE_APARTMENT_LAYOUT') and config.USE_APARTMENT_LAYOUT:
            self._generate_apartment_layout()
        else:
            self._generate_random_layout()
        
        return self._get_observation()
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Execute one time step in the environment.
        
        Args:
            action: Action index from config.ACTIONS
        
        Returns:
            observation: Current state observation
            reward: Reward for this step
            done: Whether episode is finished
            info: Additional information dictionary
        """
        self.episode_step += 1
        reward = 0.0
        done = False
        info = {
            "kills": self.player.kills if self.player else 0,
            "enemies_alive": sum(1 for e in self.enemies if e.alive),
            "player_alive": self.player.alive if self.player else False,
        }
        
        # Execute action
        if action in config.ACTIONS:
            dx, dy = config.ACTIONS[action]
            
            # Check if player is making a movement (not staying still)
            if not self.game_started and (dx != 0 or dy != 0):
                self.game_started = True
            
            if self.player:
                self.player.move(dx, dy, list(self.obstacles), 
                               config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        
        # Update enemies and collect bullets (only if game has started)
        if self.game_started:
            for enemy in self.enemies:
                if enemy.alive:
                    bullet = enemy.update_ai(
                        self.player, 
                        list(self.obstacles),
                        1.0,  # delta_time
                        self.grid_width,
                        self.grid_height,
                        self.tile_size
                    )
                    if bullet:
                        self.bullets.append(bullet)
        
        # Update bullets
        bullets_to_remove = []
        for bullet in self.bullets:
            should_remove = bullet.update(list(self.obstacles))
            if should_remove:
                bullets_to_remove.append(bullet)
        
        # Remove inactive bullets
        for bullet in bullets_to_remove:
            self.bullets.remove(bullet)
        
        # Check bullet hits on player
        if self.player and self.player.alive:
            for bullet in self.bullets[:]:  # Use slice to avoid modification during iteration
                if bullet.check_hit_player(self.player):
                    self.player.die()
                    reward += config.DEATH_PENALTY
                    done = True
                    info["death"] = True
                    info["hit_by_bullet"] = True
                    bullet.active = False
                    break
        
        # Update player attack animation
        if self.player and self.player.alive:
            # Update ongoing attack
            if self.player.update_attack():
                # Deal damage at the right moment in animation
                if self.player.attack_target and self.player.attack_target.alive:
                    self.player.attack_target.die()
                    self.player.kills += 1
                    reward += config.PLAYER_KILL_REWARD
                    info["kill"] = True
            
            # Check if player can start a new attack
            if not self.player.is_attacking:
                for enemy in self.enemies:
                    if enemy.alive and self.player.can_attack(enemy):
                        # Start attack animation instead of instant kill
                        self.player.start_attack(enemy)
                        break  # Only attack one enemy at a time
        
        # Distance-based reward (encourage getting closer to enemies)
        if self.player and self.player.alive:
            min_distance = self._get_min_enemy_distance()
            if self.previous_min_enemy_distance is not None and min_distance < self.previous_min_enemy_distance:
                reward += config.DISTANCE_REWARD_SCALE * (self.previous_min_enemy_distance - min_distance) * 0.1
            self.previous_min_enemy_distance = min_distance
        
        # Step penalty
        reward += config.STEP_PENALTY
        
        # Check win condition
        enemies_alive = sum(1 for e in self.enemies if e.alive)
        if enemies_alive == 0:
            reward += config.WIN_REWARD
            done = True
            info["win"] = True
        
        # Check max steps
        if self.episode_step >= config.MAX_STEPS_PER_EPISODE:
            done = True
            info["timeout"] = True
        
        self.total_reward += reward
        info["total_reward"] = self.total_reward
        
        return self._get_observation(), reward, done, info
    
    def _get_observation(self) -> np.ndarray:
        """
        Get current state observation.
        
        Returns:
            Numpy array containing:
                - Ray cast distances (NUM_RAYS)
                - Player position (x, y normalized)
                - Player alive status (1 or 0)
                - For each enemy (up to NUM_ENEMIES):
                    - Relative position (x, y)
                    - Distance
                    - Alive status
                    - Alerted status
        """
        obs = []
        
        # Ray casting for distance sensing
        if self.player:
            for i in range(config.NUM_RAYS):
                angle = (360 / config.NUM_RAYS) * i
                distance, _ = cast_ray(
                    self.player.center_x, self.player.center_y,
                    angle, config.RAY_MAX_DISTANCE,
                    list(self.obstacles)
                )
                # Normalize distance
                obs.append(distance / config.RAY_MAX_DISTANCE)
            
            # Player position (normalized)
            obs.append(self.player.center_x / config.SCREEN_WIDTH)
            obs.append(self.player.center_y / config.SCREEN_HEIGHT)
            obs.append(1.0 if self.player.alive else 0.0)
        else:
            # Dead player
            obs.extend([1.0] * config.NUM_RAYS)  # Max distance
            obs.extend([0.0, 0.0, 0.0])  # Position and alive status
        
        # Enemy information
        enemy_list = list(self.enemies)
        num_enemies = getattr(config, 'NUM_GUARDS', getattr(config, 'NUM_ENEMIES', len(enemy_list)))
        for i in range(num_enemies):
            if i < len(enemy_list):
                enemy = enemy_list[i]
                if self.player:
                    # Relative position
                    rel_x = (enemy.center_x - self.player.center_x) / config.SCREEN_WIDTH
                    rel_y = (enemy.center_y - self.player.center_y) / config.SCREEN_HEIGHT
                    distance = get_distance(self.player.center_x, self.player.center_y,
                                          enemy.center_x, enemy.center_y)
                    norm_distance = min(distance / config.SCREEN_WIDTH, 1.0)
                    
                    obs.extend([
                        rel_x,
                        rel_y,
                        norm_distance,
                        1.0 if enemy.alive else 0.0,
                        1.0 if enemy.state in ["chase", "alert"] else 0.0
                    ])
                else:
                    obs.extend([0.0, 0.0, 1.0, 0.0, 0.0])
            else:
                # Padding for missing enemies
                obs.extend([0.0, 0.0, 1.0, 0.0, 0.0])
        
        return np.array(obs, dtype=np.float32)
    
    def _get_min_enemy_distance(self) -> float:
        """Get distance to nearest alive enemy."""
        if not self.player or not self.player.alive:
            return float('inf')
        
        min_dist = float('inf')
        for enemy in self.enemies:
            if enemy.alive:
                dist = get_distance(self.player.center_x, self.player.center_y,
                                  enemy.center_x, enemy.center_y)
                min_dist = min(min_dist, dist)
        return min_dist
    
    def _generate_json_map(self):
        """Generate map from JSON file."""
        from map_loader import load_map
        
        map_data = load_map(config.JSON_MAP_PATH)
        
        # Update grid dimensions from map
        self.grid_width = map_data.size[0]
        self.grid_height = map_data.size[1]
        self.tile_size = config.TILE_SIZE
        
        # Create walls from tilemap
        for y in range(len(map_data.tiles)):
            for x in range(len(map_data.tiles[y])):
                if map_data.is_wall(x, y):
                    world_x, world_y = map_data.tile_to_world(x, y, config.TILE_SIZE)
                    obstacle = Obstacle(
                        world_x, world_y,
                        config.TILE_SIZE, config.TILE_SIZE,
                        config.WALL_COLOR
                    )
                    self.obstacles.append(obstacle)
        
        # Create player at spawn
        player_tile_x, player_tile_y = map_data.player_start
        player_x, player_y = map_data.tile_to_world(player_tile_x, player_tile_y, config.TILE_SIZE)
        self.player = Player(player_x, player_y)
        
        # Create guards from map data
        for guard_data in map_data.guards:
            guard_tile_x, guard_tile_y = guard_data.pos
            guard_x, guard_y = map_data.tile_to_world(guard_tile_x, guard_tile_y, config.TILE_SIZE)
            enemy = Enemy(guard_x, guard_y)
            self.enemies.append(enemy)
        
        # Store map data for objectives, hide spots, etc.
        self.map_data = map_data
    
    def _generate_apartment_layout(self):
        """Generate the fixed apartment layout with player and enemies."""
        layout = get_apartment_layout()
        
        # Create walls from layout
        for wall_def in layout.get_walls():
            obstacle = Obstacle(
                wall_def['x'], 
                wall_def['y'], 
                wall_def['width'], 
                wall_def['height'],
                wall_def['color']
            )
            self.obstacles.append(obstacle)
        
        # Create player at fixed spawn
        player_x, player_y = layout.get_player_spawn()
        self.player = Player(player_x, player_y)
        
        # Create enemies at fixed spawns with patrol routes
        enemy_spawns = layout.get_enemy_spawns(config.NUM_ENEMIES)
        for i, (enemy_x, enemy_y) in enumerate(enemy_spawns):
            patrol_points = layout.get_enemy_patrol_routes(i)
            enemy = Enemy(enemy_x, enemy_y, patrol_points)
            self.enemies.append(enemy)
    
    def _generate_random_layout(self):
        """Generate random obstacles and spawn positions (original behavior)."""
        # Generate obstacles
        self._generate_obstacles()
        
        # Create player
        player_x, player_y = self._find_valid_spawn_position()
        self.player = Player(player_x, player_y)
        
        # Create enemies
        for _ in range(config.NUM_ENEMIES):
            enemy_x, enemy_y = self._find_valid_spawn_position(min_distance_from_player=150)
            patrol_points = self._generate_patrol_points(enemy_x, enemy_y)
            enemy = Enemy(enemy_x, enemy_y, patrol_points)
            self.enemies.append(enemy)
    
    def _generate_obstacles(self):
        """Generate random obstacles in the environment."""
        for _ in range(config.NUM_OBSTACLES):
            width = random.randint(config.OBSTACLE_MIN_SIZE, config.OBSTACLE_MAX_SIZE)
            height = random.randint(config.OBSTACLE_MIN_SIZE, config.OBSTACLE_MAX_SIZE)
            
            # Random position with boundaries
            x = random.randint(width // 2 + 20, config.SCREEN_WIDTH - width // 2 - 20)
            y = random.randint(height // 2 + 20, config.SCREEN_HEIGHT - height // 2 - 20)
            
            obstacle = Obstacle(x, y, width, height)
            self.obstacles.append(obstacle)
    
    def _find_valid_spawn_position(self, min_distance_from_player: float = 0) -> Tuple[float, float]:
        """Find a valid spawn position that doesn't overlap with obstacles."""
        max_attempts = 100
        for _ in range(max_attempts):
            x = random.randint(50, config.SCREEN_WIDTH - 50)
            y = random.randint(50, config.SCREEN_HEIGHT - 50)
            
            # Check obstacle collision
            valid = True
            for obstacle in self.obstacles:
                if (obstacle.left - 30 <= x <= obstacle.right + 30 and
                    obstacle.bottom - 30 <= y <= obstacle.top + 30):
                    valid = False
                    break
            
            # Check distance from player if needed
            if valid and self.player and min_distance_from_player > 0:
                dist = get_distance(x, y, self.player.center_x, self.player.center_y)
                if dist < min_distance_from_player:
                    valid = False
            
            if valid:
                return x, y
        
        # Fallback to center if no valid position found
        return config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2
    
    def _generate_patrol_points(self, start_x: float, start_y: float, 
                               num_points: int = 4) -> List[Tuple[float, float]]:
        """Generate patrol waypoints for an enemy."""
        points = [(start_x, start_y)]
        
        for _ in range(num_points - 1):
            x, y = self._find_valid_spawn_position()
            points.append((x, y))
        
        return points
    
    def on_draw(self):
        """Render the game."""
        if not self.render_mode:
            return
        
        self.clear()
        
        # Draw floor background
        if config.USE_JSON_MAP or (hasattr(config, 'USE_APARTMENT_LAYOUT') and config.USE_APARTMENT_LAYOUT):
            # Draw floor with subtle grid pattern
            arcade.draw_lrbt_rectangle_filled(
                0, config.SCREEN_WIDTH,
                0, config.SCREEN_HEIGHT,
                config.FLOOR_COLOR
            )
            
            # Draw subtle grid lines for floor texture
            grid_size = config.TILE_SIZE if hasattr(config, 'TILE_SIZE') else 80
            grid_color = tuple(min(255, c + 5) for c in config.FLOOR_COLOR)
            
            # Vertical lines
            for x in range(0, config.SCREEN_WIDTH, grid_size):
                arcade.draw_line(x, 0, x, config.SCREEN_HEIGHT, grid_color, 1)
            
            # Horizontal lines
            for y in range(0, config.SCREEN_HEIGHT, grid_size):
                arcade.draw_line(0, y, config.SCREEN_WIDTH, y, grid_color, 1)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw_colored()

        
        # Draw enemy vision cones with gradient effect
        if self.show_enemy_vision:
            for enemy in self.enemies:
                if enemy.alive:
                    # Draw filled vision cone with gradient effect
                    # We'll draw multiple layers with decreasing opacity
                    angle_start = enemy.vision_angle - enemy.fov / 2
                    angle_end = enemy.vision_angle + enemy.fov / 2
                    
                    # Draw 3 layers for gradient effect
                    layers = [
                        (enemy.vision_range * 1.0, (255, 255, 0, 20)),  # Full range, very transparent
                        (enemy.vision_range * 0.7, (255, 200, 0, 30)),  # 70% range, more visible
                        (enemy.vision_range * 0.4, (255, 150, 0, 40)),  # 40% range, most visible
                    ]
                    
                    for radius, color in layers:
                        # Draw the vision cone as a filled arc/wedge
                        self._draw_vision_cone(
                            enemy.center_x, enemy.center_y,
                            radius, angle_start, angle_end, color
                        )
                    
                    # Draw vision direction line (the "aiming" line)
                    angle_rad = math.radians(enemy.vision_angle)
                    end_x = enemy.center_x + math.cos(angle_rad) * 40
                    end_y = enemy.center_y + math.sin(angle_rad) * 40
                    arcade.draw_line(
                        enemy.center_x, enemy.center_y,
                        end_x, end_y,
                        (255, 200, 0) if enemy.can_see_player else (200, 200, 0), 3
                    )
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw_colored()
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw_colored()
        
        # Draw player
        if self.player:
            self.player.draw_colored()
            
            # Draw pathfinding waypoints and path
            if self.player.path_waypoints:
                # Draw path as connected lines
                prev_x, prev_y = self.player.center_x, self.player.center_y
                for i, (waypoint_x, waypoint_y) in enumerate(self.player.path_waypoints):
                    # Draw line from previous point to this waypoint
                    arcade.draw_line(prev_x, prev_y, waypoint_x, waypoint_y,
                                   (0, 255, 255, 150), 2)
                    
                    # Draw waypoint marker (small circles)
                    if i == self.player.current_waypoint_idx:
                        # Current target waypoint (filled, brighter)
                        arcade.draw_circle_filled(waypoint_x, waypoint_y, 5, (0, 255, 255))
                    else:
                        # Future waypoints (outline)
                        arcade.draw_circle_outline(waypoint_x, waypoint_y, 4, (0, 200, 200), 2)
                    
                    prev_x, prev_y = waypoint_x, waypoint_y
                
                # Draw X marker at final destination
                if self.player.target_position:
                    target_x, target_y = self.player.target_position
                    size = 10
                    arcade.draw_line(target_x - size, target_y - size, 
                                   target_x + size, target_y + size,
                                   (0, 255, 255), 2)
                    arcade.draw_line(target_x - size, target_y + size,
                                   target_x + size, target_y - size,
                                   (0, 255, 255), 2)
                    # Draw circle around destination
                    arcade.draw_circle_outline(target_x, target_y, 15, (0, 255, 255), 2)
        
        # Draw UI
        self._draw_ui()

    def _draw_vision_cone(self, center_x: float, center_y: float,
                          radius: float, angle_start: float, angle_end: float,
                          color: Tuple[int, int, int, int]):
        """
        Draw a filled vision cone that stops at walls.

        Args:
            center_x, center_y: Center point of the cone
            radius: Radius of the cone
            angle_start: Starting angle in degrees
            angle_end: Ending angle in degrees
            color: RGBA color tuple
        """
        # Create points for the cone/wedge
        points = [(center_x, center_y)]  # Start at center

        # Number of segments for smooth arc
        num_segments = max(3, int(abs(angle_end - angle_start) / 5))

        # Add points along the arc, but ray cast to find wall intersections
        for i in range(num_segments + 1):
            angle = angle_start + (angle_end - angle_start) * i / num_segments

            # Cast a ray to find where it hits a wall
            distance, hit_point = cast_ray(
                center_x, center_y,
                angle, radius,
                list(self.obstacles)
            )

            # Use the hit point (which stops at walls)
            angle_rad = math.radians(angle)
            x = center_x + math.cos(angle_rad) * distance
            y = center_y + math.sin(angle_rad) * distance
            points.append((x, y))

        # Draw filled polygon
        arcade.draw_polygon_filled(points, color)
    
    def _draw_ui(self):
        """Draw UI elements."""
        # Game start indicator
        if not self.game_started:
            # Draw prominent "READY" message
            self.text_start.draw()
            self.text_start_hint.draw()
        
        # Score
        self.text_kills.text = f"Kills: {self.player.kills if self.player else 0}"
        self.text_kills.draw()
        
        # Enemies alive
        enemies_alive = sum(1 for e in self.enemies if e.alive)
        total_enemies = len(self.enemies)
        self.text_guards.text = f"Guards: {enemies_alive}/{total_enemies}"
        self.text_guards.draw()
        
        # Episode step
        self.text_step.text = f"Step: {self.episode_step}/{config.MAX_STEPS_PER_EPISODE}"
        self.text_step.draw()
        
        # Total reward
        self.text_reward.text = f"Reward: {self.total_reward:.1f}"
        self.text_reward.draw()
        
        # Bullets count (for debugging)
        self.text_bullets.text = f"Bullets: {len(self.bullets)}"
        self.text_bullets.draw()
        
        # Controls hint
        self.text_controls.draw()
    
    def on_update(self, delta_time: float):
        """Update game state (for manual play mode)."""
        if not self.player or not self.player.alive:
            return
        
        # Update point-and-click movement first
        if self.player.target_position and not self.player.is_attacking:
            self.player.update_movement(list(self.obstacles), 
                                       config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        
        # Update idle animation if not moving and not attacking
        if not self.player.target_position and not self.player.is_attacking:
            # Check if any keys are pressed
            dx, dy = 0, 0
            if self.key_state[arcade.key.W] or self.key_state[arcade.key.UP]:
                dy = 1
            if self.key_state[arcade.key.S] or self.key_state[arcade.key.DOWN]:
                dy = -1
            if self.key_state[arcade.key.A] or self.key_state[arcade.key.LEFT]:
                dx = -1
            if self.key_state[arcade.key.D] or self.key_state[arcade.key.RIGHT]:
                dx = 1
            
            if dx == 0 and dy == 0:
                # No movement, update idle animation
                self.player.animated_sprite.update_animation(0, 0)
        
        # Get action from keyboard (overrides click movement)
        dx, dy = 0, 0
        if self.key_state[arcade.key.W] or self.key_state[arcade.key.UP]:
            dy = 1
        if self.key_state[arcade.key.S] or self.key_state[arcade.key.DOWN]:
            dy = -1
        if self.key_state[arcade.key.A] or self.key_state[arcade.key.LEFT]:
            dx = -1
        if self.key_state[arcade.key.D] or self.key_state[arcade.key.RIGHT]:
            dx = 1
        
        # Convert to action index
        action = self._get_action_from_direction(dx, dy)
        
        # Execute step
        self.step(action)
    
    def _get_action_from_direction(self, dx: int, dy: int) -> int:
        """Convert direction to action index."""
        for action_idx, (action_dx, action_dy) in config.ACTIONS.items():
            if action_dx == dx and action_dy == dy:
                return action_idx
        return 0  # Stay still
    
    def on_key_press(self, key: int, modifiers: int):
        """Handle key press events."""
        if key in self.key_state:
            self.key_state[key] = True
        
        if key == arcade.key.R:
            self.reset()
        
        if key == arcade.key.V:
            self.show_enemy_vision = not self.show_enemy_vision
    
    def on_key_release(self, key: int, modifiers: int):
        """Handle key release events."""
        if key in self.key_state:
            self.key_state[key] = False
    
    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """Handle mouse clicks for point-and-click movement with pathfinding."""
        if button == arcade.MOUSE_BUTTON_LEFT and self.player and self.player.alive:
            # Set target position for player with pathfinding
            self.player.set_target(
                x, y,
                list(self.obstacles),
                self.grid_width,
                self.grid_height,
                self.tile_size
            )
    
    def get_observation_space_size(self) -> int:
        """Get size of observation vector."""
        # Rays + player info + enemy info
        num_enemies = getattr(config, 'NUM_GUARDS', getattr(config, 'NUM_ENEMIES', len(self.enemies) if hasattr(self, 'enemies') else 5))
        return config.NUM_RAYS + 3 + (num_enemies * 5)
    
    def get_action_space_size(self) -> int:
        """Get number of discrete actions."""
        return config.NUM_ACTIONS

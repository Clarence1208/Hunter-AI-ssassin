"""
Player Animation System for Hunter Assassin
Manages sprite animations for the top-view player character with knife weapon
"""
import arcade
import math
from typing import List, Tuple
import os


class PlayerAnimationManager:
    """
    Manages all player animations including idle, move, and melee attack.
    """
    
    def __init__(self):
        """Initialize the animation manager and load all sprites."""
        self.animations = {}
        self.current_animation = "idle"
        self.current_frame = 0
        self.animation_speed = 0.15  # Base frames to advance per update
        self.attack_animation_speed = 0.5  # Faster speed for attack animations only
        self.frame_counter = 0.0
        
        # Animation state
        self.is_attacking = False
        self.attack_frame_start = 0
        self.attack_target = None  # Target enemy for attack
        
        # Scale factor for sprites
        self.sprite_scale = 1.0
        
        # Load all animations
        self._load_animations()
        
    def _load_animations(self):
        """Load all knife animation frames from the sprite directory."""
        base_path = "ressources/img/top-view-player/knife"
        
        # Load idle animation (20 frames)
        self.animations["idle"] = self._load_animation_frames(
            f"{base_path}/idle",
            "survivor-idle_knife",
            20
        )
        
        # Load move animation (20 frames)
        self.animations["move"] = self._load_animation_frames(
            f"{base_path}/move",
            "survivor-move_knife",
            20
        )
        
        # Load melee attack animation (15 frames)
        self.animations["meleeattack"] = self._load_animation_frames(
            f"{base_path}/meleeattack",
            "survivor-meleeattack_knife",
            15
        )
        
    def _load_animation_frames(self, directory: str, prefix: str, num_frames: int) -> List[arcade.Texture]:
        """
        Load animation frames from a directory.
        
        Args:
            directory: Path to the animation directory
            prefix: Filename prefix (without number and extension)
            num_frames: Number of frames in the animation
            
        Returns:
            List of arcade.Texture objects
        """
        frames = []
        for i in range(num_frames):
            filename = f"{directory}/{prefix}_{i}.png"
            try:
                texture = arcade.load_texture(filename)
                frames.append(texture)
            except FileNotFoundError:
                print(f"Warning: Could not load {filename}")
                # Create a placeholder if file not found
                if frames:
                    frames.append(frames[0])  # Reuse first frame
        
        if not frames:
            print(f"Error: No frames loaded for {prefix}")
            # Create a simple placeholder texture
            frames.append(arcade.load_texture(":resources:images/topdown_tanks/tankBody_blue.png"))
        
        return frames
    
    def start_attack(self, target_enemy):
        """
        Start the melee attack animation.
        
        Args:
            target_enemy: The enemy being attacked
        """
        self.is_attacking = True
        self.attack_target = target_enemy
        self.current_animation = "meleeattack"
        self.current_frame = 0
        self.frame_counter = 0.0
        self.attack_frame_start = 0
    
    def update(self, is_moving: bool):
        """
        Update the animation state.
        
        Args:
            is_moving: Whether the player is currently moving
        """
        # Use faster speed for attack animations
        speed = self.attack_animation_speed if self.current_animation == "meleeattack" else self.animation_speed
        
        # Update frame counter
        self.frame_counter += speed
        
        # Check if we should advance to next frame
        if self.frame_counter >= 1.0:
            self.frame_counter -= 1.0
            self.current_frame += 1
            
            # Check for animation completion
            current_frames = self.animations[self.current_animation]
            if self.current_frame >= len(current_frames):
                # Animation completed
                if self.current_animation == "meleeattack":
                    # Attack animation finished
                    self.is_attacking = False
                    self.attack_target = None
                    self.current_animation = "idle"
                
                # Loop the animation
                self.current_frame = 0
        
        # Set animation based on state (if not attacking)
        if not self.is_attacking:
            if is_moving:
                if self.current_animation != "move":
                    self.current_animation = "move"
                    self.current_frame = 0
                    self.frame_counter = 0.0
            else:
                if self.current_animation != "idle":
                    self.current_animation = "idle"
                    self.current_frame = 0
                    self.frame_counter = 0.0
    
    def get_current_texture(self) -> arcade.Texture:
        """
        Get the current frame's texture.
        
        Returns:
            arcade.Texture for the current frame
        """
        if self.current_animation not in self.animations:
            return self.animations["idle"][0]
        
        frames = self.animations[self.current_animation]
        if not frames:
            return None
        
        # Ensure frame index is valid
        frame_idx = int(self.current_frame) % len(frames)
        return frames[frame_idx]
    
    def is_attack_active(self) -> bool:
        """Check if attack animation is currently playing."""
        return self.is_attacking
    
    def get_attack_progress(self) -> float:
        """
        Get the progress of the current attack animation (0.0 to 1.0).
        
        Returns:
            Attack progress as a float between 0 and 1, or 0 if not attacking
        """
        if not self.is_attacking:
            return 0.0
        
        total_frames = len(self.animations["meleeattack"])
        if total_frames == 0:
            return 1.0
        
        return (self.current_frame + self.frame_counter) / total_frames
    
    def should_deal_damage(self) -> bool:
        """
        Check if the attack animation is at the point where damage should be dealt.
        Typically this is around 50-60% through the attack animation.
        
        Returns:
            True if damage should be dealt this frame
        """
        if not self.is_attacking:
            return False
        
        progress = self.get_attack_progress()
        # Deal damage at 50% of the animation
        # We check if we just crossed the 50% threshold
        prev_progress = (self.current_frame - 1 + self.frame_counter) / len(self.animations["meleeattack"])
        
        return prev_progress < 0.5 <= progress


class AnimatedPlayerSprite(arcade.Sprite):
    """
    A sprite that uses the PlayerAnimationManager for animations.
    Replaces the simple circle rendering with animated sprites.
    """
    
    def __init__(self, x: float, y: float):
        """
        Initialize the animated player sprite.
        
        Args:
            x, y: Starting position
        """
        super().__init__()
        
        self.center_x = x
        self.center_y = y
        
        # Animation manager
        self.animation_manager = PlayerAnimationManager()
        
        # Set initial texture
        self.texture = self.animation_manager.get_current_texture()
        
        # Movement tracking
        self.last_dx = 0
        self.last_dy = 0
        self.facing_angle = 0  # Angle the player is facing (in degrees)
        
        # Scale the sprite to be 0.75 of a tile (48 pixels)
        # Assuming sprites are around 289x224, we need to scale down significantly
        import config
        target_size = config.TILE_SIZE * 1.2  # 48 pixels (was 0.5 = 32 pixels)
        if self.texture:
            # Scale based on the larger dimension to fit properly
            texture_size = max(self.texture.width, self.texture.height)
            self.scale = target_size / texture_size
        else:
            self.scale = 0.22  # Fallback scale
        
    def update_animation(self, dx: float = 0, dy: float = 0):
        """
        Update the animation based on movement.
        
        Args:
            dx, dy: Movement direction this frame
        """
        # Track if player is moving
        is_moving = (dx != 0 or dy != 0)
        
        # Update facing direction if moving
        if is_moving:
            self.last_dx = dx
            self.last_dy = dy
            # Calculate angle (arcade uses degrees, 0 = right, 90 = up)
            # Invert dy to fix up/down reversal issue
            self.facing_angle = math.degrees(math.atan2(-dy, dx))
        
        # Update the animation manager
        self.animation_manager.update(is_moving)
        
        # Update the texture
        self.texture = self.animation_manager.get_current_texture()
        
        # Set rotation to face the movement direction
        # The sprites face right by default (0 degrees), so we just use facing_angle
        self.angle = self.facing_angle
    
    def start_attack_animation(self, target_enemy):
        """
        Start the attack animation toward a target enemy.
        
        Args:
            target_enemy: The enemy being attacked
        """
        # Calculate angle to target
        dx = target_enemy.center_x - self.center_x
        dy = target_enemy.center_y - self.center_y
        if dx != 0 or dy != 0:
            # Invert dy to fix up/down reversal issue
            self.facing_angle = math.degrees(math.atan2(-dy, dx))
            self.angle = self.facing_angle
        
        # Start attack animation
        self.animation_manager.start_attack(target_enemy)
    
    def is_attacking(self) -> bool:
        """Check if currently playing attack animation."""
        return self.animation_manager.is_attack_active()
    
    def should_deal_damage(self) -> bool:
        """Check if at the damage-dealing frame of attack animation."""
        return self.animation_manager.should_deal_damage()


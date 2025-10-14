"""
Guard AI State Machine for stealth game
States: PATROL → SUSPICIOUS → ALERTED → SEARCHING → PATROL
"""
from enum import Enum
from typing import Optional, Tuple
import math


class GuardState(Enum):
    """Guard AI states"""
    PATROL = "patrol"
    SUSPICIOUS = "suspicious"  # Heard something or brief visual
    ALERTED = "alerted"        # Confirmed player visual, chasing
    SEARCHING = "searching"    # Lost player, investigating last known position


class DetectionLevel:
    """Tracks detection progress"""
    def __init__(self, detection_threshold: float = 0.3):
        self.value = 0.0  # 0.0 to 1.0
        self.threshold = detection_threshold  # Seconds to full detection
        self.decay_rate = 2.0  # How fast detection fades when not visible
    
    def update_seeing(self, delta_time: float, can_see: bool):
        """Update detection based on visibility"""
        if can_see:
            self.value = min(1.0, self.value + delta_time / self.threshold)
        else:
            self.value = max(0.0, self.value - delta_time * self.decay_rate / self.threshold)
    
    def is_suspicious(self) -> bool:
        """Is guard becoming suspicious (20-50% detected)?"""
        return 0.2 <= self.value < 0.5
    
    def is_alerted(self) -> bool:
        """Is guard fully alerted (>= 100% detected)?"""
        return self.value >= 1.0
    
    def reset(self):
        """Clear detection"""
        self.value = 0.0


class GuardStateMachine:
    """
    AI state machine for a single guard.
    Manages transitions between patrol, suspicious, alerted, and searching states.
    """
    
    def __init__(self, detection_threshold: float = 0.3):
        self.state = GuardState.PATROL
        self.detection = DetectionLevel(detection_threshold)
        
        # State timers
        self.suspicious_timer = 0.0
        self.suspicious_duration = 2.0  # Seconds to investigate before returning
        
        self.search_timer = 0.0
        self.search_duration = 6.0  # Seconds searching before giving up
        
        self.lost_sight_timer = 0.0
        self.lost_sight_delay = 3.0  # Seconds without sight before entering search
        
        # Last known player position
        self.last_known_position: Optional[Tuple[float, float]] = None
        
        # Investigation position (for suspicious state)
        self.investigation_pos: Optional[Tuple[float, float]] = None
    
    def update(self, delta_time: float, can_see_player: bool, player_pos: Tuple[float, float],
               guard_pos: Tuple[float, float]):
        """
        Update state machine.
        
        Args:
            delta_time: Time since last frame
            can_see_player: Whether guard has clear line of sight to player
            player_pos: Current player position
            guard_pos: Current guard position
        """
        # Update detection level
        self.detection.update_seeing(delta_time, can_see_player)
        
        # Update last known position if player is visible
        if can_see_player:
            self.last_known_position = player_pos
            self.lost_sight_timer = 0.0
        else:
            self.lost_sight_timer += delta_time
        
        # State transitions
        if self.state == GuardState.PATROL:
            self._update_patrol(delta_time, can_see_player, player_pos)
        
        elif self.state == GuardState.SUSPICIOUS:
            self._update_suspicious(delta_time, can_see_player)
        
        elif self.state == GuardState.ALERTED:
            self._update_alerted(delta_time, can_see_player)
        
        elif self.state == GuardState.SEARCHING:
            self._update_searching(delta_time, can_see_player, guard_pos)
    
    def _update_patrol(self, delta_time: float, can_see_player: bool, player_pos: Tuple[float, float]):
        """Update PATROL state"""
        # Transition to SUSPICIOUS if detection starts
        if self.detection.is_suspicious():
            self.state = GuardState.SUSPICIOUS
            self.suspicious_timer = 0.0
            self.investigation_pos = player_pos  # Where we think we saw something
        
        # Direct transition to ALERTED if detection is instant (very close)
        elif self.detection.is_alerted():
            self.state = GuardState.ALERTED
    
    def _update_suspicious(self, delta_time: float, can_see_player: bool):
        """Update SUSPICIOUS state"""
        self.suspicious_timer += delta_time
        
        # Transition to ALERTED if detection completes
        if self.detection.is_alerted():
            self.state = GuardState.ALERTED
            self.suspicious_timer = 0.0
        
        # Return to PATROL if nothing confirmed and timer expires
        elif self.suspicious_timer >= self.suspicious_duration and not can_see_player:
            self.state = GuardState.PATROL
            self.detection.reset()
            self.suspicious_timer = 0.0
            self.investigation_pos = None
    
    def _update_alerted(self, delta_time: float, can_see_player: bool):
        """Update ALERTED state"""
        # Transition to SEARCHING if lost sight for too long
        if not can_see_player and self.lost_sight_timer >= self.lost_sight_delay:
            self.state = GuardState.SEARCHING
            self.search_timer = 0.0
        
        # Stay alerted if still can see player
        if can_see_player:
            self.lost_sight_timer = 0.0
    
    def _update_searching(self, delta_time: float, can_see_player: bool, guard_pos: Tuple[float, float]):
        """Update SEARCHING state"""
        self.search_timer += delta_time
        
        # Re-alert if player spotted again
        if self.detection.is_alerted():
            self.state = GuardState.ALERTED
            self.search_timer = 0.0
        
        # Give up search and return to patrol
        elif self.search_timer >= self.search_duration:
            self.state = GuardState.PATROL
            self.detection.reset()
            self.search_timer = 0.0
            self.last_known_position = None
    
    def get_awareness_color(self) -> Tuple[int, int, int]:
        """Get color for awareness indicator above guard head"""
        if self.state == GuardState.PATROL:
            if self.detection.value > 0:
                # Slight detection, light yellow
                intensity = int(self.detection.value * 255)
                return (intensity, intensity, 0)
            return (128, 128, 128)  # Grey - idle
        
        elif self.state == GuardState.SUSPICIOUS:
            # Yellow, filling up based on detection
            intensity = int(128 + self.detection.value * 127)
            return (255, intensity, 0)
        
        elif self.state == GuardState.ALERTED:
            return (255, 0, 0)  # Red - alerted
        
        elif self.state == GuardState.SEARCHING:
            return (255, 128, 0)  # Orange - searching
        
        return (128, 128, 128)  # Default grey
    
    def get_awareness_fill(self) -> float:
        """Get fill percentage for awareness indicator (0.0 to 1.0)"""
        return self.detection.value
    
    def should_chase(self) -> bool:
        """Should guard chase the player?"""
        return self.state == GuardState.ALERTED
    
    def should_investigate(self) -> bool:
        """Should guard investigate a position?"""
        return self.state == GuardState.SUSPICIOUS or self.state == GuardState.SEARCHING
    
    def get_target_position(self) -> Optional[Tuple[float, float]]:
        """Get position guard should move to (investigation or last known)"""
        if self.state == GuardState.SUSPICIOUS and self.investigation_pos:
            return self.investigation_pos
        elif self.state == GuardState.SEARCHING and self.last_known_position:
            return self.last_known_position
        return None


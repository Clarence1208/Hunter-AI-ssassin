"""
Observation Visualization Tool

This script helps visualize what the RL agent "sees" by displaying the observation vector
in a human-readable format. Useful for debugging and understanding the state representation.
"""
import numpy as np
from game_env import HunterAssassinEnv
import config
import time


def print_observation_breakdown(obs: np.ndarray):
    """
    Print a detailed breakdown of the observation vector.
    
    Args:
        obs: Observation array from the environment
    """
    idx = 0
    
    print("\n" + "="*60)
    print("OBSERVATION BREAKDOWN")
    print("="*60)
    
    # Ray cast distances
    print(f"\n1. Ray Cast Distances ({config.NUM_RAYS} rays):")
    print("   (Normalized: 0=close obstacle, 1=max distance)")
    ray_distances = obs[idx:idx+config.NUM_RAYS]
    idx += config.NUM_RAYS
    
    for i, dist in enumerate(ray_distances):
        angle = (360 / config.NUM_RAYS) * i
        bar = "█" * int(dist * 20)
        print(f"   Ray {i:2d} ({angle:3.0f}°): [{bar:<20}] {dist:.3f}")
    
    # Player info
    print(f"\n2. Player Information:")
    player_x = obs[idx]
    player_y = obs[idx+1]
    player_alive = obs[idx+2]
    idx += 3
    
    print(f"   Position: ({player_x:.3f}, {player_y:.3f}) [normalized]")
    print(f"   Actual Position: ({player_x * config.SCREEN_WIDTH:.1f}, {player_y * config.SCREEN_HEIGHT:.1f})")
    print(f"   Alive: {'Yes' if player_alive > 0.5 else 'No'}")
    
    # Enemy info
    print(f"\n3. Enemy Information (up to {config.NUM_ENEMIES} enemies):")
    for i in range(config.NUM_ENEMIES):
        enemy_rel_x = obs[idx]
        enemy_rel_y = obs[idx+1]
        enemy_dist = obs[idx+2]
        enemy_alive = obs[idx+3]
        enemy_alert = obs[idx+4]
        idx += 5
        
        print(f"\n   Enemy {i+1}:")
        print(f"     Relative Position: ({enemy_rel_x:+.3f}, {enemy_rel_y:+.3f})")
        print(f"     Distance: {enemy_dist:.3f} ({'~' + str(int(enemy_dist * config.SCREEN_WIDTH)) + ' pixels'})")
        print(f"     Alive: {'Yes' if enemy_alive > 0.5 else 'No'}")
        print(f"     Alert: {'Yes' if enemy_alert > 0.5 else 'No'}")
        
        if enemy_alive > 0.5:
            # Show direction
            if abs(enemy_rel_x) > abs(enemy_rel_y):
                direction = "RIGHT" if enemy_rel_x > 0 else "LEFT"
            else:
                direction = "UP" if enemy_rel_y > 0 else "DOWN"
            print(f"     Direction: {direction}")
    
    print("\n" + "="*60)
    print(f"Total observation size: {len(obs)}")
    print("="*60 + "\n")


def visualize_live_observations(num_steps: int = 50, delay: float = 0.5):
    """
    Run the game and continuously display observations.
    
    Args:
        num_steps: Number of steps to visualize
        delay: Delay between steps in seconds
    """
    env = HunterAssassinEnv(render_mode=True)
    obs = env.reset()
    
    print("\n" + "="*60)
    print("LIVE OBSERVATION VISUALIZATION")
    print("="*60)
    print(f"Running for {num_steps} steps with random actions")
    print(f"Delay: {delay}s between steps")
    print("="*60)
    
    for step in range(num_steps):
        # Random action
        action = np.random.randint(0, config.NUM_ACTIONS)
        action_name = list(config.ACTIONS.keys())[action]
        action_dir = config.ACTIONS[action]
        
        print(f"\n{'='*60}")
        print(f"STEP {step + 1}/{num_steps}")
        print(f"Action: {action_name} -> Direction: {action_dir}")
        print(f"{'='*60}")
        
        obs, reward, done, info = env.step(action)
        
        print(f"\nReward: {reward:.2f}")
        print(f"Kills: {info['kills']}")
        print(f"Enemies Alive: {info['enemies_alive']}")
        
        # Show observation breakdown
        print_observation_breakdown(obs)
        
        # Render
        env.on_draw()
        env.flip()
        
        if done:
            print("\n" + "="*60)
            print("EPISODE ENDED")
            print("="*60)
            if info.get('win'):
                print("Result: VICTORY! All enemies eliminated!")
            elif info.get('death'):
                print("Result: DEFEATED! Player was caught!")
            elif info.get('timeout'):
                print("Result: TIMEOUT! Episode limit reached!")
            print(f"Final Reward: {info['total_reward']:.2f}")
            print("="*60 + "\n")
            break
        
        time.sleep(delay)
    
    env.close()


def compare_observations():
    """
    Compare observations from different game states.
    Useful for understanding how observations change.
    """
    env = HunterAssassinEnv(render_mode=False)
    
    print("\n" + "="*60)
    print("OBSERVATION COMPARISON")
    print("="*60)
    
    # Initial state
    print("\n--- INITIAL STATE ---")
    obs1 = env.reset()
    print_observation_breakdown(obs1)
    
    # After moving
    print("\n--- AFTER MOVING RIGHT ---")
    obs2, _, _, _ = env.step(4)  # Move right
    print_observation_breakdown(obs2)
    
    # Show differences
    print("\n--- OBSERVATION DIFFERENCES ---")
    diff = obs2 - obs1
    significant_changes = np.where(np.abs(diff) > 0.01)[0]
    
    print(f"Number of changed values: {len(significant_changes)}")
    print("Significant changes (abs > 0.01):")
    for i in significant_changes:
        print(f"  Index {i}: {obs1[i]:.4f} -> {obs2[i]:.4f} (Δ {diff[i]:+.4f})")
    
    env.close()


def main():
    """Main visualization tool menu."""
    print("\n" + "="*60)
    print("OBSERVATION VISUALIZATION TOOL")
    print("="*60)
    print("\nThis tool helps you understand what the RL agent observes.")
    print("\nOptions:")
    print("  1. Show single observation breakdown")
    print("  2. Live observation visualization (with rendering)")
    print("  3. Compare observations between states")
    print("  4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        env = HunterAssassinEnv(render_mode=False)
        obs = env.reset()
        print_observation_breakdown(obs)
        env.close()
        
    elif choice == "2":
        num_steps = int(input("Number of steps to visualize [50]: ").strip() or "50")
        delay = float(input("Delay between steps in seconds [0.5]: ").strip() or "0.5")
        visualize_live_observations(num_steps, delay)
        
    elif choice == "3":
        compare_observations()
        
    else:
        print("Exiting...")


if __name__ == "__main__":
    main()

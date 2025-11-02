"""
Hunter Assassin Game - Main Entry Point

This is the main entry point for running the Hunter Assassin game.
You can run this for manual play or use game_env.HunterAssassinEnv for RL training.

Usage:
    python main.py              # Run game with rendering
    python main.py --no-render  # Run without rendering (faster for RL)
    python main.py --demo       # Run a quick demo with random actions
"""
import arcade
import argparse
import numpy as np
from game_env import HunterAssassinEnv
import config


def play_game(render: bool = True):
    """
    Run the game in manual play mode.
    
    Args:
        render: If True, render the game window
    """
    game = HunterAssassinEnv(render_mode=render)
    
    if render:
        print("\n" + "="*60)
        print("Hunter Assassin - Manual Play Mode")
        print("="*60)
        print("\nControls:")
        print("  WASD or Arrow Keys - Move")
        print("  SPACE - Toggle vision rays")
        print("  V - Toggle enemy vision cones")
        print("  R - Reset game")
        print("  ESC - Quit")
        print("\nObjective:")
        print("  Eliminate all enemies without being caught!")
        print("  Get close to enemies to attack them.")
        print("  Stay out of enemy vision cones (yellow).")
        print("="*60 + "\n")
        
        arcade.run()
    else:
        print("Running in headless mode (no rendering)")
        # In headless mode, you would typically call step() manually
        # This is useful for RL training loops


def run_demo(num_episodes: int = 3, render: bool = True):
    """
    Run a demo with random actions to showcase the game.

    Args:
        num_episodes: Number of episodes to run
        render: If True, render the game
    """
    print("\n" + "="*60)
    print("Hunter Assassin - Random Action Demo")
    print("="*60)
    print(f"\nRunning {num_episodes} episodes with random actions...")
    print("This demonstrates the RL interface.\n")

    game = HunterAssassinEnv(render_mode=render)

    for episode in range(num_episodes):
        print(f"\n--- Episode {episode + 1}/{num_episodes} ---")
        obs = game.reset()
        print(f"Observation space size: {len(obs)}")
        print(f"Action space size: {config.NUM_ACTIONS}")

        arcade.run()
        done = False
        episode_reward = 0
        steps = 0

        while not done:
            # Random action
            action = np.random.randint(0, config.NUM_ACTIONS)
            obs, reward, done, info = game.step(action)

            episode_reward += reward
            steps += 1

            if render:
                game.on_draw()
                game.flip()

            # Print significant events
            if "kill" in info:
                print(f"  [Step {steps}] Enemy eliminated! Reward: +{config.PLAYER_KILL_REWARD}")
            if "death" in info:
                print(f"  [Step {steps}] Player caught! Reward: {config.DEATH_PENALTY}")
            if "win" in info:
                print(f"  [Step {steps}] Victory! All enemies eliminated!")
            if "timeout" in info:
                print(f"  [Step {steps}] Episode timeout reached.")

        print(f"\nEpisode {episode + 1} Summary:")
        print(f"  Total Steps: {steps}")
        print(f"  Total Reward: {episode_reward:.2f}")
        print(f"  Kills: {info['kills']}")
        print(f"  Enemies Remaining: {info['enemies_alive']}")
        print(f"  Player Survived: {info['player_alive']}")

    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60 + "\n")

    if render:
        game.close()


def test_rl_interface():
    """
    Test the RL interface without rendering.
    Demonstrates how to use the environment for training.
    """
    print("\n" + "="*60)
    print("Testing RL Interface (Headless)")
    print("="*60 + "\n")

    # Create environment without rendering
    env = HunterAssassinEnv(render_mode=True)

    print("Environment Information:")
    print(f"  Observation Space Size: {env.get_observation_space_size()}")
    print(f"  Action Space Size: {env.get_action_space_size()}")
    print(f"  Max Steps per Episode: {config.MAX_STEPS_PER_EPISODE}")

    # Run a quick test episode
    print("\nRunning test episode...")
    obs = env.reset()
    print(f"  Initial observation shape: {obs.shape}")
    print(f"  Initial observation (first 10 values): {obs[:10]}")

    # Take a few random steps
    total_reward = 0
    for step in range(10):
        action = np.random.randint(0, env.get_action_space_size())
        obs, reward, done, info = env.step(action)
        total_reward += reward

        if done:
            print(f"\n  Episode ended at step {step + 1}")
            break

    print(f"\n  Reward after 10 steps: {total_reward:.2f}")
    print(f"  Final observation shape: {obs.shape}")

    env.close()

    print("\n" + "="*60)
    print("RL Interface Test Complete!")
    print("="*60)
    print("\nYou can now integrate this environment with your RL framework.")
    print("Example integration patterns:")
    print("  - Stable-Baselines3: Use a wrapper to convert to Gym interface")
    print("  - PyTorch/TensorFlow: Use env.step() and env.reset() directly")
    print("  - RLlib: Create a custom RLlib environment wrapper")
    print("="*60 + "\n")


def main():
    """Main entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(description="Hunter Assassin Game - RL Ready")
    parser.add_argument(
        "--mode",
        type=str,
        default="play",
        choices=["play", "demo", "test"],
        help="Game mode: play (manual), demo (random actions), or test (RL interface test)"
    )
    parser.add_argument(
        "--no-render",
        action="store_true",
        help="Run without rendering (headless mode)"
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=3,
        help="Number of episodes for demo mode"
    )
    
    args = parser.parse_args()
    
    render = not args.no_render
    
    if args.mode == "play":
        play_game(render=render)
    elif args.mode == "demo":
        run_demo(num_episodes=args.episodes, render=render)
    elif args.mode == "test":
        test_rl_interface()


if __name__ == "__main__":
    main()
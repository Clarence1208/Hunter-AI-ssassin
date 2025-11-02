import numpy as np
from game_env import HunterAssassinEnv


class RandomAgent:
    """
    A simple random agent baseline.
    Useful for testing the environment and as a baseline for comparison.
    """
    
    def __init__(self, action_space_size):
        self.action_space_size = action_space_size
    
    def select_action(self, observation):
        """Select a random action."""
        return np.random.randint(0, self.action_space_size)
    
    def learn(self, obs, action, reward, next_obs, done):
        """Random agent doesn't learn."""
        pass


class SimpleQLearningAgent:
    """
    A simple Q-learning agent with discretized state space.
    This is a basic example - for real training, use deep RL algorithms.
    """
    
    def __init__(self, observation_size, action_space_size):
        self.observation_size = observation_size
        self.action_space_size = action_space_size
        
        # Hyperparameters
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.gamma = 0.99  # Discount factor
        

        print(f"Initialized agent with obs_size={observation_size}, action_size={action_space_size}")
    
    def select_action(self, observation):
        """Epsilon-greedy action selection."""
        if np.random.random() < self.epsilon:
            return np.random.randint(0, self.action_space_size)
        else:
            # In real implementation, this would use your Q-network
            return np.random.randint(0, self.action_space_size)
    
    def learn(self, obs, action, reward, next_obs, done):
        """Update Q-values based on experience."""
        # In real implementation, this would update your neural network
        # using the (obs, action, reward, next_obs, done) tuple
        pass
    
    def decay_epsilon(self):
        """Decay exploration rate."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)


def train_agent(agent, num_episodes=1000, render=True, print_every=10):
    """
    Train an agent in the Hunter Assassin environment.
    
    Args:
        agent: The agent to train (must have select_action and learn methods)
        num_episodes: Number of episodes to train
        render: Whether to render the game
        print_every: Print statistics every N episodes
    """
    env = HunterAssassinEnv(render_mode=render)
    
    # Statistics
    episode_rewards = []
    episode_lengths = []
    episode_kills = []
    wins = 0
    
    print("\n" + "="*60)
    print("Starting Training")
    print("="*60)
    print(f"Episodes: {num_episodes}")
    print(f"Observation size: {env.get_observation_space_size()}")
    print(f"Action space: {env.get_action_space_size()}")
    print(f"Rendering: {render}")
    print("="*60 + "\n")
    
    for episode in range(num_episodes):
        obs = env.reset()
        done = False
        episode_reward = 0
        steps = 0
        
        while not done:
            # Agent selects action
            action = agent.select_action(obs)
            
            # Execute action
            next_obs, reward, done, info = env.step(action)
            
            # Agent learns from experience
            agent.learn(obs, action, reward, next_obs, done)
            
            # Update state
            obs = next_obs
            episode_reward += reward
            steps += 1
            
            # Render if enabled
            if render:
                env.on_draw()
                env.flip()
        
        # Record statistics
        episode_rewards.append(episode_reward)
        episode_lengths.append(steps)
        episode_kills.append(info['kills'])
        if info.get('win', False):
            wins += 1
        
        # Decay exploration (if agent supports it)
        if hasattr(agent, 'decay_epsilon'):
            agent.decay_epsilon()
        
        # Print progress
        if (episode + 1) % print_every == 0:
            avg_reward = np.mean(episode_rewards[-print_every:])
            avg_length = np.mean(episode_lengths[-print_every:])
            avg_kills = np.mean(episode_kills[-print_every:])
            win_rate = sum(1 for i in range(episode - print_every + 1, episode + 1) 
                          if i < len(episode_rewards) and info.get('win', False)) / print_every
            
            print(f"Episode {episode + 1}/{num_episodes}")
            print(f"  Avg Reward: {avg_reward:.2f}")
            print(f"  Avg Length: {avg_length:.1f}")
            print(f"  Avg Kills: {avg_kills:.2f}")
            print(f"  Win Rate: {win_rate*100:.1f}%")
            print(f"  Total Wins: {wins}")
            if hasattr(agent, 'epsilon'):
                print(f"  Epsilon: {agent.epsilon:.4f}")
            print()
    
    env.close()
    
    print("\n" + "="*60)
    print("Training Complete")
    print("="*60)
    print(f"Total Episodes: {num_episodes}")
    print(f"Total Wins: {wins} ({wins/num_episodes*100:.1f}%)")
    print(f"Average Reward: {np.mean(episode_rewards):.2f}")
    print(f"Average Kills: {np.mean(episode_kills):.2f}")
    print(f"Best Episode Reward: {max(episode_rewards):.2f}")
    print("="*60 + "\n")
    
    return episode_rewards, episode_lengths, episode_kills


def evaluate_agent(agent, num_episodes=5, render=False):
    env = HunterAssassinEnv(render_mode=render)
    total_rewards = []

    for episode in range(num_episodes):
        state, _ = env.reset()
        done = False
        episode_reward = 0

        while not done:
            action = agent.choose_action(state)
            next_state, reward, done, truncated, _ = env.step(action)
            episode_reward += reward
            state = next_state

            if render:
                env.render()

        total_rewards.append(episode_reward)
        print(f"Épisode {episode+1}/{num_episodes} terminé — Score: {episode_reward:.2f}")

        # ✅ Relance la partie automatiquement
        if done:
            state, _ = env.reset()

    env.close()
    avg_reward = sum(total_rewards) / len(total_rewards)
    print(f"Récompense moyenne sur {num_episodes} épisodes : {avg_reward:.2f}")


def main():
    """Main training script."""
    print("\n" + "="*60)
    print("Hunter Assassin - RL Training Example")
    print("="*60)
    print("\nThis is a template for training RL agents.")
    print("Replace RandomAgent with your actual RL algorithm.\n")
    
    # Create environment to get dimensions
    temp_env = HunterAssassinEnv(render_mode=False)
    obs_size = temp_env.get_observation_space_size()
    action_size = temp_env.get_action_space_size()
    temp_env.close()
    
    # Choose agent type
    print("Select agent type:")
    print("  1. Random Agent (baseline)")
    print("  2. Q-Learning Agent (placeholder)")
    print("  3. Your Custom Agent (modify this script)")
    
    choice = input("\nEnter choice (1-3) [default: 1]: ").strip()
    
    if choice == "2":
        agent = SimpleQLearningAgent(obs_size, action_size)
        print("\nNote: This Q-Learning agent is a placeholder.")
        print("For real training, integrate with DQN, PPO, A3C, etc.\n")
    else:
        agent = RandomAgent(action_size)
        print("\nUsing Random Agent as baseline.\n")
    
    # Training parameters
    num_episodes = int(input("Number of training episodes [default: 100]: ").strip() or "100")
    render = input("Render during training? (y/n) [default: n]: ").strip().lower() == 'y'
    
    # Train
    rewards, lengths, kills = train_agent(
        agent,
        num_episodes=num_episodes,
        render=render,
        print_every=max(1, num_episodes // 10)
    )
    
    # Evaluate
    eval_choice = input("\nEvaluate agent? (y/n) [default: y]: ").strip().lower()
    if eval_choice != 'n':
        num_eval_episodes = int(input("Number of evaluation episodes [default: 5]: ").strip() or "5")
        evaluate_agent(agent, num_episodes=num_eval_episodes, render=True)



if __name__ == "__main__":
    main()

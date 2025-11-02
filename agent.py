"""
Simple Q-Learning Agent for Hunter Assassin Game
Q-table gardée uniquement en mémoire (dans le code)
"""
import numpy as np
from typing import Tuple
import random


"""
Simple Q-Learning Agent for Hunter Assassin Game
Version adaptée au déplacement grille 16×16, 4 actions (haut, bas, gauche, droite)
"""
import numpy as np
from typing import Tuple
import random


class SimpleAgent:
    """
    Agent Q-Learning discret pour environnement grille 16x16.
    Chaque état = position (x, y) du joueur dans la grille.
    """

    def __init__(self):
        """Initialiser l'agent simple."""
        # Q-table en mémoire: dictionnaire {état: [Q-values pour chaque action]}
        # 4 actions possibles: haut, bas, gauche, droite
        self.qtable = {}

        # Paramètres d'apprentissage
        self.alpha = 0.1     # Learning rate
        self.gamma = 0.95    # Discount factor
        self.epsilon = 1.0   # Exploration initiale
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995

        # Statistiques
        self.episodes = 0
        self.total_reward = 0
        self.episode_rewards = []

        print("✓ Agent initialisé (4 actions, Q-table vide en mémoire)")

    def get_state(self, observation: np.ndarray) -> Tuple[int, int]:
        """
        Convertir l'observation en état discret basé sur la position du joueur.

        Args:
            observation: observation brute du jeu

        Returns:
            état sous forme de tuple (x, y)
        """
        num_rays = 16
        player_x = observation[num_rays]      # Position X normalisée (0-1)
        player_y = observation[num_rays + 1]  # Position Y normalisée (0-1)

        # Convertir en coordonnées grille 16x16
        grid_x = int(player_x * 16)
        grid_y = int(player_y * 16)

        # Bornes de sécurité
        grid_x = max(0, min(15, grid_x))
        grid_y = max(0, min(15, grid_y))

        return (grid_x, grid_y)

    def choose_action(self, state: Tuple[int, int]) -> int:
        """
        Choisir une action selon la stratégie epsilon-greedy.
        Actions: 0=Up, 1=Down, 2=Left, 3=Right
        """
        num_actions = 4

        # Exploration
        if random.random() < self.epsilon:
            return random.randint(0, num_actions - 1)

        # Exploitation
        if state in self.qtable:
            return int(np.argmax(self.qtable[state]))
        else:
            return random.randint(0, num_actions - 1)

    def learn(self, state: Tuple[int, int], action: int, reward: float, next_state: Tuple[int, int], done: bool):
        """
        Met à jour la Q-table selon la règle du Q-learning.
        """
        num_actions = 4

        if state not in self.qtable:
            self.qtable[state] = [0.0] * num_actions
        if next_state not in self.qtable:
            self.qtable[next_state] = [0.0] * num_actions

        current_q = self.qtable[state][action]
        max_next_q = 0 if done else max(self.qtable[next_state])

        # Q-learning update
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.qtable[state][action] = new_q

        self.total_reward += reward

    def end_episode(self, episode_reward: float):
        """
        Appelé à la fin d’un épisode.
        """
        self.episodes += 1
        self.episode_rewards.append(episode_reward)
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def get_stats(self) -> dict:
        """Retourne les statistiques d'entraînement."""
        if not self.episode_rewards:
            return {
                "episodes": 0,
                "qtable_size": 0,
                "avg_reward": 0,
                "best_reward": 0,
                "recent_avg": 0
            }

        recent_window = min(100, len(self.episode_rewards))
        recent_rewards = self.episode_rewards[-recent_window:]

        return {
            "episodes": self.episodes,
            "qtable_size": len(self.qtable),
            "avg_reward": np.mean(self.episode_rewards),
            "best_reward": max(self.episode_rewards),
            "recent_avg": np.mean(recent_rewards)
        }

    def show_qtable(self):
        """Afficher un extrait de la Q-table."""
        print("\n" + "=" * 60)
        print("Q-TABLE (extrait)")
        print("=" * 60)

        if not self.qtable:
            print("Q-table vide!")
            return

        for i, (state, q_values) in enumerate(self.qtable.items()):
            if i >= 10:
                print(f"... et {len(self.qtable) - 10} autres états")
                break
            best_action = int(np.argmax(q_values))
            best_value = max(q_values)
            print(f"État {state}: meilleure action={best_action}, Q={best_value:.2f}")

        print("=" * 60 + "\n")

def train_simple(num_episodes: int = 100, render: bool = False):
    """
    Entraîner l'agent simple.

    Args:
        num_episodes: nombre d'épisodes d'entraînement
        render: afficher le jeu?
    """
    from game_env import HunterAssassinEnv

    print("\n" + "=" * 60)
    print("ENTRAÎNEMENT AGENT SIMPLE")
    print("=" * 60)
    print(f"Épisodes: {num_episodes}")
    print(f"Affichage: {'Oui' if render else 'Non'}")
    print("=" * 60 + "\n")

    # Créer environnement et agent
    env = HunterAssassinEnv(render_mode=render)
    agent = SimpleAgent()

    for episode in range(num_episodes):
        # Reset
        obs = env.reset()
        state = agent.get_state(obs)

        episode_reward = 0
        steps = 0
        done = False

        while not done:
            # Choisir et exécuter action
            action = agent.choose_action(state)
            next_obs, reward, done, info = env.step(action)
            next_state = agent.get_state(next_obs)

            # Apprendre
            agent.learn(state, action, reward, next_state, done)

            state = next_state
            episode_reward += reward
            steps += 1

            if render:
                env.on_draw()
                env.flip()

        # Fin épisode
        agent.end_episode(episode_reward)

        # Afficher progression tous les 10 épisodes
        if (episode + 1) % 10 == 0:
            print(f"Épisode {agent.episodes:3d}/{num_episodes} | "
                  f"Reward: {episode_reward:6.1f} | "
                  f"Steps: {steps:3d} | "
                  f"Epsilon: {agent.epsilon:.3f} | "
                  f"États Q: {len(agent.qtable)}")

    # Afficher statistiques finales
    stats = agent.get_stats()

    print("\n" + "=" * 60)
    print("ENTRAÎNEMENT TERMINÉ!")
    print("=" * 60)
    print(f"Total épisodes: {stats['episodes']}")
    print(f"États dans Q-table: {stats['qtable_size']}")
    print(f"Reward moyen: {stats['avg_reward']:.1f}")
    print(f"Meilleur reward: {stats['best_reward']:.1f}")
    print(f"Reward moyen (100 derniers): {stats['recent_avg']:.1f}")
    print(f"Epsilon final: {agent.epsilon:.4f}")
    print("=" * 60 + "\n")

    # Afficher un extrait de la Q-table
    agent.show_qtable()

    if render:
        env.close()

    return agent  # Retourner l'agent entraîné


class TestWindow:
    """Classe pour gérer l'affichage du test de l'agent."""

    def __init__(self, agent: SimpleAgent, num_episodes: int = 5):
        from game_env import HunterAssassinEnv

        self.agent = agent
        self.num_episodes = num_episodes
        self.env = HunterAssassinEnv(render_mode=True)

        # Statistiques
        self.current_episode = 0
        self.episode_reward = 0
        self.steps = 0
        self.wins = 0
        self.total_reward = 0

        # État du jeu
        self.state = None
        self.done = False
        self.frame_counter = 0

        # Démarrer premier épisode
        self._start_episode()

    def _start_episode(self):
        """Démarrer un nouvel épisode."""
        if self.current_episode >= self.num_episodes:
            print(f"\n{'=' * 60}")
            print("TEST TERMINÉ!")
            print(f"{'=' * 60}")
            print(f"Victoires: {self.wins}/{self.num_episodes} ({100 * self.wins / self.num_episodes:.0f}%)")
            print(f"Reward moyen: {self.total_reward / self.num_episodes:.1f}")
            print(f"{'=' * 60}\n")
            self.env.close()
            return

        self.current_episode += 1
        print(f"\nÉpisode {self.current_episode}/{self.num_episodes}")

        obs = self.env.reset()
        self.state = self.agent.get_state(obs)
        self.episode_reward = 0
        self.steps = 0
        self.done = False
        self.frame_counter = 0

    def update(self):
        """Mise à jour de chaque frame."""
        if self.done:
            # Pause entre les épisodes
            self.frame_counter += 1
            if self.frame_counter > 60:  # 1 seconde de pause
                self._start_episode()
            return

        # Ralentir l'agent pour qu'on puisse le voir (1 action toutes les 3 frames)
        self.frame_counter += 1
        if self.frame_counter % 3 != 0:
            return

        # Choisir et exécuter action
        action = self.agent.choose_action(self.state)
        next_obs, reward, self.done, info = self.env.step(action)
        next_state = self.agent.get_state(next_obs)

        self.state = next_state
        self.episode_reward += reward
        self.steps += 1

        # Si l'épisode est terminé
        if self.done:
            self.total_reward += self.episode_reward

            print(f"  Reward: {self.episode_reward:.1f} | Steps: {self.steps}")
            if "win" in info:
                print("  ✓ VICTOIRE!")
                self.wins += 1
            elif "death" in info:
                print("  ✗ Mort")

            self.frame_counter = 0


def test_simple(agent: SimpleAgent = None, num_episodes: int = 5):
    """
    Tester l'agent entraîné (avec affichage).

    Args:
        agent: agent déjà entraîné (ou None pour en créer un vide)
        num_episodes: nombre d'épisodes de test
    """
    import arcade

    print("\n" + "=" * 60)
    print("TEST AGENT SIMPLE")
    print("=" * 60 + "\n")

    if agent is None:
        print("⚠ Aucun agent fourni, création d'un agent vide (non entraîné)")
        agent = SimpleAgent()
    else:
        print(f"✓ Utilisation d'un agent entraîné ({len(agent.qtable)} états)")

    # Mode exploitation pure (pas d'exploration)
    original_epsilon = agent.epsilon
    agent.epsilon = 0.0

    # Créer le gestionnaire de test
    test_window = TestWindow(agent, num_episodes)

    # Fonction de mise à jour appelée par arcade
    def on_update(delta_time):
        test_window.update()
        test_window.env.on_draw()

    # Lancer la boucle arcade
    arcade.schedule(on_update, 1 / 60)  # 60 FPS
    arcade.run()

    # Restaurer epsilon
    agent.epsilon = original_epsilon


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "train":
            episodes = int(sys.argv[2]) if len(sys.argv) > 2 else 100
            agent = train_simple(num_episodes=episodes, render=False)

            # Proposer de tester
            print("\nVoulez-vous tester l'agent? (Il va perdre sa mémoire après)")
            response = input("Taper 'oui' pour tester: ")
            if response.lower() in ['oui', 'o', 'yes', 'y']:
                test_simple(agent=agent, num_episodes=5)

        elif sys.argv[1] == "test":
            print("⚠ Mode test sans entraînement préalable")
            print("L'agent va jouer aléatoirement (Q-table vide)\n")
            test_simple(num_episodes=5)

        else:
            print("Usage:")
            print("  python rl_agent.py train [episodes]  # Entraîner")
            print("  python rl_agent.py test              # Tester (vide)")
    else:
        print("Agent Q-Learning Simple (Q-table en mémoire)")
        print("\nUsage:")
        print("  python rl_agent.py train 100   # Entraîner 100 épisodes")
        print("  python rl_agent.py train 500   # Entraîner 500 épisodes")
        print("  python rl_agent.py test        # Tester agent vide")
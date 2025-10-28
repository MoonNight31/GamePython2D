import os
import numpy as np
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import BaseCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
import matplotlib.pyplot as plt
from typing import Any, Dict
import time

from .ai_environment import GameAIEnvironment

class TrainingCallback(BaseCallback):
    """Callback personnalisé pour surveiller l'entraînement."""
    
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.episode_rewards = []
        self.episode_lengths = []
        self.enemies_killed_log = []
        self.survival_times = []
        
    def _on_step(self) -> bool:
        # Récupérer les infos de l'environnement
        if len(self.locals.get('infos', [])) > 0:
            info = self.locals['infos'][0]
            
            # Si un épisode est terminé
            if self.locals.get('dones', [False])[0]:
                episode_reward = info.get('total_reward', 0)
                survival_time = info.get('survival_time', 0)
                enemies_killed = info.get('enemies_killed', 0)
                
                self.episode_rewards.append(episode_reward)
                self.survival_times.append(survival_time)
                self.enemies_killed_log.append(enemies_killed)
                
                if self.verbose > 0 and len(self.episode_rewards) % 10 == 0:
                    print(f"Épisode {len(self.episode_rewards)}: "
                          f"Récompense={episode_reward:.2f}, "
                          f"Survie={survival_time}, "
                          f"Ennemis tués={enemies_killed}")
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques d'entraînement."""
        if not self.episode_rewards:
            return {}
        
        return {
            'episodes_count': len(self.episode_rewards),
            'avg_reward': np.mean(self.episode_rewards[-100:]),  # Moyenne des 100 derniers
            'max_reward': np.max(self.episode_rewards),
            'avg_survival': np.mean(self.survival_times[-100:]),
            'max_survival': np.max(self.survival_times),
            'avg_enemies_killed': np.mean(self.enemies_killed_log[-100:]),
            'max_enemies_killed': np.max(self.enemies_killed_log)
        }

class GameAITrainer:
    """Classe principale pour entraîner l'IA."""
    
    def __init__(self, model_name: str = "game_ai_model"):
        self.model_name = model_name
        self.model_dir = "ai_models"
        self.log_dir = "ai_logs"
        
        # Créer les répertoires
        os.makedirs(self.model_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.model = None
        self.env = None
        self.callback = None
        
    def create_environment(self, n_envs: int = 4, render_mode: str = None):
        """Crée l'environnement d'entraînement."""
        def make_env():
            env = GameAIEnvironment(render_mode=render_mode)
            env = Monitor(env, filename=None)  # Pour logging automatique
            return env
        
        if n_envs == 1:
            self.env = DummyVecEnv([make_env])
        else:
            # Environnements parallèles pour accélérer l'entraînement
            self.env = DummyVecEnv([make_env for _ in range(n_envs)])
        
        return self.env
    
    def create_model(self, learning_rate: float = 3e-4, n_steps: int = 2048, 
                    batch_size: int = 64, n_epochs: int = 10):
        """Crée le modèle PPO."""
        if self.env is None:
            raise ValueError("L'environnement doit être créé avant le modèle")
        
        # Configuration du modèle PPO
        self.model = PPO(
            "MlpPolicy",  # Politique Multi-Layer Perceptron
            self.env,
            learning_rate=learning_rate,
            n_steps=n_steps,
            batch_size=batch_size,
            n_epochs=n_epochs,
            gamma=0.99,  # Facteur de discount
            gae_lambda=0.95,  # Generalized Advantage Estimation
            clip_range=0.2,  # Clipping PPO
            ent_coef=0.01,  # Coefficient d'entropie pour l'exploration
            vf_coef=0.5,  # Coefficient de la value function
            max_grad_norm=0.5,  # Gradient clipping
            tensorboard_log=self.log_dir,
            verbose=1
        )
        
        return self.model
    
    def train(self, total_timesteps: int = 100000, save_freq: int = 10000):
        """Entraîne le modèle."""
        if self.model is None:
            raise ValueError("Le modèle doit être créé avant l'entraînement")
        
        print(f"🤖 Début de l'entraînement pour {total_timesteps} timesteps")
        print(f"📊 Logs sauvegardés dans : {self.log_dir}")
        print(f"💾 Modèles sauvegardés dans : {self.model_dir}")
        
        # Callback pour surveiller l'entraînement
        self.callback = TrainingCallback(verbose=1)
        
        # Callback pour sauvegarder périodiquement
        checkpoint_callback = None
        if save_freq > 0:
            checkpoint_callback = [
                self.callback,
                # Sauvegarde automatique
                EvalCallback(
                    self.env, 
                    best_model_save_path=f"{self.model_dir}/best_{self.model_name}",
                    log_path=f"{self.log_dir}/eval",
                    eval_freq=save_freq,
                    deterministic=True,
                    render=False
                )
            ]
        else:
            checkpoint_callback = self.callback
        
        # Entraînement
        start_time = time.time()
        self.model.learn(
            total_timesteps=total_timesteps,
            callback=checkpoint_callback,
            tb_log_name=self.model_name
        )
        
        training_time = time.time() - start_time
        print(f"✅ Entraînement terminé en {training_time:.2f} secondes")
        
        # Sauvegarder le modèle final
        model_path = f"{self.model_dir}/{self.model_name}_final"
        self.model.save(model_path)
        print(f"💾 Modèle final sauvegardé : {model_path}")
        
        return self.model
    
    def load_model(self, model_path: str = None):
        """Charge un modèle pré-entraîné."""
        if model_path is None:
            model_path = f"{self.model_dir}/{self.model_name}_final"
        
        if not os.path.exists(f"{model_path}.zip"):
            raise FileNotFoundError(f"Modèle non trouvé : {model_path}.zip")
        
        self.model = PPO.load(model_path, env=self.env)
        print(f"📂 Modèle chargé : {model_path}")
        return self.model
    
    def evaluate(self, n_episodes: int = 10, render: bool = False):
        """Évalue les performances du modèle."""
        if self.model is None:
            raise ValueError("Aucun modèle chargé")
        
        print(f"🎯 Évaluation sur {n_episodes} épisodes...")
        
        # Créer un environnement de test
        test_env = GameAIEnvironment(render_mode="human" if render else None)
        
        episode_rewards = []
        episode_lengths = []
        enemies_killed_list = []
        survival_times = []
        
        for episode in range(n_episodes):
            obs, _ = test_env.reset()
            episode_reward = 0
            episode_length = 0
            done = False
            
            while not done:
                action, _ = self.model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = test_env.step(action)
                episode_reward += reward
                episode_length += 1
                done = terminated or truncated
                
                if render:
                    test_env.render()
            
            episode_rewards.append(episode_reward)
            episode_lengths.append(episode_length)
            enemies_killed_list.append(info.get('enemies_killed', 0))
            survival_times.append(info.get('survival_time', 0))
            
            print(f"Épisode {episode + 1}: "
                  f"Récompense={episode_reward:.2f}, "
                  f"Survie={survival_times[-1]}, "
                  f"Ennemis={enemies_killed_list[-1]}")
        
        test_env.close()
        
        # Statistiques
        stats = {
            'avg_reward': np.mean(episode_rewards),
            'std_reward': np.std(episode_rewards),
            'max_reward': np.max(episode_rewards),
            'min_reward': np.min(episode_rewards),
            'avg_length': np.mean(episode_lengths),
            'avg_survival': np.mean(survival_times),
            'max_survival': np.max(survival_times),
            'avg_enemies_killed': np.mean(enemies_killed_list),
            'max_enemies_killed': np.max(enemies_killed_list)
        }
        
        print("\n📊 Statistiques d'évaluation:")
        for key, value in stats.items():
            print(f"  {key}: {value:.2f}")
        
        return stats
    
    def plot_training_progress(self):
        """Affiche les graphiques de progression de l'entraînement."""
        if self.callback is None or not self.callback.episode_rewards:
            print("Aucune donnée d'entraînement à afficher")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Progression de l\'entraînement IA', fontsize=16)
        
        episodes = range(len(self.callback.episode_rewards))
        
        # Récompenses par épisode
        axes[0, 0].plot(episodes, self.callback.episode_rewards)
        axes[0, 0].set_title('Récompenses par épisode')
        axes[0, 0].set_xlabel('Épisode')
        axes[0, 0].set_ylabel('Récompense')
        axes[0, 0].grid(True)
        
        # Temps de survie
        axes[0, 1].plot(episodes, self.callback.survival_times, color='green')
        axes[0, 1].set_title('Temps de survie par épisode')
        axes[0, 1].set_xlabel('Épisode')
        axes[0, 1].set_ylabel('Temps de survie')
        axes[0, 1].grid(True)
        
        # Ennemis tués
        axes[1, 0].plot(episodes, self.callback.enemies_killed_log, color='red')
        axes[1, 0].set_title('Ennemis tués par épisode')
        axes[1, 0].set_xlabel('Épisode')
        axes[1, 0].set_ylabel('Ennemis tués')
        axes[1, 0].grid(True)
        
        # Moyenne mobile des récompenses
        window_size = min(50, len(self.callback.episode_rewards) // 4)
        if window_size > 1:
            moving_avg = np.convolve(self.callback.episode_rewards, 
                                   np.ones(window_size)/window_size, mode='valid')
            axes[1, 1].plot(episodes[:len(moving_avg)], moving_avg, color='purple')
            axes[1, 1].set_title(f'Moyenne mobile des récompenses (fenêtre={window_size})')
            axes[1, 1].set_xlabel('Épisode')
            axes[1, 1].set_ylabel('Récompense moyenne')
            axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        # Sauvegarder le graphique
        plot_path = f"{self.log_dir}/training_progress.png"
        plt.savefig(plot_path)
        print(f"📈 Graphiques sauvegardés : {plot_path}")
        
        plt.show()
        
        return fig
    
    def close(self):
        """Ferme l'environnement."""
        if self.env:
            self.env.close()

# Fonctions utilitaires pour usage rapide
def quick_train(timesteps: int = 50000, model_name: str = "quick_ai"):
    """Entraînement rapide avec paramètres par défaut."""
    trainer = GameAITrainer(model_name=model_name)
    trainer.create_environment(n_envs=4)
    trainer.create_model()
    trainer.train(total_timesteps=timesteps)
    trainer.evaluate(n_episodes=5)
    trainer.plot_training_progress()
    trainer.close()
    return trainer

def test_pretrained_model(model_path: str, n_episodes: int = 5, render: bool = True):
    """Teste un modèle pré-entraîné."""
    trainer = GameAITrainer()
    trainer.create_environment(n_envs=1, render_mode="human" if render else None)
    trainer.load_model(model_path)
    stats = trainer.evaluate(n_episodes=n_episodes, render=render)
    trainer.close()
    return stats
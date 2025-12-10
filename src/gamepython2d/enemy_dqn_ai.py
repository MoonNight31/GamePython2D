"""
Deep Q-Network (DQN) pour l'Apprentissage des Ennemis
Utilise un réseau de neurones pour apprendre les meilleures stratégies
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
import math
from typing import Dict, List, Tuple, Optional
from collections import deque
import pygame


class DQNetwork(nn.Module):
    """
    Réseau de neurones pour approximer la fonction Q.
    Architecture: Input → Dense → ReLU → Dense → ReLU → Output
    """
    
    def __init__(self, state_size: int, action_size: int, hidden_size: int = 128):
        super(DQNetwork, self).__init__()
        
        self.network = nn.Sequential(
            nn.Linear(state_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, action_size)
        )
        
        # Initialisation Xavier pour meilleure convergence
        for layer in self.network:
            if isinstance(layer, nn.Linear):
                nn.init.xavier_uniform_(layer.weight)
                nn.init.zeros_(layer.bias)
    
    def forward(self, state):
        """Forward pass du réseau."""
        return self.network(state)


class ReplayBuffer:
    """
    Mémoire de replay pour stocker les expériences.
    Permet l'apprentissage par batch et brise la corrélation temporelle.
    """
    
    def __init__(self, capacity: int = 10000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        """Ajoute une expérience au buffer."""
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size: int):
        """Échantillonne un batch aléatoire."""
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (
            np.array(states),
            np.array(actions),
            np.array(rewards, dtype=np.float32),
            np.array(next_states),
            np.array(dones, dtype=np.float32)
        )
    
    def __len__(self):
        return len(self.buffer)


class DQNEnemyBrain:
    """
    Cerveau d'ennemi basé sur Deep Q-Network.
    Utilise un réseau de neurones pour apprendre les meilleures actions.
    """
    
    # Actions possibles (identiques au système précédent)
    ACTIONS = {
        'APPROACH': 0,
        'CIRCLE_LEFT': 1,
        'CIRCLE_RIGHT': 2,
        'RETREAT': 3,
        'STRAFE_LEFT': 4,
        'STRAFE_RIGHT': 5,
        'ZIGZAG': 6,
        'RUSH': 7,
    }
    
    ACTION_SIZE = len(ACTIONS)
    STATE_SIZE = 16  # Taille du vecteur d'état (voir encode_state)
    
    def __init__(self, learning_rate: float = 0.001, discount_factor: float = 0.95, 
                 epsilon: float = 0.3, device: str = 'cpu'):
        
        self.device = torch.device(device)
        
        # Réseaux de neurones (Double DQN: réseau principal + réseau cible)
        self.policy_net = DQNetwork(self.STATE_SIZE, self.ACTION_SIZE).to(self.device)
        self.target_net = DQNetwork(self.STATE_SIZE, self.ACTION_SIZE).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()  # Mode évaluation pour le réseau cible
        
        # Optimiseur
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=learning_rate)
        self.criterion = nn.SmoothL1Loss()  # Huber Loss
        
        # Hyperparamètres
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.9995
        
        # Mémoire de replay
        self.replay_buffer = ReplayBuffer(capacity=10000)
        self.batch_size = 64
        self.min_replay_size = 500
        
        # Compteurs
        self.steps = 0
        self.update_target_every = 100  # Mise à jour du réseau cible tous les N steps
        
        # État actuel de l'épisode
        self.current_state = None
        self.current_action = None
        self.lifetime = 0
        self.damage_dealt = 0
        self.damage_received = 0
        self.time_near_player = 0
        
        # Statistiques d'apprentissage
        self.total_reward = 0
        self.episode_rewards = []
        self.losses = []
    
    def encode_state(self, enemy_pos: Tuple[float, float], player_pos: Tuple[float, float],
                     player_velocity: pygame.Vector2, distance: float,
                     player_health_ratio: float, enemy_health_ratio: float = 1.0) -> np.ndarray:
        """
        Encode l'état en vecteur numérique pour le réseau de neurones.
        
        Vecteur d'état (16 dimensions):
        [0-1]   : Position relative x, y (normalisée)
        [2]     : Distance (normalisée 0-1000)
        [3-4]   : Vélocité joueur x, y (normalisée)
        [5]     : Vitesse joueur (magnitude, normalisée)
        [6]     : Angle vers joueur (normalisé 0-2π)
        [7]     : Santé joueur (ratio 0-1)
        [8]     : Santé ennemi (ratio 0-1)
        [9-12]  : Distance catégorisée (one-hot: close, medium, far, very_far)
        [13-14] : Mouvement joueur (one-hot: static, moving)
        [15]    : Bias (toujours 1.0)
        """
        state = np.zeros(self.STATE_SIZE, dtype=np.float32)
        
        # Position relative normalisée
        dx = (player_pos[0] - enemy_pos[0]) / 1000.0
        dy = (player_pos[1] - enemy_pos[1]) / 1000.0
        state[0] = np.clip(dx, -1, 1)
        state[1] = np.clip(dy, -1, 1)
        
        # Distance normalisée
        state[2] = np.clip(distance / 1000.0, 0, 1)
        
        # Vélocité joueur normalisée
        state[3] = np.clip(player_velocity.x / 300.0, -1, 1)
        state[4] = np.clip(player_velocity.y / 300.0, -1, 1)
        state[5] = np.clip(player_velocity.length() / 300.0, 0, 1)
        
        # Angle vers le joueur (normalisé)
        angle = math.atan2(dy, dx)
        state[6] = (angle + math.pi) / (2 * math.pi)  # 0-1
        
        # Santé
        state[7] = player_health_ratio
        state[8] = enemy_health_ratio
        
        # Distance catégorisée (one-hot)
        if distance < 100:
            state[9] = 1.0  # CLOSE
        elif distance < 250:
            state[10] = 1.0  # MEDIUM
        elif distance < 500:
            state[11] = 1.0  # FAR
        else:
            state[12] = 1.0  # VERY_FAR
        
        # Mouvement joueur (one-hot)
        if player_velocity.length() > 50:
            state[13] = 1.0  # MOVING
        else:
            state[14] = 1.0  # STATIC
        
        # Bias
        state[15] = 1.0
        
        return state
    
    def choose_action(self, state: np.ndarray, training: bool = True) -> int:
        """
        Choisit une action selon epsilon-greedy.
        
        Args:
            state: Vecteur d'état encodé
            training: Si True, utilise epsilon-greedy. Si False, toujours greedy.
        """
        # Exploration
        if training and random.random() < self.epsilon:
            return random.randint(0, self.ACTION_SIZE - 1)
        
        # Exploitation: utiliser le réseau de neurones
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.policy_net(state_tensor)
            action = q_values.argmax().item()
        
        return action
    
    def store_experience(self, state, action, reward, next_state, done):
        """Stocke une expérience dans le replay buffer."""
        self.replay_buffer.push(state, action, reward, next_state, done)
        self.total_reward += reward
    
    def train_step(self):
        """
        Effectue une étape d'apprentissage (si assez d'expériences).
        Utilise le Double DQN pour stabilité.
        """
        if len(self.replay_buffer) < self.min_replay_size:
            return
        
        # Échantillonner un batch
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(self.batch_size)
        
        # Convertir en tenseurs
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        
        # Q-values actuelles
        current_q_values = self.policy_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        
        # Q-values cibles (Double DQN)
        with torch.no_grad():
            # Utiliser policy_net pour sélectionner l'action
            next_actions = self.policy_net(next_states).argmax(1)
            # Utiliser target_net pour évaluer l'action
            next_q_values = self.target_net(next_states).gather(1, next_actions.unsqueeze(1)).squeeze(1)
            target_q_values = rewards + (1 - dones) * self.discount_factor * next_q_values
        
        # Calculer la perte et backpropagation
        loss = self.criterion(current_q_values, target_q_values)
        
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)  # Gradient clipping
        self.optimizer.step()
        
        # Sauvegarder la perte
        self.losses.append(loss.item())
        
        # Mettre à jour le réseau cible périodiquement
        self.steps += 1
        if self.steps % self.update_target_every == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
        
        # Décrémenter epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def calculate_reward(self, dt: float, hit_player: bool = False,
                        got_hit: bool = False, distance: float = 0,
                        distance_decreased: bool = False, player_died: bool = False) -> float:
        """
        Calcule la récompense pour l'action effectuée.
        Récompenses façonnées pour encourager un bon comportement.
        Focus: Apprendre à TUER le joueur !
        """
        reward = 0.0
        
        # 🎯 OBJECTIF PRINCIPAL: TUER LE JOUEUR
        if player_died:
            reward += 100.0  # ÉNORME RÉCOMPENSE !!! L'objectif ultime
        
        # Récompenses positives
        if hit_player:
            reward += 20.0  # Très grosse récompense pour toucher
        
        # Survivre
        reward += 0.05 * (dt / 1000.0)
        
        # Être à distance optimale (100-200px) - ajusté pour être plus agressif
        if 100 < distance < 200:
            reward += 1.0 * (dt / 1000.0)
        elif 80 < distance < 100:
            reward += 0.6 * (dt / 1000.0)
        elif distance < 50:
            reward += 0.8 * (dt / 1000.0)  # Très proche = bien pour attaquer !
        
        # Récompense pour se rapprocher
        if distance_decreased and distance > 80:
            reward += 0.3 * (dt / 1000.0)
        
        # Pénalités
        if got_hit:
            reward -= 8.0  # Grosse pénalité
        
        return reward
    
    def execute_action(self, action: int, enemy_pos: Tuple[float, float],
                      player_pos: Tuple[float, float], speed: float,
                      dt: float) -> pygame.Vector2:
        """
        Exécute l'action choisie et retourne le vecteur de mouvement.
        Identique au système Q-Learning simple.
        """
        direction = pygame.Vector2(
            player_pos[0] - enemy_pos[0],
            player_pos[1] - enemy_pos[1]
        )
        
        if direction.length() == 0:
            return pygame.Vector2(0, 0)
        
        distance = direction.length()
        direction = direction.normalize()
        perpendicular = pygame.Vector2(-direction.y, direction.x)
        
        if action == self.ACTIONS['APPROACH']:
            velocity = direction * speed
        elif action == self.ACTIONS['CIRCLE_LEFT']:
            circle_direction = direction * 0.3 + perpendicular * 0.7
            velocity = circle_direction.normalize() * speed
        elif action == self.ACTIONS['CIRCLE_RIGHT']:
            circle_direction = direction * 0.3 - perpendicular * 0.7
            velocity = circle_direction.normalize() * speed
        elif action == self.ACTIONS['RETREAT']:
            velocity = -direction * speed * 0.8
        elif action == self.ACTIONS['STRAFE_LEFT']:
            strafe_direction = direction * 0.5 + perpendicular * 0.5
            velocity = strafe_direction.normalize() * speed
        elif action == self.ACTIONS['STRAFE_RIGHT']:
            strafe_direction = direction * 0.5 - perpendicular * 0.5
            velocity = strafe_direction.normalize() * speed
        elif action == self.ACTIONS['ZIGZAG']:
            time_factor = pygame.time.get_ticks() / 1000.0
            zigzag_offset = perpendicular * math.sin(time_factor * 5) * 0.6
            zigzag_direction = direction * 0.7 + zigzag_offset
            velocity = zigzag_direction.normalize() * speed
        elif action == self.ACTIONS['RUSH']:
            velocity = direction * speed * 1.5
        else:
            velocity = direction * speed
        
        return velocity
    
    def end_episode(self, final_reward: float = 0.0):
        """Appelé à la fin d'un épisode (mort de l'ennemi)."""
        self.episode_rewards.append(self.total_reward + final_reward)
        self.total_reward = 0


class DQNLearningSystem:
    """
    Système global d'apprentissage DQN.
    Gère le réseau partagé et l'entraînement collectif.
    """
    
    def __init__(self, device: str = None):
        # Détection automatique du device (GPU si disponible)
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        
        print(f"🧠 DQN Learning System initialisé sur: {self.device.upper()}")
        
        # Réseau partagé (tous les ennemis utilisent le même)
        self.shared_brain = DQNEnemyBrain(
            learning_rate=0.0005,
            discount_factor=0.95,
            epsilon=0.3,
            device=self.device
        )
        
        # Statistiques globales
        self.total_episodes = 0
        self.total_training_steps = 0
        self.best_episode_reward = float('-inf')
        
        # Compteur pour l'entraînement par batch
        self.train_every = 4  # Entraîner tous les N steps
        self.step_counter = 0
    
    def create_enemy_brain(self) -> DQNEnemyBrain:
        """
        Retourne une référence au cerveau partagé.
        Tous les ennemis utilisent le même réseau de neurones.
        """
        return self.shared_brain
    
    def enemy_died(self, brain: DQNEnemyBrain, killed_by_player: bool = True):
        """
        Appelé quand un ennemi meurt.
        Finalise l'épisode et entraîne le réseau.
        """
        self.total_episodes += 1
        
        # Récompense finale
        final_reward = -15.0 if killed_by_player else -5.0
        
        # Si l'ennemi a une expérience actuelle, la stocker
        if brain.current_state is not None and brain.current_action is not None:
            # État terminal (zéros)
            terminal_state = np.zeros(DQNEnemyBrain.STATE_SIZE, dtype=np.float32)
            brain.store_experience(
                brain.current_state,
                brain.current_action,
                final_reward,
                terminal_state,
                done=True
            )
        
        brain.end_episode(final_reward)
        
        # Entraîner le réseau
        if len(brain.replay_buffer) >= brain.min_replay_size:
            # Entraîner plusieurs fois pour utiliser toutes les expériences
            for _ in range(3):
                brain.train_step()
                self.total_training_steps += 1
        
        # Mettre à jour les statistiques
        if brain.episode_rewards:
            last_reward = brain.episode_rewards[-1]
            if last_reward > self.best_episode_reward:
                self.best_episode_reward = last_reward
    
    def step_update(self):
        """
        Appelé à chaque step de jeu.
        Entraîne périodiquement le réseau.
        """
        self.step_counter += 1
        
        if self.step_counter >= self.train_every:
            self.step_counter = 0
            if len(self.shared_brain.replay_buffer) >= self.shared_brain.min_replay_size:
                self.shared_brain.train_step()
                self.total_training_steps += 1
    
    def get_learning_stats(self) -> Dict:
        """Retourne les statistiques d'apprentissage."""
        brain = self.shared_brain
        
        avg_loss = np.mean(brain.losses[-100:]) if brain.losses else 0.0
        avg_reward = np.mean(brain.episode_rewards[-100:]) if brain.episode_rewards else 0.0
        
        return {
            'total_episodes': self.total_episodes,
            'total_training_steps': self.total_training_steps,
            'buffer_size': len(brain.replay_buffer),
            'current_epsilon': brain.epsilon,
            'avg_loss': avg_loss,
            'avg_reward': avg_reward,
            'best_reward': self.best_episode_reward,
            'device': self.device
        }
    
    def save_model(self, path: str):
        """Sauvegarde le modèle entraîné."""
        torch.save({
            'policy_net': self.shared_brain.policy_net.state_dict(),
            'target_net': self.shared_brain.target_net.state_dict(),
            'optimizer': self.shared_brain.optimizer.state_dict(),
            'epsilon': self.shared_brain.epsilon,
            'episodes': self.total_episodes,
        }, path)
        print(f"✅ Modèle sauvegardé: {path}")
    
    def load_model(self, path: str):
        """Charge un modèle pré-entraîné."""
        checkpoint = torch.load(path, map_location=self.device)
        self.shared_brain.policy_net.load_state_dict(checkpoint['policy_net'])
        self.shared_brain.target_net.load_state_dict(checkpoint['target_net'])
        self.shared_brain.optimizer.load_state_dict(checkpoint['optimizer'])
        self.shared_brain.epsilon = checkpoint['epsilon']
        self.total_episodes = checkpoint['episodes']
        print(f"✅ Modèle chargé: {path} ({self.total_episodes} épisodes)")

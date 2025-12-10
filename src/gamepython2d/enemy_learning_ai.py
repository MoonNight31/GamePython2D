"""
Système d'Apprentissage par Renforcement pour les Ennemis
Les ennemis apprennent les meilleures stratégies contre le joueur
"""

import random
import math
from typing import Dict, List, Tuple
from collections import defaultdict, deque
import pygame


class EnemyBrain:
    """
    Cerveau d'apprentissage pour un ennemi individuel.
    Utilise du Q-Learning simplifié pour apprendre les meilleures actions.
    """
    
    # Actions possibles pour un ennemi
    ACTIONS = {
        'APPROACH': 0,          # Approcher directement
        'CIRCLE_LEFT': 1,       # Tourner autour (gauche)
        'CIRCLE_RIGHT': 2,      # Tourner autour (droite)
        'RETREAT': 3,           # Reculer
        'STRAFE_LEFT': 4,       # Déplacement latéral gauche
        'STRAFE_RIGHT': 5,      # Déplacement latéral droit
        'ZIGZAG': 6,            # Zigzag pour esquiver
        'RUSH': 7,              # Charge rapide
    }
    
    def __init__(self, learning_rate=0.1, discount_factor=0.95, epsilon=0.2):
        # Q-Table : {state: {action: q_value}}
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        # Paramètres d'apprentissage
        self.learning_rate = learning_rate      # Alpha (vitesse d'apprentissage)
        self.discount_factor = discount_factor  # Gamma (importance du futur)
        self.epsilon = epsilon                  # Taux d'exploration
        
        # Historique de l'épisode en cours
        self.current_state = None
        self.current_action = None
        self.lifetime = 0
        self.damage_dealt = 0
        self.damage_received = 0
        self.time_near_player = 0
        
        # Expérience récente
        self.experience_buffer = deque(maxlen=100)
    
    def get_state(self, enemy_pos: Tuple[float, float], player_pos: Tuple[float, float], 
                  player_velocity: pygame.Vector2, distance: float, 
                  player_health_ratio: float) -> str:
        """
        Encode l'état actuel en une clé pour la Q-table.
        Discrétise l'espace des états pour rendre l'apprentissage possible.
        """
        # Distance discrétisée
        if distance < 100:
            dist_state = "CLOSE"
        elif distance < 250:
            dist_state = "MEDIUM"
        elif distance < 500:
            dist_state = "FAR"
        else:
            dist_state = "VERY_FAR"
        
        # Direction relative du joueur
        dx = player_pos[0] - enemy_pos[0]
        dy = player_pos[1] - enemy_pos[1]
        angle = math.atan2(dy, dx)
        
        # Discrétiser l'angle en 8 directions
        angle_deg = math.degrees(angle)
        angle_sector = int((angle_deg + 22.5) // 45) % 8
        
        # Vitesse du joueur (est-il en mouvement ?)
        player_moving = "MOVING" if player_velocity.length() > 50 else "STATIC"
        
        # Santé du joueur
        if player_health_ratio > 0.7:
            health_state = "HIGH"
        elif player_health_ratio > 0.3:
            health_state = "MED"
        else:
            health_state = "LOW"
        
        # État composite
        state = f"{dist_state}_{angle_sector}_{player_moving}_{health_state}"
        return state
    
    def choose_action(self, state: str, training: bool = True) -> int:
        """
        Choisit une action selon la politique epsilon-greedy.
        
        Args:
            state: L'état actuel
            training: Si True, explore parfois. Si False, toujours exploite.
        """
        # Exploration : action aléatoire
        if training and random.random() < self.epsilon:
            return random.choice(list(self.ACTIONS.values()))
        
        # Exploitation : meilleure action connue
        q_values = self.q_table[state]
        if not q_values:
            return random.choice(list(self.ACTIONS.values()))
        
        # Choisir l'action avec la meilleure Q-value
        best_action = max(q_values.items(), key=lambda x: x[1])[0]
        return best_action
    
    def update_q_value(self, state: str, action: int, reward: float, next_state: str):
        """
        Met à jour la Q-value selon l'équation de Bellman.
        Q(s,a) = Q(s,a) + α * [R + γ * max(Q(s',a')) - Q(s,a)]
        """
        current_q = self.q_table[state][action]
        
        # Meilleure Q-value pour le prochain état
        next_q_values = self.q_table[next_state]
        max_next_q = max(next_q_values.values()) if next_q_values else 0.0
        
        # Nouvelle Q-value
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state][action] = new_q
    
    def calculate_reward(self, dt: float, hit_player: bool = False, 
                        got_hit: bool = False, distance: float = 0) -> float:
        """
        Calcule la récompense pour l'action effectuée.
        """
        reward = 0.0
        
        # Récompenses positives
        if hit_player:
            reward += 10.0  # Grosse récompense pour toucher le joueur
        
        # Survivre est positif
        reward += 0.1 * (dt / 1000.0)
        
        # Être proche du joueur est bon (mais pas trop proche)
        if 100 < distance < 250:
            reward += 0.5 * (dt / 1000.0)
        elif distance < 50:
            reward -= 0.2 * (dt / 1000.0)  # Trop proche = risque
        
        # Pénalités
        if got_hit:
            reward -= 5.0  # Pénalité pour être touché
        
        return reward
    
    def execute_action(self, action: int, enemy_pos: Tuple[float, float], 
                      player_pos: Tuple[float, float], speed: float, 
                      dt: float) -> pygame.Vector2:
        """
        Exécute l'action choisie et retourne le vecteur de mouvement.
        """
        direction = pygame.Vector2(
            player_pos[0] - enemy_pos[0],
            player_pos[1] - enemy_pos[1]
        )
        
        if direction.length() == 0:
            return pygame.Vector2(0, 0)
        
        distance = direction.length()
        direction = direction.normalize()
        
        # Perpendiculaire pour les mouvements latéraux
        perpendicular = pygame.Vector2(-direction.y, direction.x)
        
        # Exécution selon l'action
        if action == self.ACTIONS['APPROACH']:
            # Approche directe
            velocity = direction * speed
            
        elif action == self.ACTIONS['CIRCLE_LEFT']:
            # Tourner autour dans le sens anti-horaire
            circle_direction = direction * 0.3 + perpendicular * 0.7
            velocity = circle_direction.normalize() * speed
            
        elif action == self.ACTIONS['CIRCLE_RIGHT']:
            # Tourner autour dans le sens horaire
            circle_direction = direction * 0.3 - perpendicular * 0.7
            velocity = circle_direction.normalize() * speed
            
        elif action == self.ACTIONS['RETREAT']:
            # Reculer
            velocity = -direction * speed * 0.8
            
        elif action == self.ACTIONS['STRAFE_LEFT']:
            # Déplacement latéral gauche tout en avançant
            strafe_direction = direction * 0.5 + perpendicular * 0.5
            velocity = strafe_direction.normalize() * speed
            
        elif action == self.ACTIONS['STRAFE_RIGHT']:
            # Déplacement latéral droit tout en avançant
            strafe_direction = direction * 0.5 - perpendicular * 0.5
            velocity = strafe_direction.normalize() * speed
            
        elif action == self.ACTIONS['ZIGZAG']:
            # Zigzag pour esquiver
            time_factor = pygame.time.get_ticks() / 1000.0
            zigzag_offset = perpendicular * math.sin(time_factor * 5) * 0.6
            zigzag_direction = direction * 0.7 + zigzag_offset
            velocity = zigzag_direction.normalize() * speed
            
        elif action == self.ACTIONS['RUSH']:
            # Charge rapide
            velocity = direction * speed * 1.5
            
        else:
            velocity = direction * speed
        
        return velocity


class EnemyLearningSystem:
    """
    Système global d'apprentissage qui partage les connaissances entre ennemis.
    """
    
    def __init__(self):
        # Q-Table partagée entre tous les ennemis
        self.shared_q_table = defaultdict(lambda: defaultdict(float))
        
        # Statistiques d'apprentissage
        self.total_episodes = 0
        self.successful_strategies = defaultdict(int)
        self.failed_strategies = defaultdict(int)
        
        # Mémoire collective (replay buffer)
        self.replay_buffer = deque(maxlen=1000)
        
        # Paramètres d'apprentissage globaux
        self.global_learning_rate = 0.1
        self.epsilon_decay = 0.995
        self.min_epsilon = 0.05
        self.current_epsilon = 0.3
    
    def create_enemy_brain(self) -> EnemyBrain:
        """Crée un nouveau cerveau pour un ennemi avec la connaissance partagée."""
        brain = EnemyBrain(
            learning_rate=self.global_learning_rate,
            epsilon=self.current_epsilon
        )
        # Transférer la connaissance partagée
        brain.q_table = defaultdict(lambda: defaultdict(float), self.shared_q_table)
        return brain
    
    def enemy_died(self, brain: EnemyBrain, killed_by_player: bool = True):
        """
        Appelé quand un ennemi meurt. Met à jour l'apprentissage global.
        """
        self.total_episodes += 1
        
        # Récompense finale négative si tué par le joueur
        if killed_by_player and brain.current_state and brain.current_action is not None:
            final_reward = -10.0 - (brain.damage_received * 0.1)
            brain.update_q_value(
                brain.current_state,
                brain.current_action,
                final_reward,
                "TERMINAL"
            )
        
        # Fusionner l'expérience dans la Q-table partagée
        self._merge_knowledge(brain)
        
        # Décrémenter epsilon (moins d'exploration avec le temps)
        self.current_epsilon = max(
            self.min_epsilon,
            self.current_epsilon * self.epsilon_decay
        )
    
    def _merge_knowledge(self, brain: EnemyBrain):
        """Fusionne les connaissances d'un ennemi dans la base collective."""
        for state, actions in brain.q_table.items():
            for action, q_value in actions.items():
                # Moyenne pondérée avec la connaissance existante
                current_q = self.shared_q_table[state][action]
                self.shared_q_table[state][action] = (
                    current_q * 0.8 + q_value * 0.2
                )
    
    def get_best_strategies(self, top_n: int = 5) -> List[Dict]:
        """Retourne les meilleures stratégies apprises."""
        strategies = []
        for state, actions in self.shared_q_table.items():
            if actions:
                best_action = max(actions.items(), key=lambda x: x[1])
                strategies.append({
                    'state': state,
                    'action': best_action[0],
                    'q_value': best_action[1]
                })
        
        # Trier par Q-value
        strategies.sort(key=lambda x: x['q_value'], reverse=True)
        return strategies[:top_n]
    
    def get_learning_stats(self) -> Dict:
        """Retourne les statistiques d'apprentissage."""
        total_states = len(self.shared_q_table)
        avg_q_values = []
        
        for actions in self.shared_q_table.values():
            if actions:
                avg_q = sum(actions.values()) / len(actions)
                avg_q_values.append(avg_q)
        
        return {
            'total_episodes': self.total_episodes,
            'states_explored': total_states,
            'avg_q_value': sum(avg_q_values) / len(avg_q_values) if avg_q_values else 0.0,
            'current_epsilon': self.current_epsilon,
            'knowledge_size': sum(len(actions) for actions in self.shared_q_table.values())
        }

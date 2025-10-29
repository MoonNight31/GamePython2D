import gymnasium as gym
import numpy as np
import pygame
import math
import random
from typing import Dict, Tuple, Any, Optional
from gymnasium import spaces

# Import du jeu original
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from gamepython2d.player import Player
from gamepython2d.enemy import EnemySpawner, XPOrb
from gamepython2d.xp_system import XPSystem
from gamepython2d.card_system import CardDatabase, Card

class GameAIEnvironment(gym.Env):
    """
    Environnement OpenAI Gym pour entraîner une IA sur GamePython2D.
    """
    
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}
    
    def __init__(self, render_mode: str = None, screen_width: int = 1200, screen_height: int = 800):
        super().__init__()
        
        # Configuration de l'environnement
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.render_mode = render_mode
        
        # Initialisation de Pygame (nécessaire même en mode headless)
        pygame.init()
        if render_mode == "human":
            self.screen = pygame.display.set_mode((screen_width, screen_height))
            pygame.display.set_caption("GamePython2D - IA Training")
        else:
            # Mode headless pour l'entraînement rapide
            self.screen = pygame.Surface((screen_width, screen_height))
        
        self.clock = pygame.time.Clock()
        
        # Espaces d'action et d'observation
        self._setup_action_space()
        self._setup_observation_space()
        
        # État du jeu
        self.player = None
        self.enemy_spawner = None
        self.xp_system = None
        
        # Métriques pour l'entraînement
        self.step_count = 0
        self.max_steps = 10000  # Limite par épisode
        self.last_player_health = 100
        self.enemies_killed = 0
        self.enemies_killed_by_projectiles = 0  # Nouvellement ajouté
        self.enemies_killed_by_collision = 0    # Nouvellement ajouté
        self.total_damage_dealt = 0
        self.survival_time = 0
        self.projectiles_fired = 0              # Nouvellement ajouté
        self.last_projectile_count = 0          # Nouvellement ajouté
        
        # Timer pour spawning
        self.spawn_timer = 0
        self.spawn_interval = 2000  # ms
        
        # Récompenses cumulées
        self.episode_reward = 0
        
    def _setup_action_space(self):
        """Définit l'espace des actions possibles."""
        # Actions : [move_x, move_y, attack_x, attack_y, should_attack]
        # move_x, move_y : [-1, 1] pour direction de mouvement
        # attack_x, attack_y : [-1, 1] pour direction d'attaque
        # should_attack : [0, 1] pour décider d'attaquer ou non
        self.action_space = spaces.Box(
            low=np.array([-1, -1, -1, -1, 0]),
            high=np.array([1, 1, 1, 1, 1]),
            dtype=np.float32
        )
    
    def _setup_observation_space(self):
        """Définit l'espace d'observation."""
        # Observation : état simplifié du jeu
        # [player_x, player_y, player_health, player_xp, level, 
        #  closest_enemy_x, closest_enemy_y, closest_enemy_health,
        #  second_closest_enemy_x, second_closest_enemy_y,
        #  enemy_count, survival_time]
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0, 1, -1, -1, 0, -1, -1, 0, 0]),
            high=np.array([
                self.screen_width, self.screen_height, 200, 1000, 50,
                self.screen_width, self.screen_height, 100,
                self.screen_width, self.screen_height, 100, 100000
            ]),
            dtype=np.float32
        )
    
    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
        """Remet l'environnement à zéro."""
        super().reset(seed=seed)
        
        # Réinitialiser les composants du jeu (mode training = pas d'images)
        self.player = Player(self.screen_width // 2, self.screen_height // 2, use_images=False)
        self.enemy_spawner = EnemySpawner(self.screen_width, self.screen_height, use_images=False)
        self.xp_system = XPSystem()
        
        # Système de cartes
        self.card_database = CardDatabase()
        self.cards_obtained = []  # Liste des cartes obtenues
        
        # Liste des orbes d'XP
        self.xp_orbs = []
        
        # Réinitialiser les métriques
        self.step_count = 0
        self.last_player_health = self.player.health
        self.enemies_killed = 0
        self.enemies_killed_by_projectiles = 0
        self.enemies_killed_by_collision = 0
        self.total_damage_dealt = 0
        self.survival_time = 0
        self.spawn_timer = 0
        self.projectiles_fired = 0
        self.last_projectile_count = 0
        self.episode_reward = 0
        
        # Première observation
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, info
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """Exécute une action dans l'environnement."""
        self.step_count += 1
        self.survival_time += 1
        
        # Traiter l'action de l'IA
        self._process_action(action)
        
        # Mettre à jour le jeu (simulation d'un frame)
        dt = 16.67  # ~60 FPS
        self._update_game(dt)
        
        # Calculer la récompense
        reward = self._calculate_reward()
        self.episode_reward += reward
        
        # Vérifier les conditions de fin
        terminated = self.player.health <= 0
        truncated = self.step_count >= self.max_steps
        
        # Nouvelle observation
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, reward, terminated, truncated, info
    
    def _process_action(self, action: np.ndarray):
        """Traite l'action de l'IA (array de 5 valeurs)."""
        move_x, move_y, attack_x, attack_y, should_attack = action
        
        # Sauvegarder l'action pour le calcul de récompense
        self.last_action = action
        
        # Simuler les touches pressées pour le mouvement
        keys_pressed = {
            'w': move_y < -0.3,
            's': move_y > 0.3,
            'a': move_x < -0.3,
            'd': move_x > 0.3
        }
        
        # Appliquer le mouvement
        velocity = pygame.Vector2(0, 0)
        if keys_pressed['w']:
            velocity.y = -1
        if keys_pressed['s']:
            velocity.y = 1
        if keys_pressed['a']:
            velocity.x = -1
        if keys_pressed['d']:
            velocity.x = 1
        
        if velocity.length() > 0:
            velocity = velocity.normalize()
            effective_speed = self.player.speed * self.player.card_effects['speed_multiplier']
            self.player.rect.x += velocity.x * effective_speed * 16.67 / 1000
            self.player.rect.y += velocity.y * effective_speed * 16.67 / 1000
            self.player.facing_direction = velocity
            
            # Mettre à jour l'angle et l'image du vaisseau
            self.player.angle = -math.degrees(math.atan2(velocity.y, velocity.x)) - 90
            self.player._update_rotated_image()
        
        # Limites de l'écran
        self.player.rect.clamp_ip(pygame.Rect(0, 0, self.screen_width, self.screen_height))
        
        # Attaquer si décidé
        if should_attack > 0.5:
            # Calculer la position d'attaque basée sur la direction
            attack_target_x = self.player.rect.centerx + attack_x * 200
            attack_target_y = self.player.rect.centery + attack_y * 200
            self.player.attack((attack_target_x, attack_target_y))
    
    def _update_game(self, dt: float):
        """Met à jour la logique du jeu."""
        # Mettre à jour le joueur
        self.player.update(dt)
        
        # Spawning des ennemis
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.enemy_spawner.spawn_enemy(self.player.rect.center)
            self.spawn_timer = 0
            # Augmenter la difficulté progressivement
            self.spawn_interval = max(500, self.spawn_interval - 5)
        
        # Mettre à jour les ennemis
        self.enemy_spawner.update(dt, self.player.rect.center)
        
        # Mettre à jour et collecter les orbes d'XP
        player_pos = (self.player.rect.centerx, self.player.rect.centery)
        
        # D'abord vérifier la collecte AVANT de filtrer
        for orb in self.xp_orbs[:]:  # Copie de la liste pour itération sûre
            still_active = orb.update(dt, player_pos)
            
            if orb.collected:
                # Donner l'XP au joueur
                xp_gained = self.xp_system.gain_xp(orb.xp_value)
                
                # Vérifier le level up et sélectionner une carte automatiquement
                if self.xp_system.check_level_up():
                    self._auto_select_card()
                
                # Retirer l'orbe de la liste
                self.xp_orbs.remove(orb)
            elif not still_active:
                # L'orbe a expiré, le retirer
                self.xp_orbs.remove(orb)
        
        # Détecter les collisions
        self._handle_collisions()
        
        # Mettre à jour le total des ennemis tués
        self.enemies_killed = self.enemies_killed_by_projectiles + self.enemies_killed_by_collision
    
    def _handle_collisions(self):
        """Gère les collisions du jeu."""
        # Collision joueur-ennemis (kills passifs - pas de récompense)
        for enemy in self.enemy_spawner.enemies[:]:  # Copie pour modification
            if self.player.rect.colliderect(enemy.rect):
                self.player.take_damage(enemy.damage)
                enemy.health = 0  # L'ennemi meurt après attaque
                self.enemies_killed_by_collision += 1  # Comptage kill passif
        
        # Collision projectiles-ennemis (kills actifs - récompensés)
        for projectile in self.player.projectiles:
            if projectile.active:
                for enemy in self.enemy_spawner.enemies[:]:  # Copie pour modification
                    if projectile.rect.colliderect(enemy.rect):
                        damage_dealt = projectile.damage
                        enemy.take_damage(damage_dealt)
                        projectile.active = False
                        self.total_damage_dealt += damage_dealt
                        
                        # Si l'ennemi meurt par projectile, créer un orbe d'XP
                        if enemy.health <= 0:
                            self.enemies_killed_by_projectiles += 1
                            # Créer un orbe d'XP à la position de l'ennemi
                            xp_orb = XPOrb(enemy.rect.centerx, enemy.rect.centery, enemy.xp_value)
                            self.xp_orbs.append(xp_orb)
    
    def _auto_select_card(self):
        """Sélectionne et applique automatiquement une carte lors d'un level up."""
        # Obtenir 3 cartes aléatoires selon le niveau
        level = self.xp_system.level
        
        # Ajuster les probabilités selon le niveau
        if level >= 20:
            rarity_weights = {'common': 0.2, 'uncommon': 0.3, 'rare': 0.3, 'epic': 0.15, 'legendary': 0.05}
        elif level >= 15:
            rarity_weights = {'common': 0.3, 'uncommon': 0.35, 'rare': 0.25, 'epic': 0.08, 'legendary': 0.02}
        elif level >= 10:
            rarity_weights = {'common': 0.4, 'uncommon': 0.35, 'rare': 0.2, 'epic': 0.05, 'legendary': 0.0}
        elif level >= 5:
            rarity_weights = {'common': 0.5, 'uncommon': 0.35, 'rare': 0.15, 'epic': 0.0, 'legendary': 0.0}
        else:
            rarity_weights = {'common': 0.7, 'uncommon': 0.25, 'rare': 0.05, 'epic': 0.0, 'legendary': 0.0}
        
        # Obtenir 3 cartes aléatoires
        available_cards = self.card_database.get_random_cards(3, rarity_weights)
        
        # Stratégie de sélection intelligente pour l'IA
        selected_card = self._choose_best_card(available_cards)
        
        if selected_card:
            # Appliquer les effets de la carte au joueur
            self._apply_card_effects(selected_card)
            self.cards_obtained.append(selected_card)
    
    def _choose_best_card(self, cards: list) -> Optional[Card]:
        """Choisit la meilleure carte selon une stratégie."""
        if not cards:
            return None
        
        # Stratégie prioritaire basée sur le niveau et les besoins
        priorities = {
            'damage_boost': 10.0,      # Priorité très haute (tuer plus vite)
            'attack_speed_boost': 8.0, # Priorité haute (tirer plus)
            'speed_boost': 6.0,        # Priorité moyenne-haute (éviter)
            'health_boost': 5.0,       # Priorité moyenne (survivre)
            'heal': 4.0,               # Priorité moyenne-basse (urgence seulement)
            'multi_shot': 12.0         # Priorité MAXIMUM (plusieurs cibles)
        }
        
        # Ajuster selon la santé actuelle
        health_ratio = self.player.health / self.player.max_health
        if health_ratio < 0.3:
            # Santé basse : prioriser survie
            priorities['heal'] = 15.0
            priorities['health_boost'] = 12.0
        
        # Calculer les scores
        best_card = None
        best_score = -1
        
        for card in cards:
            score = priorities.get(card.effect_type, 1.0)
            
            # Bonus pour rareté
            rarity_bonus = {
                'common': 1.0,
                'uncommon': 1.2,
                'rare': 1.5,
                'epic': 2.0,
                'legendary': 3.0
            }
            score *= rarity_bonus.get(card.rarity, 1.0)
            
            # Bonus pour valeur élevée
            score *= (1.0 + card.value * 0.1)
            
            if score > best_score:
                best_score = score
                best_card = card
        
        return best_card
    
    def _apply_card_effects(self, card: Card):
        """Applique les effets d'une carte au joueur."""
        effect_type = card.effect_type
        value = card.value
        
        if effect_type == "speed_boost":
            self.player.card_effects['speed_multiplier'] *= (1 + value)
        
        elif effect_type == "damage_boost":
            self.player.card_effects['damage_multiplier'] *= (1 + value)
            new_damage = int(self.player.attack_damage * self.player.card_effects['damage_multiplier'])
        
        elif effect_type == "attack_speed_boost":
            self.player.card_effects['attack_speed_multiplier'] *= (1 + value)
            new_speed = self.player.attack_speed * self.player.card_effects['attack_speed_multiplier']
        
        elif effect_type == "health_boost":
            self.player.max_health += int(value)
            self.player.health += int(value)
        
        elif effect_type == "heal":
            self.player.health = min(self.player.max_health, self.player.health + int(value))
        
        elif effect_type == "multi_shot":
            self.player.card_effects['projectile_count'] += int(value)
    
    def _calculate_reward(self) -> float:
        """SYSTÈME DE RÉCOMPENSES ULTRA-SIMPLIFIÉ - FOCUS COMBAT ACTIF."""
        reward = 0.0
        
        # 🏆 RÉCOMPENSE PRINCIPALE : Kills actifs (objectif principal)
        reward += self.enemies_killed_by_projectiles * 25.0  # ÉNORME récompense !
        
        # 🎯 TIR = TOUJOURS POSITIF (suppression de toute complexité)
        current_projectile_count = len([p for p in self.player.projectiles if p.active])
        projectiles_fired_this_step = max(0, current_projectile_count - self.last_projectile_count)
        if projectiles_fired_this_step > 0:
            reward += projectiles_fired_this_step * 4.0  # Récompense TRÈS généreuse
            self.projectiles_fired += projectiles_fired_this_step
        self.last_projectile_count = current_projectile_count
        
        # 🏃 MOUVEMENT = TOUJOURS POSITIF
        if hasattr(self, 'last_action'):
            move_x, move_y, attack_x, attack_y, should_attack = self.last_action
            is_moving = abs(move_x) > 0.1 or abs(move_y) > 0.1
            if is_moving:
                reward += 1.0  # Récompense généreuse pour bouger
        
        # 🛡️ SURVIE DE BASE
        reward += 0.2  # Un peu augmenté
        
        # 🚨 SEULES PÉNALITÉS : DÉGÂTS ET COINS EXTRÊMES
        # Pénalité pour dégâts
        health_lost = self.last_player_health - self.player.health
        if health_lost > 0:
            reward -= health_lost * 3.0  # Pénalité forte pour encourager évitement
            self.last_player_health = self.player.health
        
        # Pénalité UNIQUEMENT pour être collé aux murs (coins)
        player_x = self.player.rect.centerx
        player_y = self.player.rect.centery
        if (player_x < 10 or player_x > self.screen_width - 10 or 
            player_y < 10 or player_y > self.screen_height - 10):
            reward -= 5.0  # Pénalité forte pour éviter les coins mortels
        
        # 💀 Pénalité mort
        if self.player.health <= 0:
            reward -= 30.0
        
        return reward

    def _get_observation(self) -> np.ndarray:
        """Génère l'observation actuelle."""
        # Position et stats du joueur
        player_x = self.player.rect.centerx / self.screen_width
        player_y = self.player.rect.centery / self.screen_height
        player_health = self.player.health / 200.0  # Normaliser
        player_xp = min(self.xp_system.current_xp / 1000.0, 1.0)  # Normaliser
        level = min(self.xp_system.level / 50.0, 1.0)  # Normaliser
        
        # Informations sur les ennemis les plus proches
        enemies_data = self._get_closest_enemies_data(2)
        
        # Nombre d'ennemis
        enemy_count = min(len(self.enemy_spawner.enemies) / 100.0, 1.0)  # Normaliser
        
        # Temps de survie
        survival_norm = min(self.survival_time / 100000.0, 1.0)  # Normaliser
        
        observation = np.array([
            player_x, player_y, player_health, player_xp, level,
            enemies_data[0], enemies_data[1], enemies_data[2],  # Premier ennemi
            enemies_data[3], enemies_data[4],  # Deuxième ennemi
            enemy_count, survival_norm
        ], dtype=np.float32)
        
        return observation
    
    def _get_closest_enemies_data(self, count: int) -> list:
        """Obtient les données des ennemis les plus proches."""
        if not self.enemy_spawner.enemies:
            return [0, 0, 0, 0, 0]  # Pas d'ennemi = direction nulle
        
        # Calculer les distances
        player_pos = self.player.rect.center
        enemies_with_distance = []
        
        for enemy in self.enemy_spawner.enemies:
            distance = math.sqrt(
                (enemy.rect.centerx - player_pos[0])**2 + 
                (enemy.rect.centery - player_pos[1])**2
            )
            enemies_with_distance.append((enemy, distance))
        
        # Trier par distance
        enemies_with_distance.sort(key=lambda x: x[1])
        
        result = []
        for i in range(count):
            if i < len(enemies_with_distance):
                enemy, distance = enemies_with_distance[i]
                # Direction vers l'ennemi (directement utilisable pour l'action !)
                direction_x = enemy.rect.centerx - player_pos[0]
                direction_y = enemy.rect.centery - player_pos[1]
                
                # Normaliser la direction (-1 à +1)
                max_distance = max(abs(direction_x), abs(direction_y), 1)
                rel_x = direction_x / max_distance
                rel_y = direction_y / max_distance
                
                health_norm = enemy.health / 100.0
                result.extend([rel_x, rel_y, health_norm])
            else:
                result.extend([0, 0, 0])  # Pas d'ennemi
        
        return result
    
    def _get_closest_enemy_distance(self) -> float:
        """Obtient la distance à l'ennemi le plus proche."""
        if not self.enemy_spawner.enemies:
            return float('inf')
        
        player_pos = self.player.rect.center
        min_distance = float('inf')
        
        for enemy in self.enemy_spawner.enemies:
            distance = math.sqrt(
                (enemy.rect.centerx - player_pos[0])**2 + 
                (enemy.rect.centery - player_pos[1])**2
            )
            min_distance = min(min_distance, distance)
        
        return min_distance
    
    def _get_info(self) -> Dict:
        """Retourne des informations supplémentaires."""
        return {
            'player_health': self.player.health,
            'enemies_killed': self.enemies_killed,
            'enemies_killed_by_projectiles': self.enemies_killed_by_projectiles,
            'enemies_killed_by_collision': self.enemies_killed_by_collision,
            'projectiles_fired': self.projectiles_fired,
            'survival_time': self.survival_time,
            'level': self.xp_system.level,
            'total_reward': self.episode_reward,
            'enemy_count': len(self.enemy_spawner.enemies),
            'cards_obtained': len(self.cards_obtained),
            'card_effects': {
                'speed': self.player.card_effects['speed_multiplier'],
                'damage': self.player.card_effects['damage_multiplier'],
                'attack_speed': self.player.card_effects['attack_speed_multiplier'],
                'projectiles': self.player.card_effects['projectile_count']
            }
        }
    
    def render(self):
        """Affiche le jeu (optionnel)."""
        if self.render_mode == "human":
            # Nettoyer l'écran
            self.screen.fill((20, 20, 30))
            
            # Dessiner les éléments du jeu
            self.player.draw(self.screen)
            self.enemy_spawner.draw(self.screen)
            
            # Dessiner les orbes d'XP
            for orb in self.xp_orbs:
                orb.draw(self.screen)
            
            # Afficher quelques infos pour le débogage
            font = pygame.font.Font(None, 24)
            info_text = f"Health: {self.player.health} | Enemies: {len(self.enemy_spawner.enemies)} | Step: {self.step_count}"
            text_surface = font.render(info_text, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, 10))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        elif self.render_mode == "rgb_array":
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(self.screen)), axes=(1, 0, 2)
            )
    
    def close(self):
        """Ferme l'environnement."""
        if hasattr(self, 'screen'):
            pygame.quit()
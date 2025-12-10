import pygame
import random
import math
import os
import numpy as np
from typing import List, Tuple
from dataclasses import dataclass
from PIL import Image

from .enemy_dqn_ai import DQNEnemyBrain

class XPOrb:
    """Orbe d'expérience qui doit être collecté par le joueur."""
    
    def __init__(self, x: int, y: int, xp_value: int):
        self.x = float(x)
        self.y = float(y)
        self.xp_value = xp_value
        
        # Taille de l'orbe selon la valeur d'XP
        self.size = max(8, min(20, 8 + xp_value // 5))
        self.rect = pygame.Rect(int(x) - self.size // 2, int(y) - self.size // 2, self.size, self.size)
        
        # Animation
        self.pulse_timer = 0
        self.pulse_speed = 3.0  # Vitesse de pulsation
        
        # Magnétisme (attraction vers le joueur)
        self.magnetic_range = 150  # Distance à laquelle l'orbe est attiré
        self.magnetic_speed = 200  # Vitesse d'attraction
        self.velocity_x = 0
        self.velocity_y = 0
        
        # Durée de vie
        self.lifetime = 30000  # 30 secondes avant de disparaître
        self.age = 0
        self.collected = False
        
        # Couleur selon la valeur
        if xp_value >= 20:
            self.color = (255, 215, 0)  # Or (haute valeur)
        elif xp_value >= 15:
            self.color = (100, 200, 255)  # Bleu (moyenne valeur)
        else:
            self.color = (100, 255, 100)  # Vert (basse valeur)
    
    def update(self, dt: float, player_pos: Tuple[int, int]):
        """Met à jour l'orbe d'XP."""
        self.age += dt
        self.pulse_timer += dt / 1000.0
        
        # Vérifier si l'orbe a expiré
        if self.age >= self.lifetime:
            return False
        
        # Calculer la distance au joueur
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Attraction magnétique si le joueur est proche
        if distance < self.magnetic_range and distance > 5:
            # Normaliser la direction
            dx /= distance
            dy /= distance
            
            # Appliquer la vitesse magnétique
            strength = 1.0 - (distance / self.magnetic_range)  # Plus fort quand proche
            self.velocity_x = dx * self.magnetic_speed * strength
            self.velocity_y = dy * self.magnetic_speed * strength
            
            # Appliquer le mouvement
            self.x += self.velocity_x * dt / 1000.0
            self.y += self.velocity_y * dt / 1000.0
        
        # Mettre à jour le rect
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
        # Vérifier la collecte (collision avec le joueur)
        if distance < 20:
            self.collected = True
            return False
        
        return True
    
    def draw(self, screen):
        """Dessine l'orbe d'XP avec effet de pulsation."""
        # Effet de pulsation
        pulse = math.sin(self.pulse_timer * self.pulse_speed) * 0.2 + 1.0
        current_size = int(self.size * pulse)
        
        # Effet de fade si proche de l'expiration
        if self.age > self.lifetime * 0.8:
            alpha = int(255 * (1.0 - (self.age - self.lifetime * 0.8) / (self.lifetime * 0.2)))
        else:
            alpha = 255
        
        # Dessiner l'orbe avec halo
        if alpha > 0:
            # Halo externe
            halo_size = current_size + 6
            halo_surface = pygame.Surface((halo_size * 2, halo_size * 2), pygame.SRCALPHA)
            halo_color = (*self.color, min(alpha // 2, 100))
            pygame.draw.circle(halo_surface, halo_color, (halo_size, halo_size), halo_size)
            screen.blit(halo_surface, (int(self.x) - halo_size, int(self.y) - halo_size))
            
            # Orbe principal
            orb_color = (*self.color, alpha)
            orb_surface = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(orb_surface, orb_color, (current_size, current_size), current_size)
            screen.blit(orb_surface, (int(self.x) - current_size, int(self.y) - current_size))
            
            # Centre brillant
            center_size = current_size // 2
            center_color = (255, 255, 255, alpha)
            center_surface = pygame.Surface((center_size * 2, center_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(center_surface, center_color, (center_size, center_size), center_size)
            screen.blit(center_surface, (int(self.x) - center_size, int(self.y) - center_size))

class Enemy:
    """Classe représentant un ennemi basique."""
    
    # Variable de classe pour stocker les frames du GIF (partagées entre tous les ennemis)
    _alien_frames = None
    _frames_loaded = False
    _use_images = True  # Par défaut, utiliser les images
    
    def __init__(self, x: int, y: int, enemy_type: str = "basic", use_images: bool = True):
        # Définir si on utilise les images
        Enemy._use_images = use_images
        
        # Charger le GIF si ce n'est pas déjà fait et qu'on utilise les images
        if use_images and not Enemy._frames_loaded:
            self._load_alien_gif()
        
        # Taille de l'ennemi basée sur le sprite
        sprite_size = 40  # Taille par défaut
        if use_images and Enemy._alien_frames and len(Enemy._alien_frames) > 0:
            sprite_size = Enemy._alien_frames[0].get_width()
        
        self.rect = pygame.Rect(x, y, sprite_size, sprite_size)
        self.enemy_type = enemy_type
        
        # Position flottante pour mouvement précis
        self.x_float = float(x)
        self.y_float = float(y)
        
        # Animation
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 100  # ms entre chaque frame
        
        # Statistiques selon le type
        if enemy_type == "basic":
            self.max_health = 30
            self.speed = 80
            self.damage = 15
            self.xp_value = 10
            self.color = (255, 100, 100)
            self.scale = 1.0
        elif enemy_type == "fast":
            self.max_health = 20
            self.speed = 150
            self.damage = 10
            self.xp_value = 15
            self.color = (255, 150, 100)
            self.scale = 0.8
            self.animation_speed = 50  # Plus rapide
        elif enemy_type == "tank":
            self.max_health = 80
            self.speed = 40
            self.damage = 25
            self.xp_value = 25
            self.color = (150, 50, 50)
            self.scale = 1.3
            self.animation_speed = 150  # Plus lent
        
        self.health = self.max_health
        self.velocity = pygame.Vector2(0, 0)
        
        # Intelligence de l'IA (peut être modifié par l'adaptive AI)
        self.ai_intelligence = 1.0
        
        # 🧠 NOUVEAU: Cerveau d'apprentissage
        self.brain = None  # Sera initialisé par le système global
        self.last_distance = 0
        self.got_hit_this_frame = False
        self.hit_player_this_frame = False
        
        # État d'animation
        self.damage_flash_time = 0
        self.original_color = self.color
    
    @classmethod
    def _load_alien_gif(cls):
        """Charge les frames du GIF alien."""
        try:
            # Chemin vers le GIF
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            gif_path = os.path.join(project_root, 'img', 'alien', 'alien.gif')
            
            print(f"👽 Chargement du GIF alien: {gif_path}")
            
            # Ouvrir le GIF avec PIL
            gif = Image.open(gif_path)
            
            frames = []
            try:
                while True:
                    # Convertir la frame en surface pygame
                    frame = gif.copy().convert('RGBA')
                    
                    # Convertir PIL Image en pygame Surface
                    mode = frame.mode
                    size = frame.size
                    data = frame.tobytes()
                    
                    pygame_surface = pygame.image.fromstring(data, size, mode)
                    
                    # Redimensionner pour une taille raisonnable
                    scaled_surface = pygame.transform.scale(pygame_surface, (40, 40))
                    frames.append(scaled_surface)
                    
                    # Passer à la frame suivante
                    gif.seek(gif.tell() + 1)
            except EOFError:
                pass  # Fin du GIF
            
            cls._alien_frames = frames
            cls._frames_loaded = True
            print(f"✅ GIF alien chargé avec succès! ({len(frames)} frames)")
            
        except Exception as e:
            print(f"⚠️  Impossible de charger le GIF alien: {e}")
            print(f"   Utilisation de sprites par défaut")
            cls._alien_frames = []
            cls._frames_loaded = True
    
    def update(self, dt: float, player_pos: Tuple[int, int], player_velocity: pygame.Vector2 = None, player_health_ratio: float = 1.0):
        """Met à jour l'ennemi (IA, mouvement, etc.)."""
        # Mise à jour de l'animation
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            if Enemy._alien_frames and len(Enemy._alien_frames) > 0:
                self.current_frame = (self.current_frame + 1) % len(Enemy._alien_frames)
        
        # Si pas de velocity fournie, créer un vecteur nul
        if player_velocity is None:
            player_velocity = pygame.Vector2(0, 0)
        
        # Calculer la distance
        direction = pygame.Vector2(
            player_pos[0] - self.rect.centerx,
            player_pos[1] - self.rect.centery
        )
        distance = direction.length() if direction.length() > 0 else 0
        
        # 🧠 SYSTÈME D'APPRENTISSAGE DQN : Si le cerveau est activé
        if self.brain is not None:
            # Calculer la santé de l'ennemi
            enemy_health_ratio = self.health / self.max_health if self.max_health > 0 else 0.0
            
            # Obtenir l'état actuel (encodé en vecteur)
            current_state = self.brain.encode_state(
                (self.rect.centerx, self.rect.centery),
                player_pos,
                player_velocity,
                distance,
                player_health_ratio,
                enemy_health_ratio
            )
            
            # Si c'est la première frame, juste sauvegarder l'état
            if self.brain.current_state is None:
                self.brain.current_state = current_state
                self.brain.current_action = self.brain.choose_action(current_state)
            else:
                # Calculer la récompense pour l'action précédente
                distance_decreased = distance < self.last_distance
                reward = self.brain.calculate_reward(
                    dt,
                    hit_player=self.hit_player_this_frame,
                    got_hit=self.got_hit_this_frame,
                    distance=distance,
                    distance_decreased=distance_decreased
                )
                
                # Stocker l'expérience dans le replay buffer
                self.brain.store_experience(
                    self.brain.current_state,
                    self.brain.current_action,
                    reward,
                    current_state,
                    done=False
                )
                
                # Choisir la prochaine action
                self.brain.current_state = current_state
                self.brain.current_action = self.brain.choose_action(current_state)
            
            # Exécuter l'action choisie
            self.velocity = self.brain.execute_action(
                self.brain.current_action,
                (self.rect.centerx, self.rect.centery),
                player_pos,
                self.speed,
                dt
            )
            
            # Mettre à jour les stats du cerveau
            self.brain.lifetime += dt
            if distance < 200:
                self.brain.time_near_player += dt
            
            # Reset des flags
            self.got_hit_this_frame = False
            self.hit_player_this_frame = False
            
        else:
            # IA adaptative standard (comportement basé sur l'intelligence)
            if direction.length() > 0:
                direction = direction.normalize()
                
                # Intelligence > 1.5: esquive latérale et approche tactique
                if self.ai_intelligence > 1.5:
                    import math
                    # Mouvement sinusoïdal pour esquiver
                    time_factor = pygame.time.get_ticks() / 1000.0
                    perpendicular = pygame.Vector2(-direction.y, direction.x)
                    lateral_movement = perpendicular * math.sin(time_factor * 3) * 0.3
                    
                    # Si proche, reculer légèrement (kite strategy)
                    if distance < 150:
                        direction *= 0.5
                    
                    direction += lateral_movement
                    direction = direction.normalize()
                
                # Intelligence > 1.2: anticipation de la position du joueur
                elif self.ai_intelligence > 1.2:
                    # Prédire où sera le joueur (simple lead)
                    lead_factor = min(distance / 300.0, 1.0) * 0.3
                    direction = direction.normalize()
                    # Ajout d'une composante de prédiction simple
                    if hasattr(self, '_last_player_pos'):
                        player_velocity_calc = pygame.Vector2(
                            player_pos[0] - self._last_player_pos[0],
                            player_pos[1] - self._last_player_pos[1]
                        )
                        if player_velocity_calc.length() > 0:
                            direction += player_velocity_calc.normalize() * lead_factor
                            direction = direction.normalize()
                    self._last_player_pos = player_pos
                
                # Intelligence normale: comportement basique
                self.velocity = direction * self.speed
        
        # Application du mouvement avec position flottante
        self.x_float += self.velocity.x * dt / 1000
        self.y_float += self.velocity.y * dt / 1000
        
        # Mise à jour du rect avec les positions entières
        self.rect.x = int(self.x_float)
        self.rect.y = int(self.y_float)
        
        # Sauvegarder la distance pour le prochain calcul
        self.last_distance = distance
        
        # Réduction du flash de dégâts
        if self.damage_flash_time > 0:
            self.damage_flash_time -= dt
    
    def take_damage(self, damage: int):
        """L'ennemi subit des dégâts."""
        self.health -= damage
        self.damage_flash_time = 150  # Flash blanc pendant 150ms
        
        # 🧠 Marquer pour l'apprentissage
        self.got_hit_this_frame = True
        if self.brain:
            self.brain.damage_received += damage
        
        if self.health < 0:
            self.health = 0
    
    def is_dead(self) -> bool:
        """Vérifie si l'ennemi est mort."""
        return self.health <= 0
    
    def draw(self, screen):
        """Dessine l'ennemi."""
        # Mode training : sprite simple
        if not Enemy._use_images:
            # Dessiner un cercle simple coloré
            if self.damage_flash_time > 0:
                current_color = (255, 255, 255)  # Flash blanc
            else:
                current_color = self.original_color
            pygame.draw.circle(screen, current_color, self.rect.center, self.rect.width // 2)
        else:
            # Mode normal : utiliser le sprite animé si disponible
            if Enemy._alien_frames and len(Enemy._alien_frames) > 0:
                current_sprite = Enemy._alien_frames[self.current_frame]
                
                # Appliquer l'échelle selon le type
                if self.scale != 1.0:
                    width = int(current_sprite.get_width() * self.scale)
                    height = int(current_sprite.get_height() * self.scale)
                    current_sprite = pygame.transform.scale(current_sprite, (width, height))
                    # Ajuster le rect pour garder le centre
                    old_center = self.rect.center
                    self.rect = current_sprite.get_rect()
                    self.rect.center = old_center
                
                # Appliquer un effet de flash blanc si endommagé
                if self.damage_flash_time > 0:
                    # Créer une copie avec teinte blanche
                    flash_sprite = current_sprite.copy()
                    flash_sprite.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
                    screen.blit(flash_sprite, self.rect)
                else:
                    screen.blit(current_sprite, self.rect)
            else:
                # Fallback: dessiner un rectangle coloré
                if self.damage_flash_time > 0:
                    current_color = (255, 255, 255)  # Flash blanc
                else:
                    current_color = self.original_color
                pygame.draw.rect(screen, current_color, self.rect)
        
        # Barre de vie si endommagé
        if self.health < self.max_health:
            self._draw_health_bar(screen)
    
    def _draw_health_bar(self, screen):
        """Dessine la barre de vie au-dessus de l'ennemi."""
        bar_width = 25
        bar_height = 4
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.y - 8
        
        # Fond de la barre
        pygame.draw.rect(screen, (100, 100, 100), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Barre de vie
        health_percentage = self.health / self.max_health
        health_width = int(bar_width * health_percentage)
        if health_width > 0:
            pygame.draw.rect(screen, (255, 0, 0), 
                            (bar_x, bar_y, health_width, bar_height))

class EnemySpawner:
    """Gestionnaire pour l'apparition et la gestion des ennemis."""
    
    def __init__(self, screen_width: int, screen_height: int, use_images: bool = True):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.enemies: List[Enemy] = []
        self.use_images = use_images
        
        # Configuration du spawning
        self.spawn_zones = self._create_spawn_zones()
        self.enemy_types = ["basic", "fast", "tank"]
        self.type_weights = [0.6, 0.3, 0.1]  # Probabilités de spawn
        
        # Statistiques
        self.total_spawned = 0
        self.enemies_killed = 0
    
    def _create_spawn_zones(self) -> List[pygame.Rect]:
        """Crée les zones de spawn autour de l'écran."""
        margin = 50
        zones = [
            # Zone du haut
            pygame.Rect(-margin, -margin, self.screen_width + 2*margin, margin),
            # Zone du bas
            pygame.Rect(-margin, self.screen_height, self.screen_width + 2*margin, margin),
            # Zone de gauche
            pygame.Rect(-margin, 0, margin, self.screen_height),
            # Zone de droite
            pygame.Rect(self.screen_width, 0, margin, self.screen_height)
        ]
        return zones
    
    def spawn_enemy(self, player_pos: Tuple[int, int]):
        """Fait apparaître un nouvel ennemi."""
        # Choisir une zone de spawn aléatoire
        spawn_zone = random.choice(self.spawn_zones)
        
        # Position aléatoire dans la zone
        x = random.randint(spawn_zone.left, spawn_zone.right - 20)
        y = random.randint(spawn_zone.top, spawn_zone.bottom - 20)
        
        # S'assurer que l'ennemi ne spawn pas trop près du joueur
        distance_to_player = math.sqrt(
            (x - player_pos[0])**2 + (y - player_pos[1])**2
        )
        
        if distance_to_player < 100:
            # Repositionner loin du joueur
            angle = random.uniform(0, 2 * math.pi)
            x = player_pos[0] + math.cos(angle) * 150
            y = player_pos[1] + math.sin(angle) * 150
        
        # Choisir le type d'ennemi selon les probabilités
        enemy_type = random.choices(self.enemy_types, weights=self.type_weights)[0]
        
        # Créer et ajouter l'ennemi (avec ou sans images)
        enemy = Enemy(x, y, enemy_type, use_images=self.use_images)
        
        self.enemies.append(enemy)
        self.total_spawned += 1
        
        return enemy  # Retourner l'ennemi créé
    
    def update(self, dt: float, player_pos: Tuple[int, int], player_velocity: pygame.Vector2 = None, player_health_ratio: float = 1.0):
        """Met à jour tous les ennemis."""
        # Mise à jour de chaque ennemi
        for enemy in self.enemies:
            enemy.update(dt, player_pos, player_velocity, player_health_ratio)
        
        # Suppression des ennemis morts
        initial_count = len(self.enemies)
        self.enemies = [enemy for enemy in self.enemies if not enemy.is_dead()]
        self.enemies_killed += initial_count - len(self.enemies)
        
        # Augmentation progressive de la difficulté
        self._adjust_difficulty()
    
    def _adjust_difficulty(self):
        """Ajuste la difficulté selon le nombre d'ennemis tués."""
        if self.enemies_killed > 50:
            # Plus d'ennemis rapides et tanks
            self.type_weights = [0.4, 0.4, 0.2]
        elif self.enemies_killed > 20:
            self.type_weights = [0.5, 0.35, 0.15]
    
    def get_enemies_in_range(self, position: Tuple[int, int], range_radius: float) -> List[Enemy]:
        """Retourne les ennemis dans un rayon donné."""
        enemies_in_range = []
        for enemy in self.enemies:
            distance = math.sqrt(
                (enemy.rect.centerx - position[0])**2 + 
                (enemy.rect.centery - position[1])**2
            )
            if distance <= range_radius:
                enemies_in_range.append(enemy)
        return enemies_in_range
    
    def clear_all_enemies(self):
        """Supprime tous les ennemis (utile pour certains effets de cartes)."""
        self.enemies_killed += len(self.enemies)
        self.enemies.clear()
    
    def draw(self, screen):
        """Dessine tous les ennemis."""
        for enemy in self.enemies:
            enemy.draw(screen)
    
    def get_stats(self) -> dict:
        """Retourne les statistiques du spawner."""
        return {
            'total_spawned': self.total_spawned,
            'enemies_killed': self.enemies_killed,
            'current_enemies': len(self.enemies)
        }
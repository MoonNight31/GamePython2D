import pygame
import random
import math
from typing import List, Tuple
from dataclasses import dataclass

class Enemy:
    """Classe représentant un ennemi basique."""
    
    def __init__(self, x: int, y: int, enemy_type: str = "basic"):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.enemy_type = enemy_type
        
        # Position flottante pour mouvement précis
        self.x_float = float(x)
        self.y_float = float(y)
        
        # Statistiques selon le type
        if enemy_type == "basic":
            self.max_health = 30
            self.speed = 80
            self.damage = 15
            self.xp_value = 10
            self.color = (255, 100, 100)
        elif enemy_type == "fast":
            self.max_health = 20
            self.speed = 150
            self.damage = 10
            self.xp_value = 15
            self.color = (255, 150, 100)
        elif enemy_type == "tank":
            self.max_health = 80
            self.speed = 40
            self.damage = 25
            self.xp_value = 25
            self.color = (150, 50, 50)
        
        self.health = self.max_health
        self.velocity = pygame.Vector2(0, 0)
        
        # État d'animation
        self.damage_flash_time = 0
        self.original_color = self.color
    
    def update(self, dt: float, player_pos: Tuple[int, int]):
        """Met à jour l'ennemi (IA, mouvement, etc.)."""
        # IA simple : se diriger vers le joueur
        direction = pygame.Vector2(
            player_pos[0] - self.rect.centerx,
            player_pos[1] - self.rect.centery
        )
        
        if direction.length() > 0:
            direction = direction.normalize()
            self.velocity = direction * self.speed
            
            # Application du mouvement avec position flottante
            self.x_float += self.velocity.x * dt / 1000
            self.y_float += self.velocity.y * dt / 1000
            
            # Mise à jour du rect avec les positions entières
            self.rect.x = int(self.x_float)
            self.rect.y = int(self.y_float)
        
        # Réduction du flash de dégâts
        if self.damage_flash_time > 0:
            self.damage_flash_time -= dt
    
    def take_damage(self, damage: int):
        """L'ennemi subit des dégâts."""
        self.health -= damage
        self.damage_flash_time = 150  # Flash blanc pendant 150ms
        
        if self.health < 0:
            self.health = 0
    
    def is_dead(self) -> bool:
        """Vérifie si l'ennemi est mort."""
        return self.health <= 0
    
    def draw(self, screen):
        """Dessine l'ennemi."""
        # Couleur selon l'état
        if self.damage_flash_time > 0:
            current_color = (255, 255, 255)  # Flash blanc
        else:
            current_color = self.original_color
        
        # Corps de l'ennemi
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
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.enemies: List[Enemy] = []
        
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
        
        # Créer et ajouter l'ennemi
        enemy = Enemy(x, y, enemy_type)
        self.enemies.append(enemy)
        self.total_spawned += 1
    
    def update(self, dt: float, player_pos: Tuple[int, int]):
        """Met à jour tous les ennemis."""
        # Mise à jour de chaque ennemi
        for enemy in self.enemies:
            enemy.update(dt, player_pos)
        
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
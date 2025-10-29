import pygame
import math
from typing import List
from dataclasses import dataclass

@dataclass
class Projectile:
    """Classe représentant un projectile tiré par le joueur."""
    rect: pygame.Rect
    velocity_x: float
    velocity_y: float
    damage: int
    speed: float
    active: bool = True
    
    def update(self, dt: float):
        """Met à jour la position du projectile."""
        self.rect.x += self.velocity_x * dt / 1000
        self.rect.y += self.velocity_y * dt / 1000
        
        # Désactiver si hors écran
        if (self.rect.x < -50 or self.rect.x > 1250 or 
            self.rect.y < -50 or self.rect.y > 850):
            self.active = False
    
    def draw(self, screen):
        """Dessine le projectile."""
        # Projectile avec effet de glow
        # Centre brillant
        pygame.draw.circle(screen, (255, 255, 200), self.rect.center, 4)
        # Cercle principal
        pygame.draw.circle(screen, (255, 255, 100), self.rect.center, 3)
        # Halo externe
        glow_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 255, 0, 60), (10, 10), 8)
        screen.blit(glow_surface, (self.rect.centerx - 10, self.rect.centery - 10))

class Player:
    """Classe représentant le joueur avec déplacement et attaque."""
    
    def __init__(self, x: int, y: int):
        # Position et collision
        self.rect = pygame.Rect(x, y, 30, 30)
        self.speed = 200  # pixels par seconde
        
        # Statistiques
        self.max_health = 100
        self.health = self.max_health
        self.attack_damage = 25
        self.attack_speed = 10.0  # 10 attaques par seconde pour l'IA !
        
        # État du joueur
        self.last_attack_time = 0
        self.facing_direction = pygame.Vector2(1, 0)  # Direction vers laquelle le joueur regarde
        
        # Projectiles
        self.projectiles: List[Projectile] = []
        self.projectile_speed = 300
        
        # Animation simple
        self.color = (0, 150, 255)
        self.damaged_color = (255, 100, 100)
        self.damage_flash_time = 0
        
        # Améliorations par cartes
        self.card_effects = {
            'speed_multiplier': 1.0,
            'damage_multiplier': 1.0,
            'attack_speed_multiplier': 1.0,
            'health_bonus': 0,
            'projectile_count': 1
        }
    
    def handle_event(self, event):
        """Gère les événements d'entrée spécifiques au joueur."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                self.attack(pygame.mouse.get_pos())
    
    def update(self, dt: float):
        """Met à jour l'état du joueur."""
        # Gestion du mouvement
        self._handle_movement(dt)
        
        # Mise à jour des projectiles
        self._update_projectiles(dt)
        
        # Réduction du flash de dégâts
        if self.damage_flash_time > 0:
            self.damage_flash_time -= dt
    
    def _handle_movement(self, dt: float):
        """Gère le déplacement du joueur."""
        keys = pygame.key.get_pressed()
        velocity = pygame.Vector2(0, 0)
        
        # Mouvement WASD ou flèches
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            velocity.y = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            velocity.y = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            velocity.x = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            velocity.x = 1
        
        # Normalisation pour le mouvement diagonal
        if velocity.length() > 0:
            velocity = velocity.normalize()
            
            # Application de la vitesse et des bonus
            effective_speed = self.speed * self.card_effects['speed_multiplier']
            self.rect.x += velocity.x * effective_speed * dt / 1000
            self.rect.y += velocity.y * effective_speed * dt / 1000
            
            # Mise à jour de la direction
            self.facing_direction = velocity
        
        # Limites de l'écran
        self.rect.clamp_ip(pygame.Rect(0, 0, 1200, 800))
    
    def _update_projectiles(self, dt: float):
        """Met à jour tous les projectiles."""
        # Suppression des projectiles inactifs
        self.projectiles = [p for p in self.projectiles if p.active]
        
        # Mise à jour des projectiles actifs
        for projectile in self.projectiles:
            projectile.update(dt)
    
    def attack(self, target_pos):
        """Effectue une attaque vers la position cible."""
        current_time = pygame.time.get_ticks()
        attack_cooldown = 1000 / (self.attack_speed * self.card_effects['attack_speed_multiplier'])
        
        if current_time - self.last_attack_time >= attack_cooldown:
            self.last_attack_time = current_time
            
            # Calcul de la direction vers la cible
            direction = pygame.Vector2(
                target_pos[0] - self.rect.centerx,
                target_pos[1] - self.rect.centery
            )
            
            if direction.length() > 0:
                direction = direction.normalize()
                
                # Création des projectiles (peut être multiple avec certaines cartes)
                projectile_count = self.card_effects['projectile_count']
                angle_spread = 0.3 if projectile_count > 1 else 0
                
                for i in range(projectile_count):
                    # Calcul de l'angle pour chaque projectile
                    if projectile_count > 1:
                        angle_offset = (i - (projectile_count - 1) / 2) * angle_spread
                        rotated_direction = direction.rotate(math.degrees(angle_offset))
                    else:
                        rotated_direction = direction
                    
                    # Création du projectile
                    projectile = Projectile(
                        rect=pygame.Rect(self.rect.centerx - 3, self.rect.centery - 3, 6, 6),
                        velocity_x=rotated_direction.x * self.projectile_speed,
                        velocity_y=rotated_direction.y * self.projectile_speed,
                        damage=int(self.attack_damage * self.card_effects['damage_multiplier']),
                        speed=self.projectile_speed
                    )
                    
                    self.projectiles.append(projectile)
    
    def take_damage(self, damage: int):
        """Le joueur subit des dégâts."""
        self.health -= damage
        self.damage_flash_time = 200  # Flash rouge pendant 200ms
        
        if self.health < 0:
            self.health = 0
    
    def heal(self, amount: int):
        """Soigne le joueur."""
        self.health = min(self.max_health + self.card_effects['health_bonus'], 
                         self.health + amount)
    
    def apply_card_effect(self, card):
        """Applique l'effet d'une carte sélectionnée."""
        effect_type = card['effect_type']
        value = card['value']
        
        if effect_type == 'speed_boost':
            self.card_effects['speed_multiplier'] += value
        elif effect_type == 'damage_boost':
            self.card_effects['damage_multiplier'] += value
        elif effect_type == 'attack_speed_boost':
            self.card_effects['attack_speed_multiplier'] += value
        elif effect_type == 'health_boost':
            self.card_effects['health_bonus'] += value
            self.max_health += value
            self.health += value
        elif effect_type == 'multi_shot':
            self.card_effects['projectile_count'] += value
        elif effect_type == 'heal':
            self.heal(value)
        elif effect_type == 'all_stats':
            # Améliore tous les stats
            self.card_effects['speed_multiplier'] += value
            self.card_effects['damage_multiplier'] += value
            self.card_effects['attack_speed_multiplier'] += value
            health_bonus = int(value * 100)
            self.card_effects['health_bonus'] += health_bonus
            self.max_health += health_bonus
            self.health += health_bonus
    
    def draw(self, screen):
        """Dessine le joueur et ses projectiles."""
        # Couleur selon l'état
        current_color = self.damaged_color if self.damage_flash_time > 0 else self.color
        
        # Corps principal du joueur
        pygame.draw.rect(screen, current_color, self.rect)
        
        # Indicateur de direction
        direction_end = (
            self.rect.centerx + self.facing_direction.x * 20,
            self.rect.centery + self.facing_direction.y * 20
        )
        pygame.draw.line(screen, (255, 255, 255), self.rect.center, direction_end, 2)
        
        # Projectiles
        for projectile in self.projectiles:
            projectile.draw(screen)
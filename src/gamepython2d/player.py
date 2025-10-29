import pygame
import math
import os
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
    
    def __init__(self, x: int, y: int, use_images: bool = True):
        # Charger l'image du vaisseau (ou utiliser un sprite simple)
        self.use_images = use_images
        self._load_image()
        
        # Position et collision (ajusté à la taille de l'image)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 200  # pixels par seconde
        
        # Statistiques
        self.max_health = 100
        self.health = self.max_health
        self.attack_damage = 25
        self.attack_speed = 10.0  # 10 attaques par seconde pour l'IA !
        
        # État du joueur
        self.last_attack_time = 0
        self.facing_direction = pygame.Vector2(1, 0)  # Direction vers laquelle le joueur regarde
        self.angle = 0  # Angle de rotation du vaisseau
        
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
    
    def _load_image(self):
        """Charge l'image du vaisseau spatial ou crée un sprite simple."""
        # Mode training : utiliser un simple carré pour performance
        if not self.use_images:
            self.original_image = pygame.Surface((30, 30), pygame.SRCALPHA)
            # Dessiner un triangle (vaisseau simplifié)
            pygame.draw.polygon(self.original_image, (0, 150, 255), 
                              [(15, 0), (30, 30), (15, 22), (0, 30)])
            self.image = self.original_image.copy()
            return
        
        # Mode normal : charger l'image
        try:
            # Chemin relatif vers l'image
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Remonter de src/gamepython2d au projet root
            project_root = os.path.dirname(os.path.dirname(current_dir))
            image_path = os.path.join(project_root, 'img', 'spaceship', 'spaceship.png')
            
            print(f"🚀 Chargement de l'image: {image_path}")
            
            # Charger et redimensionner l'image
            original_image = pygame.image.load(image_path).convert_alpha()
            # Redimensionner à une taille raisonnable (environ 50x50)
            self.original_image = pygame.transform.scale(original_image, (50, 50))
            self.image = self.original_image.copy()
            
            print(f"✅ Image du vaisseau chargée avec succès!")
            
        except (pygame.error, FileNotFoundError) as e:
            # Fallback: créer une surface de base si l'image n'est pas trouvée
            print(f"⚠️  Impossible de charger l'image du vaisseau: {e}")
            print(f"   Utilisation d'un sprite par défaut")
            self.original_image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.polygon(self.original_image, (0, 150, 255), 
                              [(15, 0), (30, 30), (15, 22), (0, 30)])
            self.image = self.original_image.copy()
    
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
        if keys[pygame.K_z] or keys[pygame.K_UP]:
            velocity.y = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            velocity.y = 1
        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
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
            
            # Mise à jour de la direction et angle
            self.facing_direction = velocity
            # Calculer l'angle pour la rotation
            # L'image de base pointe vers le haut (0°), donc on ajuste de -90°
            # atan2 donne l'angle depuis l'axe X (droite), on soustrait 90° pour partir du haut
            self.angle = -math.degrees(math.atan2(velocity.y, velocity.x)) - 90
            self._update_rotated_image()
        
        # Limites de l'écran
        self.rect.clamp_ip(pygame.Rect(0, 0, 1200, 800))
    
    def _update_rotated_image(self):
        """Met à jour l'image avec la rotation actuelle."""
        # Rotation de l'image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        # Mettre à jour le rect pour garder le centre
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
    
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
        # Appliquer un effet de flash rouge si endommagé
        if self.damage_flash_time > 0:
            # Créer une copie de l'image avec teinte rouge
            flash_image = self.image.copy()
            flash_image.fill((255, 100, 100, 128), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(flash_image, self.rect)
        else:
            # Dessiner l'image normale du vaisseau
            screen.blit(self.image, self.rect)
        
        # Projectiles
        for projectile in self.projectiles:
            projectile.draw(screen)
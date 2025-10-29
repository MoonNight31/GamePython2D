#!/usr/bin/env python3
"""
🎆 Système d'effets visuels pour GamePython2D
Particules, animations et effets spéciaux pour les cartes et actions
"""

import pygame
import math
import random
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Particle:
    """Particule individuelle pour les effets."""
    x: float
    y: float
    vel_x: float
    vel_y: float
    life: float
    max_life: float
    size: float
    color: Tuple[int, int, int]
    alpha: int = 255
    gravity: float = 0.0

class EffectsSystem:
    """Système de gestion des effets visuels."""
    
    def __init__(self):
        self.particles: List[Particle] = []
        self.screen_shakes = []
        self.flash_effects = []
        
        # Cache des surfaces pour optimisation
        self.particle_surfaces = {}
        
        # Couleurs prédéfinies par rareté
        self.rarity_colors = {
            'common': [(200, 200, 200), (150, 150, 150)],
            'uncommon': [(100, 255, 100), (50, 200, 50)],
            'rare': [(100, 150, 255), (50, 100, 200)],
            'epic': [(255, 100, 255), (200, 50, 200)],
            'legendary': [(255, 215, 0), (255, 165, 0)]
        }
    
    def update(self, dt: float):
        """Met à jour tous les effets."""
        self._update_particles(dt)
        self._update_screen_shakes(dt)
        self._update_flash_effects(dt)
    
    def _update_particles(self, dt: float):
        """Met à jour les particules."""
        for particle in self.particles[:]:
            # Mouvement
            particle.x += particle.vel_x * dt
            particle.y += particle.vel_y * dt
            particle.vel_y += particle.gravity * dt
            
            # Vie
            particle.life -= dt
            if particle.life <= 0:
                self.particles.remove(particle)
                continue
            
            # Alpha basé sur la vie restante
            life_ratio = particle.life / particle.max_life
            particle.alpha = int(255 * life_ratio)
    
    def _update_screen_shakes(self, dt: float):
        """Met à jour les tremblements d'écran."""
        for shake in self.screen_shakes[:]:
            shake['duration'] -= dt
            if shake['duration'] <= 0:
                self.screen_shakes.remove(shake)
    
    def _update_flash_effects(self, dt: float):
        """Met à jour les effets de flash."""
        for flash in self.flash_effects[:]:
            flash['duration'] -= dt
            if flash['duration'] <= 0:
                self.flash_effects.remove(flash)
    
    def create_card_selection_effect(self, x: int, y: int, rarity: str):
        """Crée un effet de sélection de carte spectaculaire."""
        colors = self.rarity_colors.get(rarity, self.rarity_colors['common'])
        
        # Explosion de particules selon la rareté
        particle_count = {
            'common': 20,
            'uncommon': 35,
            'rare': 50,
            'epic': 75,
            'legendary': 100
        }.get(rarity, 20)
        
        # Particules d'explosion
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 200)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            # Couleur aléatoire de la rareté
            color = random.choice(colors)
            
            particle = Particle(
                x=x + random.uniform(-50, 50),
                y=y + random.uniform(-50, 50),
                vel_x=vel_x,
                vel_y=vel_y,
                life=random.uniform(0.5, 1.5),
                max_life=1.5,
                size=random.uniform(2, 8),
                color=color,
                gravity=100
            )
            self.particles.append(particle)
        
        # Particules montantes (effet magique)
        for _ in range(particle_count // 2):
            particle = Particle(
                x=x + random.uniform(-100, 100),
                y=y + random.uniform(50, 100),
                vel_x=random.uniform(-20, 20),
                vel_y=random.uniform(-100, -200),
                life=random.uniform(1.0, 2.0),
                max_life=2.0,
                size=random.uniform(1, 4),
                color=colors[0],
                gravity=-20  # Anti-gravité pour effet magique
            )
            self.particles.append(particle)
        
        # Effet de flash selon la rareté
        flash_intensity = {
            'common': 0.3,
            'uncommon': 0.5,
            'rare': 0.7,
            'epic': 0.9,
            'legendary': 1.0
        }.get(rarity, 0.3)
        
        self.flash_effects.append({
            'color': colors[0],
            'intensity': flash_intensity,
            'duration': 0.2,
            'max_duration': 0.2
        })
        
        # Tremblement d'écran pour les cartes rares+
        if rarity in ['rare', 'epic', 'legendary']:
            shake_intensity = {
                'rare': 5,
                'epic': 8,
                'legendary': 12
            }.get(rarity, 5)
            
            self.screen_shakes.append({
                'intensity': shake_intensity,
                'duration': 0.3,
                'max_duration': 0.3
            })
    
    def create_upgrade_effect(self, x: int, y: int, effect_type: str):
        """Crée un effet pour l'application d'un upgrade."""
        effect_colors = {
            'speed_boost': [(100, 255, 255), (50, 200, 255)],  # Cyan
            'damage_boost': [(255, 100, 100), (200, 50, 50)],  # Rouge
            'attack_speed_boost': [(255, 255, 100), (200, 200, 50)],  # Jaune
            'health_boost': [(100, 255, 100), (50, 200, 50)],  # Vert
            'heal': [(255, 200, 255), (200, 150, 200)],  # Rose
            'multi_shot': [(200, 100, 255), (150, 50, 200)],  # Violet
            'all_stats': [(255, 215, 0), (255, 165, 0)]  # Or
        }
        
        colors = effect_colors.get(effect_type, [(255, 255, 255), (200, 200, 200)])
        
        # Cercle de particules qui s'étend
        for i in range(30):
            angle = (i / 30) * 2 * math.pi
            speed = random.uniform(80, 120)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            particle = Particle(
                x=x,
                y=y,
                vel_x=vel_x,
                vel_y=vel_y,
                life=1.0,
                max_life=1.0,
                size=random.uniform(3, 6),
                color=random.choice(colors)
            )
            self.particles.append(particle)
        
        # Flash d'application
        self.flash_effects.append({
            'color': colors[0],
            'intensity': 0.4,
            'duration': 0.15,
            'max_duration': 0.15
        })
    
    def draw(self, screen: pygame.Surface):
        """Dessine tous les effets."""
        # Appliquer les tremblements d'écran
        shake_offset_x = 0
        shake_offset_y = 0
        
        for shake in self.screen_shakes:
            progress = 1.0 - (shake['duration'] / shake['max_duration'])
            intensity = shake['intensity'] * (1.0 - progress)  # Diminue avec le temps
            
            shake_offset_x += random.uniform(-intensity, intensity)
            shake_offset_y += random.uniform(-intensity, intensity)
        
        # Sauvegarder la position originale si shake
        original_offset = (0, 0)
        if shake_offset_x != 0 or shake_offset_y != 0:
            # Note: Le shake sera appliqué lors du blit final
            pass
        
        # Dessiner les particules
        for particle in self.particles:
            self._draw_particle(screen, particle, (shake_offset_x, shake_offset_y))
        
        # Appliquer les effets de flash
        for flash in self.flash_effects:
            progress = 1.0 - (flash['duration'] / flash['max_duration'])
            alpha = int(255 * flash['intensity'] * (1.0 - progress))
            
            if alpha > 0:
                flash_surface = pygame.Surface(screen.get_size())
                flash_surface.set_alpha(alpha)
                flash_surface.fill(flash['color'])
                screen.blit(flash_surface, (0, 0))
    
    def _draw_particle(self, screen: pygame.Surface, particle: Particle, shake_offset: Tuple[float, float]):
        """Dessine une particule individuelle."""
        if particle.alpha <= 0:
            return
        
        # Position avec shake
        x = int(particle.x + shake_offset[0])
        y = int(particle.y + shake_offset[1])
        
        # Créer une surface pour la particule avec alpha
        size = max(1, int(particle.size))
        particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # Couleur avec alpha
        color_with_alpha = (*particle.color, particle.alpha)
        
        # Dessiner un cercle avec dégradé
        pygame.draw.circle(particle_surf, color_with_alpha, (size, size), size)
        
        # Effet de glow (halo)
        if particle.size > 3:
            glow_color = (*particle.color, particle.alpha // 3)
            pygame.draw.circle(particle_surf, glow_color, (size, size), size + 2)
        
        # Blit sur l'écran
        screen.blit(particle_surf, (x - size, y - size))
    
    def create_projectile_impact_effect(self, x: int, y: int):
        """Effet d'impact des projectiles."""
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 80)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            particle = Particle(
                x=x,
                y=y,
                vel_x=vel_x,
                vel_y=vel_y,
                life=0.3,
                max_life=0.3,
                size=random.uniform(1, 3),
                color=(255, 255, 100),
                gravity=50
            )
            self.particles.append(particle)
    
    def create_projectile_fire_effect(self, x: int, y: int):
        """Effet de tir d'un projectile."""
        for _ in range(5):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(10, 30)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            particle = Particle(
                x=x,
                y=y,
                vel_x=vel_x,
                vel_y=vel_y,
                life=0.2,
                max_life=0.2,
                size=random.uniform(1, 2),
                color=(255, 255, 200),
                gravity=20
            )
            self.particles.append(particle)
    
    def create_enemy_death_effect(self, x: int, y: int):
        """Effet de mort d'ennemi."""
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(40, 100)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            particle = Particle(
                x=x,
                y=y,
                vel_x=vel_x,
                vel_y=vel_y,
                life=0.5,
                max_life=0.5,
                size=random.uniform(2, 5),
                color=(255, 50, 50),
                gravity=80
            )
            self.particles.append(particle)
    
    def create_level_up_effect(self, x: int, y: int):
        """Effet de montée de niveau spectaculaire."""
        # Grande explosion de particules dorées
        for _ in range(50):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(80, 200)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            particle = Particle(
                x=x,
                y=y,
                vel_x=vel_x,
                vel_y=vel_y,
                life=random.uniform(1.0, 2.0),
                max_life=2.0,
                size=random.uniform(3, 8),
                color=random.choice([(255, 215, 0), (255, 255, 0), (255, 165, 0)]),
                gravity=50
            )
            self.particles.append(particle)
        
        # Particules montantes
        for _ in range(30):
            particle = Particle(
                x=x + random.uniform(-80, 80),
                y=y + random.uniform(0, 100),
                vel_x=random.uniform(-30, 30),
                vel_y=random.uniform(-150, -250),
                life=random.uniform(1.5, 2.5),
                max_life=2.5,
                size=random.uniform(2, 6),
                color=(255, 255, 200),
                gravity=-30  # Anti-gravité
            )
            self.particles.append(particle)
        
        # Flash intense
        self.flash_effects.append({
            'color': (255, 215, 0),
            'intensity': 1.0,
            'duration': 0.3,
            'max_duration': 0.3
        })
        
        # Gros tremblement
        self.screen_shakes.append({
            'intensity': 15,
            'duration': 0.5,
            'max_duration': 0.5
        })
    
    def create_projectile_trail(self, x: int, y: int):
        """Crée une traînée pour les projectiles en mouvement."""
        particle = Particle(
            x=x + random.uniform(-2, 2),
            y=y + random.uniform(-2, 2),
            vel_x=random.uniform(-5, 5),
            vel_y=random.uniform(-5, 5),
            life=0.15,
            max_life=0.15,
            size=random.uniform(1, 2),
            color=(255, 255, 150),
            gravity=0
        )
        self.particles.append(particle)
    
    def clear_all_effects(self):
        """Nettoie tous les effets."""
        self.particles.clear()
        self.screen_shakes.clear()
        self.flash_effects.clear()
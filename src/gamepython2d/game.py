import pygame
import sys
from typing import List, Optional
from .player import Player
from .enemy import EnemySpawner
from .xp_system import XPSystem
from .card_system import CardDraft
from .ui import GameUI

class Game:
    """Classe principale du jeu gérant la boucle de jeu et tous les systèmes."""
    
    def __init__(self, width: int = 1200, height: int = 800):
        pygame.init()
        
        # Configuration de l'écran
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Game Python 2D - Roguelike")
        
        # Horloge pour contrôler les FPS
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # État du jeu
        self.running = True
        self.paused = False
        self.game_state = "playing"  # "playing", "drafting", "game_over"
        
        # Initialisation des systèmes de jeu
        self.player = Player(width // 2, height // 2)
        self.enemy_spawner = EnemySpawner(width, height)
        self.xp_system = XPSystem()
        self.card_draft = CardDraft()
        self.ui = GameUI(width, height)
        
        # Timer pour le spawning des ennemis
        self.spawn_timer = 0
        self.spawn_interval = 2000  # millisecondes
        
    def handle_events(self):
        """Gère tous les événements d'entrée."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE and self.game_state == "playing":
                    self.paused = not self.paused
            
            # Gestion des événements spécifiques selon l'état du jeu
            if self.game_state == "drafting":
                self.card_draft.handle_event(event)
            elif self.game_state == "playing" and not self.paused:
                self.player.handle_event(event)
    
    def update(self, dt: float):
        """Met à jour la logique du jeu."""
        if self.paused or self.game_state != "playing":
            return
        
        # Mise à jour du joueur
        self.player.update(dt)
        
        # Spawning des ennemis
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.enemy_spawner.spawn_enemy(self.player.rect.center)
            self.spawn_timer = 0
            # Augmente la difficulté progressivement
            self.spawn_interval = max(500, self.spawn_interval - 10)
        
        # Mise à jour des ennemis
        self.enemy_spawner.update(dt, self.player.rect.center)
        
        # Détection des collisions
        self._handle_collisions()
        
        # Vérification de la mort du joueur
        if self.player.health <= 0:
            self.game_state = "game_over"
    
    def _handle_collisions(self):
        """Gère toutes les collisions du jeu."""
        # Collision joueur-ennemis
        for enemy in self.enemy_spawner.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.player.take_damage(enemy.damage)
                enemy.health = 0  # L'ennemi meurt après attaque
        
        # Collision attaques joueur-ennemis
        for projectile in self.player.projectiles:
            for enemy in self.enemy_spawner.enemies:
                if projectile.rect.colliderect(enemy.rect):
                    enemy.take_damage(projectile.damage)
                    projectile.active = False
                    
                    # Si l'ennemi meurt, donner de l'XP
                    if enemy.health <= 0:
                        xp_gained = self.xp_system.gain_xp(enemy.xp_value)
                        
                        # Vérification du level up
                        if self.xp_system.check_level_up():
                            self.game_state = "drafting"
                            self.card_draft.start_draft(self.xp_system.level)
    
    def render(self):
        """Effectue le rendu de tous les éléments."""
        # Fond noir
        self.screen.fill((20, 20, 30))
        
        if self.game_state == "playing":
            # Rendu des éléments de jeu
            self.player.draw(self.screen)
            self.enemy_spawner.draw(self.screen)
            
            # Interface utilisateur
            self.ui.draw_hud(self.screen, self.player, self.xp_system)
            
            if self.paused:
                self.ui.draw_pause_screen(self.screen)
        
        elif self.game_state == "drafting":
            # Écran de draft des cartes
            self.card_draft.draw(self.screen)
            
            # Vérifier si le draft est terminé
            if self.card_draft.is_complete():
                selected_card = self.card_draft.get_selected_card()
                if selected_card:
                    self.player.apply_card_effect(selected_card)
                self.game_state = "playing"
        
        elif self.game_state == "game_over":
            self.ui.draw_game_over(self.screen, self.xp_system.level)
        
        pygame.display.flip()
    
    def run(self):
        """Boucle principale du jeu."""
        print("Démarrage du jeu...")
        print("Contrôles:")
        print("- WASD ou flèches : déplacement")
        print("- Clic gauche : attaquer")
        print("- Espace : pause")
        print("- Échap : quitter")
        
        while self.running:
            dt = self.clock.tick(self.fps)
            
            self.handle_events()
            self.update(dt)
            self.render()
        
        pygame.quit()
        sys.exit()
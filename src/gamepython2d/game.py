import pygame
import sys
import random
from typing import List, Optional
from .player import Player
from .enemy import EnemySpawner, XPOrb
from .xp_system import XPSystem
from .card_system import CardDraft
from .ui import GameUI
from .effects_system import EffectsSystem
from .audio_system import AudioSystem

class Game:
    """Classe principale du jeu gérant la boucle de jeu et tous les systèmes."""
    
    def __init__(self, width: int = 800, height: int = 600):
        pygame.init()
        
        # Configuration de l'écran
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Game Python 2D - Roguelike")
        
        # Horloge pour contrôler les FPS
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # ✅ NOUVEAU : Système de caméra
        self.world_size = max(width, height)  # Monde = taille de l'écran
        self.camera_x = 0
        self.camera_y = 0
        self.tile_size = 100  # Taille des tuiles du fond
        
        # État du jeu
        self.running = True
        self.paused = False
        self.game_state = "menu"  # "menu", "playing", "drafting", "game_over"
        
        # Configuration du menu
        self.menu_font_title = pygame.font.Font(None, 80)
        self.menu_font_button = pygame.font.Font(None, 50)
        self.menu_buttons = [
            {"text": "Jouer", "rect": pygame.Rect(width // 2 - 150, height // 2 - 50, 300, 70), "action": "play"},
            {"text": "Quitter", "rect": pygame.Rect(width // 2 - 150, height // 2 + 50, 300, 70), "action": "quit"}
        ]
        self.menu_selected = 0
        
        # Initialisation des systèmes de jeu
        world_center = self.world_size // 2
        self.player = Player(world_center, world_center)
        self.enemy_spawner = EnemySpawner(self.world_size, self.world_size)
        self.xp_system = XPSystem()
        self.card_draft = CardDraft()
        self.ui = GameUI(width, height)
        
        # Liste des orbes d'XP à collecter
        self.xp_orbs = []
        
        # Systèmes d'effets et audio
        self.effects = EffectsSystem()
        self.audio = AudioSystem()
        
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
                    if self.game_state == "menu":
                        self.running = False
                    else:
                        self.game_state = "menu"
                elif event.key == pygame.K_SPACE and self.game_state == "playing":
                    self.paused = not self.paused
                
                # Navigation dans le menu
                elif self.game_state == "menu":
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_selected = (self.menu_selected - 1) % len(self.menu_buttons)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_selected = (self.menu_selected + 1) % len(self.menu_buttons)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self._handle_menu_action(self.menu_buttons[self.menu_selected]["action"])
            
            # Clic souris dans le menu
            elif event.type == pygame.MOUSEBUTTONDOWN and self.game_state == "menu":
                mouse_pos = pygame.mouse.get_pos()
                for i, button in enumerate(self.menu_buttons):
                    if button["rect"].collidepoint(mouse_pos):
                        self.menu_selected = i
                        self._handle_menu_action(button["action"])
            
            # Gestion des événements spécifiques selon l'état du jeu
            if self.game_state == "drafting":
                self.card_draft.handle_event(event)
            elif self.game_state == "playing" and not self.paused:
                # Convertir la position de la souris en coordonnées monde
                mouse_screen_pos = pygame.mouse.get_pos()
                mouse_world_pos = self._screen_to_world(mouse_screen_pos[0], mouse_screen_pos[1])
                self.player.handle_event(event, mouse_world_pos)
    
    def _handle_menu_action(self, action: str):
        """Gère les actions du menu principal."""
        if action == "play":
            self._start_new_game()
        elif action == "quit":
            self.running = False
    
    def _start_new_game(self):
        """Démarre une nouvelle partie en réinitialisant tous les systèmes."""
        # Réinitialiser le joueur au centre du monde
        world_center = self.world_size // 2
        self.player = Player(world_center, world_center)
        
        # Réinitialiser les ennemis avec la taille du monde
        self.enemy_spawner = EnemySpawner(self.world_size, self.world_size)
        
        # Réinitialiser le système d'XP
        self.xp_system.reset()
        
        # Vider les orbes
        self.xp_orbs.clear()
        
        # Réinitialiser les timers
        self.spawn_timer = 0
        
        # ✅ NOUVEAU : Centrer la caméra
        self._update_camera()
        
        # Passer en mode jeu
        self.game_state = "playing"
        self.paused = False
    
    def update(self, dt: float):
        """Met à jour la logique du jeu."""
        if self.paused or self.game_state != "playing":
            return
        
        # Compter les projectiles avant mise à jour
        projectiles_before = len(self.player.projectiles)
        
        # Convertir la position de la souris en coordonnées monde pour le tir continu
        mouse_screen_pos = pygame.mouse.get_pos()
        mouse_world_pos = self._screen_to_world(mouse_screen_pos[0], mouse_screen_pos[1])
        
        # Mise à jour du joueur (avec world_size et position souris monde)
        self.player.update(dt, self.world_size, mouse_world_pos)
        
        # ✅ Limiter le CENTRE du joueur au monde (pas le rect entier)
        if self.player.rect.centerx < 0:
            self.player.rect.centerx = 0
        elif self.player.rect.centerx > self.world_size:
            self.player.rect.centerx = self.world_size
            
        if self.player.rect.centery < 0:
            self.player.rect.centery = 0
        elif self.player.rect.centery > self.world_size:
            self.player.rect.centery = self.world_size
        
        # ✅ NOUVEAU : Mettre à jour la caméra pour suivre le joueur
        self._update_camera()
        
        # Vérifier si de nouveaux projectiles ont été créés
        projectiles_after = len(self.player.projectiles)
        if projectiles_after > projectiles_before:
            # Effet visuel et sonore pour le tir
            for i in range(projectiles_after - projectiles_before):
                projectile = self.player.projectiles[-(i+1)]
                self.effects.create_projectile_fire_effect(
                    projectile.rect.centerx,
                    projectile.rect.centery
                )
            self.audio.play_combat_sound('projectile_fire')
        
        # Créer des traînées pour les projectiles en mouvement
        for projectile in self.player.projectiles:
            if random.random() < 0.3:  # 30% de chance par frame
                self.effects.create_projectile_trail(
                    projectile.rect.centerx,
                    projectile.rect.centery
                )
        
        # Spawning des ennemis
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.enemy_spawner.spawn_enemy(self.player.rect.center)
            self.spawn_timer = 0
            # Augmente la difficulté progressivement
            self.spawn_interval = max(500, self.spawn_interval - 10)
        
        # Mise à jour des ennemis
        self.enemy_spawner.update(dt, self.player.rect.center)
        
        # Mise à jour et collecte des orbes d'XP
        player_pos = (self.player.rect.centerx, self.player.rect.centery)
        
        # D'abord vérifier la collecte AVANT de filtrer
        for orb in self.xp_orbs[:]:  # Copie de la liste pour itération sûre
            still_active = orb.update(dt, player_pos)
            
            if orb.collected:
                # Effet de collecte d'XP
                self.effects.create_upgrade_effect(
                    orb.rect.centerx,
                    orb.rect.centery,
                    'health_boost'  # Utiliser un effet vert pour l'XP
                )
                self.audio.play_upgrade_effect('health_boost')
                
                # Donner l'XP au joueur
                xp_gained = self.xp_system.gain_xp(orb.xp_value)
                
                # Vérification du level up
                if self.xp_system.check_level_up():
                    # Effet de level up spectaculaire
                    self.effects.create_level_up_effect(
                        self.player.rect.centerx,
                        self.player.rect.centery
                    )
                    
                    self.game_state = "drafting"
                    self.card_draft.start_draft(self.xp_system.level)
                
                # Retirer l'orbe de la liste
                self.xp_orbs.remove(orb)
            elif not still_active:
                # L'orbe a expiré, le retirer
                self.xp_orbs.remove(orb)
        
        # Mise à jour des effets visuels
        self.effects.update(dt / 1000.0)  # Convertir ms en secondes
        
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
                
                # Effet visuel de mort d'ennemi
                self.effects.create_enemy_death_effect(enemy.rect.centerx, enemy.rect.centery)
                self.audio.play_combat_sound('enemy_death')
        
        # Collision attaques joueur-ennemis
        for projectile in self.player.projectiles:
            for enemy in self.enemy_spawner.enemies:
                if projectile.rect.colliderect(enemy.rect):
                    enemy.take_damage(projectile.damage)
                    projectile.active = False
                    
                    # Effet d'impact du projectile
                    self.effects.create_projectile_impact_effect(projectile.rect.centerx, projectile.rect.centery)
                    self.audio.play_combat_sound('projectile_impact')
                    
                    # Si l'ennemi meurt, créer un orbe d'XP
                    if enemy.health <= 0:
                        # Effet de mort d'ennemi
                        self.effects.create_enemy_death_effect(enemy.rect.centerx, enemy.rect.centery)
                        self.audio.play_combat_sound('enemy_death')
                        
                        # Créer un orbe d'XP à la position de l'ennemi
                        xp_orb = XPOrb(enemy.rect.centerx, enemy.rect.centery, enemy.xp_value)
                        self.xp_orbs.append(xp_orb)
    
    def _update_camera(self):
        """Met à jour la position de la caméra pour centrer sur le joueur."""
        # Centrer la caméra sur le joueur
        self.camera_x = self.player.rect.centerx
        self.camera_y = self.player.rect.centery
    
    def _world_to_screen(self, world_x: float, world_y: float):
        """Convertit des coordonnées monde en coordonnées écran.
        La caméra (camera_x, camera_y) représente le centre de l'écran dans le monde.
        """
        screen_x = world_x - self.camera_x + self.width // 2
        screen_y = world_y - self.camera_y + self.height // 2
        return screen_x, screen_y
    
    def _screen_to_world(self, screen_x: float, screen_y: float):
        """Convertit des coordonnées écran en coordonnées monde.
        Inverse de _world_to_screen().
        """
        world_x = screen_x + self.camera_x - self.width // 2
        world_y = screen_y + self.camera_y - self.height // 2
        return world_x, world_y
    
    def _draw_background(self):
        """Dessine le fond avec grille qui défile."""
        # Calculer l'offset de la grille basé sur la position de la caméra
        offset_x = int(self.camera_x % self.tile_size)
        offset_y = int(self.camera_y % self.tile_size)
        
        # Dessiner les lignes verticales
        for x in range(-offset_x, self.width + self.tile_size, self.tile_size):
            pygame.draw.line(self.screen, (30, 30, 40), (x, 0), (x, self.height), 1)
        
        # Dessiner les lignes horizontales
        for y in range(-offset_y, self.height + self.tile_size, self.tile_size):
            pygame.draw.line(self.screen, (30, 30, 40), (0, y), (self.width, y), 1)
        
        # Dessiner des points aux intersections pour plus de détail
        for x in range(-offset_x, self.width + self.tile_size, self.tile_size):
            for y in range(-offset_y, self.height + self.tile_size, self.tile_size):
                pygame.draw.circle(self.screen, (40, 40, 50), (x, y), 2)
    
    def render(self):
        """Effectue le rendu de tous les éléments."""
        # Fond noir
        self.screen.fill((15, 15, 25))
        
        if self.game_state == "menu":
            # Dessiner le menu principal
            self._draw_menu()
        
        elif self.game_state == "playing":
            # ✅ Dessiner le fond avec grille qui défile
            self._draw_background()
            
            # ✅ Rendu des éléments avec coordonnées caméra
            # Joueur (toujours au centre de l'écran)
            player_screen_x, player_screen_y = self._world_to_screen(
                self.player.rect.centerx, self.player.rect.centery
            )
            player_rect = self.player.rect.copy()
            player_rect.center = (player_screen_x, player_screen_y)
            old_rect = self.player.rect
            self.player.rect = player_rect
            self.player.draw(self.screen)
            self.player.rect = old_rect
            
            # Ennemis (avec culling : ne dessiner que ceux visibles)
            for enemy in self.enemy_spawner.enemies:
                enemy_screen_x, enemy_screen_y = self._world_to_screen(
                    enemy.rect.centerx, enemy.rect.centery
                )
                if (-100 < enemy_screen_x < self.width + 100 and 
                    -100 < enemy_screen_y < self.height + 100):
                    enemy_rect = enemy.rect.copy()
                    enemy_rect.center = (enemy_screen_x, enemy_screen_y)
                    old_enemy_rect = enemy.rect
                    enemy.rect = enemy_rect
                    enemy.draw(self.screen)
                    enemy.rect = old_enemy_rect
            
            # Projectiles
            for projectile in self.player.projectiles:
                if projectile.active:
                    proj_screen_x, proj_screen_y = self._world_to_screen(
                        projectile.rect.centerx, projectile.rect.centery
                    )
                    if (-100 < proj_screen_x < self.width + 100 and 
                        -100 < proj_screen_y < self.height + 100):
                        proj_rect = projectile.rect.copy()
                        proj_rect.center = (proj_screen_x, proj_screen_y)
                        old_proj_rect = projectile.rect
                        projectile.rect = proj_rect
                        projectile.draw(self.screen)
                        projectile.rect = old_proj_rect
            
            # Rendu des orbes d'XP
            for orb in self.xp_orbs:
                orb_screen_x, orb_screen_y = self._world_to_screen(orb.x, orb.y)
                if (-100 < orb_screen_x < self.width + 100 and 
                    -100 < orb_screen_y < self.height + 100):
                    old_orb_x, old_orb_y = orb.x, orb.y
                    orb.x, orb.y = orb_screen_x, orb_screen_y
                    orb.rect.center = (orb_screen_x, orb_screen_y)
                    orb.draw(self.screen)
                    orb.x, orb.y = old_orb_x, old_orb_y
            
            # ✅ Effets visuels avec offset de caméra
            self.effects.draw(self.screen, (self.camera_x, self.camera_y))
            
            # Interface utilisateur (toujours en haut)
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
                    # Effet visuel et sonore de sélection de carte
                    card_center_x = self.width // 2
                    card_center_y = self.height // 2
                    self.effects.create_card_selection_effect(
                        card_center_x, 
                        card_center_y, 
                        selected_card['rarity']
                    )
                    self.audio.play_card_selection(selected_card['rarity'])
                    
                    # Appliquer l'effet de la carte
                    self.player.apply_card_effect(selected_card)
                    
                    # Effet d'application de l'upgrade
                    self.effects.create_upgrade_effect(
                        self.player.rect.centerx,
                        self.player.rect.centery,
                        selected_card['effect_type']
                    )
                    self.audio.play_upgrade_effect(selected_card['effect_type'])
                    
                self.game_state = "playing"
        
        elif self.game_state == "game_over":
            self.ui.draw_game_over(self.screen, self.xp_system.level)
        
        pygame.display.flip()
    
    def _draw_menu(self):
        """Dessine le menu principal."""
        # Titre du jeu
        title_text = self.menu_font_title.render("Game Python 2D", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width // 2, self.height // 4))
        self.screen.blit(title_text, title_rect)
        
        # Sous-titre
        subtitle_font = pygame.font.Font(None, 36)
        subtitle_text = subtitle_font.render("Roguelike Survivor", True, (150, 150, 200))
        subtitle_rect = subtitle_text.get_rect(center=(self.width // 2, self.height // 4 + 60))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Dessiner les boutons
        mouse_pos = pygame.mouse.get_pos()
        for i, button in enumerate(self.menu_buttons):
            # Vérifier si la souris survole le bouton
            is_hovered = button["rect"].collidepoint(mouse_pos)
            is_selected = i == self.menu_selected
            
            # Couleurs selon l'état
            if is_selected or is_hovered:
                bg_color = (100, 100, 150)
                text_color = (255, 255, 255)
                border_color = (200, 200, 255)
            else:
                bg_color = (50, 50, 80)
                text_color = (180, 180, 200)
                border_color = (100, 100, 120)
            
            # Dessiner le fond du bouton
            pygame.draw.rect(self.screen, bg_color, button["rect"])
            pygame.draw.rect(self.screen, border_color, button["rect"], 3)
            
            # Dessiner le texte du bouton
            button_text = self.menu_font_button.render(button["text"], True, text_color)
            button_text_rect = button_text.get_rect(center=button["rect"].center)
            self.screen.blit(button_text, button_text_rect)
        
        # Instructions
        instructions_font = pygame.font.Font(None, 28)
        instructions = [
            "Utilisez les flèches ↑↓ ou la souris pour naviguer",
            "Appuyez sur ENTRÉE ou cliquez pour sélectionner"
        ]
        y_offset = self.height - 120
        for instruction in instructions:
            text = instructions_font.render(instruction, True, (120, 120, 140))
            text_rect = text.get_rect(center=(self.width // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 35
    
    def run(self):
        """Boucle principale du jeu."""
        print("Démarrage du jeu...")
        print("Contrôles:")
        print("- ZQSD ou flèches : déplacement")
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
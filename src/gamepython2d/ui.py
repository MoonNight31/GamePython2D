import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player
    from .xp_system import XPSystem

class GameUI:
    """Interface utilisateur du jeu avec HUD, barres de vie/XP, etc."""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Fonts
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Couleurs
        self.colors = {
            'health_bg': (100, 0, 0),
            'health_fg': (255, 0, 0),
            'xp_bg': (0, 100, 0),
            'xp_fg': (0, 255, 0),
            'bar_border': (255, 255, 255),
            'text': (255, 255, 255),
            'text_shadow': (0, 0, 0),
            'overlay': (0, 0, 0, 180)
        }
        
        # Dimensions des barres
        self.bar_width = 300
        self.bar_height = 20
        self.bar_border_width = 2
    
    def draw_hud(self, screen, player: 'Player', xp_system: 'XPSystem'):
        """Dessine le HUD principal (barres de vie, XP, niveau, etc.)."""
        # Barre de vie
        self._draw_health_bar(screen, player)
        
        # Barre d'XP
        self._draw_xp_bar(screen, xp_system)
        
        # Niveau actuel
        self._draw_level_display(screen, xp_system)
        
        # Statistiques du joueur
        self._draw_player_stats(screen, player)
        
        # Compteur d'ennemis (si disponible)
        # self._draw_enemy_counter(screen, enemy_spawner)
    
    def _draw_health_bar(self, screen, player: 'Player'):
        """Dessine la barre de vie du joueur."""
        x = 20
        y = 20
        
        # Calcul du pourcentage de vie
        max_health = player.max_health + player.card_effects.get('health_bonus', 0)
        health_percentage = player.health / max_health if max_health > 0 else 0
        
        # Fond de la barre
        bg_rect = pygame.Rect(x, y, self.bar_width, self.bar_height)
        pygame.draw.rect(screen, self.colors['health_bg'], bg_rect)
        
        # Barre de vie actuelle
        health_width = int(self.bar_width * health_percentage)
        if health_width > 0:
            health_rect = pygame.Rect(x, y, health_width, self.bar_height)
            pygame.draw.rect(screen, self.colors['health_fg'], health_rect)
        
        # Bordure
        pygame.draw.rect(screen, self.colors['bar_border'], bg_rect, self.bar_border_width)
        
        # Texte de la vie
        health_text = f"Vie: {player.health}/{max_health}"
        self._draw_text_with_shadow(screen, health_text, x, y - 25, self.font_small)
    
    def _draw_xp_bar(self, screen, xp_system: 'XPSystem'):
        """Dessine la barre d'expérience."""
        x = 20
        y = 70
        
        # Calcul du pourcentage d'XP
        xp_progress = xp_system.get_xp_progress()
        
        # Fond de la barre
        bg_rect = pygame.Rect(x, y, self.bar_width, self.bar_height)
        pygame.draw.rect(screen, self.colors['xp_bg'], bg_rect)
        
        # Barre d'XP actuelle
        xp_width = int(self.bar_width * xp_progress)
        if xp_width > 0:
            xp_rect = pygame.Rect(x, y, xp_width, self.bar_height)
            pygame.draw.rect(screen, self.colors['xp_fg'], xp_rect)
        
        # Bordure
        pygame.draw.rect(screen, self.colors['bar_border'], bg_rect, self.bar_border_width)
        
        # Texte de l'XP
        xp_info = xp_system.get_xp_display_info()
        xp_text = f"XP: {xp_info['current_xp']}/{xp_info['xp_needed']}"
        self._draw_text_with_shadow(screen, xp_text, x, y - 25, self.font_small)
    
    def _draw_level_display(self, screen, xp_system: 'XPSystem'):
        """Dessine l'affichage du niveau actuel."""
        x = self.screen_width - 150
        y = 20
        
        level_text = f"Niveau {xp_system.level}"
        text_surface = self.font_medium.render(level_text, True, self.colors['text'])
        
        # Fond pour le niveau
        text_rect = text_surface.get_rect()
        bg_rect = pygame.Rect(x - 10, y - 5, text_rect.width + 20, text_rect.height + 10)
        pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
        pygame.draw.rect(screen, self.colors['bar_border'], bg_rect, 2)
        
        screen.blit(text_surface, (x, y))
    
    def _draw_player_stats(self, screen, player: 'Player'):
        """Dessine les statistiques détaillées du joueur."""
        x = self.screen_width - 200
        y = 70
        
        stats = [
            f"Vitesse: {player.speed * player.card_effects['speed_multiplier']:.0f}",
            f"Dégâts: {player.attack_damage * player.card_effects['damage_multiplier']:.0f}",
            f"Cadence: {player.attack_speed * player.card_effects['attack_speed_multiplier']:.1f}/s"
        ]
        
        for i, stat in enumerate(stats):
            self._draw_text_with_shadow(screen, stat, x, y + i * 25, self.font_small)
    
    def _draw_text_with_shadow(self, screen, text: str, x: int, y: int, font: pygame.font.Font):
        """Dessine du texte avec une ombre pour améliorer la lisibilité."""
        # Ombre
        shadow_surface = font.render(text, True, self.colors['text_shadow'])
        screen.blit(shadow_surface, (x + 1, y + 1))
        
        # Texte principal
        text_surface = font.render(text, True, self.colors['text'])
        screen.blit(text_surface, (x, y))
    
    def draw_pause_screen(self, screen):
        """Dessine l'écran de pause."""
        # Overlay semi-transparent
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Texte de pause
        pause_text = self.font_large.render("PAUSE", True, self.colors['text'])
        pause_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        screen.blit(pause_text, pause_rect)
        
        # Instructions
        instruction_text = "Appuyez sur ESPACE pour continuer"
        instruction_surface = self.font_medium.render(instruction_text, True, self.colors['text'])
        instruction_rect = instruction_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 60))
        screen.blit(instruction_surface, instruction_rect)
    
    def draw_game_over(self, screen, final_level: int):
        """Dessine l'écran de game over."""
        # Overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((100, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Titre Game Over
        game_over_text = self.font_large.render("GAME OVER", True, (255, 255, 255))
        game_over_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        screen.blit(game_over_text, game_over_rect)
        
        # Niveau atteint
        level_text = f"Niveau atteint: {final_level}"
        level_surface = self.font_medium.render(level_text, True, (255, 255, 255))
        level_rect = level_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
        screen.blit(level_surface, level_rect)
        
        # Instructions pour redémarrer
        restart_text = "Appuyez sur ECHAP pour quitter"
        restart_surface = self.font_small.render(restart_text, True, (200, 200, 200))
        restart_rect = restart_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 80))
        screen.blit(restart_surface, restart_rect)
    
    def draw_level_up_notification(self, screen, level: int):
        """Dessine une notification de montée de niveau."""
        # Cette fonction peut être appelée temporairement lors d'un level up
        notification_text = f"NIVEAU {level} ATTEINT!"
        text_surface = self.font_large.render(notification_text, True, (255, 255, 0))
        
        # Position centrée en haut de l'écran
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, 100))
        
        # Fond semi-transparent
        bg_rect = text_rect.inflate(40, 20)
        overlay = pygame.Surface((bg_rect.width, bg_rect.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, bg_rect)
        
        # Bordure dorée
        pygame.draw.rect(screen, (255, 215, 0), bg_rect, 3)
        
        screen.blit(text_surface, text_rect)
    
    def draw_damage_numbers(self, screen, damage_events: list):
        """Dessine les nombres de dégâts flottants."""
        for event in damage_events:
            if event['timer'] > 0:
                # Calcul de l'alpha en fonction du timer
                alpha = int(255 * (event['timer'] / 1000))
                
                # Création de la surface avec alpha
                damage_text = str(int(event['damage']))
                text_surface = self.font_small.render(damage_text, True, (255, 100, 100))
                text_surface.set_alpha(alpha)
                
                # Position avec déplacement vers le haut
                y_offset = (1000 - event['timer']) * 0.05
                screen.blit(text_surface, (event['x'], event['y'] - y_offset))
    
    def draw_mini_map(self, screen, player_pos: tuple, enemies: list):
        """Dessine une mini-carte dans le coin de l'écran."""
        # Dimensions de la mini-carte
        mini_map_size = 150
        mini_map_x = self.screen_width - mini_map_size - 20
        mini_map_y = self.screen_height - mini_map_size - 20
        
        # Fond de la mini-carte
        mini_map_rect = pygame.Rect(mini_map_x, mini_map_y, mini_map_size, mini_map_size)
        pygame.draw.rect(screen, (20, 20, 30), mini_map_rect)
        pygame.draw.rect(screen, self.colors['bar_border'], mini_map_rect, 2)
        
        # Facteur d'échelle pour la mini-carte
        scale_x = mini_map_size / self.screen_width
        scale_y = mini_map_size / self.screen_height
        
        # Position du joueur sur la mini-carte
        player_mini_x = mini_map_x + int(player_pos[0] * scale_x)
        player_mini_y = mini_map_y + int(player_pos[1] * scale_y)
        pygame.draw.circle(screen, (0, 255, 0), (player_mini_x, player_mini_y), 3)
        
        # Positions des ennemis sur la mini-carte
        for enemy in enemies[:20]:  # Limiter à 20 ennemis pour éviter l'encombrement
            enemy_mini_x = mini_map_x + int(enemy.rect.centerx * scale_x)
            enemy_mini_y = mini_map_y + int(enemy.rect.centery * scale_y)
            pygame.draw.circle(screen, (255, 0, 0), (enemy_mini_x, enemy_mini_y), 1)
    
    def draw_controls_help(self, screen):
        """Dessine l'aide des contrôles (peut être activée avec une touche)."""
        # Position en bas à gauche
        x = 20
        y = self.screen_height - 150
        
        controls = [
            "CONTRÔLES:",
            "WASD/Flèches - Déplacement",
            "Clic gauche - Attaquer",
            "Espace - Pause",
            "Échap - Quitter"
        ]
        
        # Fond semi-transparent
        bg_height = len(controls) * 25 + 20
        bg_rect = pygame.Rect(x - 10, y - 10, 250, bg_height)
        overlay = pygame.Surface((bg_rect.width, bg_rect.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, bg_rect)
        
        # Bordure
        pygame.draw.rect(screen, self.colors['bar_border'], bg_rect, 2)
        
        # Texte des contrôles
        for i, control in enumerate(controls):
            font = self.font_small if i > 0 else self.font_medium
            color = self.colors['text'] if i > 0 else (255, 255, 0)
            self._draw_text_with_shadow(screen, control, x, y + i * 25, font)
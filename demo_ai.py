#!/usr/bin/env python3
"""
Démonstration IA - Version finale
Menu graphique dans la fenêtre pygame pour sélectionner et lancer l'IA
"""

import sys
import os
import time
import pygame

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class GameMenu:
    """Menu graphique pour sélectionner et lancer l'IA."""
    
    def __init__(self):
        pygame.init()
        self.screen_width = 1200
        self.screen_height = 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("GamePython2D - Démonstration IA")
        
        # Couleurs
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (50, 150, 255)
        self.GREEN = (50, 255, 150)
        self.RED = (255, 50, 50)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (200, 200, 200)
        
        # Polices
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # État du menu
        self.selected_model = None
        self.models = self.scan_models()
        self.clock = pygame.time.Clock()
        
    def scan_models(self):
        """Scanne les modèles IA disponibles."""
        models = []
        
        if os.path.exists("ai_models/game_ai_model_final.zip"):
            models.append({
                "path": "ai_models/game_ai_model_final",
                "name": "IA ACTIVE",
                "description": "IA qui tire des projectiles",
                "icon": "🤖",
                "color": self.GREEN
            })
        
        if os.path.exists("ai_models/demo_ai_final.zip"):
            models.append({
                "path": "ai_models/demo_ai_final",
                "name": "IA PASSIVE", 
                "description": "IA qui évite les ennemis",
                "icon": "🐌",
                "color": self.BLUE
            })
        
        return models
    
    def draw_button(self, text, x, y, width, height, color, text_color=None, border=False):
        """Dessine un bouton avec texte centré."""
        if text_color is None:
            text_color = self.WHITE
            
        # Bouton
        pygame.draw.rect(self.screen, color, (x, y, width, height))
        if border:
            pygame.draw.rect(self.screen, self.WHITE, (x, y, width, height), 2)
        
        # Texte centré
        text_surface = self.font_medium.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)
        
        return pygame.Rect(x, y, width, height)
    
    def draw_text(self, text, x, y, font, color=None, center=False):
        """Dessine du texte."""
        if color is None:
            color = self.WHITE
            
        text_surface = font.render(text, True, color)
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
            self.screen.blit(text_surface, text_rect)
        else:
            self.screen.blit(text_surface, (x, y))
    
    def show_menu(self):
        """Affiche le menu et retourne le modèle sélectionné."""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Vérifier les clics sur les modèles
                    y_start = 250
                    for i, model in enumerate(self.models):
                        button_rect = pygame.Rect(300, y_start + i * 120, 600, 80)
                        if button_rect.collidepoint(mouse_pos):
                            return model
                    
                    # Bouton quitter
                    quit_rect = pygame.Rect(500, 650, 200, 50)
                    if quit_rect.collidepoint(mouse_pos):
                        return None
            
            # Effacer l'écran
            self.screen.fill(self.BLACK)
            
            # Titre
            self.draw_text("GamePython2D", self.screen_width // 2, 80, 
                          self.font_large, self.WHITE, center=True)
            self.draw_text("Démonstration IA", self.screen_width // 2, 130, 
                          self.font_medium, self.GRAY, center=True)
            
            if not self.models:
                # Aucun modèle trouvé
                self.draw_text("❌ Aucun modèle IA trouvé", self.screen_width // 2, 300, 
                              self.font_medium, self.RED, center=True)
                self.draw_text("Entraînez d'abord une IA avec train_ai.py", 
                              self.screen_width // 2, 340, 
                              self.font_small, self.GRAY, center=True)
            else:
                # Instructions
                self.draw_text("Choisissez un modèle IA :", self.screen_width // 2, 180, 
                              self.font_medium, self.WHITE, center=True)
                
                # Dessiner les options de modèles
                y_start = 250
                mouse_pos = pygame.mouse.get_pos()
                
                for i, model in enumerate(self.models):
                    y = y_start + i * 120
                    button_rect = pygame.Rect(300, y, 600, 80)
                    
                    # Couleur selon survol
                    color = model["color"] if button_rect.collidepoint(mouse_pos) else self.GRAY
                    
                    # Bouton principal
                    pygame.draw.rect(self.screen, color, button_rect)
                    pygame.draw.rect(self.screen, self.WHITE, button_rect, 2)
                    
                    # Icône et nom
                    self.draw_text(f"{model['icon']} {model['name']}", 320, y + 15, 
                                  self.font_medium, self.WHITE)
                    
                    # Description
                    self.draw_text(model['description'], 320, y + 45, 
                                  self.font_small, self.LIGHT_GRAY)
            
            # Bouton quitter
            quit_rect = pygame.Rect(500, 650, 200, 50)
            mouse_pos = pygame.mouse.get_pos()
            quit_color = self.RED if quit_rect.collidepoint(mouse_pos) else self.GRAY
            
            self.draw_button("Quitter", 500, 650, 200, 50, quit_color, border=True)
            
            # Instructions de contrôle
            self.draw_text("Échap ou fermer la fenêtre pour quitter", 
                          self.screen_width // 2, 750, 
                          self.font_small, self.GRAY, center=True)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return None

def demo_ai():
    """Démonstration IA avec menu graphique intégré."""
    print("🎬 Lancement de la démonstration IA avec menu graphique")
    
    # Créer et afficher le menu
    menu = GameMenu()
    selected_model = menu.show_menu()
    
    if not selected_model:
        print("👋 Démonstration annulée")
        pygame.quit()
        return
    
    print(f"🤖 Modèle sélectionné: {selected_model['name']}")
    
    # Fermer le menu mais garder pygame initialisé
    del menu
    
    # Lancer la démonstration avec le modèle sélectionné
    run_ai_demo(selected_model)

def run_ai_demo(selected_model):
    """Lance la démonstration IA avec le modèle sélectionné."""
    env = None
    trainer = None
    
    try:
        from gamepython2d.ai_trainer import GameAITrainer
        from gamepython2d.ai_environment import GameAIEnvironment
        
        print("🔧 Initialisation de l'environnement...")
        # Créer l'environnement (pygame déjà initialisé)
        env = GameAIEnvironment(render_mode="human")
        
        print("🧠 Chargement du modèle IA...")
        trainer = GameAITrainer()
        trainer.create_environment(n_envs=1)
        trainer.load_model(selected_model["path"])
        
        print(f"🚀 Démarrage de la simulation - {selected_model['name']}")
        print("📊 Statistiques en temps réel:")
        print("-" * 60)
        
        obs, _ = env.reset()
        total_reward = 0
        steps = 0
        running = True
        
        # Clock pour contrôler le framerate
        clock = pygame.time.Clock()
        
        while steps < 10000 and running:
            # Gérer les événements pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break
            
            if not running:
                break
                
            action, _ = trainer.model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            steps += 1
            
            # IMPORTANT: Afficher le jeu à chaque step
            env.render()
            
            # Limiter à 60 FPS pour un affichage normal
            clock.tick(60)
            
            # Affichage des statistiques toutes les 1800 steps (30 secondes à 60 FPS)
            if steps % 1800 == 0:
                cards_count = info.get('cards_obtained', 0)
                level = info.get('level', 1)
                print(f"⏱️ Step {steps:4d} │ ❤️ Vie: {info.get('player_health', 0):3d} │ " +
                      f"📊 Niveau: {level:2d} │ 🃏 Cartes: {cards_count:2d} │ " +
                      f"⚔️ Kills actifs: {info.get('enemies_killed_by_projectiles', 0):2d} │ " +
                      f"🏆 Récompense: {total_reward:6.1f}")
            
            if terminated or truncated:
                print(f"\n💀 Fin de partie au step {steps}")
                break
        
        if not running:
            print(f"\n⏸️ Démonstration arrêtée par l'utilisateur au step {steps}")
        
        # Résultats finaux
        print(f"\n🏆 RÉSULTAT FINAL - {selected_model['name']}:")
        print(f"   ⏱️ Temps de survie: {steps} steps ({steps/60:.1f} secondes)")
        print(f"   � Niveau atteint: {info.get('level', 1)}")
        print(f"   🃏 Cartes obtenues: {info.get('cards_obtained', 0)}")
        
        # Afficher les effets des cartes
        card_effects = info.get('card_effects', {})
        if card_effects:
            print(f"   ✨ Améliorations actives:")
            print(f"      ⚡ Vitesse: x{card_effects.get('speed', 1.0):.2f}")
            print(f"      ⚔️ Dégâts: x{card_effects.get('damage', 1.0):.2f}")
            print(f"      🎯 Cadence: x{card_effects.get('attack_speed', 1.0):.2f}")
            print(f"      🎯 Projectiles: {card_effects.get('projectiles', 1)}")
        
        print(f"   �🚀 Projectiles tirés: {info.get('projectiles_fired', 0)}")
        print(f"   ⚔️ Ennemis tués activement: {info.get('enemies_killed_by_projectiles', 0)}")
        print(f"   💥 Ennemis tués passivement: {info.get('enemies_killed_by_collision', 0)}")
        print(f"   🏆 Récompense totale: {total_reward:.1f}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la démonstration: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Nettoyage
        print("\n🧹 Nettoyage en cours...")
        if trainer:
            trainer.close()
        if env:
            env.close()
        pygame.quit()
        print("✅ Démonstration terminée")

if __name__ == "__main__":
    demo_ai()
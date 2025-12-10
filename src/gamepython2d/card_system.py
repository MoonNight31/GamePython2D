import pygame
import random
from typing import List, Dict, Optional

# Import des nouveaux systèmes d'effets
try:
    from .effects_system import EffectsSystem
    from .audio_system import AudioSystem
except ImportError:
    # Fallback si les modules ne sont pas disponibles
    EffectsSystem = None
    AudioSystem = None

class Card:
    """Classe représentant une carte d'amélioration."""
    
    def __init__(self, name: str, description: str, effect_type: str, value: float, rarity: str = "common"):
        self.name = name
        self.description = description
        self.effect_type = effect_type
        self.value = value
        self.rarity = rarity
        
        # Couleurs selon la rareté
        self.rarity_colors = {
            'common': (200, 200, 200),
            'uncommon': (100, 200, 100),
            'rare': (100, 100, 255),
            'epic': (200, 100, 255),
            'legendary': (255, 200, 50)
        }
        
        self.color = self.rarity_colors.get(rarity, (200, 200, 200))
    
    def to_dict(self) -> Dict:
        """Convertit la carte en dictionnaire pour faciliter les échanges."""
        return {
            'name': self.name,
            'description': self.description,
            'effect_type': self.effect_type,
            'value': self.value,
            'rarity': self.rarity
        }

class CardDatabase:
    """Base de données de toutes les cartes disponibles."""
    
    def __init__(self):
        self.cards = self._initialize_cards()
    
    def _initialize_cards(self) -> List[Card]:
        """Initialise toutes les cartes du jeu."""
        cards = []
        
        # Cartes communes
        cards.extend([
            Card("Vitesse+", "Augmente la vitesse de déplacement", "speed_boost", 0.2, "common"),
            Card("Force+", "Augmente les dégâts d'attaque", "damage_boost", 0.3, "common"),
            Card("Rapidité+", "Augmente la vitesse d'attaque", "attack_speed_boost", 0.25, "common"),
            Card("Vie+", "Augmente la vie maximale", "health_boost", 25, "common"),
            Card("Soin", "Restaure la vie", "heal", 50, "common"),
        ])
        
        # Cartes peu communes
        cards.extend([
            Card("Sprint", "Boost de vitesse important", "speed_boost", 0.4, "uncommon"),
            Card("Puissance", "Boost de dégâts important", "damage_boost", 0.5, "uncommon"),
            Card("Cadence", "Boost d'attaque important", "attack_speed_boost", 0.4, "uncommon"),
            Card("Vitalité", "Boost de vie important", "health_boost", 50, "uncommon"),
            Card("Tir double", "Tire un projectile supplémentaire", "multi_shot", 1, "uncommon"),
        ])
        
        # Cartes rares
        cards.extend([
            Card("Vélocité", "Grande augmentation de vitesse", "speed_boost", 0.6, "rare"),
            Card("Devastation", "Grande augmentation des dégâts", "damage_boost", 0.8, "rare"),
            Card("Fusillade", "Vitesse d'attaque très élevée", "attack_speed_boost", 0.6, "rare"),
            Card("Constitution", "Augmentation massive de vie", "health_boost", 100, "rare"),
            Card("Tir triple", "Tire deux projectiles supplémentaires", "multi_shot", 2, "rare"),
        ])
        
        # Cartes épiques
        cards.extend([
            Card("Supersonique", "Vitesse extrême", "speed_boost", 1.0, "epic"),
            Card("Annihilation", "Dégâts dévastateurs", "damage_boost", 1.2, "epic"),
            Card("Mitraillage", "Attaque ultra-rapide", "attack_speed_boost", 1.0, "epic"),
            Card("Régénération", "Guérison complète + bonus vie", "heal", 200, "epic"),
        ])
        
        # Cartes légendaires
        cards.extend([
            Card("Transcendance", "Amélioration de tous les stats", "all_stats", 0.5, "legendary"),
            Card("Arsenal", "Tire dans toutes les directions", "multi_shot", 5, "legendary"),
            Card("Immortel", "Vie et régénération massives", "health_boost", 200, "legendary"),
        ])
        
        return cards
    
    def get_cards_by_rarity(self, rarity: str) -> List[Card]:
        """Retourne toutes les cartes d'une rareté donnée."""
        return [card for card in self.cards if card.rarity == rarity]
    
    def get_random_cards(self, count: int, rarity_weights: Dict[str, float] = None) -> List[Card]:
        """Retourne des cartes aléatoires selon les poids de rareté."""
        if rarity_weights is None:
            rarity_weights = {
                'common': 0.5,
                'uncommon': 0.3,
                'rare': 0.15,
                'epic': 0.04,
                'legendary': 0.01
            }
        
        selected_cards = []
        
        for _ in range(count):
            # Choisir une rareté selon les poids
            rarity = random.choices(
                list(rarity_weights.keys()), 
                weights=list(rarity_weights.values())
            )[0]
            
            # Choisir une carte de cette rareté
            cards_of_rarity = self.get_cards_by_rarity(rarity)
            if cards_of_rarity:
                card = random.choice(cards_of_rarity)
                selected_cards.append(card)
        
        return selected_cards

class CardDraft:
    """Système de draft de cartes à 3 choix."""
    
    def __init__(self):
        self.card_database = CardDatabase()
        self.available_cards: List[Card] = []
        self.selected_card: Optional[Card] = None
        self.is_drafting = False
        
        # Interface (sera initialisée quand pygame sera prêt)
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        
        # Positions des cartes (adaptées pour écran 800x600)
        self.card_width = 200
        self.card_height = 280
        self.card_spacing = 30
    
    def _ensure_fonts_initialized(self):
        """S'assure que les fonts sont initialisées."""
        if self.font_large is None:
            pygame.font.init()
            self.font_large = pygame.font.Font(None, 32)  # Réduit de 36 à 32
            self.font_medium = pygame.font.Font(None, 20)  # Réduit de 24 à 20
            self.font_small = pygame.font.Font(None, 16)  # Réduit de 18 à 16
        
    def start_draft(self, level: int = 1):
        """Démarre une session de draft avec 3 cartes."""
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
        
        self.available_cards = self.card_database.get_random_cards(3, rarity_weights)
        self.selected_card = None
        self.is_drafting = True
    
    def handle_event(self, event):
        """Gère les événements pendant le draft."""
        if not self.is_drafting or event.type != pygame.MOUSEBUTTONDOWN:
            return
        
        if event.button == 1:  # Clic gauche
            mouse_pos = event.pos
            
            # Vérifier quelle carte a été cliquée
            for i, card in enumerate(self.available_cards):
                card_rect = self._get_card_rect(i)
                if card_rect.collidepoint(mouse_pos):
                    self.selected_card = card
                    self.is_drafting = False
                    break
    
    def _get_card_rect(self, card_index: int, screen=None) -> pygame.Rect:
        """Calcule la position d'une carte dans l'interface."""
        if screen:
            screen_width = screen.get_width()
        else:
            screen_width = 800  # Valeur par défaut
        total_width = 3 * self.card_width + 2 * self.card_spacing
        start_x = (screen_width - total_width) // 2
        
        x = start_x + card_index * (self.card_width + self.card_spacing)
        y = 150  # Position verticale ajustée pour écran 600px de hauteur
        
        return pygame.Rect(x, y, self.card_width, self.card_height)
    
    def draw(self, screen):
        """Dessine l'interface de draft."""
        if not self.is_drafting:
            return
        
        self._ensure_fonts_initialized()
        
        # Fond semi-transparent
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Titre
        title_text = self.font_large.render("Choisissez une amélioration", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen_width // 2, 100))
        screen.blit(title_text, title_rect)
        
        # Dessiner les cartes
        for i, card in enumerate(self.available_cards):
            self._draw_card(screen, card, i)
        
        # Instructions
        instruction_text = self.font_small.render("Cliquez sur une carte pour la sélectionner", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(screen_width // 2, screen_height - 150))
        screen.blit(instruction_text, instruction_rect)
    
    def _draw_card(self, screen, card: Card, index: int):
        """Dessine une carte individuelle."""
        self._ensure_fonts_initialized()
        
        card_rect = self._get_card_rect(index, screen)
        
        # Effet de survol
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = card_rect.collidepoint(mouse_pos)
        
        # Fond de la carte
        border_color = (255, 255, 255) if is_hovered else card.color
        pygame.draw.rect(screen, border_color, card_rect, 3)
        pygame.draw.rect(screen, (40, 40, 50), card_rect.inflate(-6, -6))
        
        # En-tête avec rareté
        header_rect = pygame.Rect(card_rect.x + 8, card_rect.y + 8, card_rect.width - 16, 35)
        pygame.draw.rect(screen, card.color, header_rect)
        
        # Nom de la carte
        name_text = self.font_medium.render(card.name, True, (0, 0, 0))
        name_rect = name_text.get_rect(center=header_rect.center)
        screen.blit(name_text, name_rect)
        
        # Rareté
        rarity_text = self.font_small.render(card.rarity.upper(), True, (200, 200, 200))
        rarity_rect = rarity_text.get_rect(center=(card_rect.centerx, card_rect.y + 55))
        screen.blit(rarity_text, rarity_rect)
        
        # Description
        self._draw_wrapped_text(screen, card.description, 
                               card_rect.x + 12, card_rect.y + 75,
                               card_rect.width - 24, self.font_small, (255, 255, 255))
        
        # Effet
        effect_text = f"Effet: +{card.value}"
        if card.effect_type == "multi_shot":
            effect_text = f"Projectiles: +{int(card.value)}"
        elif card.effect_type == "heal":
            effect_text = f"Soins: +{int(card.value)} PV"
        elif card.effect_type == "health_boost":
            effect_text = f"Vie max: +{int(card.value)} PV"
        
        effect_surface = self.font_medium.render(effect_text, True, (100, 255, 100))
        effect_rect = effect_surface.get_rect(center=(card_rect.centerx, card_rect.y + 245))  # Ajusté pour carte 280px
        screen.blit(effect_surface, effect_rect)
    
    def _draw_wrapped_text(self, screen, text: str, x: int, y: int, max_width: int, 
                          font: pygame.font.Font, color: tuple):
        """Dessine du texte avec retour à la ligne automatique."""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines):
            line_surface = font.render(line, True, color)
            screen.blit(line_surface, (x, y + i * font.get_height()))
    
    def is_complete(self) -> bool:
        """Vérifie si le draft est terminé."""
        return not self.is_drafting and self.selected_card is not None
    
    def get_selected_card(self) -> Optional[Dict]:
        """Retourne la carte sélectionnée sous forme de dictionnaire."""
        if self.selected_card:
            card_dict = self.selected_card.to_dict()
            self.selected_card = None  # Reset pour le prochain draft
            return card_dict
        return None
"""
GamePython2D - Un jeu 2D de type roguelike avec système de cartes
"""

from .game import Game
from .player import Player
from .enemy import Enemy, EnemySpawner, XPOrb
from .xp_system import XPSystem
from .card_system import Card, CardDatabase, CardDraft
from .ui import GameUI
from .effects_system import EffectsSystem
from .audio_system import AudioSystem

__version__ = "1.0.0"
__author__ = "Votre nom"

def main():
    """Point d'entrée principal du jeu."""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
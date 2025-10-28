#!/usr/bin/env python3
"""
Point d'entrée principal pour GamePython2D
"""

import sys
import os

# Ajouter le répertoire src au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gamepython2d import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nJeu fermé par l'utilisateur.")
        sys.exit(0)
    except Exception as e:
        print(f"Erreur lors de l'exécution du jeu: {e}")
        sys.exit(1)
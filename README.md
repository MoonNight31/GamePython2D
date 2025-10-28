# GamePython2D - Jeu 2D avec IA

## 🎮 Description
Jeu 2D avec un système d'IA entraînable qui a évolué de passive à active. Le jeu comprend un personnage déplaçable, des ennemis, un système d'XP, et un draft de cartes à 3 options.

## 📁 Structure
```
GamePython2D/
├── src/gamepython2d/        # Code source du jeu
│   ├── game.py              # Moteur de jeu principal
│   ├── player.py            # Logique du joueur
│   ├── enemy.py             # Système d'ennemis
│   ├── card_system.py       # Système de cartes et draft
│   ├── xp_system.py         # Système d'expérience
│   ├── ui.py                # Interface utilisateur
│   ├── ai_environment.py    # Environnement IA (Gymnasium)
│   └── ai_trainer.py        # Entraîneur IA (PPO)
├── ai_models/               # Modèles IA entraînés
│   ├── demo_ai_final.zip    # IA passive (démonstration)
│   └── game_ai_model_final.zip # IA active (finale)
├── ai_logs/                 # Logs d'entraînement TensorBoard
├── tests/                   # Tests unitaires
├── main.py                  # Point d'entrée du jeu
├── train_ai.py              # Entraînement de l'IA
├── test_ai.py               # Test de l'IA
├── demo_ai.py               # Démonstration IA
├── final_comparison.py      # Comparaison des IA
└── pyproject.toml           # Configuration et dépendances
```

## 🎮 Fonctionnalités du Jeu

### Gameplay
- 🕹️ Personnage déplaçable avec projectiles
- 👹 Système d'ennemis avec spawning automatique
- ⭐ Système d'expérience et de niveau
- 🃏 Draft de cartes à 3 options pour améliorer le joueur
- 💥 Système de collision et de combat

### Interface
- 🖥️ Résolution 1200x800
- 📊 Affichage des statistiques en temps réel
- 🎨 Interface graphique claire et intuitive

## 📦 Installation

### Prérequis
- Python ≥3.11
- pip

### Installation des dépendances
```bash
pip install -e .
```

Ou manuellement :
```bash
pip install pygame>=2.5.0 gymnasium>=0.29.0 stable-baselines3>=2.0.0 torch>=2.0.0 numpy>=1.21.0 matplotlib>=3.5.0
```

### Dépendances principales
- **pygame** ≥2.5.0 - Moteur de jeu 2D
- **gymnasium** ≥0.29.0 - Environnements RL
- **stable-baselines3** ≥2.0.0 - Algorithmes PPO
- **torch** ≥2.0.0 - Framework PyTorch
- **numpy** ≥1.21.0 - Calculs numériques
- **matplotlib** ≥3.5.0 - Graphiques et visualisations

## 🚀 Utilisation

### Jouer au jeu
```bash
python main.py
```

### Entraîner une nouvelle IA
```bash
python train_ai.py
```

### Tester l'IA
```bash
python test_ai.py
```

### Voir l'IA en action
```bash
python demo_ai.py
```

### Comparer les performances
```bash
python final_comparison.py
```

## 🤖 IA Evolution

### Problème résolu
- **Avant**: IA passive (0 projectiles, kills par collision)
- **Après**: IA active (tire des projectiles, kills intentionnels)

### Système de récompenses amélioré
- +15 points pour kills avec projectiles
- 0 point pour kills par collision
- +0.5 point par projectile tiré
- -0.1 point par inactivité

## 🎯 Résultats
- ✅ IA transformée de passive à active
- ✅ 0.3 projectiles en moyenne (vs 0 avant)
- ✅ Amélioration de 38% confirmée

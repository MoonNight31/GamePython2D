# 🤖 Système d'IA Adaptative

## Vue d'ensemble

Le système d'IA adaptative ajuste dynamiquement la difficulté du jeu en fonction des performances du joueur. Plus vous jouez bien, plus les ennemis deviennent forts, créant une expérience de jeu équilibrée et engageante.

## Fonctionnalités

### 📊 Métriques de performance

Le système suit en continu les performances du joueur :

- **Kills par minute (KPM)** : Nombre d'ennemis éliminés par minute
- **Précision des tirs** : Pourcentage de projectiles qui touchent une cible
- **Dégâts subis** : Quantité de dégâts reçus par le joueur
- **Temps de survie** : Durée de la partie actuelle
- **Niveau** : Niveau actuel du joueur

### 🎯 Calcul du score de performance

Le score est calculé avec plusieurs facteurs pondérés :

```python
Score = (KPM_factor × 0.4) + (Level_factor × 0.3) + 
        (Health_factor × 0.2) + (Accuracy_factor × 0.1)
```

- **KPM_factor** : Basé sur les kills/minute (0.5-2.0)
- **Level_factor** : Basé sur le niveau du joueur (1.0-2.5)
- **Health_factor** : Ratio santé actuelle/santé max (0.3-1.0)
- **Accuracy_factor** : Précision des tirs (0.5-1.5)

**Plage du score** : 0.3 (minimum) - 2.5 (maximum)

### 📈 Niveaux de difficulté

Le système classifie la difficulté en 6 niveaux :

| Score | Niveau | Couleur | Description |
|-------|--------|---------|-------------|
| < 0.6 | Très Facile | 🟢 Vert clair | Ennemis affaiblis |
| 0.6-0.9 | Facile | 🟢 Vert | Ennemis légèrement affaiblis |
| 0.9-1.2 | Normal | 🟡 Jaune | Ennemis standards |
| 1.2-1.5 | Difficile | 🟠 Orange clair | Ennemis renforcés |
| 1.5-2.0 | Très Difficile | 🔴 Orange foncé | Ennemis très renforcés |
| > 2.0 | Expert | 🔴 Rouge | Ennemis au maximum |

### 💪 Buffs des ennemis

Les statistiques des ennemis sont multipliées selon la difficulté :

#### Santé (Health)
```
Multiplier = 0.8 + (difficulty × 0.65)
```
- Facile : 0.8x (20% moins de PV)
- Normal : 1.0x (PV standards)
- Expert : 2.1x (110% plus de PV)

#### Vitesse (Speed)
```
Multiplier = 0.9 + (difficulty × 0.4)
```
- Facile : 0.9x (10% plus lent)
- Normal : 1.0x (vitesse standard)
- Expert : 1.9x (90% plus rapide)

#### Dégâts (Damage)
```
Multiplier = 0.85 + (difficulty × 0.5)
```
- Facile : 0.85x (15% moins de dégâts)
- Normal : 1.0x (dégâts standards)
- Expert : 2.1x (110% plus de dégâts)

#### Intelligence (AI Intelligence)
```
Multiplier = 1.0 + (difficulty × 0.6)
```
- Normal : 1.0 (comportement basique)
- Difficile (1.2+) : Anticipation de mouvement
- Expert (1.5+) : Esquive latérale + stratégie de kite

### 🧠 Comportements intelligents

Les ennemis adaptent leur comportement selon leur niveau d'intelligence :

#### Intelligence < 1.2 : Comportement basique
- Se déplace directement vers le joueur
- Aucune stratégie particulière

#### Intelligence 1.2-1.5 : Anticipation
- Prédit la position future du joueur
- Ajuste sa trajectoire pour intercepter
- Utilise l'historique de mouvement du joueur

#### Intelligence > 1.5 : Tactique avancée
- **Mouvement sinusoïdal** : Esquive latérale pour éviter les projectiles
- **Kite strategy** : Recule légèrement quand trop proche (< 150px)
- **Prédiction avancée** : Anticipe les déplacements du joueur

### ⚙️ Adaptation progressive

- **Fréquence de mise à jour** : Toutes les 5 secondes
- **Vitesse d'adaptation** : 
  - Augmentation : +10% par update si performance élevée
  - Diminution : -5% par update si performance faible
- **Lissage** : Les transitions sont graduelles pour éviter les changements brusques

### 🕒 Modificateur de spawn

En plus des buffs individuels, le système ajuste la fréquence d'apparition :

```python
Spawn_modifier = 1.0 - (difficulty × 0.15)
```

- Facile : 1.0x (spawn normal)
- Normal : 0.85x (15% plus rapide)
- Expert : 0.625x (37.5% plus rapide)

## Affichage en jeu

Un panneau d'information en bas à droite affiche :
- 🎯 Titre "Difficulté IA"
- Niveau de difficulté actuel (avec couleur)
- Score de performance

## Utilisation dans le code

### Initialisation

```python
from adaptive_ai import AdaptiveEnemyAI

# Dans Game.__init__
self.adaptive_ai = AdaptiveEnemyAI()
```

### Enregistrement des métriques

```python
# À chaque tir
self.adaptive_ai.register_projectile_fired()

# Quand un projectile touche
self.adaptive_ai.register_hit()

# Quand le joueur prend des dégâts
self.adaptive_ai.register_damage_taken(damage_amount)

# Quand un ennemi meurt
self.adaptive_ai.register_kill()
```

### Mise à jour de la difficulté

```python
# Dans la boucle de jeu
self.adaptive_ai.update_player_metrics(
    player.health,
    player.max_health,
    xp_system.level,
    xp_system.total_xp_gained
)
self.adaptive_ai.update_difficulty()
```

### Application des buffs aux ennemis

```python
# Lors du spawn d'un ennemi
base_stats = {
    'health': enemy.max_health,
    'speed': enemy.speed,
    'damage': enemy.damage
}

buffed_stats = adaptive_ai.apply_buffs_to_enemy(base_stats)

enemy.max_health = buffed_stats['health']
enemy.speed = buffed_stats['speed']
enemy.damage = buffed_stats['damage']
enemy.ai_intelligence = buffed_stats['ai_intelligence']
```

## Configuration

Les paramètres d'adaptation peuvent être ajustés dans `adaptive_ai.py` :

```python
# Seuils de difficulté
DIFFICULTY_THRESHOLDS = {
    'easy': 0.6,
    'normal': 0.9,
    'hard': 1.2,
    'very_hard': 1.5,
    'expert': 2.0
}

# Vitesse d'adaptation
ADAPTATION_SPEED_UP = 0.1    # Augmentation par update
ADAPTATION_SPEED_DOWN = 0.05  # Diminution par update

# Intervalle de mise à jour
UPDATE_INTERVAL = 5.0  # secondes
```

## Bénéfices

✅ **Équilibrage automatique** : Le jeu s'adapte au niveau du joueur
✅ **Rejouabilité** : Chaque partie est différente
✅ **Courbe d'apprentissage** : Les débutants ne sont pas submergés
✅ **Challenge continu** : Les joueurs expérimentés restent engagés
✅ **Feedback visible** : L'affichage montre clairement la progression

## Améliorations futures possibles

- 🎮 Adaptation du type d'ennemis spawn (plus de tanks en difficile)
- 📊 Historique des performances sur plusieurs parties
- 🏆 Système de classement basé sur le score max atteint
- 🎯 Objectifs dynamiques selon la difficulté
- 💾 Sauvegarde des statistiques de progression

# 💎 Système d'Orbes d'XP

## Vue d'ensemble

Le système d'orbes d'XP remplace l'ancien système de gain d'XP instantané. Désormais, lorsqu'un ennemi meurt, il laisse tomber un orbe d'XP que le joueur doit collecter en se déplaçant dessus.

## Fonctionnalités

### 🎯 Collecte Active
- Les ennemis ne donnent plus d'XP automatiquement à leur mort
- Ils laissent tomber un **orbe d'XP lumineux** à leur position
- Le joueur doit se déplacer pour collecter les orbes
- Ajoute un aspect stratégique : risquer de collecter l'XP ou rester en sécurité

### 🧲 Attraction Magnétique
- Les orbes sont attirés vers le joueur dans un rayon de **150 pixels**
- Plus le joueur est proche, plus l'attraction est forte
- Facilite la collecte sans avoir à passer exactement dessus

### ⏱️ Durée de Vie
- Les orbes restent sur le terrain pendant **30 secondes**
- Après ce délai, ils commencent à disparaître progressivement (fade out)
- Incite le joueur à récupérer l'XP rapidement

### 🎨 Visuels Dynamiques

#### Couleurs selon la valeur
- **Vert** 🟢 : 10 XP (ennemi basique)
- **Bleu** 🔵 : 15 XP (ennemi rapide)
- **Or** 🟡 : 20+ XP (ennemi tank)

#### Effets visuels
- **Pulsation** : Les orbes pulsent en continu pour attirer l'attention
- **Halo lumineux** : Un halo brillant entoure chaque orbe
- **Centre brillant** : Un point blanc lumineux au centre
- **Fade progressif** : Disparition en douceur après expiration

### 🎵 Son et Effets
- **Son de collecte** : `xp_gain` joué lors de la collection
- **Effet visuel** : Particules dorées apparaissent lors de la collecte (upgrade effect)
- **Level up** : L'effet spectaculaire de level up se déclenche après collecte si niveau atteint

## Implémentation Technique

### Classe XPOrb

```python
class XPOrb:
    def __init__(self, x: int, y: int, xp_value: int):
        # Position et valeur
        # Taille adaptée à la valeur d'XP
        # Animation et magnétisme
        # Durée de vie
```

### Propriétés principales

| Propriété | Description |
|-----------|-------------|
| `xp_value` | Quantité d'XP donnée lors de la collecte |
| `size` | Taille de l'orbe (8-20px selon la valeur) |
| `magnetic_range` | Distance d'attraction (150px) |
| `magnetic_speed` | Vitesse d'attraction (200px/s) |
| `lifetime` | Durée de vie (30000ms) |
| `collected` | Indicateur de collecte |

### Méthodes

#### `update(dt, player_pos)`
- Met à jour la position de l'orbe
- Calcule l'attraction magnétique vers le joueur
- Vérifie la collision pour la collecte
- Gère l'expiration

#### `draw(screen)`
- Dessine le halo externe
- Dessine l'orbe principal avec la couleur appropriée
- Dessine le centre brillant
- Applique l'effet de pulsation et de fade

## Intégration dans le Jeu

### Dans game.py

```python
# Liste des orbes
self.xp_orbs = []

# Création lors de la mort d'un ennemi
if enemy.health <= 0:
    xp_orb = XPOrb(enemy.rect.centerx, enemy.rect.centery, enemy.xp_value)
    self.xp_orbs.append(xp_orb)

# Mise à jour et collecte
player_pos = (self.player.rect.centerx, self.player.rect.centery)
self.xp_orbs = [orb for orb in self.xp_orbs if orb.update(dt, player_pos)]

for orb in self.xp_orbs[:]:
    if orb.collected:
        self.xp_system.gain_xp(orb.xp_value)
        # Effets visuels et sonores
        self.xp_orbs.remove(orb)

# Rendu
for orb in self.xp_orbs:
    orb.draw(self.screen)
```

### Dans ai_environment.py

Le système fonctionne de la même manière pour l'IA, permettant à l'agent d'apprendre à :
- Collecter efficacement l'XP
- Prioriser les orbes de haute valeur
- Équilibrer combat et collecte

## Avantages Gameplay

### 🎮 Pour le Joueur
1. **Engagement actif** : Nécessite de se déplacer et de prendre des décisions
2. **Risk/Reward** : Prendre des risques pour collecter l'XP
3. **Feedback visuel** : Voir clairement l'XP disponible sur le terrain
4. **Stratégie** : Choisir quand et comment collecter l'XP

### 🤖 Pour l'IA
1. **Nouvelle dimension d'apprentissage** : L'IA doit apprendre à collecter l'XP
2. **Comportement plus réaliste** : Se déplace vers les récompenses
3. **Équilibrage** : Balance entre combat et collecte
4. **Objectifs multiples** : Tuer les ennemis ET collecter l'XP

## Configuration

### Paramètres ajustables

```python
# Dans la classe XPOrb
self.magnetic_range = 150      # Distance d'attraction (px)
self.magnetic_speed = 200      # Vitesse d'attraction (px/s)
self.lifetime = 30000          # Durée de vie (ms)
self.pulse_speed = 3.0         # Vitesse de pulsation
```

### Ajustements de difficulté

**Plus facile** :
- Augmenter `magnetic_range` (ex: 200)
- Augmenter `lifetime` (ex: 45000)
- Augmenter la taille des orbes

**Plus difficile** :
- Diminuer `magnetic_range` (ex: 100)
- Diminuer `lifetime` (ex: 20000)
- Désactiver l'attraction magnétique

## Performance

### Optimisations
- Les orbes expirés sont automatiquement supprimés
- Utilisation de list comprehension pour le filtrage efficace
- Rendu optimisé avec surfaces temporaires
- Calcul de distance simple sans racine carrée quand possible

### Impact
- **Négligeable** sur les performances avec <100 orbes
- Nettoyage automatique des orbes anciens
- Pas de leak mémoire

## Tests

### Vérifications
✅ Les orbes apparaissent à la mort des ennemis  
✅ L'attraction magnétique fonctionne correctement  
✅ La collecte donne bien l'XP au joueur  
✅ Les effets visuels et sonores se déclenchent  
✅ Le level up fonctionne après collecte  
✅ Les orbes expirent correctement après 30s  
✅ L'IA peut collecter les orbes  

### Commandes de test

```bash
# Jeu principal
python -m gamepython2d

# Démonstration IA
python demo_ai.py
```

## Évolutions Futures

### Améliorations possibles
1. **Orbes spéciaux** : Orbes de santé, bonus temporaires
2. **Effets de zone** : Collecte automatique dans une zone
3. **Multiplicateurs** : Chaînes de collecte pour bonus
4. **Animations** : Trajectoires plus complexes
5. **Sons variés** : Différents sons selon la valeur
6. **Particules** : Traînées derrière les orbes en mouvement

### Cartes possibles
- **Aimant puissant** : Augmente le rayon magnétique
- **Collecteur automatique** : Collecte auto dans un rayon
- **Durée infinie** : Les orbes ne disparaissent jamais
- **XP booster** : Double la valeur des orbes collectés

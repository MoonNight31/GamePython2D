# 🧠 Système d'Apprentissage par Renforcement des Ennemis

## Vue d'ensemble

Le système d'apprentissage permet aux ennemis d'**apprendre** les meilleures stratégies contre vous, plutôt que de simplement gagner en statistiques. Chaque ennemi possède un "cerveau" qui utilise le **Q-Learning** pour améliorer son comportement au fil du temps.

## Différence avec le système adaptatif

### 🤖 IA Adaptative (ancien)
- Les ennemis deviennent **plus forts** (PV, vitesse, dégâts)
- Comportement préprogrammé basé sur l'intelligence
- Réagit à vos performances globales

### 🧠 IA d'Apprentissage (nouveau)
- Les ennemis **apprennent** les meilleures tactiques
- Comportement **évolutif** basé sur l'expérience
- Partage de connaissances entre tous les ennemis
- Amélioration continue par essai-erreur

## Comment ça fonctionne

### 1. Q-Learning simplifié

Chaque ennemi utilise une **Q-table** qui stocke la valeur de chaque action dans chaque situation :

```
Q-Table
├── État: "CLOSE_0_MOVING_HIGH"
│   ├── APPROACH: 2.5
│   ├── RETREAT: 1.8
│   ├── CIRCLE_LEFT: 3.2  ← Meilleure action
│   └── ...
└── État: "FAR_4_STATIC_LOW"
    ├── RUSH: 4.1  ← Meilleure action
    └── ...
```

### 2. Les 8 actions disponibles

Chaque ennemi peut choisir parmi 8 comportements :

| Action | Description | Usage |
|--------|-------------|-------|
| **APPROACH** | Approche directe | Action basique |
| **CIRCLE_LEFT** | Tourner autour (sens anti-horaire) | Esquive + pression |
| **CIRCLE_RIGHT** | Tourner autour (sens horaire) | Esquive + pression |
| **RETREAT** | Reculer | Quand en danger |
| **STRAFE_LEFT** | Déplacement latéral gauche | Esquive tout en avançant |
| **STRAFE_RIGHT** | Déplacement latéral droit | Esquive tout en avançant |
| **ZIGZAG** | Mouvement en zigzag | Esquive des projectiles |
| **RUSH** | Charge rapide | Attaque agressive |

### 3. États du jeu

L'ennemi perçoit la situation selon 4 dimensions :

#### Distance au joueur
- `CLOSE` : < 100 pixels
- `MEDIUM` : 100-250 pixels
- `FAR` : 250-500 pixels
- `VERY_FAR` : > 500 pixels

#### Direction relative (8 secteurs)
- 0 : Est (droite)
- 1 : Nord-Est
- 2 : Nord (haut)
- 3 : Nord-Ouest
- 4 : Ouest (gauche)
- 5 : Sud-Ouest
- 6 : Sud (bas)
- 7 : Sud-Est

#### Mouvement du joueur
- `STATIC` : Immobile (< 50 vitesse)
- `MOVING` : En déplacement

#### Santé du joueur
- `HIGH` : > 70%
- `MED` : 30-70%
- `LOW` : < 30%

**Exemple d'état** : `"MEDIUM_2_MOVING_HIGH"` = Ennemi à distance moyenne, au Nord, joueur en mouvement avec beaucoup de PV.

### 4. Système de récompenses

L'apprentissage se fait via des récompenses :

#### Récompenses positives ✅
```python
+10.0  : Toucher le joueur (grosse récompense !)
+0.1/s : Survivre
+0.5/s : Être à distance optimale (100-250px)
```

#### Pénalités négatives ❌
```python
-5.0   : Être touché par un projectile
-0.2/s : Être trop proche (< 50px, risque)
-10.0  : Mourir (pénalité finale)
```

### 5. Stratégie d'exploration vs exploitation

#### Epsilon-greedy
- **Exploration** : Essayer des actions aléatoires (ε = 30% au début)
- **Exploitation** : Choisir la meilleure action connue (70%)

L'epsilon **diminue progressivement** :
```python
ε = 30% → 25% → 20% → ... → 5% (minimum)
```

Au fil du temps, les ennemis explorent moins et exploitent plus leurs connaissances.

### 6. Apprentissage collectif

**Mémoire partagée** : Tous les ennemis partagent la même Q-table !

```
Ennemi 1 meurt → Met à jour Q-table locale
                ↓
         Fusionne dans Q-table globale (80% ancien + 20% nouveau)
                ↓
Ennemi 2 spawn → Hérite de la Q-table globale
                ↓
         Utilise les connaissances de tous les ennemis précédents
```

**Avantage** : Les ennemis deviennent de plus en plus intelligents à mesure que la partie avance.

## Équation de mise à jour

Équation de Bellman pour le Q-Learning :

```
Q(s,a) = Q(s,a) + α × [R + γ × max(Q(s',a')) - Q(s,a)]
```

Où :
- `Q(s,a)` : Valeur actuelle de l'action `a` dans l'état `s`
- `α` : Taux d'apprentissage (0.1 = 10% de la nouvelle info)
- `R` : Récompense reçue
- `γ` : Facteur de discount (0.95 = importance du futur)
- `max(Q(s',a'))` : Meilleure Q-value du prochain état

## Progression de l'apprentissage

### Phase 1 : Exploration (0-50 ennemis tués)
- Epsilon élevé (30%)
- Beaucoup d'actions aléatoires
- Découverte des stratégies

### Phase 2 : Apprentissage (50-200 ennemis)
- Epsilon moyen (15-20%)
- Mix exploration/exploitation
- Convergence vers bonnes stratégies

### Phase 3 : Expertise (200+ ennemis)
- Epsilon faible (5-10%)
- Comportement optimisé
- Ennemis très prévisibles dans leurs "bonnes" actions

## Métriques affichées en jeu

Dans le panneau en bas à droite :

### 🧠 Apprentissage
- **États : X** : Nombre de situations différentes rencontrées
- **Explore : Y%** : Pourcentage d'exploration actuel

Plus le nombre d'états est élevé, plus les ennemis ont exploré de situations !

## Exemples de stratégies apprises

### Situation 1 : Joueur faible santé
```
État: "CLOSE_ANY_MOVING_LOW"
Action optimale: RUSH
Raisonnement: Le joueur est faible, charger rapidement maximise les chances de kill
```

### Situation 2 : Joueur pleine santé à distance
```
État: "FAR_ANY_STATIC_HIGH"
Action optimale: APPROACH
Raisonnement: Pas de danger immédiat, approcher pour engager
```

### Situation 3 : Joueur en mouvement, distance moyenne
```
État: "MEDIUM_ANY_MOVING_HIGH"
Action optimale: ZIGZAG
Raisonnement: Esquiver les projectiles tout en approchant
```

### Situation 4 : Ennemi en danger
```
État: "CLOSE_ANY_MOVING_ANY" + got_hit=True
Action optimale: RETREAT
Raisonnement: Prendre des dégâts → Reculer pour survivre
```

## Configuration avancée

Dans `enemy_learning_ai.py`, vous pouvez ajuster :

```python
# Vitesse d'apprentissage
learning_rate = 0.1      # Alpha (10% de nouvelle info)

# Importance du futur
discount_factor = 0.95   # Gamma (95% de valeur future)

# Exploration
epsilon = 0.3            # 30% d'exploration au départ
epsilon_decay = 0.995    # Décroissance par épisode
min_epsilon = 0.05       # 5% minimum (toujours un peu d'exploration)
```

## Différences de comportement observable

### Sans apprentissage (IA adaptative seule)
- Tous les ennemis du même type se comportent pareil
- Prévisible après quelques minutes
- Difficultés via stats uniquement

### Avec apprentissage
- Chaque ennemi peut agir différemment (exploration)
- Comportement global s'améliore avec le temps
- Surprises tactiques (nouvelles stratégies)
- Les ennemis "apprennent de vos patterns"

## Performance

- **Coût calcul** : Très faible (1 recherche Q-table par ennemi par frame)
- **Mémoire** : Croît avec les états explorés (typiquement < 1000 états)
- **Pas de ML lourd** : Pas de TensorFlow, PyTorch, etc.
- **Pure Python** : Algorithme léger et efficace

## Synergies avec l'IA adaptative

Les deux systèmes fonctionnent **ensemble** :

1. **IA Adaptative** augmente les stats (PV, vitesse, dégâts)
2. **IA d'Apprentissage** optimise le comportement tactique

Résultat : Ennemis **forts ET intelligents** !

## Désactiver l'apprentissage

Pour désactiver temporairement (mode test) :

Dans `game.py`, commentez cette ligne lors du spawn :
```python
# new_enemy.brain = self.enemy_learning.create_enemy_brain()
```

L'ennemi utilisera alors le comportement adaptatif standard.

## Améliorations futures possibles

- 🎯 **Apprentissage profond** : Remplacer Q-table par réseau de neurones
- 🤝 **Coordination** : Ennemis qui apprennent à attaquer en groupe
- 📊 **Analyse de patterns** : Détecter les habitudes du joueur
- 💾 **Sauvegarde** : Conserver la Q-table entre sessions
- 🏆 **Variantes** : Ennemis avec différents styles d'apprentissage

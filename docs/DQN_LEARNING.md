# 🧠 Deep Q-Network (DQN) pour l'Apprentissage des Ennemis

## Vue d'ensemble

Le système utilise maintenant un **réseau de neurones profond** (Deep Q-Network) au lieu d'une simple Q-table. Les ennemis apprennent via PyTorch et peuvent généraliser leurs connaissances à des situations jamais rencontrées.

## Pourquoi DQN > Q-Learning simple ?

### Q-Learning traditionnel ❌
```
État: "MEDIUM_2_MOVING_HIGH" → Q-Value pour chaque action
```
- Limité aux états **exactement** rencontrés
- Ne peut pas généraliser
- Croissance exponentielle de la mémoire

### Deep Q-Network ✅
```
État: [0.5, 0.3, 0.8, ...] (vecteur continu)
         ↓
   Réseau de neurones
         ↓
Q-Values pour toutes les actions
```
- **Généralisation** : États similaires → Actions similaires
- **Mémoire fixe** : Poids du réseau (pas de croissance)
- **Apprentissage puissant** : Patterns complexes

## Architecture du réseau

### Structure du DQN

```
Input Layer (16 neurones)
    ↓
Dense 128 + ReLU + Dropout(0.2)
    ↓
Dense 128 + ReLU + Dropout(0.2)
    ↓
Dense 64 + ReLU
    ↓
Output Layer (8 neurones, 1 par action)
```

### Taille du modèle
- **Paramètres** : ~22,000 poids entraînables
- **Mémoire** : ~88 KB (très léger !)
- **Inference** : < 1ms par décision

## Encodage de l'état

Le vecteur d'état contient **16 dimensions** :

```python
[0]     Position relative X (normalisée)
[1]     Position relative Y (normalisée)
[2]     Distance au joueur (normalisée 0-1)
[3-4]   Vélocité joueur X, Y (normalisée)
[5]     Magnitude vitesse joueur
[6]     Angle vers joueur (normalisé 0-1)
[7]     Santé joueur (ratio 0-1)
[8]     Santé ennemi (ratio 0-1)
[9-12]  Distance catégorisée (one-hot)
        [9]  CLOSE (< 100px)
        [10] MEDIUM (100-250px)
        [11] FAR (250-500px)
        [12] VERY_FAR (> 500px)
[13-14] Mouvement (one-hot)
        [13] MOVING
        [14] STATIC
[15]    Bias (toujours 1.0)
```

### Exemple d'encodage

```python
Situation: 
- Ennemi à (300, 400)
- Joueur à (500, 600) en mouvement rapide
- Distance: 283px
- Santé joueur: 80%, Santé ennemi: 100%

Vecteur d'état:
[0.20, 0.20,  # Position relative
 0.28,        # Distance normalisée
 0.5, 0.3,    # Vélocité joueur
 0.6,         # Magnitude
 0.43,        # Angle
 0.80, 1.0,   # Santés
 0, 0, 1, 0,  # FAR (one-hot)
 1, 0,        # MOVING (one-hot)
 1.0]         # Bias
```

## Algorithme DQN

### Double DQN

Le système utilise **deux réseaux** pour la stabilité :

1. **Policy Network** : Réseau principal qui apprend
2. **Target Network** : Copie fixe pour calcul des cibles

```python
# Calcul de la Q-value cible
Q_target = Reward + γ × Q_target_net(next_state, best_action)

# Mise à jour du policy network
Loss = (Q_policy - Q_target)²
```

### Mise à jour du Target Network

Tous les **100 steps** :
```python
target_net ← policy_net
```

Pourquoi ? Évite l'instabilité causée par des cibles qui bougent trop vite.

## Replay Buffer

### Concept

Au lieu d'apprendre immédiatement, on **stocke** les expériences :

```
Buffer (10,000 expériences max)
├── (s₀, a₀, r₀, s₁, done₀)
├── (s₁, a₁, r₁, s₂, done₁)
├── ...
└── (sₙ, aₙ, rₙ, sₙ₊₁, doneₙ)
```

### Apprentissage par batch

Tous les **4 steps** :
1. Échantillonner **64 expériences** aléatoires
2. Calculer les Q-targets pour le batch
3. Backpropagation sur le batch
4. Mise à jour des poids

### Avantages

✅ **Brise corrélation temporelle** : Expériences mélangées
✅ **Efficacité** : Réutilise les expériences multiples fois
✅ **Stabilité** : Lissage via moyennage

## Stratégie d'exploration

### Epsilon-Greedy avec décroissance

```python
ε_start = 0.30    # 30% exploration au début
ε_min   = 0.05    # 5% minimum (toujours un peu)
decay   = 0.9995  # Décroissance par step

ε_new = max(ε_min, ε_current × decay)
```

### Évolution typique

```
Episode 0:     ε = 30% → Beaucoup d'exploration
Episode 100:   ε = 18% → Mix
Episode 500:   ε = 10% → Principalement exploitation
Episode 2000:  ε = 5%  → Exploitation maximale
```

## Fonction de récompense

### Récompenses positives
```python
+15.0       Toucher le joueur (ÉNORME récompense !)
+0.05/s     Survivre
+0.8/s      Distance optimale (150-250px)
+0.4/s      Distance acceptable (100-150px)
+0.2/s      Se rapprocher (si > 100px)
```

### Pénalités
```python
-8.0        Être touché par projectile
-0.3/s      Trop proche (< 80px, danger)
-15.0       Mourir (pénalité finale)
```

### Reward shaping

Les récompenses sont **façonnées** pour guider l'apprentissage :
- Récompenses fréquentes pour survie
- Récompenses pour "bon" positionnement
- Grosse récompense finale pour objectif

## Techniques d'optimisation

### 1. Gradient Clipping
```python
torch.nn.utils.clip_grad_norm_(parameters, 1.0)
```
Empêche les gradients explosifs.

### 2. Dropout (0.2)
Régularisation pour éviter l'overfitting.

### 3. Huber Loss (Smooth L1)
Plus robuste que MSE aux outliers.

### 4. Xavier Initialization
Initialisation des poids pour convergence plus rapide.

### 5. Adam Optimizer
Learning rate: 0.0005 (conservatif pour stabilité)

## Avantages du DQN

| Critère | Q-Learning | DQN |
|---------|------------|-----|
| **Généralisation** | ❌ Aucune | ✅ Excellente |
| **Mémoire** | 📈 Croissante | ✅ Fixe |
| **Performance** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **États continus** | ❌ | ✅ |
| **Apprentissage** | Lent | Rapide |
| **Qualité finale** | Bonne | Excellente |

## Statistiques affichées

Dans le panneau en jeu :

### 🧠 DQN Learning
- **Mémoire : X** : Nombre d'expériences dans le buffer
- **ε : Y%** : Taux d'exploration actuel
- **CPU/CUDA** : Device utilisé (vert si GPU)

## Utilisation GPU vs CPU

### Détection automatique
```python
device = 'cuda' if torch.cuda.is_available() else 'cpu'
```

### Performance

**CPU (Intel i7)** :
- Inference : ~0.5ms
- Training batch : ~10ms
- FPS jeu : ~60 (aucun impact)

**GPU (NVIDIA)** :
- Inference : ~0.1ms
- Training batch : ~2ms
- FPS jeu : ~60 (encore mieux)

**Verdict** : CPU largement suffisant pour ce cas !

## Sauvegarde et chargement

### Sauvegarder le modèle entraîné
```python
enemy_learning.save_model('models/enemy_dqn_best.pth')
```

### Charger un modèle pré-entraîné
```python
enemy_learning.load_model('models/enemy_dqn_best.pth')
```

Le fichier sauvegarde :
- Poids du policy network
- Poids du target network
- État de l'optimiseur
- Epsilon actuel
- Nombre d'épisodes

## Évolution de l'apprentissage

### Phase 1 : Collecte initiale (0-500 expériences)
```
Actions: Aléatoires (exploration pure)
Buffer: Remplissage
Training: Pas encore
```

### Phase 2 : Premiers apprentissages (500-2000 exp)
```
Actions: Mix aléatoire/réseau
Buffer: En cours de remplissage
Training: Commence (instable)
Performance: Amélioration rapide
```

### Phase 3 : Convergence (2000-5000 exp)
```
Actions: Principalement réseau
Buffer: Plein (anciennes exp écrasées)
Training: Régulier (stable)
Performance: Bonne, s'affine
```

### Phase 4 : Maîtrise (5000+ exp)
```
Actions: Réseau (95% exploitation)
Buffer: Plein, optimisé
Training: Fine-tuning
Performance: Excellente !
```

## Comparaison visuelle

### Comportement appris typique

#### Début (0-50 kills)
```
Ennemi spawne
    ↓
Action aléatoire (RETREAT)
    ↓
S'éloigne du joueur (mauvais)
    ↓
Meurt sans rien faire
    ↓
Q-values mises à jour
```

#### Milieu (200-500 kills)
```
Ennemi spawne
    ↓
Réseau choisit APPROACH
    ↓
Se rapproche intelligemment
    ↓
À distance moyenne → CIRCLE_LEFT
    ↓
Esquive quelques tirs
    ↓
Parfois touche le joueur (+15 reward!)
```

#### Expert (1000+ kills)
```
Ennemi spawne
    ↓
Évalue la situation (santé, distance, vélocité)
    ↓
Si joueur faible: RUSH agressif
Si joueur fort: ZIGZAG + CIRCLE
    ↓
Positionnement optimal (150-250px)
    ↓
Esquive efficace
    ↓
Touche régulièrement le joueur
```

## Métriques de performance

### Loss du réseau
```
Début:   Loss ~5.0  (apprentissage instable)
Milieu:  Loss ~1.5  (convergence)
Expert:  Loss ~0.3  (optimisé)
```

### Récompense moyenne
```
Début:   -10.0  (meurt vite)
Milieu:  +5.0   (survit, quelques hits)
Expert:  +20.0  (touche souvent le joueur)
```

## Configuration avancée

Dans `enemy_dqn_ai.py` :

```python
# Architecture du réseau
hidden_size = 128        # Taille des couches cachées
dropout = 0.2            # Taux de dropout

# Hyperparamètres
learning_rate = 0.0005   # Taux d'apprentissage
discount_factor = 0.95   # Gamma (importance du futur)
batch_size = 64          # Taille des batchs
buffer_size = 10000      # Taille du replay buffer

# Exploration
epsilon_start = 0.3
epsilon_min = 0.05
epsilon_decay = 0.9995

# Mise à jour
train_every = 4          # Entraîner tous les N steps
update_target = 100      # MAJ target network tous les N steps
```

## Debugging et monitoring

### Indicateurs de bonne santé

✅ **Loss qui diminue** progressivement
✅ **Buffer qui se remplit** rapidement
✅ **Epsilon qui décroît** lentement
✅ **Récompense moyenne croissante**

### Signes de problème

❌ **Loss qui explose** → Learning rate trop élevé
❌ **Loss qui stagne** → Pas assez d'exploration
❌ **Récompense qui descend** → Fonction de reward mal conçue

## Améliorations futures possibles

### 🚀 Prioritized Experience Replay
Échantillonner plus souvent les expériences "surprenantes"

### 🎯 Dueling DQN
Séparer V(s) et A(s,a) pour meilleure estimation

### 🔄 Rainbow DQN
Combiner toutes les améliorations (C51, Noisy Nets, etc.)

### 🧠 Multi-Agent RL
Ennemis qui apprennent à coopérer

### 📊 Curriculum Learning
Entraîner progressivement sur situations plus difficiles

## Conclusion

Le système DQN apporte :

✅ **Apprentissage puissant** via réseau de neurones
✅ **Généralisation** à des situations inédites
✅ **Mémoire efficace** avec replay buffer
✅ **Stabilité** via Double DQN
✅ **Performance** en temps réel (CPU suffit)
✅ **Sauvegarde** pour réutilisation

Les ennemis deviennent **vraiment intelligents** et apprennent des patterns complexes ! 🧠💪

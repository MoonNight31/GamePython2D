# 🎓 Curriculum Learning - 7 Étapes

## Vue d'ensemble

Le système d'apprentissage par curriculum a été étendu à **7 étapes progressives** pour former une IA complète et performante. Chaque étape se concentre sur une compétence spécifique tout en conservant les acquis des étapes précédentes.

## 📋 Les 7 Étapes

### 🎯 Étape 1 : Apprendre à Tirer
**Objectif** : L'IA doit apprendre à tirer des projectiles de manière régulière.

**Récompenses** :
- ✅ **+10.0** par projectile tiré (très généreux)
- ✅ **+5.0** bonus si tire vers un ennemi (dans un rayon de 45°)
- ✅ **+0.1** bonus de survie minimal
- ❌ **-20.0** pénalité mort

**Critères de passage** :
- Moyenne de **5 projectiles/épisode** sur 10 épisodes

**Durée d'entraînement** : 100,000 timesteps

---

### 🎨 Étape 2 : Apprendre à Viser
**Objectif** : L'IA doit apprendre à orienter ses tirs vers les ennemis.

**Récompenses** :
- ✅ **+8.0** bonus proportionnel à la précision de la visée
- ✅ **+12.0** JACKPOT si tire ET vise bien (dot product > 0.3)
- ✅ **+3.0** par projectile tiré (acquis de l'étape 1)
- ✅ **+20.0** par ennemi tué (preuve de bonne visée)
- ❌ **-25.0** pénalité mort

**Critères de passage** :
- **30% de précision** de visée sur 10 épisodes

**Durée d'entraînement** : 100,000 timesteps

---

### 🏃 Étape 3 : Apprendre à se Déplacer
**Objectif** : L'IA doit apprendre à se déplacer intelligemment pour éviter les ennemis.

**Récompenses** :
- ✅ **+3.0** bonus pour mouvement
- ✅ **+2.0** bonus proportionnel si s'éloigne des ennemis
- ✅ **+2.0** par projectile (acquis étapes 1-2)
- ✅ **+0.2** survie
- ❌ **-2.0** si trop proche des bords (< 50px)
- ❌ **-2.0** par point de dégât reçu
- ❌ **-30.0** pénalité mort

**Critères de passage** :
- Score de mouvement **> 0.7** sur 10 épisodes

**Durée d'entraînement** : 100,000 timesteps

---

### 🛡️ Étape 4 : Apprendre à Survivre
**Objectif** : L'IA doit combiner toutes les compétences pour survivre longtemps.

**Récompenses** :
- ✅ **+0.5** bonus de survie par step
- ✅ **+15.0** par ennemi tué
- ✅ **+1.0** pour mouvement (acquis étape 3)
- ✅ **+1.0** par projectile (acquis étapes 1-2)
- ✅ **+0.5** si bonne position (loin des bords)
- ❌ **-3.0** si trop proche des bords (< 100px)
- ❌ **-5.0** par point de dégât reçu
- ❌ **-100.0** pénalité mort

**Critères de passage** :
- Survie moyenne de **1000 steps** sur 5 épisodes

**Durée d'entraînement** : 100,000 timesteps

---

### 💎 Étape 5 : Apprendre à Ramasser les Orbes d'XP
**Objectif** : L'IA doit collecter activement les orbes d'XP laissés par les ennemis.

**Récompenses** :
- ✅ **+2.0** par point d'XP collecté (ÉNORME)
- ✅ **+3.0** bonus proportionnel si se dirige vers un orbe
- ✅ **+10.0** par ennemi tué (réduit, priorité à la collecte)
- ✅ **+0.5** par projectile (acquis)
- ✅ **+0.3** survie
- ❌ **-3.0** par point de dégât reçu
- ❌ **-80.0** pénalité mort

**Critères de passage** :
- Moyenne de **3 orbes collectés** (30 XP) par épisode sur 10 épisodes

**Durée d'entraînement** : 100,000 timesteps

---

### 🃏 Étape 6 : Apprendre à Sélectionner les Cartes
**Objectif** : L'IA doit atteindre des level-ups pour obtenir des améliorations via les cartes.

**Récompenses** :
- ✅ **+50.0** par level up atteint (MASSIF)
- ✅ **+1.5** par point d'XP collecté (pour atteindre les level ups)
- ✅ **+12.0** par ennemi tué
- ✅ **+0.8** par projectile (acquis)
- ✅ **+0.4** survie
- ❌ **-4.0** par point de dégât reçu
- ❌ **-100.0** pénalité mort

**Critères de passage** :
- Moyenne d'**1 level up** par épisode sur 5 épisodes

**Durée d'entraînement** : 100,000 timesteps

**Note** : L'IA n'a pas besoin de sélectionner manuellement les cartes (pas d'input utilisateur), mais elle apprend à atteindre les niveaux pour les obtenir automatiquement.

---

### 🏆 Étape 7 : Maîtrise Complète avec Améliorations
**Objectif** : Excellence dans tous les domaines avec optimisation des améliorations.

**Récompenses** :
- ✅ **+0.6** survie par step
- ✅ **+20.0** par ennemi tué
- ✅ **+10.0** bonus par niveau au-delà de 4 (exponentiel)
- ✅ **+1.0** par point d'XP collecté
- ✅ **+1.5** par projectile tiré
- ✅ **+1.5** pour mouvement tactique
- ✅ **+1.0** si position optimale (> 200px des bords)
- ❌ **-5.0** si trop proche des bords (< 100px)
- ❌ **-8.0** par point de dégât reçu (très punitif)
- ❌ **-150.0** pénalité mort (MASSIVE)

**Critères de passage** :
- Survie moyenne de **2000 steps** sur 5 épisodes
- Moyenne de **5 kills** par épisode

**Durée d'entraînement** : 100,000 timesteps

---

## 🎯 Métriques d'Évaluation

Pour chaque étape, l'évaluation mesure :

| Métrique | Description |
|----------|-------------|
| **Projectiles/épisode** | Nombre de projectiles tirés |
| **Précision visée** | Pourcentage de tirs bien orientés vers les ennemis |
| **Score de mouvement** | Intensité et qualité du déplacement |
| **Temps de survie** | Nombre de steps avant la mort |
| **Kills/épisode** | Nombre d'ennemis tués par projectiles |
| **Orbes XP collectés** | Quantité d'XP ramassée |
| **Cartes obtenues** | Nombre de level-ups atteints |
| **Niveau moyen final** | Niveau atteint en fin d'épisode |

---

## 🚀 Utilisation

### Lancer le curriculum complet

```bash
cd tools/training
python curriculum_trainer.py
```

### Lancer une étape spécifique

```python
from curriculum_trainer import CurriculumLearningTrainer

trainer = CurriculumLearningTrainer()
trainer.train_stage(stage=5, total_timesteps=100000)  # Étape 5 : Orbes XP
```

### Évaluer une étape

```python
trainer._evaluate_stage(stage=3)
```

---

## 📊 Progression Typique

### Étape 1 → Étape 2 (Tir → Visée)
L'IA passe de tirs aléatoires à des tirs orientés vers les ennemis.
- **Avant** : Tire dans toutes les directions
- **Après** : Vise majoritairement les ennemis proches

### Étape 2 → Étape 3 (Visée → Mouvement)
L'IA apprend à se déplacer tout en maintenant sa précision de tir.
- **Avant** : Reste statique en tirant
- **Après** : Se déplace tactiquement en tirant

### Étape 3 → Étape 4 (Mouvement → Survie)
L'IA optimise la combinaison mouvement + tir pour maximiser la survie.
- **Avant** : Meurt rapidement malgré le mouvement
- **Après** : Survit longtemps en évitant les dégâts

### Étape 4 → Étape 5 (Survie → Collecte XP)
L'IA ajoute la collecte active d'XP à son comportement de survie.
- **Avant** : Ignore les orbes d'XP au sol
- **Après** : Se dirige vers les orbes tout en survivant

### Étape 5 → Étape 6 (Collecte XP → Level-ups)
L'IA optimise la collecte d'XP pour atteindre rapidement les level-ups.
- **Avant** : Collecte peu d'XP, niveau bas
- **Après** : Collecte activement, monte en niveau

### Étape 6 → Étape 7 (Level-ups → Maîtrise)
L'IA utilise les améliorations obtenues pour exceller dans tous les domaines.
- **Avant** : Niveau 1-2 en moyenne
- **Après** : Niveau 5+ avec comportement expert

---

## ⚙️ Configuration des Timesteps

Chaque étape utilise **100,000 timesteps** par défaut, soit :
- ~1,666 épisodes de 60 steps
- ~10-15 minutes d'entraînement (selon CPU)
- **Total : 700,000 timesteps** pour le curriculum complet

### Ajustements recommandés

**Entraînement rapide (test)** :
```python
trainer.train_stage(stage, total_timesteps=50000)
```

**Entraînement standard** :
```python
trainer.train_stage(stage, total_timesteps=100000)  # Par défaut
```

**Entraînement approfondi** :
```python
trainer.train_stage(stage, total_timesteps=200000)
```

---

## 🔄 Transfer Learning

Le curriculum utilise le **transfer learning** :
- Chaque étape charge le modèle de l'étape précédente
- Les acquis sont conservés et raffinés
- L'apprentissage est cumulatif, pas isolé

### Sauvegarde des modèles

| Fichier | Description |
|---------|-------------|
| `curriculum_stage_1.zip` | Modèle après étape 1 (Tir) |
| `curriculum_stage_2.zip` | Modèle après étape 2 (Visée) |
| `curriculum_stage_3.zip` | Modèle après étape 3 (Mouvement) |
| `curriculum_stage_4.zip` | Modèle après étape 4 (Survie) |
| `curriculum_stage_5.zip` | Modèle après étape 5 (Collecte XP) |
| `curriculum_stage_6.zip` | Modèle après étape 6 (Cartes) |
| `curriculum_stage_7.zip` | **Modèle final complet** |

---

## 🎮 Intégration des Systèmes de Jeu

### Système d'Orbes XP (Étape 5)
L'environnement AI gère automatiquement :
- Création d'orbes à la mort des ennemis
- Attraction magnétique vers le joueur
- Collecte par collision
- Gain d'XP au système

### Système de Cartes (Étape 6-7)
Pour l'entraînement, les cartes sont **automatiquement sélectionnées** :
- L'IA n'a pas de choix manuel
- Les améliorations sont appliquées automatiquement au level-up
- Focus sur l'apprentissage de la progression plutôt que du choix

**Note** : Pour un modèle complet avec choix de cartes, il faudrait étendre l'espace d'action pour inclure la sélection.

---

## 🐛 Dépannage

### L'IA ne progresse pas d'une étape
- Augmenter les timesteps d'entraînement
- Vérifier que le modèle précédent se charge correctement
- Réduire les critères de passage temporairement

### L'IA oublie les compétences précédentes
- Vérifier que les récompenses des étapes précédentes sont conservées
- Augmenter le poids des compétences acquises dans les récompenses
- Réduire le learning rate pour stabiliser l'apprentissage

### Entraînement trop lent
- Augmenter le nombre d'environnements parallèles (n_envs)
- Réduire max_steps par épisode
- Utiliser CPU uniquement (plus rapide que GPU pour PPO + Pygame)

---

## 📈 Résultats Attendus

Après le curriculum complet (7 étapes), l'IA devrait être capable de :

✅ **Tirer régulièrement** (15+ projectiles/épisode)  
✅ **Viser avec précision** (>50% de précision)  
✅ **Se déplacer intelligemment** (évite les ennemis et les bords)  
✅ **Survivre longtemps** (>2000 steps)  
✅ **Collecter l'XP activement** (>50 XP/épisode)  
✅ **Atteindre des level-ups** (Niveau 3-5+ par épisode)  
✅ **Tuer efficacement** (>5 ennemis/épisode)  
✅ **Optimiser sa progression** (Combine toutes les compétences)

---

## 🎯 Prochaines Améliorations

### Étape 8 potentielle : Stratégie de Cartes
- Espace d'action étendu pour choisir les cartes
- Récompenses basées sur les synergies de cartes
- Apprentissage de builds optimaux

### Étape 9 potentielle : Multi-objectifs
- Équilibrage dynamique entre survie et kills
- Adaptation au niveau de difficulté
- Comportement émergent complexe

### Optimisations
- Curriculum adaptatif (ajuste les timesteps selon la progression)
- Multi-stage parallel training (entraîner plusieurs étapes en parallèle)
- Récompenses dynamiques (ajustement automatique selon les performances)

---

## 📚 Ressources

- **PPO Algorithm** : [Stable Baselines3 Documentation](https://stable-baselines3.readthedocs.io/)
- **Curriculum Learning** : [OpenAI Research](https://openai.com/research/)
- **Reinforcement Learning** : [Gymnasium Documentation](https://gymnasium.farama.org/)

---

## 🏆 Conclusion

Le système de curriculum learning à 7 étapes permet de former une IA complète et performante de manière progressive et efficace. Chaque étape construit sur les précédentes, créant un agent capable de maîtriser tous les aspects du jeu.

**Temps total d'entraînement estimé** : 1.5 - 2 heures  
**Modèle final** : `ai_models/curriculum_stage_7.zip`  
**Performance attendue** : Agent expert capable de survie prolongée et progression efficace

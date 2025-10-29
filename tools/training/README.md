# 🎓 Training Tools - Curriculum Learning

Ce dossier contient les outils d'entraînement avancés pour l'IA du jeu, notamment le **Curriculum Learning à 7 étapes**.

## 📁 Fichiers

### `curriculum_trainer.py`
Entraîneur principal avec apprentissage progressif en 7 étapes :
1. 🎯 Apprendre à tirer
2. 🎨 Apprendre à viser
3. 🏃 Apprendre à se déplacer
4. 🛡️ Apprendre à survivre
5. 💎 Apprendre à ramasser les orbes d'XP
6. 🃏 Apprendre à sélectionner les cartes
7. 🏆 Maîtrise complète avec améliorations

### `test_curriculum.py`
Tests automatisés pour vérifier la structure et le fonctionnement du curriculum.

## 🚀 Utilisation

### Entraînement Complet (7 étapes)

```bash
cd tools/training
python curriculum_trainer.py
```

Durée estimée : **1.5 - 2 heures** (700,000 timesteps total)

### Entraînement d'une Étape Spécifique

```python
from curriculum_trainer import CurriculumLearningTrainer

trainer = CurriculumLearningTrainer()
trainer.train_stage(stage=3, total_timesteps=100000)  # Étape 3 : Mouvement
```

### Test de Validation

```bash
# Test rapide de la structure
python test_curriculum.py --quick

# Test avec entraînement court
python test_curriculum.py --train
```

## 📊 Résultats

Les modèles entraînés sont sauvegardés dans `ai_models/` :
- `curriculum_stage_1.zip` → `curriculum_stage_7.zip`
- Le modèle final (`stage_7`) est le plus performant

## 📚 Documentation

Voir `/docs/CURRICULUM_7_STAGES.md` pour une documentation complète :
- Détails de chaque étape
- Système de récompenses
- Critères de passage
- Métriques d'évaluation
- Résultats attendus

## 🎯 Objectifs par Étape

| Étape | Objectif | Critère |
|-------|----------|---------|
| 1 | Tirer régulièrement | 5+ projectiles/épisode |
| 2 | Viser les ennemis | 30%+ précision |
| 3 | Se déplacer intelligemment | Score > 0.7 |
| 4 | Survivre longtemps | 1000+ steps |
| 5 | Collecter les orbes XP | 3+ orbes/épisode |
| 6 | Atteindre des level-ups | 1+ level-up/épisode |
| 7 | Excellence complète | 2000+ steps, 5+ kills |

## ⚙️ Configuration

### Modifier les Timesteps

Dans `curriculum_trainer.py`, ligne `run_full_curriculum()` :
```python
self.train_stage(stage, total_timesteps=100000)  # Augmenter pour plus d'entraînement
```

### Modifier les Critères de Passage

Dans `__init__()` :
```python
self.stage_criteria = {
    1: {"projectiles_per_episode": 5.0, "episodes_to_check": 10},
    # ...modifier les valeurs selon vos besoins
}
```

### Modifier les Récompenses

Chaque fonction `_stageX_reward()` peut être ajustée pour changer le comportement de l'IA.

## 🐛 Résolution de Problèmes

### L'IA ne progresse pas
- Augmenter `total_timesteps`
- Vérifier que le modèle précédent se charge
- Réduire les critères de passage

### Erreur de mémoire
- Réduire `n_envs` dans `create_environment()`
- Réduire `max_steps` dans l'environnement

### Entraînement trop lent
- Augmenter `n_envs` (plus de parallélisme)
- Utiliser CPU uniquement (déjà configuré)

## 🎮 Intégration

Le système s'intègre avec :
- ✅ Système d'orbes XP
- ✅ Système de cartes (level-up automatique)
- ✅ Effets visuels et audio
- ✅ IA environnement Gymnasium

## 📈 Améliorations Futures

- [ ] Étape 8 : Stratégie de choix de cartes
- [ ] Curriculum adaptatif (ajuste automatiquement)
- [ ] Multi-objectifs (équilibrage dynamique)
- [ ] Hyperparameter tuning automatique

## 🏆 Performance Attendue

Après le curriculum complet, l'IA devrait :
- ✅ Tirer efficacement (15+ projectiles/épisode)
- ✅ Viser avec précision (50%+)
- ✅ Se déplacer intelligemment
- ✅ Survivre >2000 steps
- ✅ Collecter activement l'XP
- ✅ Progresser en niveau
- ✅ Tuer efficacement (5+ ennemis)

## 📞 Support

Pour plus d'informations, consultez :
- `/docs/CURRICULUM_7_STAGES.md` - Documentation complète
- `/docs/XP_ORB_SYSTEM.md` - Système d'orbes XP
- `../../src/gamepython2d/ai_trainer.py` - Entraîneur de base
- `../../src/gamepython2d/ai_environment.py` - Environnement RL

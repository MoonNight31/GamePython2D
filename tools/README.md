# 🧰 Tools - Outils de développement GamePython2D

Ce dossier contient tous les outils de développement, debug et test pour le projet GamePython2D.

## 📁 Structure

### `/debug/` - Outils de diagnostic
- `debug_projectile_creation.py` - Debug création des projectiles
- `debug_rewards_complete.py` - Debug système de récompenses complet
- `debug_reward_system.py` - Debug système de récompenses

### `/training/` - Outils d'entraînement IA
- `curriculum_trainer.py` - Entraîneur curriculum (3 étapes)
- `precision_trainer.py` - Entraîneur spécialisé précision
- `smart_shooting_trainer.py` - Entraîneur tir intelligent
- `training_monitor.py` - Moniteur de progression d'entraînement
- `continue_curriculum.py` - Utilitaire de continuation curriculum

### `/testing/` - Outils de test et analyse
- `test_ai_effectiveness.py` - Test efficacité globale IA
- `test_ai_shooting.py` - Test système de tir IA
- `test_aiming_system.py` - Test système de visée
- `test_tank_movement.py` - Test mouvement des tanks
- `test_ai.py` - Test général IA
- `analyze_ai_behavior.py` - Analyseur comportement IA
- `final_comparison.py` - Comparaison finale des modèles
- `simple_shooting_test.py` - Test de tir simple
- `verify_system.py` - Vérificateur de système

## 🚀 Utilisation

### Pour tester l'IA :
```bash
python tools/testing/test_ai_effectiveness.py
```

### Pour entraîner l'IA :
```bash
python tools/training/curriculum_trainer.py
```

### Pour diagnostiquer des problèmes :
```bash
python tools/debug/debug_projectile_creation.py
```

## 📝 Notes

- Tous les outils utilisent le même environnement Python (.venv)
- Les chemins relatifs sont ajustés automatiquement
- Les modèles IA sont sauvegardés dans `/ai_models/`
- Les logs d'entraînement sont dans `/ai_logs/`
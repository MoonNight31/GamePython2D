#!/usr/bin/env python3
"""
Curriculum Trainer - Étape 2 seulement
Lance l'étape 2 du curriculum (mouvement) avec le modèle de l'étape 1
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from curriculum_trainer import CurriculumLearningTrainer

def main():
    print("🏃 ÉTAPE 2 : Apprentissage du mouvement")
    print("=" * 50)
    
    trainer = CurriculumLearningTrainer()
    
    # Charger le modèle de l'étape 1
    trainer.trainer.create_environment(n_envs=4)
    
    # Charger le modèle existant (il devrait être dans game_ai_model_final)
    try:
        trainer.trainer.load_model("ai_models/game_ai_model_final")
        print("✅ Modèle étape 1 chargé")
    except:
        print("❌ Impossible de charger le modèle étape 1")
        print("🆕 Création d'un nouveau modèle")
        trainer.trainer.create_model(learning_rate=0.0005)
    
    # Lancer l'étape 2
    trainer.train_stage(2, total_timesteps=100000)
    
    # Puis l'étape 3
    trainer.train_stage(3, total_timesteps=100000)
    
    print("🎉 CURRICULUM TERMINÉ !")

if __name__ == "__main__":
    main()
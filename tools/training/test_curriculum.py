#!/usr/bin/env python3
"""
Test rapide du nouveau curriculum à 7 étapes
"""

import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from curriculum_trainer import CurriculumLearningTrainer

def test_curriculum_structure():
    """Teste la structure du curriculum."""
    print("🧪 TEST DU CURRICULUM À 7 ÉTAPES")
    print("="*60)
    
    trainer = CurriculumLearningTrainer()
    
    # Vérifier que les 7 étapes existent
    print("\n📋 Vérification des étapes...")
    assert len(trainer.stages) == 7, f"Erreur: {len(trainer.stages)} étapes au lieu de 7"
    
    for stage_num, stage_name in trainer.stages.items():
        print(f"  ✅ Étape {stage_num}: {stage_name}")
    
    # Vérifier les critères
    print("\n📊 Vérification des critères de passage...")
    assert len(trainer.stage_criteria) == 7, f"Erreur: {len(trainer.stage_criteria)} critères au lieu de 7"
    
    expected_criteria = {
        1: ["projectiles_per_episode"],
        2: ["accuracy_score"],
        3: ["movement_score"],
        4: ["survival_time"],
        5: ["xp_orbs_collected"],
        6: ["cards_selected"],
        7: ["survival_time", "kills"]
    }
    
    for stage, criteria in expected_criteria.items():
        stage_criteria = trainer.stage_criteria[stage]
        for criterion in criteria:
            assert criterion in stage_criteria, f"Critère '{criterion}' manquant pour étape {stage}"
        print(f"  ✅ Étape {stage}: {list(stage_criteria.keys())}")
    
    # Vérifier que les fonctions de reward existent
    print("\n🎁 Vérification des fonctions de récompenses...")
    for stage in range(1, 8):
        reward_func = f"_stage{stage}_reward"
        assert hasattr(trainer, reward_func), f"Fonction {reward_func} manquante"
        print(f"  ✅ {reward_func} existe")
    
    print("\n✅ TOUS LES TESTS PASSÉS !")
    print("Le curriculum à 7 étapes est correctement configuré.")
    print("\n🚀 Vous pouvez maintenant lancer l'entraînement avec:")
    print("   python curriculum_trainer.py")

def test_single_stage():
    """Teste l'entraînement d'une seule étape (court)."""
    print("\n🧪 TEST D'ENTRAÎNEMENT RAPIDE (Étape 1)")
    print("="*60)
    
    trainer = CurriculumLearningTrainer()
    
    print("\n📝 Entraînement de l'étape 1 avec 5000 timesteps...")
    try:
        trainer.train_stage(1, total_timesteps=5000)
        print("✅ Entraînement réussi !")
    except Exception as e:
        print(f"❌ Erreur durant l'entraînement: {e}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test du curriculum à 7 étapes')
    parser.add_argument('--quick', action='store_true', help='Test rapide de structure uniquement')
    parser.add_argument('--train', action='store_true', help='Test avec entraînement court')
    
    args = parser.parse_args()
    
    # Test de structure (toujours)
    test_curriculum_structure()
    
    # Test d'entraînement (si demandé)
    if args.train:
        test_single_stage()
    elif not args.quick:
        response = input("\n❓ Voulez-vous tester l'entraînement rapide ? (o/n): ").strip().lower()
        if response in ['o', 'oui', 'y', 'yes']:
            test_single_stage()

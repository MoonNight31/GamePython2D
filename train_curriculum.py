"""Lance le curriculum learning complet sur les 7 étapes."""
import sys
import os

# Ajouter le chemin du projet
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools/training'))

from curriculum_trainer import CurriculumLearningTrainer

def main():
    """Lance l'entraînement complet avec curriculum learning."""
    print("=" * 70)
    print("🎓 CURRICULUM LEARNING - ENTRAÎNEMENT COMPLET")
    print("=" * 70)
    print("\n📋 CONFIGURATION:")
    print("   • 7 étapes progressives")
    print("   • 30 environnements parallèles")
    print("   • Récompenses normalisées (clippées -10 à +10)")
    print("   • Total: ~8.2M timesteps")
    print("   • Durée estimée: ~20-25 minutes")
    print("\n🎯 ÉTAPES:")
    print("   1. 🎯 TIR (600k)")
    print("   2. 🎨 VISÉE (800k)")
    print("   3. 🏃 MOUVEMENT (1M)")
    print("   4. 🛡️ SURVIE (1.2M)")
    print("   5. 💎 COLLECTE XP (1.4M)")
    print("   6. 🃏 CARTES (1.2M)")
    print("   7. 🏆 MAÎTRISE (2M)")
    print("=" * 70)
    
    input("\n⏸️  Appuyez sur ENTRÉE pour démarrer l'entraînement...")
    
    # Créer le trainer
    trainer = CurriculumLearningTrainer()
    
    # Lancer l'entraînement complet
    trainer.run_full_curriculum()
    
    print("\n" + "=" * 70)
    print("🎉 ENTRAÎNEMENT COMPLET TERMINÉ !")
    print("=" * 70)
    print("\n📊 Les graphiques ont été générés dans ai_logs/")
    print("💾 Le modèle final est sauvegardé dans ai_models/")
    print("\n✅ Vous pouvez maintenant tester l'IA avec demo_ai.py")

if __name__ == "__main__":
    main()

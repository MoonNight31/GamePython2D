"""Test rapide de la normalisation des récompenses."""
import sys
import os

# Ajouter le chemin du projet
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools/training'))

from curriculum_trainer import CurriculumLearningTrainer

def test_reward_normalization():
    """Test de normalisation des récompenses sur 150000 timesteps."""
    print("🧪 Test de normalisation des récompenses")
    print("=" * 60)
    
    # Créer le trainer
    trainer = CurriculumLearningTrainer()
    
    # Test avec la méthode train_stage qui applique le patching
    print("\n⏱️  Test sur 150000 timesteps avec étape 1 (TIR)...")
    print("📊 Surveillance des métriques clés:\n")
    
    trainer.train_stage(stage=1, total_timesteps=150000)
    
    print("\n✅ Test terminé!")
    print("\n📊 Vérifiez les logs ci-dessus:")
    print("   • ep_rew_mean devrait être entre 10 et 1000 (normalisé)")
    print("   • value_loss devrait être < 1000 (stable)")
    print("   • explained_variance devrait être > 0.1 (apprentissage)")
    print("\n⚠️  Si ep_rew_mean > 10000 = problème de normalisation")

if __name__ == "__main__":
    test_reward_normalization()

"""Test rapide de performance pour vérifier l'optimisation des récompenses."""
import time
import sys
import os

# Ajouter le chemin du projet
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools/training'))

from curriculum_trainer import CurriculumLearningTrainer

def test_performance():
    """Test rapide de performance sur 1000 steps."""
    print("🧪 Test de performance avec cache optimisé")
    print("=" * 60)
    
    # Créer le trainer
    trainer = CurriculumLearningTrainer()
    
    # Créer des environnements (30 parallèles)
    print("📦 Création de 30 environnements parallèles...")
    trainer.trainer.create_environment(n_envs=30)
    
    # Créer un modèle simple
    print("🤖 Création du modèle...")
    trainer.trainer.create_model(learning_rate=0.0005, batch_size=512)
    
    # Test de 1000 steps
    print("\n⏱️  Test sur 1000 timesteps...")
    start = time.time()
    
    trainer.trainer.train(total_timesteps=1000)
    
    elapsed = time.time() - start
    steps_per_sec = 1000 / elapsed
    
    print(f"\n✅ Résultats:")
    print(f"   • Temps total: {elapsed:.2f}s")
    print(f"   • Steps/sec: {steps_per_sec:.1f}")
    print(f"   • Temps par step: {(elapsed/1000)*1000:.2f}ms")
    
    if steps_per_sec > 100:
        print("\n✅ Performance excellente! (>100 steps/sec)")
    elif steps_per_sec > 50:
        print("\n✅ Performance bonne (>50 steps/sec)")
    else:
        print("\n⚠️  Performance à améliorer (<50 steps/sec)")

if __name__ == "__main__":
    test_performance()

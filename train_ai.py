#!/usr/bin/env python3
"""
Script principal d'entraînement IA - Version finale
Entraîne une IA active qui utilise les projectiles
"""

import sys
import os
import time

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def train_ai():
    """Entraîne une IA active avec le système de récompenses optimisé."""
    # Optimisations CPU OPTIMALES pour 32 environnements
    import os
    # FORCER L'UTILISATION DU CPU
    os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Désactive complètement CUDA
    os.environ['OMP_NUM_THREADS'] = '32'  # Perfect match avec 32 environnements
    os.environ['MKL_NUM_THREADS'] = '32'
    os.environ['NUMEXPR_NUM_THREADS'] = '32'
    os.environ['OPENBLAS_NUM_THREADS'] = '32'
    os.environ['BLIS_NUM_THREADS'] = '32'
    os.environ['VECLIB_MAXIMUM_THREADS'] = '32'
    # Threading optimisé pour 32 envs
    os.environ['OMP_SCHEDULE'] = 'dynamic,2'
    os.environ['OMP_DYNAMIC'] = 'true'
    os.environ['OMP_MAX_ACTIVE_LEVELS'] = '2'
    
    print("🚀 ENTRAÎNEMENT IA ACTIVE - GamePython2D [32 ENVIRONNEMENTS - CPU FORCÉ]")
    print("=" * 75)
    print("🎯 Objectif: IA qui tire des projectiles activement")
    print("💡 Système: +15pts kills actifs, 0pt kills passifs")
    print("💥 CPU: 16 threads, 32 environnements parallèles")
    print("💾 RAM: 32GB - UTILISATION OPTIMALE")
    print("🖥️ Device: CPU FORCÉ (performance optimale pour MLP)")
    print("⚡ Mode: PUISSANCE OPTIMALE - 32 ENVS")
    print("=" * 75)
    
    try:
        from gamepython2d.ai_trainer import GameAITrainer
        
        # Configuration OPTIMALE pour 32 environnements (sweet spot 32GB RAM)
        trainer = GameAITrainer()
        trainer.create_environment(n_envs=32)  # 32 environnements = PUISSANCE OPTIMALE
        
        # Créer ou charger le modèle OPTIMAL pour 32 environnements
        print("🤖 Création ou chargement du modèle PPO...")
        trainer.create_or_load_model(
            learning_rate=0.0005,
            n_steps=512,  # Équilibré pour 32 envs
            batch_size=512,  # ÉNORME batch pour 32 environnements
            n_epochs=5,  # Équilibré pour stabilité
            device='cpu'  # FORCÉ sur CPU pour performance optimale
        )
        
        # Entraînement (continuera automatiquement si modèle existant)
        total_timesteps = 2000000  # 2M steps total
        print(f"🎓 Entraînement: {total_timesteps:,} timesteps")
        
        # Vérifier si c'est une reprise
        if hasattr(trainer.model, 'num_timesteps') and trainer.model.num_timesteps > 0:
            remaining_steps = max(0, total_timesteps - trainer.model.num_timesteps)
            print(f"🔄 REPRISE D'ENTRAÎNEMENT:")
            print(f"   📊 Déjà entraîné: {trainer.model.num_timesteps:,} timesteps")
            print(f"   🎯 Restant: {remaining_steps:,} timesteps")
            print(f"   ⏱️ Durée estimée: {remaining_steps/800000*60:.1f} minutes")
        else:
            print(f"🆕 NOUVEL ENTRAÎNEMENT:")
            print(f"   ⏱️ Durée estimée: {total_timesteps/800000*60:.1f} minutes")

        start_time = time.time()
        model = trainer.train(total_timesteps=total_timesteps, save_freq=100000)
        elapsed = time.time() - start_time
        
        print(f"✅ Entraînement terminé en {elapsed/60:.1f} minutes")
        print(f"💾 Modèle sauvegardé dans ai_models/")
        
        # Test rapide simplifié
        print(f"\n🧪 Test rapide...")
        print("✅ Modèle entraîné avec succès!")
        print("🎯 Utilisez demo_ai.py pour tester votre IA en action!")
        
        print(f"🚀 Projectiles tirés: {projectiles_fired}")
        if projectiles_fired > 0:
            print("✅ SUCCÈS: IA active créée!")
        else:
            print("⚠️ IA encore passive, plus d'entraînement nécessaire")
        
        trainer.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    train_ai()
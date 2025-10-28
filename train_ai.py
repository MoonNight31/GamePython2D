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
    print("🚀 ENTRAÎNEMENT IA ACTIVE - GamePython2D")
    print("=" * 60)
    print("🎯 Objectif: IA qui tire des projectiles activement")
    print("💡 Système: +15pts kills actifs, 0pt kills passifs")
    print("=" * 60)
    
    try:
        from gamepython2d.ai_trainer import GameAITrainer
        
        # Configuration
        trainer = GameAITrainer()
        trainer.create_environment(n_envs=8)  # 8 environnements parallèles
        
        # Créer le modèle
        print("🤖 Création du modèle PPO...")
        trainer.create_model(
            learning_rate=0.0005,
            n_steps=2048,
            batch_size=64,
            n_epochs=10
        )
        
        # Entraînement
        total_timesteps = 100000  # 50k steps = ~5 minutes
        print(f"🎓 Entraînement: {total_timesteps:,} timesteps")
        print("⏱️ Durée estimée: 5-10 minutes")

        start_time = time.time()
        model = trainer.train(total_timesteps=total_timesteps, save_freq=100000)
        elapsed = time.time() - start_time
        
        print(f"✅ Entraînement terminé en {elapsed/60:.1f} minutes")
        print(f"💾 Modèle sauvegardé dans ai_models/")
        
        # Test rapide
        print(f"\n🧪 Test rapide...")
        env = trainer.env.envs[0] if hasattr(trainer.env, 'envs') else trainer.env
        obs, _ = env.reset()
        
        projectiles_fired = 0
        for _ in range(500):
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            projectiles_fired = info.get('projectiles_fired', 0)
            if terminated or truncated:
                break
        
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
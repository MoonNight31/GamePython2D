#!/usr/bin/env python3
"""
Script principal de test IA - Version finale
Teste et compare les performances des IA
"""

import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_ai_performance(model_name, model_path):
    """Teste les performances d'un modèle IA."""
    try:
        from gamepython2d.ai_trainer import GameAITrainer
        from gamepython2d.ai_environment import GameAIEnvironment
        
        env = GameAIEnvironment(render_mode=None)
        trainer = GameAITrainer()
        trainer.create_environment(n_envs=1)
        trainer.load_model(model_path)
        
        # Test sur 3 épisodes
        results = {'survival': [], 'projectiles': [], 'active_kills': [], 'passive_kills': [], 'reward': []}
        
        for episode in range(3):
            obs, _ = env.reset()
            total_reward = 0
            steps = 0
            
            for _ in range(2000):
                action, _ = trainer.model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = env.step(action)
                total_reward += reward
                steps += 1
                if terminated or truncated:
                    break
            
            results['survival'].append(steps)
            results['projectiles'].append(info.get('projectiles_fired', 0))
            results['active_kills'].append(info.get('enemies_killed_by_projectiles', 0))
            results['passive_kills'].append(info.get('enemies_killed_by_collision', 0))
            results['reward'].append(total_reward)
        
        # Moyennes
        avg_results = {key: sum(values)/len(values) for key, values in results.items()}
        
        print(f"📊 {model_name}:")
        print(f"   ⏱️ Survie: {avg_results['survival']:.0f} steps")
        print(f"   🚀 Projectiles: {avg_results['projectiles']:.1f}")
        print(f"   ⚔️ Kills actifs: {avg_results['active_kills']:.1f}")
        print(f"   💥 Kills passifs: {avg_results['passive_kills']:.1f}")
        print(f"   🏆 Récompense: {avg_results['reward']:.1f}")
        
        trainer.close()
        return avg_results
        
    except Exception as e:
        print(f"❌ Erreur avec {model_name}: {e}")
        return None

def test_ai():
    """Teste toutes les IA disponibles."""
    print("🧪 TEST DES IA - GamePython2D")
    print("=" * 50)
    
    # Modèles à tester
    models = [
        ("IA PASSIVE (ancienne)", "ai_models/demo_ai_final"),
        ("IA ACTIVE (nouvelle)", "ai_models/game_ai_model_final")
    ]
    
    results = {}
    
    for name, path in models:
        if os.path.exists(f"{path}.zip"):
            print(f"\n🔍 Test {name}")
            print("-" * 40)
            result = test_ai_performance(name, path)
            if result:
                results[name] = result
        else:
            print(f"⚠️ Modèle non trouvé: {path}")
    
    # Comparaison si on a les deux modèles
    if len(results) == 2:
        print(f"\n📈 COMPARAISON:")
        print("-" * 50)
        
        old_name = "IA PASSIVE (ancienne)"
        new_name = "IA ACTIVE (nouvelle)"
        
        if old_name in results and new_name in results:
            old = results[old_name]
            new = results[new_name]
            
            projectile_improvement = new['projectiles'] - old['projectiles']
            reward_improvement = new['reward'] - old['reward']
            
            print(f"🚀 Projectiles: {old['projectiles']:.1f} → {new['projectiles']:.1f} ({projectile_improvement:+.1f})")
            print(f"🏆 Récompense: {old['reward']:.1f} → {new['reward']:.1f} ({reward_improvement:+.1f})")
            
            if projectile_improvement > 0:
                print("✅ SUCCÈS: IA transformée de passive à active!")
            else:
                print("⚠️ IA encore passive")

if __name__ == "__main__":
    test_ai()
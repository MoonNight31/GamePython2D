#!/usr/bin/env python3
"""
Comparaison directe : Ancienne IA vs Nouvelle IA
"""

import sys
import os
import time

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def compare_old_vs_new():
    """Compare directement l'ancienne IA passive vs la nouvelle IA active."""
    print("⚡ COMPARAISON FINALE - TRANSFORMATION IA")
    print("=" * 80)
    print("🎯 Objectif: Mesurer l'impact du nouveau système de récompenses")
    print("=" * 80)
    
    try:
        from gamepython2d.ai_trainer import GameAITrainer
        from gamepython2d.ai_environment import GameAIEnvironment
        
        results = {}
        
        # Test des deux modèles
        models_to_test = [
            ("ANCIENNE IA PASSIVE", "ai_models/demo_ai_final"),
            ("NOUVELLE IA ACTIVE", "ai_models/game_ai_model_final")
        ]
        
        for name, model_path in models_to_test:
            print(f"\n🧪 TEST - {name}")
            print("-" * 60)
            
            env = GameAIEnvironment(render_mode=None)
            trainer = GameAITrainer()
            trainer.create_environment(n_envs=1)
            
            try:
                trainer.load_model(model_path)
                
                # Test sur 3 épisodes pour plus de précision
                total_results = {
                    'survival': [],
                    'active_kills': [],
                    'passive_kills': [],
                    'projectiles': [],
                    'reward': [],
                    'health': []
                }
                
                for episode in range(3):
                    obs, _ = env.reset()
                    total_reward = 0
                    steps = 0
                    
                    for _ in range(2000):  # Max 2000 steps par épisode
                        action, _ = trainer.model.predict(obs, deterministic=True)
                        obs, reward, terminated, truncated, info = env.step(action)
                        total_reward += reward
                        steps += 1
                        
                        if terminated or truncated:
                            break
                    
                    total_results['survival'].append(steps)
                    total_results['active_kills'].append(info.get('enemies_killed_by_projectiles', 0))
                    total_results['passive_kills'].append(info.get('enemies_killed_by_collision', 0))
                    total_results['projectiles'].append(info.get('projectiles_fired', 0))
                    total_results['reward'].append(total_reward)
                    total_results['health'].append(info.get('player_health', 0))
                
                # Calculer les moyennes
                avg_results = {}
                for key, values in total_results.items():
                    avg_results[key] = sum(values) / len(values)
                
                results[name] = avg_results
                
                print(f"📊 Résultats moyens sur 3 épisodes:")
                print(f"   ⏱️ Survie: {avg_results['survival']:.0f} steps")
                print(f"   💚 Vie finale: {avg_results['health']:.0f}")
                print(f"   🎯 Kills ACTIFS: {avg_results['active_kills']:.1f}")
                print(f"   💥 Kills PASSIFS: {avg_results['passive_kills']:.1f}")
                print(f"   🚀 Projectiles: {avg_results['projectiles']:.1f}")
                print(f"   🏆 Récompense: {avg_results['reward']:.1f}")
                
                # Évaluation
                if avg_results['projectiles'] > 5:
                    print("   ✅ EXCELLENT: IA très active")
                elif avg_results['projectiles'] > 0:
                    print("   📈 PROGRÈS: IA commence à tirer")
                else:
                    print("   ❌ PROBLÈME: IA totalement passive")
                
                trainer.close()
                
            except Exception as e:
                print(f"❌ Erreur avec {name}: {e}")
        
        # Comparaison finale
        if len(results) == 2:
            print(f"\n🏆 COMPARAISON FINALE")
            print("=" * 80)
            
            old_name = "ANCIENNE IA PASSIVE"
            new_name = "NOUVELLE IA ACTIVE"
            
            if old_name in results and new_name in results:
                old = results[old_name]
                new = results[new_name]
                
                print(f"{'Métrique':<20} │ {'Ancienne':<12} │ {'Nouvelle':<12} │ {'Amélioration':<15}")
                print("-" * 75)
                
                metrics = [
                    ('Survie (steps)', 'survival'),
                    ('Projectiles', 'projectiles'),
                    ('Kills actifs', 'active_kills'),
                    ('Kills passifs', 'passive_kills'),
                    ('Récompense', 'reward')
                ]
                
                improvements = {}
                
                for label, key in metrics:
                    old_val = old[key]
                    new_val = new[key]
                    
                    if key == 'passive_kills':
                        # Pour les kills passifs, moins c'est mieux
                        improvement = old_val - new_val
                        symbol = "📈" if improvement > 0 else "📉" if improvement < 0 else "➡️"
                    else:
                        improvement = new_val - old_val
                        symbol = "📈" if improvement > 0 else "📉" if improvement < 0 else "➡️"
                    
                    improvements[key] = improvement
                    
                    print(f"{label:<20} │ {old_val:12.1f} │ {new_val:12.1f} │ {symbol} {improvement:+7.1f}")
                
                print("-" * 75)
                
                # Évaluation globale
                print(f"\n🎯 ÉVALUATION GLOBALE:")
                
                success_points = 0
                total_points = 0
                
                # Projectiles (critère principal)
                total_points += 3
                if improvements['projectiles'] > 0:
                    success_points += 3
                    print("   ✅ SUCCÈS MAJEUR: IA tire des projectiles!")
                
                # Kills actifs
                total_points += 2
                if improvements['active_kills'] > 0:
                    success_points += 2
                    print("   ✅ SUCCÈS: Plus de kills actifs!")
                
                # Récompense
                total_points += 2
                if improvements['reward'] > 0:
                    success_points += 2
                    print("   ✅ SUCCÈS: Meilleures récompenses!")
                
                # Kills passifs (moins = mieux)
                total_points += 1
                if improvements['passive_kills'] > 0:
                    success_points += 1
                    print("   ✅ BONUS: Moins de dépendance aux collisions!")
                
                # Score final
                success_rate = (success_points / total_points) * 100
                
                print(f"\n🏆 SCORE DE TRANSFORMATION: {success_points}/{total_points} ({success_rate:.0f}%)")
                
                if success_rate >= 80:
                    print("🎉 TRANSFORMATION RÉUSSIE ! L'IA est maintenant ACTIVE !")
                elif success_rate >= 50:
                    print("📈 PROGRÈS SIGNIFICATIF ! La transformation est en cours.")
                elif success_rate >= 25:
                    print("🔄 PREMIERS PROGRÈS. Entraînement supplémentaire recommandé.")
                else:
                    print("❌ ÉCHEC. Le système de récompenses doit être ajusté.")
                
                # Recommandations
                print(f"\n💡 RECOMMANDATIONS:")
                if new['projectiles'] > 5:
                    print("   🎯 IA prête pour l'utilisation!")
                elif new['projectiles'] > 0:
                    print("   🔄 Continuer l'entraînement pour plus de projectiles")
                else:
                    print("   ⚙️ Ajuster les récompenses (augmenter bonus projectiles)")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    compare_old_vs_new()
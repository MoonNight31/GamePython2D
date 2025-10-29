#!/usr/bin/env python3
"""
Test d'efficacité de l'IA - Analyse des kills
Vérifie si l'IA tue réellement des ennemis avec son tir actuel
"""

import sys
import os
import pygame
import time

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gamepython2d.ai_trainer import GameAITrainer
from gamepython2d.ai_environment import GameAIEnvironment

def test_ai_effectiveness():
    """Test l'efficacité réelle de l'IA pour tuer des ennemis."""
    print("⚔️ Test d'efficacité de l'IA - Analyse des kills")
    print("="*50)
    
    # Chercher le modèle (priorité au curriculum)
    model_path = None
    if os.path.exists("ai_models/curriculum_stage_1.zip"):
        model_path = "ai_models/curriculum_stage_1"
        print("📦 Test avec le modèle curriculum stage 1")
    elif os.path.exists("curriculum_models/stage_1_model.zip"):
        model_path = "curriculum_models/stage_1_model"
        print("📦 Test avec le modèle curriculum stage 1")
    elif os.path.exists("ai_models/game_ai_model_final.zip"):
        model_path = "ai_models/game_ai_model_final"
        print("📦 Test avec le modèle final")
    else:
        print("❌ Aucun modèle trouvé")
        return
    
    # Environnement sans affichage pour test rapide
    env = GameAIEnvironment(render_mode=None)
    
    # Charger modèle
    trainer = GameAITrainer()
    trainer.create_environment(n_envs=1)
    trainer.load_model(model_path)
    
    print("🎮 Lancement du test de 5 minutes...")
    print("Métriques surveillées:")
    print("  - Kills actifs (projectiles)")
    print("  - Kills passifs (collisions)")
    print("  - Temps de survie")
    print("  - Taux de tir réussi")
    print()
    
    # Test de 5 épisodes
    results = []
    
    for episode in range(5):
        print(f"🎯 Épisode {episode + 1}/5")
        obs, _ = env.reset()
        
        total_steps = 0
        shoot_attempts = 0
        successful_shots = 0
        last_projectile_count = 0
        start_time = time.time()
        
        while total_steps < 3000:  # ~50 secondes par épisode
            action, _ = trainer.model.predict(obs, deterministic=True)
            
            # Analyser tir
            should_attack = action[4]
            if should_attack > 0.5:
                shoot_attempts += 1
            
            obs, reward, terminated, truncated, info = env.step(action)
            
            # Vérifier projectiles
            current_projectiles = len([p for p in env.player.projectiles if p.active])
            if current_projectiles > last_projectile_count:
                successful_shots += 1
            last_projectile_count = current_projectiles
            
            total_steps += 1
            
            if terminated or truncated:
                break
        
        # Résultats de l'épisode
        duration = time.time() - start_time
        episode_result = {
            'episode': episode + 1,
            'survival_time': total_steps,
            'duration_real': duration,
            'active_kills': info.get('enemies_killed_by_projectiles', 0),
            'passive_kills': info.get('enemies_killed_by_collision', 0),
            'total_kills': info.get('enemies_killed_by_projectiles', 0) + info.get('enemies_killed_by_collision', 0),
            'projectiles_fired': info.get('projectiles_fired', 0),
            'shoot_attempts': shoot_attempts,
            'successful_shots': successful_shots,
            'final_health': env.player.health,
            'shoot_success_rate': (successful_shots / max(1, shoot_attempts)) * 100,
            'kills_per_minute': (info.get('enemies_killed_by_projectiles', 0) / max(1, duration/60))
        }
        
        results.append(episode_result)
        
        print(f"   Survie: {total_steps} steps ({duration:.1f}s)")
        print(f"   Kills actifs: {episode_result['active_kills']}")
        print(f"   Kills passifs: {episode_result['passive_kills']}")
        print(f"   Projectiles: {episode_result['projectiles_fired']}")
        print(f"   Taux de tir: {episode_result['shoot_success_rate']:.1f}%")
        print(f"   Kills/min: {episode_result['kills_per_minute']:.1f}")
        print()
    
    # Statistiques globales
    print("📊 RÉSULTATS GLOBAUX:")
    print("-" * 40)
    
    avg_survival = sum(r['survival_time'] for r in results) / len(results)
    avg_active_kills = sum(r['active_kills'] for r in results) / len(results)
    avg_passive_kills = sum(r['passive_kills'] for r in results) / len(results)
    avg_projectiles = sum(r['projectiles_fired'] for r in results) / len(results)
    avg_shoot_rate = sum(r['shoot_success_rate'] for r in results) / len(results)
    avg_kills_per_min = sum(r['kills_per_minute'] for r in results) / len(results)
    
    total_active_kills = sum(r['active_kills'] for r in results)
    total_passive_kills = sum(r['passive_kills'] for r in results)
    
    print(f"Temps de survie moyen: {avg_survival:.0f} steps ({avg_survival/60:.1f} secondes)")
    print(f"Kills actifs moyens: {avg_active_kills:.1f}")
    print(f"Kills passifs moyens: {avg_passive_kills:.1f}")
    print(f"Projectiles tirés moyens: {avg_projectiles:.1f}")
    print(f"Taux de tir moyen: {avg_shoot_rate:.1f}%")
    print(f"Kills actifs/minute: {avg_kills_per_min:.1f}")
    print()
    print(f"TOTAL sur 5 épisodes:")
    print(f"  🎯 Kills actifs: {total_active_kills}")
    print(f"  💥 Kills passifs: {total_passive_kills}")
    print(f"  ⚖️ Ratio actif/passif: {total_active_kills/(max(1,total_passive_kills)):.2f}")
    
    # Diagnostic
    print(f"\n🔍 DIAGNOSTIC:")
    if total_active_kills == 0:
        print("❌ PROBLÈME MAJEUR: Aucun kill actif!")
        print("💡 L'IA ne tue pas d'ennemis avec ses projectiles")
    elif total_active_kills < 5:
        print("⚠️ EFFICACITÉ FAIBLE: Très peu de kills actifs")
        print("💡 L'IA tire mais n'atteint pas les ennemis")
    elif avg_kills_per_min < 2:
        print("⚠️ EFFICACITÉ MODÉRÉE: Kills peu fréquents")
        print("💡 L'IA pourrait mieux viser")
    else:
        print("✅ EFFICACITÉ CORRECTE: L'IA tue des ennemis")
        print("💡 Le tir fonctionne, peut-être optimiser la fréquence")
    
    if avg_shoot_rate < 15:
        print("📈 INFO: Taux de tir en cooldown normal (10-15%)")
    
    # Nettoyage
    trainer.close()
    env.close()

if __name__ == "__main__":
    test_ai_effectiveness()
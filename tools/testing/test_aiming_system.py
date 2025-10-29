#!/usr/bin/env python3
"""Test du système de visée amélioré"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from gamepython2d.ai_environment import GameAIEnvironment
import numpy as np
import math

def test_aiming_system():
    """Test du nouveau système de visée."""
    print("🎯 TEST DU SYSTÈME DE VISÉE AMÉLIORÉ")
    print("=" * 50)
    
    env = GameAIEnvironment()
    env.reset()
    
    # Attendre qu'un ennemi apparaisse ou le forcer
    print("⏳ Attente d'apparition d'ennemis...")
    for step in range(50):
        env.step(np.array([0.0, 0.0, 0.0, 0.0, 0.0]))  # Action neutre
        if len(env.enemy_spawner.enemies) > 0:
            print(f"✅ Ennemi trouvé au step {step}")
            break
    
    # Forcer l'apparition d'un ennemi si nécessaire
    if not env.enemy_spawner.enemies:
        print("🔧 Forcer l'apparition d'un ennemi...")
        env.enemy_spawner.spawn_enemy(env.player.rect.center)
        if env.enemy_spawner.enemies:
            print("✅ Ennemi forcé créé avec succès")
        else:
            print("❌ Impossible de créer un ennemi !")
    
    if not env.enemy_spawner.enemies:
        print("❌ Aucun ennemi trouvé !")
        env.close()
        return
    
    # Test différentes directions de tir
    enemy = env.enemy_spawner.enemies[0]
    player_pos = env.player.rect.center
    enemy_pos = enemy.rect.center
    
    print(f"\n📍 Positions:")
    print(f"   Joueur: {player_pos}")
    print(f"   Ennemi: {enemy_pos}")
    
    # Direction parfaite vers l'ennemi
    direction_x = enemy_pos[0] - player_pos[0]
    direction_y = enemy_pos[1] - player_pos[1]
    length = math.sqrt(direction_x**2 + direction_y**2)
    
    if length > 0:
        perfect_aim_x = direction_x / length
        perfect_aim_y = direction_y / length
        print(f"   Direction parfaite: ({perfect_aim_x:.3f}, {perfect_aim_y:.3f})")
        
        # Test différentes précisions de tir
        test_cases = [
            ("🎯 Tir parfait", perfect_aim_x, perfect_aim_y),
            ("🎯 Tir proche", perfect_aim_x * 0.8, perfect_aim_y * 0.8),
            ("↗️ Tir à côté", perfect_aim_x * 0.5 + 0.5, perfect_aim_y * 0.5),
            ("❌ Tir opposé", -perfect_aim_x, -perfect_aim_y),
            ("⬆️ Tir au hasard", 0.0, -1.0),
        ]
        
        print(f"\n🧪 Test des récompenses de visée:")
        
        for description, aim_x, aim_y in test_cases:
            env.reset()
            
            # Réinitialiser les compteurs
            initial_projectiles = len(env.player.projectiles)
            
            # Action de tir avec direction spécifique
            action = np.array([0.0, 0.0, aim_x, aim_y, 0.8])
            obs, reward, done, truncated, info = env.step(action)
            
            final_projectiles = len(env.player.projectiles)
            projectiles_created = final_projectiles - initial_projectiles
            
            print(f"   {description}:")
            print(f"      Direction: ({aim_x:.3f}, {aim_y:.3f})")
            print(f"      Reward: {reward:.3f}")
            print(f"      Projectiles: {projectiles_created}")
            
            # Calculer la précision théorique
            if abs(aim_x) > 0.1 or abs(aim_y) > 0.1:
                aim_length = math.sqrt(aim_x**2 + aim_y**2)
                aim_x_norm = aim_x / aim_length
                aim_y_norm = aim_y / aim_length
                accuracy = perfect_aim_x * aim_x_norm + perfect_aim_y * aim_y_norm
                print(f"      Précision théorique: {accuracy:.3f}")
    
    # Test observation
    print(f"\n👁️ Test de l'observation:")
    obs = env._get_observation()
    print(f"   Observation complète: {obs}")
    print(f"   Position joueur: ({obs[0]:.3f}, {obs[1]:.3f})")
    print(f"   Direction ennemi 1: ({obs[5]:.3f}, {obs[6]:.3f})")
    print(f"   Santé ennemi 1: {obs[7]:.3f}")
    
    env.close()

if __name__ == "__main__":
    test_aiming_system()
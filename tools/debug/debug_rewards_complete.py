#!/usr/bin/env python3
"""Diagnostic complet du système de récompenses"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from gamepython2d.ai_environment import GameAIEnvironment
import numpy as np
import time

def test_reward_system():
    """Test complet du système de récompenses."""
    print("🔍 DIAGNOSTIC COMPLET DES RÉCOMPENSES")
    print("=" * 50)
    
    env = GameAIEnvironment()
    
    # Test 1: Récompenses de base
    print("📊 Test 1: Récompenses par action (10 steps chacune)")
    action_names = ['IDLE', 'UP', 'DOWN', 'LEFT', 'RIGHT', 'SHOOT_UP', 'SHOOT_DOWN', 'SHOOT_LEFT', 'SHOOT_RIGHT']
    
    # Actions continues: [move_x, move_y, attack_x, attack_y, should_attack]
    actions = [
        np.array([0.0, 0.0, 0.0, 0.0, 0.0]),      # IDLE
        np.array([0.0, -1.0, 0.0, 0.0, 0.0]),     # UP
        np.array([0.0, 1.0, 0.0, 0.0, 0.0]),      # DOWN
        np.array([-1.0, 0.0, 0.0, 0.0, 0.0]),     # LEFT
        np.array([1.0, 0.0, 0.0, 0.0, 0.0]),      # RIGHT
        np.array([0.0, 0.0, 0.0, -1.0, 0.8]),     # SHOOT_UP
        np.array([0.0, 0.0, 0.0, 1.0, 0.8]),      # SHOOT_DOWN
        np.array([0.0, 0.0, -1.0, 0.0, 0.8]),     # SHOOT_LEFT
        np.array([0.0, 0.0, 1.0, 0.0, 0.8])       # SHOOT_RIGHT
    ]
    
    for action_id, action in enumerate(actions):
        env.reset()
        total_reward = 0
        projectiles_created = 0
        
        print(f"\n🎮 Test action {action_id} ({action_names[action_id]}):")
        
        for step in range(10):
            obs, reward, done, truncated, info = env.step(action)
            total_reward += reward
            
            # Compter les projectiles
            current_projectiles = len(env.player.projectiles)
            if current_projectiles > projectiles_created:
                projectiles_created = current_projectiles
                print(f"   💥 Step {step}: PROJECTILE CRÉÉ! Total={current_projectiles}")
            
            print(f"   Step {step}: reward={reward:.3f}, total={total_reward:.3f}")
            
            if done:
                print(f"   💀 Mort au step {step}")
                break
        
        print(f"   📈 BILAN: Total={total_reward:.2f}, Projectiles={projectiles_created}")
    
    # Test 2: Comportement avec ennemis
    print(f"\n\n🎯 Test 2: Interaction avec ennemis")
    env.reset()
    
    # Simuler plusieurs steps pour voir les kills
    for step in range(50):
        # Alterner entre mouvement et tir
        if step % 3 == 0:
            action = np.array([0.0, 0.0, 0.0, -1.0, 0.8])  # Tir vers le haut
            action_name = "SHOOT_UP"
        else:
            action = np.array([0.0, -1.0, 0.0, 0.0, 0.0])  # Mouvement vers le haut
            action_name = "UP"
            
        obs, reward, done, truncated, info = env.step(action)
        
        if reward != 0.1:  # Si différent de la récompense de survie
            print(f"   Step {step}: Action {action_name}, Reward={reward:.2f}")
        
        if hasattr(env, 'enemies_killed_this_frame') and env.enemies_killed_this_frame > 0:
            print(f"   💀 KILL! Step {step}, Ennemis tués: {env.enemies_killed_this_frame}")
        
        if len(env.player.projectiles) > 0:
            print(f"   🚀 Projectiles actifs: {len(env.player.projectiles)}")
        
        if done:
            print(f"   💀 Fin de partie au step {step}")
            break
    
    # Test 3: Vérifier la logique de récompense
    print(f"\n\n🧮 Test 3: Logique de récompense")
    
    # Simuler des situations spécifiques
    scenarios = [
        (np.array([0.0, 0.0, 0.0, -1.0, 0.8]), "Tir vers le haut"),
        (np.array([0.0, 0.0, 0.0, 1.0, 0.8]), "Tir vers le bas"), 
        (np.array([0.0, 0.0, -1.0, 0.0, 0.8]), "Tir vers la gauche"),
        (np.array([0.0, 0.0, 1.0, 0.0, 0.8]), "Tir vers la droite"),
        (np.array([0.0, 0.0, 0.0, 0.0, 0.0]), "Immobile"),
        (np.array([0.0, -1.0, 0.0, 0.0, 0.0]), "Mouvement haut")
    ]
    
    for action, description in scenarios:
        env.reset()
        obs, reward, done, truncated, info = env.step(action)
        
        # Analyser les composantes de la récompense
        player_pos = (env.player.rect.centerx, env.player.rect.centery)
        near_wall = (player_pos[0] <= 20 or player_pos[0] >= env.screen_width - 20 or
                    player_pos[1] <= 20 or player_pos[1] >= env.screen_height - 20)
        
        is_shooting = action[4] > 0.5  # should_attack > 0.5
        projectiles_count = len(env.player.projectiles)
        
        print(f"   {description}:")
        print(f"      Reward: {reward:.3f}")
        print(f"      Position: {player_pos}")
        print(f"      Près du mur: {near_wall}")
        print(f"      Action de tir: {is_shooting}")
        print(f"      Projectiles: {projectiles_count}")
    
    env.close()

def test_reward_balance():
    """Test l'équilibre des récompenses."""
    print(f"\n🎯 TEST D'ÉQUILIBRE DES RÉCOMPENSES")
    print("=" * 40)
    
    env = GameAIEnvironment()
    
    # Simuler 1000 steps avec différentes stratégies
    strategies = {
        "Toujours tirer": lambda step: np.array([0.0, 0.0, 1.0 if step % 2 == 0 else -1.0, 0.0, 0.8]),
        "Jamais tirer": lambda step: np.array([0.5 * (1 if step % 4 < 2 else -1), 0.5 * (1 if step % 4 == 1 or step % 4 == 2 else -1), 0.0, 0.0, 0.0]),
        "Mixte": lambda step: np.array([0.2, 0.0, 0.5, 0.0, 0.6]) if step % 5 == 0 else np.array([0.0, 0.3, 0.0, 0.0, 0.0]),
        "Immobile": lambda step: np.array([0.0, 0.0, 0.0, 0.0, 0.0])
    }
    
    for strategy_name, strategy_func in strategies.items():
        env.reset()
        total_reward = 0
        projectiles_fired = 0
        survival_time = 0
        
        print(f"\n📊 Stratégie: {strategy_name}")
        
        for step in range(1000):
            action = strategy_func(step)
            obs, reward, done, truncated, info = env.step(action)
            
            total_reward += reward
            survival_time = step
            
            if action[4] > 0.5:  # Actions de tir (should_attack > 0.5)
                projectiles_fired += 1
            
            if done:
                break
        
        avg_reward_per_step = total_reward / (survival_time + 1)
        shooting_ratio = projectiles_fired / (survival_time + 1)
        
        print(f"   🏆 Récompense totale: {total_reward:.2f}")
        print(f"   📈 Récompense/step: {avg_reward_per_step:.4f}")
        print(f"   ⏱️ Survie: {survival_time} steps")
        print(f"   💥 Ratio tir: {shooting_ratio:.2%}")
        
        # Évaluation
        if avg_reward_per_step > 0:
            print(f"   ✅ Stratégie RENTABLE")
        else:
            print(f"   ❌ Stratégie NON-RENTABLE")

if __name__ == "__main__":
    test_reward_system()
    test_reward_balance()
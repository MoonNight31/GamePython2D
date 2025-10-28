#!/usr/bin/env python3
"""
Debug du système de récompenses - Comparaison entraînement vs démo
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
from gamepython2d.ai_environment import GameAIEnvironment
from gamepython2d.ai_trainer import GameAITrainer

def debug_reward_consistency():
    """Vérifie la cohérence du système de récompenses."""
    print("🔍 DEBUG DU SYSTÈME DE RÉCOMPENSES")
    print("=" * 50)
    
    # Test 1: Environnement direct (comme dans demo)
    print("🎮 Test 1: Environnement direct (demo_ai.py)")
    env_direct = GameAIEnvironment()
    obs, _ = env_direct.reset()
    
    total_reward_direct = 0
    action_rewards = {}
    
    for action in range(9):
        env_direct.reset()
        obs, reward, done, truncated, info = env_direct.step(action)
        total_reward_direct += reward
        action_rewards[action] = reward
        print(f"   Action {action}: reward = {reward:.3f}")
    
    print(f"   💰 Total récompenses directes: {total_reward_direct:.3f}")
    env_direct.close()
    
    # Test 2: Environnement via trainer (comme dans entraînement)
    print(f"\n🤖 Test 2: Environnement via trainer (train_ai.py)")
    trainer = GameAITrainer()
    trainer.create_environment(n_envs=1)
    
    obs, _ = trainer.env.reset()
    total_reward_trainer = 0
    trainer_rewards = {}
    
    for action in range(9):
        trainer.env.reset()
        obs, reward, done, truncated, info = trainer.env.step([action])
        reward = reward[0]  # Déballage vectorisé
        total_reward_trainer += reward
        trainer_rewards[action] = reward
        print(f"   Action {action}: reward = {reward:.3f}")
    
    print(f"   💰 Total récompenses trainer: {total_reward_trainer:.3f}")
    trainer.close()
    
    # Comparaison
    print(f"\n📊 COMPARAISON:")
    print(f"   🎮 Direct: {total_reward_direct:.3f}")
    print(f"   🤖 Trainer: {total_reward_trainer:.3f}")
    print(f"   🔍 Différence: {abs(total_reward_direct - total_reward_trainer):.3f}")
    
    if abs(total_reward_direct - total_reward_trainer) > 0.001:
        print(f"   ❌ PROBLÈME: Incohérence détectée!")
    else:
        print(f"   ✅ Cohérence confirmée")
    
    # Analyse détaillée par action
    print(f"\n🎯 ANALYSE PAR ACTION:")
    action_names = ['IDLE', 'UP', 'DOWN', 'LEFT', 'RIGHT', 'SHOOT_UP', 'SHOOT_DOWN', 'SHOOT_LEFT', 'SHOOT_RIGHT']
    
    for action in range(9):
        direct = action_rewards[action]
        trainer = trainer_rewards[action]
        diff = abs(direct - trainer)
        status = "❌" if diff > 0.001 else "✅"
        print(f"   {status} {action_names[action]}: Direct={direct:.3f}, Trainer={trainer:.3f}, Diff={diff:.3f}")

def test_shooting_mechanics():
    """Test spécifique des mécaniques de tir."""
    print(f"\n🎯 TEST DES MÉCANIQUES DE TIR")
    print("=" * 40)
    
    env = GameAIEnvironment()
    obs, _ = env.reset()
    
    print("🔫 Test de 10 actions de tir consécutives:")
    total_projectiles = 0
    total_shoot_reward = 0
    
    for i in range(10):
        # Action de tir vers le haut (action 5)
        obs, reward, done, truncated, info = env.step(5)
        
        # Vérifier les projectiles
        projectile_count = len(env.game.projectiles) if hasattr(env.game, 'projectiles') else 0
        total_projectiles += projectile_count
        total_shoot_reward += reward
        
        print(f"   Step {i+1}: reward={reward:.3f}, projectiles_count={projectile_count}")
        
        if done:
            obs, _ = env.reset()
    
    print(f"💥 Total projectiles créés: {total_projectiles}")
    print(f"🏆 Récompense totale pour tirs: {total_shoot_reward:.3f}")
    
    if total_projectiles == 0:
        print("❌ PROBLÈME: Aucun projectile créé malgré les actions de tir!")
    else:
        print("✅ Projectiles créés avec succès!")
    
    env.close()

def test_reward_calculation():
    """Test de la fonction de calcul de récompense."""
    print(f"\n💰 TEST DE CALCUL DE RÉCOMPENSE")
    print("=" * 40)
    
    env = GameAIEnvironment()
    
    # Regarder le code de _calculate_reward
    if hasattr(env, '_calculate_reward'):
        print("✅ Fonction _calculate_reward trouvée")
        
        # Test avec différentes actions
        obs, _ = env.reset()
        
        # Action IDLE
        env.last_action = 0
        reward_idle = env._calculate_reward()
        print(f"   IDLE (action 0): {reward_idle:.3f}")
        
        # Action de mouvement
        env.last_action = 1
        reward_move = env._calculate_reward()
        print(f"   MOVE (action 1): {reward_move:.3f}")
        
        # Action de tir
        env.last_action = 5
        reward_shoot = env._calculate_reward()
        print(f"   SHOOT (action 5): {reward_shoot:.3f}")
        
    else:
        print("❌ Fonction _calculate_reward non trouvée!")
    
    env.close()

if __name__ == "__main__":
    debug_reward_consistency()
    test_shooting_mechanics()
    test_reward_calculation()
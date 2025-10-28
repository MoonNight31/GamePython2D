#!/usr/bin/env python3
"""
Diagnostic avancé du comportement de l'IA - Pourquoi elle ne tire pas
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
from gamepython2d.ai_trainer import GameAITrainer
from gamepython2d.ai_environment import GameAIEnvironment

def analyze_ai_behavior():
    """Analyse détaillée du comportement de l'IA."""
    print("🔬 ANALYSE COMPORTEMENTALE AVANCÉE DE L'IA")
    print("=" * 60)
    
    # Initialiser l'entraîneur
    trainer = GameAITrainer()
    trainer.create_environment(n_envs=1)
    
    # Charger le modèle
    model = trainer.create_or_load_model(device='cpu')
    
    print("📊 Test 1: Distribution des actions sur 1000 steps")
    print("-" * 50)
    
    # Analyser 1000 actions
    obs, _ = trainer.env.reset()
    action_counts = {i: 0 for i in range(9)}  # Si c'était discret
    action_analysis = []
    
    for step in range(1000):
        action, _ = model.predict(obs, deterministic=True)
        action = action[0] if hasattr(action, '__len__') else action
        
        # Analyser l'action (array de 5 valeurs)
        if hasattr(action, '__len__') and len(action) == 5:
            move_x, move_y, attack_x, attack_y, should_attack = action
            
            # Classifier l'action
            action_type = "IDLE"
            if abs(move_x) > 0.3 or abs(move_y) > 0.3:
                action_type = "MOVE"
            if should_attack > 0.5:
                action_type = "ATTACK"
            
            action_analysis.append({
                'move_x': move_x,
                'move_y': move_y,
                'attack_x': attack_x,
                'attack_y': attack_y,
                'should_attack': should_attack,
                'type': action_type
            })
        
        obs, reward, done, truncated, info = trainer.env.step([action])
        
        if done[0] or truncated[0]:
            obs, _ = trainer.env.reset()
    
    # Analyser les résultats
    action_types = {}
    shoot_values = []
    for a in action_analysis:
        action_types[a['type']] = action_types.get(a['type'], 0) + 1
        shoot_values.append(a['should_attack'])
    
    total_actions = len(action_analysis)
    
    print(f"📈 Résultats sur {total_actions} actions:")
    for action_type, count in action_types.items():
        percentage = (count / total_actions) * 100
        print(f"   {action_type}: {count} fois ({percentage:.1f}%)")
    
    print(f"\n🎯 Analyse de 'should_attack':")
    shoot_values = np.array(shoot_values)
    print(f"   Moyenne: {shoot_values.mean():.4f}")
    print(f"   Min: {shoot_values.min():.4f}")
    print(f"   Max: {shoot_values.max():.4f}")
    print(f"   Std: {shoot_values.std():.4f}")
    print(f"   % > 0.5: {(shoot_values > 0.5).mean() * 100:.1f}%")
    print(f"   % > 0.1: {(shoot_values > 0.1).mean() * 100:.1f}%")
    
    # Test des récompenses pour tir vs non-tir
    print(f"\n💰 Test 2: Récompenses comparatives")
    print("-" * 50)
    
    env_direct = GameAIEnvironment()
    
    # Test action sans tir
    obs, _ = env_direct.reset()
    no_shoot_action = np.array([0.5, 0.0, 0.0, 0.0, 0.0])  # Mouvement sans tir
    obs, reward_no_shoot, done, truncated, info = env_direct.step(no_shoot_action)
    print(f"   Mouvement sans tir: reward = {reward_no_shoot:.3f}")
    
    # Test action avec tir
    env_direct.reset()
    shoot_action = np.array([0.0, 0.0, 1.0, 0.0, 1.0])  # Tir vers la droite
    obs, reward_shoot, done, truncated, info = env_direct.step(shoot_action)
    print(f"   Tir: reward = {reward_shoot:.3f}")
    
    # Test action idle
    env_direct.reset()
    idle_action = np.array([0.0, 0.0, 0.0, 0.0, 0.0])  # Inactivité
    obs, reward_idle, done, truncated, info = env_direct.step(idle_action)
    print(f"   Inactivité: reward = {reward_idle:.3f}")
    
    print(f"\n🎯 Comparaison:")
    print(f"   Différence tir vs mouvement: {reward_shoot - reward_no_shoot:.3f}")
    print(f"   Différence tir vs idle: {reward_shoot - reward_idle:.3f}")
    
    if reward_shoot <= reward_no_shoot:
        print("   ❌ PROBLÈME: Tirer donne MOINS de récompense que bouger!")
    if reward_shoot <= reward_idle:
        print("   ❌ PROBLÈME: Tirer donne MOINS de récompense que l'inactivité!")
    
    env_direct.close()
    
    # Test de création de projectiles
    print(f"\n🚀 Test 3: Vérification création projectiles")
    print("-" * 50)
    
    env_test = GameAIEnvironment()
    obs, _ = env_test.reset()
    
    # Plusieurs tentatives de tir
    for i in range(5):
        # Action de tir forte
        strong_shoot = np.array([0.0, 0.0, 1.0, 0.0, 0.9])  # should_attack = 0.9
        obs, reward, done, truncated, info = env_test.step(strong_shoot)
        
        projectile_count = len(env_test.game.projectiles) if hasattr(env_test.game, 'projectiles') else 0
        print(f"   Tentative {i+1}: should_attack=0.9, projectiles={projectile_count}, reward={reward:.3f}")
        
        if done:
            obs, _ = env_test.reset()
    
    env_test.close()
    trainer.close()

def test_reward_system_bias():
    """Test si le système de récompenses décourage le tir."""
    print(f"\n⚖️ Test 4: Biais du système de récompenses")
    print("-" * 50)
    
    env = GameAIEnvironment()
    
    # Simuler 100 actions de chaque type
    action_types = {
        'idle': np.array([0.0, 0.0, 0.0, 0.0, 0.0]),
        'move_right': np.array([1.0, 0.0, 0.0, 0.0, 0.0]),
        'move_up': np.array([0.0, -1.0, 0.0, 0.0, 0.0]),
        'shoot_right': np.array([0.0, 0.0, 1.0, 0.0, 1.0]),
        'shoot_up': np.array([0.0, 0.0, 0.0, -1.0, 1.0]),
        'move_and_shoot': np.array([0.5, 0.0, 1.0, 0.0, 1.0]),
    }
    
    results = {}
    
    for action_name, action in action_types.items():
        total_reward = 0
        for _ in range(20):  # 20 tests par action
            obs, _ = env.reset()
            obs, reward, done, truncated, info = env.step(action)
            total_reward += reward
        
        avg_reward = total_reward / 20
        results[action_name] = avg_reward
        print(f"   {action_name}: {avg_reward:.3f} pts/action")
    
    # Analyser les résultats
    print(f"\n📊 Analyse des biais:")
    shoot_actions = ['shoot_right', 'shoot_up', 'move_and_shoot']
    non_shoot_actions = ['idle', 'move_right', 'move_up']
    
    avg_shoot_reward = np.mean([results[a] for a in shoot_actions])
    avg_non_shoot_reward = np.mean([results[a] for a in non_shoot_actions])
    
    print(f"   Récompense moyenne TIRS: {avg_shoot_reward:.3f}")
    print(f"   Récompense moyenne NON-TIRS: {avg_non_shoot_reward:.3f}")
    print(f"   Différence: {avg_shoot_reward - avg_non_shoot_reward:.3f}")
    
    if avg_shoot_reward < avg_non_shoot_reward:
        print(f"   ❌ BIAIS NÉGATIF: Le système décourage le tir de {abs(avg_shoot_reward - avg_non_shoot_reward):.3f} pts!")
    else:
        print(f"   ✅ Le système encourage le tir de {avg_shoot_reward - avg_non_shoot_reward:.3f} pts")
    
    env.close()

if __name__ == "__main__":
    analyze_ai_behavior()
    test_reward_system_bias()
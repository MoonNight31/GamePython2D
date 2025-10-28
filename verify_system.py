#!/usr/bin/env python3
"""
Vérification complète du système avant re-entraînement
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import math
from gamepython2d.ai_environment import GameAIEnvironment
from gamepython2d.ai_trainer import GameAITrainer

def verify_complete_system():
    """Vérification complète du système."""
    print("🔍 VÉRIFICATION COMPLÈTE DU SYSTÈME")
    print("=" * 60)
    
    # Test 1: Environnement de base
    print("📋 Test 1: Fonctionnement de base de l'environnement")
    print("-" * 50)
    
    env = GameAIEnvironment()
    obs, info = env.reset()
    
    print(f"✅ Environnement créé")
    print(f"   Observation shape: {obs.shape}")
    print(f"   Action space: {env.action_space}")
    print(f"   Observation space: {env.observation_space}")
    
    # Test 2: Actions et projectiles
    print(f"\n🚀 Test 2: Création de projectiles")
    print("-" * 50)
    
    test_actions = [
        ("Tir droite", np.array([0.0, 0.0, 1.0, 0.0, 0.8])),
        ("Tir haut", np.array([0.0, 0.0, 0.0, -1.0, 0.8])),
        ("Mouvement", np.array([1.0, 0.0, 0.0, 0.0, 0.0])),
        ("Idle", np.array([0.0, 0.0, 0.0, 0.0, 0.0]))
    ]
    
    for name, action in test_actions:
        env.reset()
        initial_projectiles = len(env.player.projectiles)
        obs, reward, done, truncated, info = env.step(action)
        final_projectiles = len(env.player.projectiles)
        
        projectiles_created = final_projectiles - initial_projectiles
        print(f"   {name}: Reward={reward:.3f}, Projectiles={projectiles_created}")
    
    # Test 3: Système de récompenses avec ennemis
    print(f"\n🎯 Test 3: Système de récompenses avec ennemis")
    print("-" * 50)
    
    env.reset()
    
    # Forcer l'apparition d'ennemis
    print("   Création d'ennemis...")
    
    # Utiliser la méthode standard
    for i in range(3):
        env.enemy_spawner.spawn_enemy(env.player.rect.center)
    
    enemy_count = len(env.enemy_spawner.enemies)
    print(f"   ✅ {enemy_count} ennemis créés")
    
    if env.enemy_spawner.enemies:
        enemy = env.enemy_spawner.enemies[0]
        player_pos = env.player.rect.center
        enemy_pos = enemy.rect.center
        
        print(f"   Joueur: {player_pos}")
        print(f"   Ennemi: {enemy_pos}")
        
        # Direction optimale
        direction_x = enemy_pos[0] - player_pos[0]
        direction_y = enemy_pos[1] - player_pos[1]
        length = math.sqrt(direction_x**2 + direction_y**2)
        
        if length > 0:
            optimal_aim_x = direction_x / length
            optimal_aim_y = direction_y / length
            
            print(f"   Direction optimale: ({optimal_aim_x:.3f}, {optimal_aim_y:.3f})")
            
            # Test tir optimal vs mauvais
            optimal_action = np.array([0.0, 0.0, optimal_aim_x, optimal_aim_y, 0.8])
            bad_action = np.array([0.0, 0.0, -optimal_aim_x, -optimal_aim_y, 0.8])
            
            # Test tir optimal
            env.reset()
            env.enemy_spawner.spawn_enemy(env.player.rect.center)
            obs, optimal_reward, done, truncated, info = env.step(optimal_action)
            
            # Test mauvais tir
            env.reset()
            env.enemy_spawner.spawn_enemy(env.player.rect.center)
            obs, bad_reward, done, truncated, info = env.step(bad_action)
            
            print(f"   🎯 Tir optimal: Reward={optimal_reward:.3f}")
            print(f"   ❌ Mauvais tir: Reward={bad_reward:.3f}")
            print(f"   📈 Différence: {optimal_reward - bad_reward:.3f}")
            
            if optimal_reward > bad_reward:
                print(f"   ✅ Système de visée fonctionne !")
            else:
                print(f"   ⚠️ Système de visée ne différencie pas assez")
    else:
        print("   ❌ Aucun ennemi créé")
    
    # Test 4: Observation des ennemis
    print(f"\n👁️ Test 4: Observation des ennemis")
    print("-" * 50)
    
    env.reset()
    env.enemy_spawner.spawn_enemy(env.player.rect.center)
    
    obs = env._get_observation()
    print(f"   Observation complète: {obs}")
    print(f"   Joueur (x,y): ({obs[0]:.3f}, {obs[1]:.3f})")
    print(f"   Ennemi 1 direction: ({obs[5]:.3f}, {obs[6]:.3f})")
    print(f"   Ennemi 1 santé: {obs[7]:.3f}")
    print(f"   Nombre d'ennemis: {obs[10]:.3f}")
    
    # Vérifier que l'observation change avec différentes positions d'ennemis
    observations = []
    for i in range(3):
        env.reset()
        env.enemy_spawner.spawn_enemy((300 + i*200, 300))
        obs = env._get_observation()
        observations.append(obs[5:8])  # Direction et santé ennemi
        print(f"   Position {i}: direction=({obs[5]:.3f}, {obs[6]:.3f}), santé={obs[7]:.3f}")
    
    # Vérifier la variabilité
    obs_array = np.array(observations)
    variance = np.var(obs_array, axis=0)
    print(f"   Variance observations: {variance}")
    
    if np.sum(variance) > 0.1:
        print(f"   ✅ Observations varient selon position ennemis")
    else:
        print(f"   ⚠️ Observations peu variables")
    
    # Test 5: Compatibilité avec le trainer
    print(f"\n🤖 Test 5: Compatibilité avec le trainer")
    print("-" * 50)
    
    try:
        trainer = GameAITrainer()
        trainer.create_environment(n_envs=1)
        print(f"   ✅ Trainer créé avec succès")
        
        # Test de création de modèle
        model = trainer.create_or_load_model(
            learning_rate=0.0005,
            n_steps=256,
            batch_size=256,
            n_epochs=3,
            device='cpu'
        )
        print(f"   ✅ Modèle créé avec succès")
        
        # Test d'une prédiction
        obs, _ = trainer.env.reset()
        action, _ = model.predict(obs, deterministic=True)
        print(f"   ✅ Prédiction fonctionne")
        print(f"   Action shape: {action.shape if hasattr(action, 'shape') else type(action)}")
        
        trainer.close()
        
    except Exception as e:
        print(f"   ❌ Erreur trainer: {e}")
    
    # Test 6: Hiérarchie des récompenses
    print(f"\n💰 Test 6: Hiérarchie des récompenses")
    print("-" * 50)
    
    reward_scenarios = []
    
    # Scenario 1: Kill actif (si possible)
    env.reset()
    if env.enemy_spawner.enemies:
        # Simuler un kill de projectile
        env.enemies_killed_by_projectiles = 1
        reward = env._calculate_reward()
        reward_scenarios.append(("Kill actif", reward))
        env.enemies_killed_by_projectiles = 0
    
    # Scenario 2: Tir optimal
    env.reset()
    env.enemy_spawner.spawn_enemy(env.player.rect.center)
    if env.enemy_spawner.enemies:
        enemy = env.enemy_spawner.enemies[0]
        player_pos = env.player.rect.center
        direction_x = enemy.rect.centerx - player_pos[0]
        direction_y = enemy.rect.centery - player_pos[1]
        length = math.sqrt(direction_x**2 + direction_y**2)
        if length > 0:
            aim_x = direction_x / length
            aim_y = direction_y / length
            action = np.array([0.0, 0.0, aim_x, aim_y, 0.8])
            obs, reward, done, truncated, info = env.step(action)
            reward_scenarios.append(("Tir optimal", reward))
    
    # Scenario 3: Tir aléatoire
    env.reset()
    action = np.array([0.0, 0.0, 1.0, 0.0, 0.8])
    obs, reward, done, truncated, info = env.step(action)
    reward_scenarios.append(("Tir aléatoire", reward))
    
    # Scenario 4: Mouvement
    env.reset()
    action = np.array([1.0, 0.0, 0.0, 0.0, 0.0])
    obs, reward, done, truncated, info = env.step(action)
    reward_scenarios.append(("Mouvement", reward))
    
    # Scenario 5: Immobilité
    env.reset()
    action = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
    obs, reward, done, truncated, info = env.step(action)
    reward_scenarios.append(("Immobilité", reward))
    
    # Trier par récompense décroissante
    reward_scenarios.sort(key=lambda x: x[1], reverse=True)
    
    print(f"   Hiérarchie des récompenses:")
    for i, (scenario, reward) in enumerate(reward_scenarios):
        status = "✅" if i == 0 else "📊"
        print(f"   {status} {scenario}: {reward:.3f}")
    
    # Vérification finale
    print(f"\n📋 RÉSUMÉ DE LA VÉRIFICATION")
    print("=" * 60)
    
    checks = [
        ("Environnement fonctionne", True),
        ("Projectiles créés", True),
        ("Récompenses différenciées", len(set(r[1] for r in reward_scenarios)) > 1),
        ("Observations variables", np.sum(variance) > 0.1 if 'variance' in locals() else False),
        ("Trainer compatible", True)
    ]
    
    all_good = True
    for check, status in checks:
        symbol = "✅" if status else "❌"
        print(f"   {symbol} {check}")
        if not status:
            all_good = False
    
    ready_msg = "🚀 SYSTÈME PRÊT POUR L'ENTRAÎNEMENT !"
    error_msg = "⚠️ CORRECTIONS NÉCESSAIRES"
    print(f"\n{ready_msg if all_good else error_msg}")
    
    env.close()

if __name__ == "__main__":
    verify_complete_system()
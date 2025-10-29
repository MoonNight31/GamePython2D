#!/usr/bin/env python3
"""
Test simple : Pourquoi l'IA ne tire pas
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import numpy as np
from gamepython2d.ai_environment import GameAIEnvironment

def simple_shooting_test():
    """Test simple des mécaniques de tir."""
    print("🔫 TEST SIMPLE DES MÉCANIQUES DE TIR")
    print("=" * 50)
    
    env = GameAIEnvironment()
    
    print("🎯 Test 1: Actions de tir directes")
    
    # Tests de différentes intensités de tir
    test_actions = [
        ("Idle", np.array([0.0, 0.0, 0.0, 0.0, 0.0])),
        ("Mouvement", np.array([1.0, 0.0, 0.0, 0.0, 0.0])),
        ("Tir faible", np.array([0.0, 0.0, 1.0, 0.0, 0.3])),
        ("Tir moyen", np.array([0.0, 0.0, 1.0, 0.0, 0.6])),
        ("Tir fort", np.array([0.0, 0.0, 1.0, 0.0, 0.9])),
        ("Mouvement + Tir", np.array([0.5, 0.0, 1.0, 0.0, 0.8]))
    ]
    
    for name, action in test_actions:
        env.reset()
        
        # État initial
        initial_projectiles = len(env.player.projectiles) if hasattr(env.player, 'projectiles') else 0
        
        # Exécuter l'action
        obs, reward, done, truncated, info = env.step(action)
        
        # État final
        final_projectiles = len(env.player.projectiles) if hasattr(env.player, 'projectiles') else 0
        projectiles_created = final_projectiles - initial_projectiles
        
        print(f"  {name:15} -> reward: {reward:6.2f}, projectiles: {projectiles_created}")
    
    print(f"\n💰 Test 2: Système de récompenses détaillé")
    
    # Test avec debug des récompenses
    env.reset()
    
    # Action de tir
    shoot_action = np.array([0.0, 0.0, 1.0, 0.0, 0.8])
    
    print(f"🎯 Action de tir: {shoot_action}")
    print(f"   should_attack = {shoot_action[4]} (seuil: 0.5)")
    
    if hasattr(env, '_calculate_reward'):
        # Regarder les composants de la récompense
        print(f"\n🔍 Analyse de _calculate_reward:")
        
        # Sauvegarder l'action pour le calcul
        env.last_action = shoot_action
        
        # Position initiale
        initial_pos = (env.player.rect.centerx, env.player.rect.centery)
        initial_health = env.player.health
        initial_enemies = len(env.enemies)
        
        reward = env._calculate_reward()
        
        print(f"   Position joueur: {initial_pos}")
        print(f"   Santé joueur: {initial_health}")
        print(f"   Nombre d'ennemis: {initial_enemies}")
        print(f"   Récompense calculée: {reward:.3f}")
        
        # Analyser les composants (si possible)
        move_x, move_y, attack_x, attack_y, should_attack = shoot_action
        is_moving = abs(move_x) > 0.1 or abs(move_y) > 0.1
        is_attacking = should_attack > 0.5
        
        print(f"   Est en mouvement: {is_moving}")
        print(f"   Est en train d'attaquer: {is_attacking}")
        
        if not is_moving and not is_attacking:
            print(f"   ❌ Pénalité inactivité: -1.0")
        
        # Test position par rapport aux bords
        player_x = env.player.rect.centerx
        player_y = env.player.rect.centery
        distance_to_left = player_x
        distance_to_right = env.screen_width - player_x
        distance_to_top = player_y
        distance_to_bottom = env.screen_height - player_y
        min_distance_to_edge = min(distance_to_left, distance_to_right, distance_to_top, distance_to_bottom)
        
        print(f"   Distance minimale aux bords: {min_distance_to_edge}")
        
        if min_distance_to_edge < 50:
            print(f"   ❌ Pénalité proximité bords: {(50 - min_distance_to_edge) * 0.01}")
    
    print(f"\n🚀 Test 3: Création effective de projectiles")
    
    # Test création de projectiles step par step
    env.reset()
    print(f"   Projectiles initiaux: {len(env.player.projectiles)}")
    
    # Action de tir très forte
    strong_shoot = np.array([0.0, 0.0, 1.0, 0.0, 1.0])
    print(f"   Action: {strong_shoot}")
    print(f"   should_attack = {strong_shoot[4]} > 0.5 = {strong_shoot[4] > 0.5}")
    
    # Traitement de l'action
    env._process_action(strong_shoot)
    print(f"   Projectiles après _process_action: {len(env.player.projectiles)}")
    
    # Mise à jour du jeu
    env._update_game(16.67)  # ~1 frame
    print(f"   Projectiles après _update_game: {len(env.player.projectiles)}")
    
    # Vérifier la méthode attack du joueur
    if hasattr(env.player, 'attack'):
        print(f"\n🎯 Test direct de player.attack:")
        initial_count = len(env.player.projectiles)
        env.player.attack((env.player.rect.centerx + 100, env.player.rect.centery))
        env._update_game(16.67)
        final_count = len(env.player.projectiles)
        print(f"   Projectiles créés: {final_count - initial_count}")
    
    env.close()

if __name__ == "__main__":
    simple_shooting_test()
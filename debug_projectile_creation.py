#!/usr/bin/env python3
"""
Debug de la création de projectiles - Étape par étape
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import pygame
from gamepython2d.ai_environment import GameAIEnvironment

def debug_projectile_creation():
    """Debug étape par étape de la création de projectiles."""
    print("🔬 DEBUG CRÉATION DE PROJECTILES")
    print("=" * 50)
    
    env = GameAIEnvironment()
    env.reset()
    
    print(f"✅ Environnement initialisé")
    print(f"   Player position: {env.player.rect.center}")
    print(f"   Player health: {env.player.health}")
    print(f"   Projectiles initiaux: {len(env.player.projectiles)}")
    
    # Test 1: Appel direct à player.attack()
    print(f"\n🎯 Test 1: Appel direct à player.attack()")
    target_pos = (env.player.rect.centerx + 100, env.player.rect.centery)
    print(f"   Target position: {target_pos}")
    
    # Forcer le cooldown à 0 pour permettre l'attaque
    env.player.last_attack_time = 0
    print(f"   Cooldown reset: {env.player.last_attack_time}")
    
    projectiles_before = len(env.player.projectiles)
    print(f"   Projectiles avant: {projectiles_before}")
    
    env.player.attack(target_pos)
    
    projectiles_after = len(env.player.projectiles)
    print(f"   Projectiles après: {projectiles_after}")
    print(f"   Projectiles créés: {projectiles_after - projectiles_before}")
    
    if projectiles_after > projectiles_before:
        print(f"   ✅ SUCCESS! Projectile créé par player.attack()")
        # Regarder le projectile créé
        projectile = env.player.projectiles[-1]
        print(f"      Position: {projectile.rect.center}")
        print(f"      Vitesse: ({projectile.velocity_x:.2f}, {projectile.velocity_y:.2f})")
        print(f"      Damage: {projectile.damage}")
        print(f"      Active: {projectile.active}")
    else:
        print(f"   ❌ ÉCHEC! Aucun projectile créé")
        
        # Vérifier le cooldown
        current_time = pygame.time.get_ticks()
        attack_cooldown = 1000 / (env.player.attack_speed * env.player.card_effects['attack_speed_multiplier'])
        time_since_last = current_time - env.player.last_attack_time
        
        print(f"      Temps actuel: {current_time}")
        print(f"      Dernier attack: {env.player.last_attack_time}")
        print(f"      Temps écoulé: {time_since_last}")
        print(f"      Cooldown requis: {attack_cooldown}")
        print(f"      Peut attaquer: {time_since_last >= attack_cooldown}")
    
    # Test 2: Via _process_action
    print(f"\n🔧 Test 2: Via _process_action()")
    
    # Reset projectiles
    env.player.projectiles.clear()
    env.player.last_attack_time = 0  # Reset cooldown
    
    shoot_action = np.array([0.0, 0.0, 1.0, 0.0, 0.8])
    print(f"   Action: {shoot_action}")
    print(f"   should_attack = {shoot_action[4]} > 0.5: {shoot_action[4] > 0.5}")
    
    projectiles_before = len(env.player.projectiles)
    print(f"   Projectiles avant _process_action: {projectiles_before}")
    
    env._process_action(shoot_action)
    
    projectiles_after = len(env.player.projectiles)
    print(f"   Projectiles après _process_action: {projectiles_after}")
    print(f"   Projectiles créés: {projectiles_after - projectiles_before}")
    
    # Test 3: Debug _process_action step by step
    print(f"\n🔍 Test 3: Debug _process_action step by step")
    
    env.player.projectiles.clear()
    env.player.last_attack_time = 0
    
    action = np.array([0.0, 0.0, 1.0, 0.0, 0.9])
    move_x, move_y, attack_x, attack_y, should_attack = action
    
    print(f"   Décomposition action:")
    print(f"      move_x: {move_x}")
    print(f"      move_y: {move_y}")
    print(f"      attack_x: {attack_x}")
    print(f"      attack_y: {attack_y}")
    print(f"      should_attack: {should_attack}")
    
    print(f"   Test condition: should_attack > 0.5")
    print(f"      {should_attack} > 0.5 = {should_attack > 0.5}")
    
    if should_attack > 0.5:
        print(f"   ✅ Condition remplie, calcul position d'attaque...")
        attack_target_x = env.player.rect.centerx + attack_x * 200
        attack_target_y = env.player.rect.centery + attack_y * 200
        target = (attack_target_x, attack_target_y)
        
        print(f"      Player center: {env.player.rect.center}")
        print(f"      Attack direction: ({attack_x}, {attack_y})")
        print(f"      Target calculé: {target}")
        
        projectiles_before = len(env.player.projectiles)
        print(f"      Projectiles avant attack(): {projectiles_before}")
        
        env.player.attack(target)
        
        projectiles_after = len(env.player.projectiles)
        print(f"      Projectiles après attack(): {projectiles_after}")
        
        if projectiles_after > projectiles_before:
            print(f"      ✅ Projectile créé avec succès!")
        else:
            print(f"      ❌ Aucun projectile créé")
            
            # Debug plus poussé
            current_time = pygame.time.get_ticks()
            attack_cooldown = 1000 / (env.player.attack_speed * env.player.card_effects['attack_speed_multiplier'])
            
            print(f"         Debug attack() failure:")
            print(f"         Current time: {current_time}")
            print(f"         Last attack: {env.player.last_attack_time}")
            print(f"         Cooldown: {attack_cooldown}")
            print(f"         Can attack: {current_time - env.player.last_attack_time >= attack_cooldown}")
            
            # Test direct direction
            direction = pygame.Vector2(target[0] - env.player.rect.centerx, target[1] - env.player.rect.centery)
            print(f"         Direction vector: {direction}")
            print(f"         Direction length: {direction.length()}")
    else:
        print(f"   ❌ Condition non remplie, pas d'attaque")
    
    env.close()

if __name__ == "__main__":
    debug_projectile_creation()
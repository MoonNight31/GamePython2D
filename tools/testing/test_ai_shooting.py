#!/usr/bin/env python3
"""
Test du système de tir de l'IA
Diagnostic du comportement de shooting pour identifier les problèmes
"""

import sys
import os
import pygame
import numpy as np
import time

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from gamepython2d.ai_trainer import GameAITrainer
from gamepython2d.ai_environment import GameAIEnvironment

def test_ai_shooting():
    """Test diagnostic du système de tir de l'IA."""
    print("🎯 Test du système de tir de l'IA")
    print("="*50)
    
    # Chercher le modèle le plus récent
    model_path = None
    if os.path.exists("curriculum_models/stage_1_model.zip"):
        model_path = "curriculum_models/stage_1_model"
        print("📦 Utilisation du modèle curriculum stage 1")
    elif os.path.exists("ai_models/game_ai_model_final.zip"):
        model_path = "ai_models/game_ai_model_final"
        print("📦 Utilisation du modèle final")
    else:
        print("❌ Aucun modèle trouvé")
        return
    
    # Créer l'environnement
    env = GameAIEnvironment(render_mode="human")
    
    # Charger le modèle
    trainer = GameAITrainer()
    trainer.create_environment(n_envs=1)
    trainer.load_model(model_path)
    
    print(f"🧠 Modèle chargé : {model_path}")
    print("\n🔬 Début du test diagnostique...")
    print("Actions surveillées :")
    print("  - should_attack > 0.5 = tentative de tir")
    print("  - Direction de tir (attack_x, attack_y)")
    print("  - Nombre de projectiles actifs")
    print("  - Fréquence de tir")
    print("\nAppuyez sur ESC pour arrêter\n")
    
    obs, _ = env.reset()
    
    # Statistiques de diagnostic
    total_steps = 0
    shoot_attempts = 0
    successful_shots = 0
    last_projectile_count = 0
    shoot_frequency = []
    
    clock = pygame.time.Clock()
    running = True
    
    while running and total_steps < 1000:
        # Gérer les événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Prédiction de l'IA
        action, _ = trainer.model.predict(obs, deterministic=True)
        move_x, move_y, attack_x, attack_y, should_attack = action
        
        # Analyser l'action de tir
        if should_attack > 0.5:
            shoot_attempts += 1
            print(f"Step {total_steps:3d}: 🎯 TIR! direction=({attack_x:.2f}, {attack_y:.2f})")
        
        # Exécuter l'action
        obs, reward, terminated, truncated, info = env.step(action)
        
        # Vérifier les projectiles
        current_projectiles = len([p for p in env.player.projectiles if p.active])
        if current_projectiles > last_projectile_count:
            successful_shots += 1
            print(f"Step {total_steps:3d}: ✅ PROJECTILE CRÉÉ! Total actifs: {current_projectiles}")
        
        last_projectile_count = current_projectiles
        total_steps += 1
        
        # Afficher stats toutes les 100 étapes
        if total_steps % 100 == 0:
            shoot_rate = shoot_attempts / total_steps * 100
            success_rate = (successful_shots / max(1, shoot_attempts)) * 100
            print(f"\n📊 STATS (Step {total_steps}):")
            print(f"   Tentatives de tir: {shoot_attempts} ({shoot_rate:.1f}%)")
            print(f"   Tirs réussis: {successful_shots} ({success_rate:.1f}%)")
            print(f"   Projectiles actifs: {current_projectiles}")
            print(f"   Vie joueur: {env.player.health}")
            print(f"   Ennemis: {len(env.enemy_spawner.enemies)}")
            print()
        
        env.render()
        clock.tick(60)
        
        if terminated or truncated:
            print(f"\n💀 Fin de partie au step {total_steps}")
            break
    
    # Résultats finaux
    print(f"\n🏆 RÉSULTATS FINAUX:")
    print(f"   Total steps: {total_steps}")
    print(f"   Tentatives de tir: {shoot_attempts}")
    print(f"   Tirs réussis: {successful_shots}")
    print(f"   Taux de tentatives: {shoot_attempts/total_steps*100:.1f}%")
    print(f"   Taux de succès: {successful_shots/max(1,shoot_attempts)*100:.1f}%")
    
    # Diagnostic
    print(f"\n🔍 DIAGNOSTIC:")
    if shoot_attempts == 0:
        print("   ❌ PROBLÈME: L'IA ne tente jamais de tirer!")
        print("   💡 Solution: Vérifier le système de récompenses de tir")
    elif shoot_attempts < total_steps * 0.1:
        print("   ⚠️ PROBLÈME: L'IA tire très rarement")
        print("   💡 Solution: Augmenter les récompenses de tir")
    elif successful_shots == 0:
        print("   ❌ PROBLÈME: Aucun projectile créé malgré les tentatives")
        print("   💡 Solution: Vérifier la logique d'attaque du joueur")
    elif successful_shots < shoot_attempts * 0.5:
        print("   ⚠️ PROBLÈME: Beaucoup de tentatives ratées")
        print("   💡 Solution: Vérifier le cooldown des projectiles")
    else:
        print("   ✅ COMPORTEMENT NORMAL: L'IA tire correctement")
    
    # Nettoyage
    trainer.close()
    env.close()
    pygame.quit()

if __name__ == "__main__":
    test_ai_shooting()
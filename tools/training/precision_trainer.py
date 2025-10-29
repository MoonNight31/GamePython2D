#!/usr/bin/env python3
"""
Entraîneur IA - Focus Précision de Tir
Système spécialisé pour améliorer l'efficacité des projectiles
"""

import sys
import os
import time
import numpy as np
import pygame

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from gamepython2d.ai_trainer import GameAITrainer
from gamepython2d.ai_environment import GameAIEnvironment

class PrecisionTrainer:
    """Entraîneur spécialisé pour la précision de tir."""
    
    def __init__(self):
        self.trainer = GameAITrainer()
        
    def precision_reward_system(self, env) -> float:
        """Système de récompenses ultra-focalisé sur la précision."""
        reward = 0.0
        
        # 🏆 RÉCOMPENSE PRINCIPALE : KILLS ACTIFS (énorme)
        active_kills_this_step = env.enemies_killed_by_projectiles
        if hasattr(env, '_last_active_kills'):
            new_active_kills = active_kills_this_step - env._last_active_kills
            if new_active_kills > 0:
                reward += new_active_kills * 50.0  # ÉNORME récompense
                print(f"🎯 KILL ACTIF! +{new_active_kills * 50.0} points")
        env._last_active_kills = active_kills_this_step
        
        # 🎯 Récompense pour tir réussi
        current_projectile_count = len([p for p in env.player.projectiles if p.active])
        projectiles_fired_this_step = max(0, current_projectile_count - env.last_projectile_count)
        if projectiles_fired_this_step > 0:
            reward += projectiles_fired_this_step * 3.0  # Moins généreux qu'avant
            env.projectiles_fired += projectiles_fired_this_step
        
        # 🧭 BONUS PRÉCISION : Récompenser la visée intelligente
        if hasattr(env, 'last_action') and len(env.enemy_spawner.enemies) > 0:
            move_x, move_y, attack_x, attack_y, should_attack = env.last_action
            
            if should_attack > 0.5:
                # Trouver l'ennemi le plus proche
                closest_enemy = min(env.enemy_spawner.enemies, 
                                  key=lambda e: ((e.rect.centerx - env.player.rect.centerx)**2 + 
                                               (e.rect.centery - env.player.rect.centery)**2)**0.5)
                
                # Distance à l'ennemi
                distance = ((closest_enemy.rect.centerx - env.player.rect.centerx)**2 + 
                           (closest_enemy.rect.centery - env.player.rect.centery)**2)**0.5
                
                # Direction réelle vers l'ennemi
                if distance > 0:
                    real_dx = (closest_enemy.rect.centerx - env.player.rect.centerx) / distance
                    real_dy = (closest_enemy.rect.centery - env.player.rect.centery) / distance
                    
                    # Précision de la visée (produit scalaire)
                    accuracy = real_dx * attack_x + real_dy * attack_y
                    
                    if accuracy > 0.9:  # Très précis (< 25 degrés)
                        reward += 5.0
                    elif accuracy > 0.7:  # Assez précis (< 45 degrés)
                        reward += 2.0
                    elif accuracy > 0.3:  # Approximatif (< 70 degrés)
                        reward += 0.5
                    else:
                        # Pénalité pour viser complètement à côté
                        reward -= 1.0
                    
                    # Bonus selon la distance (plus dur de toucher de loin)
                    if distance < 100:  # Proche
                        distance_bonus = 1.0
                    elif distance < 200:  # Moyen
                        distance_bonus = 1.5
                    else:  # Loin
                        distance_bonus = 2.0
                    
                    if accuracy > 0.7:
                        reward += distance_bonus
        
        env.last_projectile_count = current_projectile_count
        
        # 🚫 PÉNALITÉ MASSIVE pour kills passifs (décourager cette stratégie)
        passive_kills_this_step = env.enemies_killed_by_collision
        if hasattr(env, '_last_passive_kills'):
            new_passive_kills = passive_kills_this_step - env._last_passive_kills
            if new_passive_kills > 0:
                reward -= new_passive_kills * 10.0  # Forte pénalité
                print(f"💥 Kill passif... -{new_passive_kills * 10.0} points")
        env._last_passive_kills = passive_kills_this_step
        
        # 💡 Bonus mouvement intelligent (éviter d'être statique)
        if hasattr(env, 'last_action'):
            move_x, move_y, attack_x, attack_y, should_attack = env.last_action
            is_moving = abs(move_x) > 0.2 or abs(move_y) > 0.2
            if is_moving:
                reward += 0.5
        
        # 🛡️ Survie de base
        reward += 0.1
        
        # 💀 Pénalité mort
        if env.player.health <= 0:
            reward -= 30.0
        
        # 🩸 Pénalité dégâts (encourager l'évitement)
        health_lost = env.last_player_health - env.player.health
        if health_lost > 0:
            reward -= health_lost * 2.0
            env.last_player_health = env.player.health
        
        return reward
    
    def train_precision(self, total_timesteps: int = 150000):
        """Entraîne l'IA pour la précision de tir."""
        print("🎯 ENTRAÎNEMENT PRÉCISION DE TIR")
        print("="*50)
        print("Objectifs :")
        print("  1. 🎯 Maximiser les kills par projectiles")
        print("  2. 🧭 Améliorer la précision de visée")
        print("  3. 🚫 Décourager les kills par collision")
        print("  4. 🏃 Maintenir un mouvement intelligent")
        print()
        
        # Créer environnement
        self.trainer.create_environment(n_envs=4)
        
        # Patcher le système de récompenses
        original_calculate_reward = GameAIEnvironment._calculate_reward
        
        def patched_reward(env_self):
            return self.precision_reward_system(env_self)
        
        GameAIEnvironment._calculate_reward = patched_reward
        
        try:
            # Partir du modèle curriculum ou créer nouveau
            if os.path.exists("curriculum_models/stage_1_model.zip"):
                print("📦 Chargement du modèle curriculum Stage 1 comme base...")
                self.trainer.load_model("curriculum_models/stage_1_model")
            elif os.path.exists("ai_models/game_ai_model_final.zip"):
                print("📦 Chargement du modèle final comme base...")
                self.trainer.load_model("ai_models/game_ai_model_final")
            else:
                print("🆕 Création d'un nouveau modèle...")
                self.trainer.create_model()
            
            print(f"🚀 Début de l'entraînement spécialisé ({total_timesteps} timesteps)")
            print("⏱️ Temps estimé : ~15-20 minutes")
            print()
            
            # Callback pour suivre les progrès
            class PrecisionCallback:
                def __init__(self):
                    self.last_info_time = time.time()
                    self.episode_count = 0
                    
                def __call__(self, locals_, globals_):
                    current_time = time.time()
                    if current_time - self.last_info_time > 45:  # Toutes les 45s
                        if 'infos' in locals_ and len(locals_['infos']) > 0:
                            info = locals_['infos'][0]
                            active_kills = info.get('enemies_killed_by_projectiles', 0)
                            passive_kills = info.get('enemies_killed_by_collision', 0)
                            projectiles = info.get('projectiles_fired', 0)
                            
                            ratio = active_kills / max(1, passive_kills)
                            efficiency = active_kills / max(1, projectiles) * 100
                            
                            print(f"📊 Actifs: {active_kills}, Passifs: {passive_kills}, " +
                                  f"Ratio: {ratio:.2f}, Efficacité: {efficiency:.1f}%")
                        self.last_info_time = current_time
                    return True
            
            # Entraîner
            self.trainer.train(total_timesteps=total_timesteps)
            
            # Sauvegarder
            model_path = "ai_models/precision_shooting_model"
            self.trainer.save_model(model_path)
            print(f"💾 Modèle de précision sauvegardé : {model_path}")
            
        finally:
            # Restaurer le système original
            GameAIEnvironment._calculate_reward = original_calculate_reward
            
        print("✅ Entraînement de précision terminé!")
        print("🎯 Testez avec demo_ai.py pour voir l'amélioration")

def main():
    """Point d'entrée principal."""
    trainer = PrecisionTrainer()
    trainer.train_precision()

if __name__ == "__main__":
    main()
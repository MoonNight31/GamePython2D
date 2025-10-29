#!/usr/bin/env python3
"""
Optimisation du système de tir - Curriculum amélioré
Apprendre à tirer intelligemment plutôt qu'en spam
"""

import sys
import os
import time
import numpy as np

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from gamepython2d.ai_trainer import GameAITrainer
from gamepython2d.ai_environment import GameAIEnvironment

class SmartShootingTrainer:
    """Entraîneur pour optimiser le système de tir de l'IA."""
    
    def __init__(self):
        self.trainer = GameAITrainer()
        
    def smart_shooting_reward(self, env) -> float:
        """Système de récompenses pour un tir intelligent."""
        reward = 0.0
        
        # Compter les projectiles tirés cette frame
        current_projectile_count = len([p for p in env.player.projectiles if p.active])
        projectiles_fired_this_step = max(0, current_projectile_count - env.last_projectile_count)
        
        if projectiles_fired_this_step > 0:
            # RÉCOMPENSE ÉNORME pour les tirs réussis
            reward += projectiles_fired_this_step * 15.0
            env.projectiles_fired += projectiles_fired_this_step
            print(f"🎯 TIR RÉUSSI! Projectiles: {projectiles_fired_this_step}, Récompense: +{projectiles_fired_this_step * 15.0}")
        
        # Récompense la visée intelligente même sans tir
        if hasattr(env, 'last_action') and len(env.enemy_spawner.enemies) > 0:
            move_x, move_y, attack_x, attack_y, should_attack = env.last_action
            
            # Bonus pour viser vers l'ennemi le plus proche
            closest_enemy = min(env.enemy_spawner.enemies, 
                              key=lambda e: ((e.rect.centerx - env.player.rect.centerx)**2 + 
                                           (e.rect.centery - env.player.rect.centery)**2)**0.5)
            
            # Direction vers l'ennemi
            dx = closest_enemy.rect.centerx - env.player.rect.centerx
            dy = closest_enemy.rect.centery - env.player.rect.centery
            length = (dx**2 + dy**2)**0.5
            
            if length > 0:
                dx /= length
                dy /= length
                
                # Calculer précision de la visée
                dot_product = dx * attack_x + dy * attack_y
                if dot_product > 0.7:  # Très précis
                    reward += 2.0
                elif dot_product > 0.3:  # Assez précis
                    reward += 0.5
                
            # Pénalité pour spam de tir quand cooldown actif
            if should_attack > 0.5 and projectiles_fired_this_step == 0:
                # L'IA tente de tirer mais c'est en cooldown
                current_time = env.player.last_attack_time
                attack_cooldown = 1000 / (env.player.attack_speed * env.player.card_effects['attack_speed_multiplier'])
                
                # Si le dernier tir était il y a moins de 50ms, pénaliser légèrement
                if hasattr(env, 'last_failed_shot_time'):
                    if current_time - env.last_failed_shot_time < 50:
                        reward -= 0.1  # Petite pénalité pour spam
                env.last_failed_shot_time = current_time
        
        env.last_projectile_count = current_projectile_count
        
        # Récompenses de base
        reward += 0.1  # Survie
        
        # Pénalité mort
        if env.player.health <= 0:
            reward -= 20.0
        
        # Bonus kills
        reward += env.enemies_killed_by_projectiles * 25.0
        
        return reward
    
    def train_smart_shooting(self, total_timesteps: int = 100000):
        """Entraîne l'IA pour un tir intelligent."""
        print("🎯 Entraînement TIR INTELLIGENT")
        print("="*50)
        
        # Créer environnement
        self.trainer.create_environment(n_envs=4)
        
        # Patcher le système de récompenses
        original_calculate_reward = GameAIEnvironment._calculate_reward
        
        def patched_reward(env_self):
            return self.smart_shooting_reward(env_self)
        
        GameAIEnvironment._calculate_reward = patched_reward
        
        try:
            # Charger modèle existant si disponible
            if os.path.exists("curriculum_models/stage_1_model.zip"):
                print("📦 Chargement du modèle curriculum Stage 1...")
                self.trainer.load_model("curriculum_models/stage_1_model")
            else:
                print("🆕 Création d'un nouveau modèle...")
                self.trainer.create_model()
            
            print(f"🚀 Début de l'entraînement ({total_timesteps} timesteps)")
            
            # Callback pour suivre les progrès
            class ShootingCallback:
                def __init__(self):
                    self.last_info_time = time.time()
                    
                def __call__(self, locals_, globals_):
                    if time.time() - self.last_info_time > 30:  # Toutes les 30s
                        if 'infos' in locals_ and len(locals_['infos']) > 0:
                            info = locals_['infos'][0]
                            tirs = info.get('projectiles_fired', 0)
                            kills = info.get('enemies_killed_by_projectiles', 0)
                            print(f"📊 Projectiles: {tirs}, Kills actifs: {kills}")
                        self.last_info_time = time.time()
                    return True
            
            # Entraîner
            self.trainer.train(
                total_timesteps=total_timesteps,
                callback=ShootingCallback(),
                progress_bar=True
            )
            
            # Sauvegarder
            model_path = "ai_models/smart_shooting_model"
            self.trainer.save_model(model_path)
            print(f"💾 Modèle sauvegardé : {model_path}")
            
        finally:
            # Restaurer le système original
            GameAIEnvironment._calculate_reward = original_calculate_reward
            
        print("✅ Entraînement terminé!")

def main():
    """Point d'entrée principal."""
    trainer = SmartShootingTrainer()
    trainer.train_smart_shooting()

if __name__ == "__main__":
    main()
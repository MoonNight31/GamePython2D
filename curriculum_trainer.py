#!/usr/bin/env python3
"""
Entraîneur IA avec Curriculum Learning
Apprentissage progressif par étapes : Tir → Mouvement → Survie
"""

import sys
import os
import time
import numpy as np
from typing import Dict, Any

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gamepython2d.ai_trainer import GameAITrainer
from gamepython2d.ai_environment import GameAIEnvironment

class CurriculumLearningTrainer:
    """Entraîneur avec apprentissage par curriculum."""
    
    def __init__(self):
        self.trainer = GameAITrainer()
        self.current_stage = 1
        self.stages = {
            1: "🎯 ÉTAPE 1: Apprendre à tirer",
            2: "🏃 ÉTAPE 2: Apprendre à se déplacer", 
            3: "🛡️ ÉTAPE 3: Apprendre à survivre"
        }
        
        # Critères de passage d'étape
        self.stage_criteria = {
            1: {"projectiles_per_episode": 5.0, "episodes_to_check": 10},
            2: {"movement_score": 0.7, "episodes_to_check": 10},
            3: {"survival_time": 1000, "episodes_to_check": 5}
        }
        
        self.stage_history = []
        
    def create_stage_environment(self, stage: int) -> GameAIEnvironment:
        """Crée un environnement adapté à l'étape d'apprentissage."""
        env = GameAIEnvironment(render_mode=None)
        
        # Modifier le système de récompenses selon l'étape
        env.curriculum_stage = stage
        
        return env
    
    def train_stage(self, stage: int, total_timesteps: int = 50000):
        """Entraîne l'IA pour une étape spécifique."""
        print(f"\n{'='*60}")
        print(f"{self.stages[stage]}")
        print(f"{'='*60}")
        
        # Configurer l'entraîneur
        self.trainer.create_environment(n_envs=4)
        
        # Si c'est la première étape ou on n'a pas de modèle, créer nouveau
        if stage == 1 or not hasattr(self.trainer, 'model') or self.trainer.model is None:
            print("🆕 Création d'un nouveau modèle")
            self.trainer.create_model(learning_rate=0.0005)
        else:
            print("🔄 Continuation avec le modèle existant")
        
        # Patcher le système de récompenses APRÈS la création des environnements
        self._patch_reward_system(stage)
        
        # Entraîner
        print(f"🚀 Début de l'entraînement - Étape {stage}")
        print(f"⏱️ Timesteps: {total_timesteps:,}")
        
        start_time = time.time()
        self.trainer.train(total_timesteps=total_timesteps, save_freq=10000)
        
        training_time = time.time() - start_time
        print(f"✅ Entraînement terminé en {training_time:.1f}s")
        
        # Le modèle est automatiquement sauvegardé par train()
        # Créer une copie spécifique à l'étape si nécessaire
        if hasattr(self.trainer, 'model') and self.trainer.model:
            stage_path = f"ai_models/curriculum_stage_{stage}"
            self.trainer.model.save(stage_path)
            print(f"💾 Modèle étape {stage} sauvegardé : {stage_path}")
        
        # Évaluer les performances
        self._evaluate_stage(stage)
        
    def _patch_reward_system(self, stage: int):
        """Modifie le système de récompenses selon l'étape."""
        # Stocker les méthodes originales si ce n'est pas déjà fait
        if not hasattr(self, '_original_calculate_reward'):
            self._original_calculate_reward = GameAIEnvironment._calculate_reward
        
        # Créer la nouvelle méthode selon l'étape
        trainer_instance = self  # Capturer l'instance pour la closure
        
        def curriculum_reward_wrapper(env_self):
            if stage == 1:
                return trainer_instance._stage1_reward(env_self)
            elif stage == 2:
                return trainer_instance._stage2_reward(env_self)
            elif stage == 3:
                return trainer_instance._stage3_reward(env_self)
            else:
                return trainer_instance._original_calculate_reward(env_self)
        
        # Appliquer le patch à la classe
        GameAIEnvironment._calculate_reward = curriculum_reward_wrapper
        print(f"📊 Système de récompenses configuré pour l'étape {stage}")
        
    def _stage1_reward(self, env) -> float:
        """🎯 ÉTAPE 1: Récompenses focalisées sur le TIR."""
        reward = 0.0
        
        # OBJECTIF PRINCIPAL : TIRER DES PROJECTILES
        current_projectile_count = len([p for p in env.player.projectiles if p.active])
        projectiles_fired_this_step = max(0, current_projectile_count - env.last_projectile_count)
        if projectiles_fired_this_step > 0:
            reward += projectiles_fired_this_step * 10.0  # TRÈS généreux
            env.projectiles_fired += projectiles_fired_this_step
        env.last_projectile_count = current_projectile_count
        
        # Bonus pour viser vers les ennemis
        if hasattr(env, 'last_action') and len(env.enemy_spawner.enemies) > 0:
            move_x, move_y, attack_x, attack_y, should_attack = env.last_action
            if should_attack > 0.5:
                # Vérifier si la direction de tir est vers un ennemi
                closest_enemy = min(env.enemy_spawner.enemies, 
                                  key=lambda e: ((e.rect.centerx - env.player.rect.centerx)**2 + 
                                               (e.rect.centery - env.player.rect.centery)**2)**0.5)
                
                # Direction vers l'ennemi
                dx = closest_enemy.rect.centerx - env.player.rect.centerx
                dy = closest_enemy.rect.centery - env.player.rect.centery
                
                # Normaliser
                length = (dx**2 + dy**2)**0.5
                if length > 0:
                    dx /= length
                    dy /= length
                    
                    # Calculer similarité avec direction de tir
                    dot_product = dx * attack_x + dy * attack_y
                    if dot_product > 0.3:  # 45 degrés de tolérance
                        reward += 5.0  # Bonus pour bien viser
        
        # Survie minimale
        reward += 0.1
        
        # Pénalité mort seulement
        if env.player.health <= 0:
            reward -= 20.0
            
        return reward
    
    def _stage2_reward(self, env) -> float:
        """🏃 ÉTAPE 2: Récompenses focalisées sur le MOUVEMENT."""
        reward = 0.0
        
        # OBJECTIF PRINCIPAL : SE DÉPLACER INTELLIGEMMENT
        if hasattr(env, 'last_action'):
            move_x, move_y, attack_x, attack_y, should_attack = env.last_action
            is_moving = abs(move_x) > 0.1 or abs(move_y) > 0.1
            
            if is_moving:
                reward += 3.0  # Bonus pour bouger
                
                # Bonus pour s'éloigner des ennemis
                if len(env.enemy_spawner.enemies) > 0:
                    closest_enemy = min(env.enemy_spawner.enemies, 
                                      key=lambda e: ((e.rect.centerx - env.player.rect.centerx)**2 + 
                                                   (e.rect.centery - env.player.rect.centery)**2)**0.5)
                    
                    # Direction pour s'éloigner
                    dx = env.player.rect.centerx - closest_enemy.rect.centerx
                    dy = env.player.rect.centery - closest_enemy.rect.centery
                    length = (dx**2 + dy**2)**0.5
                    
                    if length > 0:
                        dx /= length
                        dy /= length
                        
                        # Récompenser mouvement dans la bonne direction
                        dot_product = dx * move_x + dy * move_y
                        if dot_product > 0:
                            reward += dot_product * 2.0
        
        # Garder les acquis de l'étape 1 (mais moins important)
        current_projectile_count = len([p for p in env.player.projectiles if p.active])
        projectiles_fired_this_step = max(0, current_projectile_count - env.last_projectile_count)
        if projectiles_fired_this_step > 0:
            reward += projectiles_fired_this_step * 2.0  # Moins généreux qu'étape 1
        env.last_projectile_count = current_projectile_count
        
        # Éviter les bords
        player_x = env.player.rect.centerx
        player_y = env.player.rect.centery
        if (player_x < 50 or player_x > env.screen_width - 50 or 
            player_y < 50 or player_y > env.screen_height - 50):
            reward -= 2.0
            
        # Survie
        reward += 0.2
        
        # Pénalité dégâts
        health_lost = env.last_player_health - env.player.health
        if health_lost > 0:
            reward -= health_lost * 2.0
            env.last_player_health = env.player.health
        
        # Pénalité mort
        if env.player.health <= 0:
            reward -= 30.0
            
        return reward
    
    def _stage3_reward(self, env) -> float:
        """🛡️ ÉTAPE 3: Récompenses focalisées sur la SURVIE."""
        reward = 0.0
        
        # OBJECTIF PRINCIPAL : SURVIVRE LONGTEMPS
        reward += 0.5  # Bonus de survie augmenté
        
        # Bonus pour kills (combinaison tir + survie)
        for enemy in env.enemy_spawner.enemies[:]:
            if enemy.health <= 0:
                # Vérifier si tué par projectile
                killed_by_projectile = False
                for projectile in env.player.projectiles:
                    if projectile.active and projectile.rect.colliderect(enemy.rect):
                        killed_by_projectile = True
                        break
                
                if killed_by_projectile:
                    reward += 15.0  # Gros bonus pour kill actif
                    env.enemies_killed_by_projectiles += 1
        
        # Garder les acquis des étapes précédentes
        # Mouvement (étape 2)
        if hasattr(env, 'last_action'):
            move_x, move_y, attack_x, attack_y, should_attack = env.last_action
            is_moving = abs(move_x) > 0.1 or abs(move_y) > 0.1
            if is_moving:
                reward += 1.0
        
        # Tir (étape 1)
        current_projectile_count = len([p for p in env.player.projectiles if p.active])
        projectiles_fired_this_step = max(0, current_projectile_count - env.last_projectile_count)
        if projectiles_fired_this_step > 0:
            reward += projectiles_fired_this_step * 1.0
        env.last_projectile_count = current_projectile_count
        
        # Gestion des dégâts (critique pour survie)
        health_lost = env.last_player_health - env.player.health
        if health_lost > 0:
            reward -= health_lost * 5.0  # Pénalité très forte
            env.last_player_health = env.player.health
        
        # Position tactique
        player_x = env.player.rect.centerx
        player_y = env.player.rect.centery
        
        # Éviter les bords
        min_distance_to_edge = min(player_x, env.screen_width - player_x, 
                                 player_y, env.screen_height - player_y)
        if min_distance_to_edge < 100:
            reward -= 3.0
        else:
            reward += 0.5  # Bonus position sécurisée
        
        # Pénalité mort massive
        if env.player.health <= 0:
            reward -= 100.0
            
        return reward
    
    def _evaluate_stage(self, stage: int):
        """Évalue les performances de l'étape."""
        print(f"\n📊 ÉVALUATION ÉTAPE {stage}")
        print("-" * 40)
        
        # Créer un environnement simple pour l'évaluation
        from gamepython2d.ai_environment import GameAIEnvironment
        env = GameAIEnvironment(render_mode=None)
        
        metrics = {
            "projectiles_per_episode": [],
            "survival_times": [],
            "movement_scores": [],
            "kills": []
        }
        
        for episode in range(5):  # Réduire le nombre d'épisodes pour aller plus vite
            obs, _ = env.reset()
            total_projectiles = 0
            total_movement = 0
            step_count = 0
            kills = 0
            last_projectile_count = 0
            
            while step_count < 1000:  # Réduire la durée max
                action, _ = self.trainer.model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = env.step(action)
                
                # Mesurer projectiles
                current_projectiles = len([p for p in env.player.projectiles if p.active])
                total_projectiles += max(0, current_projectiles - last_projectile_count)
                last_projectile_count = current_projectiles
                
                # Mesurer mouvement
                move_x, move_y = action[0], action[1]
                movement = (move_x**2 + move_y**2)**0.5
                total_movement += movement
                
                step_count += 1
                
                if terminated or truncated:
                    break
            
            metrics["projectiles_per_episode"].append(total_projectiles)
            metrics["survival_times"].append(step_count)
            metrics["movement_scores"].append(total_movement / step_count if step_count > 0 else 0)
            metrics["kills"].append(info.get('enemies_killed_by_projectiles', 0))
        
        # Afficher résultats
        avg_projectiles = np.mean(metrics["projectiles_per_episode"])
        avg_survival = np.mean(metrics["survival_times"])
        avg_movement = np.mean(metrics["movement_scores"])
        avg_kills = np.mean(metrics["kills"])
        
        print(f"🎯 Projectiles/épisode: {avg_projectiles:.1f}")
        print(f"⏱️ Temps de survie: {avg_survival:.0f} steps")
        print(f"🏃 Score de mouvement: {avg_movement:.3f}")
        print(f"⚔️ Kills/épisode: {avg_kills:.1f}")
        
        # Vérifier critères de passage
        criteria = self.stage_criteria.get(stage, {})
        ready_for_next = True
        
        if "projectiles_per_episode" in criteria:
            if avg_projectiles < criteria["projectiles_per_episode"]:
                ready_for_next = False
                print(f"❌ Critère projectiles non atteint: {avg_projectiles:.1f}/{criteria['projectiles_per_episode']}")
        
        if "movement_score" in criteria:
            if avg_movement < criteria["movement_score"]:
                ready_for_next = False
                print(f"❌ Critère mouvement non atteint: {avg_movement:.3f}/{criteria['movement_score']}")
        
        if "survival_time" in criteria:
            if avg_survival < criteria["survival_time"]:
                ready_for_next = False
                print(f"❌ Critère survie non atteint: {avg_survival:.0f}/{criteria['survival_time']}")
        
        if ready_for_next and stage < 3:
            print(f"✅ PRÊT POUR L'ÉTAPE {stage + 1} !")
        elif stage == 3:
            print("🏆 CURRICULUM TERMINÉ !")
        else:
            print("⚠️ Besoin d'entraînement supplémentaire")
        
        env.close()
        return ready_for_next
    
    def run_full_curriculum(self):
        """Lance l'apprentissage complet par curriculum."""
        print("🎓 DÉMARRAGE DU CURRICULUM LEARNING")
        print("="*60)
        
        for stage in [1, 2, 3]:
            self.train_stage(stage, total_timesteps=100000)
            
            print(f"\n{'='*60}")
            
        print("🎉 CURRICULUM LEARNING TERMINÉ !")
        print("Le modèle final est disponible dans ai_models/curriculum_stage_3")

def main():
    """Point d'entrée principal."""
    print("🎓 CURRICULUM LEARNING TRAINER")
    print("Apprentissage progressif : Tir → Mouvement → Survie")
    print("="*60)
    
    trainer = CurriculumLearningTrainer()
    
    # Demander à l'utilisateur
    choice = input("Voulez-vous lancer le curriculum complet ? (o/n): ").strip().lower()
    
    if choice in ['o', 'oui', 'y', 'yes']:
        trainer.run_full_curriculum()
    else:
        print("Curriculum annulé.")

if __name__ == "__main__":
    main()
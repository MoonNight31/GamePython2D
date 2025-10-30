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
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from gamepython2d.ai_trainer import GameAITrainer
from gamepython2d.ai_environment import GameAIEnvironment

class CurriculumLearningTrainer:
    """Entraîneur avec apprentissage par curriculum."""
    
    def __init__(self):
        self.trainer = GameAITrainer()
        self.current_stage = 1
        self.stages = {
            1: "🎯 ÉTAPE 1: Apprendre à tirer",
            2: "🎯 ÉTAPE 2: Apprendre à viser",
            3: "🏃 ÉTAPE 3: Apprendre à se déplacer",
            4: "🛡️ ÉTAPE 4: Apprendre à survivre",
            5: "💎 ÉTAPE 5: Apprendre à ramasser les orbes d'XP",
            6: "🃏 ÉTAPE 6: Apprendre à sélectionner les cartes",
            7: "🏆 ÉTAPE 7: Maîtrise complète avec améliorations"
        }
        
        # Critères de passage d'étape
        self.stage_criteria = {
            1: {"projectiles_per_episode": 5.0, "episodes_to_check": 10},
            2: {"accuracy_score": 0.3, "episodes_to_check": 10},
            3: {"movement_score": 0.7, "episodes_to_check": 10},
            4: {"survival_time": 1000, "episodes_to_check": 5},
            5: {"xp_orbs_collected": 3.0, "episodes_to_check": 10},
            6: {"cards_selected": 1.0, "episodes_to_check": 5},
            7: {"survival_time": 2000, "kills": 5.0, "episodes_to_check": 5}
        }
        
        # Timesteps progressifs par étape (augmentés de 300% pour meilleur apprentissage)
        self.stage_timesteps = {
            1: 600000,   # Étape 1 : Tir de base (600k - était 150k)
            2: 800000,   # Étape 2 : Visée (800k - était 200k)
            3: 1000000,  # Étape 3 : Mouvement (1M - était 250k)
            4: 1200000,  # Étape 4 : Survie (1.2M - était 300k)
            5: 1400000,  # Étape 5 : Collecte XP (1.4M - était 350k)
            6: 1200000,  # Étape 6 : Cartes (1.2M - était 300k)
            7: 2000000,  # Étape 7 : Maîtrise complète (2M - était 500k)
        }
        
        # Nombre de tentatives maximum par étape
        self.max_retries = 2
        
        self.stage_history = []
        self.stage_metrics = {
            "stage_names": [],
            "projectiles": [],
            "accuracy": [],
            "movement": [],
            "survival": [],
            "kills": [],
            "xp_collected": [],
            "levels": [],
            "training_times": []
        }
        
    def _gather_env_state(self, env):
        """Collecte et normalise les informations fréquemment utilisées par les fonctions de récompense.
        
        Utilise un cache pour éviter les recalculs coûteux dans le même step.
        Retourne un dict contenant : player pos, health, health_lost, projectile counts,
        xp_gained, closest enemy normalized direction et distance.
        """
        # Cache: évite de recalculer si déjà fait pour ce step
        current_step = getattr(env, '_current_step_id', -1)
        if hasattr(env, '_cached_state') and getattr(env, '_cached_state_step', -2) == current_step:
            return env._cached_state
        
        player = getattr(env, 'player', None)
        xp_system = getattr(env, 'xp_system', None)
        enemy_spawner = getattr(env, 'enemy_spawner', None)

        px = player.rect.centerx if player is not None else 0
        py = player.rect.centery if player is not None else 0
        p_health = getattr(player, 'health', 0)

        last_health = getattr(env, 'last_player_health', p_health)
        health_lost = max(0, last_health - p_health)
        env.last_player_health = p_health

        # Projectiles - optimisé avec sum au lieu de list comprehension
        current_projectiles = 0
        if player is not None and hasattr(player, 'projectiles'):
            current_projectiles = sum(1 for p in player.projectiles if getattr(p, 'active', False))
        
        last_proj = getattr(env, 'last_projectile_count', 0)
        projectiles_fired = max(0, current_projectiles - last_proj)
        env.last_projectile_count = current_projectiles

        # XP
        xp_now = getattr(xp_system, 'current_xp', 0) if xp_system is not None else 0
        last_xp = getattr(env, 'last_xp_count', xp_now)
        xp_gained = max(0, xp_now - last_xp)
        env.last_xp_count = xp_now

        # Closest enemy - optimisé avec boucle directe au lieu de min()+lambda
        ndx = ndy = 0.0
        enemy_dist = float('inf')
        closest_enemy = None
        
        if enemy_spawner is not None and getattr(enemy_spawner, 'enemies', None):
            enemies = enemy_spawner.enemies
            if enemies:
                min_dist_sq = float('inf')
                for enemy in enemies:
                    dx = enemy.rect.centerx - px
                    dy = enemy.rect.centery - py
                    dist_sq = dx*dx + dy*dy
                    if dist_sq < min_dist_sq:
                        min_dist_sq = dist_sq
                        closest_enemy = enemy
                
                if closest_enemy is not None:
                    dx = closest_enemy.rect.centerx - px
                    dy = closest_enemy.rect.centery - py
                    enemy_dist = min_dist_sq ** 0.5
                    if enemy_dist > 0:
                        ndx = dx / enemy_dist
                        ndy = dy / enemy_dist

        result = {
            'px': px, 'py': py, 'p_health': p_health, 'health_lost': health_lost,
            'current_projectiles': current_projectiles, 'projectiles_fired': projectiles_fired,
            'xp_gained': xp_gained, 'closest_enemy_dir': (ndx, ndy), 'closest_enemy_dist': enemy_dist,
            'closest_enemy': closest_enemy
        }
        
        # Sauvegarder dans le cache
        env._cached_state = result
        env._cached_state_step = current_step
        
        return result
        
    def create_stage_environment(self, stage: int) -> GameAIEnvironment:
        """Crée un environnement adapté à l'étape d'apprentissage."""
        env = GameAIEnvironment(render_mode=None)
        
        # Modifier le système de récompenses selon l'étape
        env.curriculum_stage = stage
        
        return env
    
    def train_stage(self, stage: int, total_timesteps: int = None):
        """Entraîne l'IA pour une étape spécifique."""
        # Utiliser les timesteps par défaut si non spécifié
        if total_timesteps is None:
            total_timesteps = self.stage_timesteps.get(stage, 100000)
        
        print(f"\n{'='*60}")
        print(f"{self.stages[stage]}")
        print(f"{'='*60}")
        
        # Configurer l'entraîneur
        self.trainer.create_environment(n_envs=30)
        print(f"🔍 Vérification: {self.trainer.env.num_envs} environnements créés")
        
        # Si c'est la première étape ou on n'a pas de modèle, créer nouveau
        if stage == 1 or not hasattr(self.trainer, 'model') or self.trainer.model is None:
            print("🆕 Création d'un nouveau modèle")
            # Batch size optimal pour 30 envs avec n_steps=2048
            # 30 * 2048 = 61440, diviseurs parfaits: 480, 512, 640
            self.trainer.create_model(learning_rate=0.0005, batch_size=512)
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
        print(f"✅ Entraînement terminé en {training_time:.1f}s ({training_time/60:.1f} minutes)")
        
        # Le modèle est automatiquement sauvegardé par train()
        # Créer une copie spécifique à l'étape si nécessaire
        if hasattr(self.trainer, 'model') and self.trainer.model:
            stage_path = f"ai_models/curriculum_stage_{stage}"
            self.trainer.model.save(stage_path)
            print(f"💾 Modèle étape {stage} sauvegardé : {stage_path}")
        
        # Évaluer les performances
        return self._evaluate_stage(stage)
    
    def train_stage_with_validation(self, stage: int):
        """Entraîne une étape avec validation stricte et retry si échec."""
        print(f"\n{'='*70}")
        print(f"🎓 ENTRAÎNEMENT AVEC VALIDATION - {self.stages[stage]}")
        print(f"{'='*70}")
        print(f"📊 Timesteps prévus: {self.stage_timesteps[stage]:,}")
        print(f"🔄 Tentatives maximum: {self.max_retries}")
        print(f"{'='*70}\n")
        
        for attempt in range(1, self.max_retries + 1):
            print(f"\n{'🔥'*30}")
            print(f"🔄 TENTATIVE {attempt}/{self.max_retries} - Étape {stage}")
            print(f"{'🔥'*30}\n")
            
            # Entraîner l'étape
            ready = self.train_stage(stage)
            
            if ready:
                print(f"\n{'✅'*30}")
                print(f"✅ ÉTAPE {stage} VALIDÉE avec succès !")
                print(f"{'✅'*30}\n")
                return True
            else:
                if attempt < self.max_retries:
                    print(f"\n{'⚠️'*30}")
                    print(f"⚠️ Étape {stage} NON VALIDÉE - Ré-entraînement avec 50% de timesteps supplémentaires...")
                    print(f"{'⚠️'*30}\n")
                    # Augmenter les timesteps de 50% pour la prochaine tentative
                    self.stage_timesteps[stage] = int(self.stage_timesteps[stage] * 1.5)
                else:
                    print(f"\n{'❌'*30}")
                    print(f"❌ ATTENTION: Étape {stage} NON VALIDÉE après {self.max_retries} tentatives")
                    print(f"❌ Passage forcé à l'étape suivante...")
                    print(f"{'❌'*30}\n")
        
        return False
        
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
            elif stage == 4:
                return trainer_instance._stage4_reward(env_self)
            elif stage == 5:
                return trainer_instance._stage5_reward(env_self)
            elif stage == 6:
                return trainer_instance._stage6_reward(env_self)
            elif stage == 7:
                return trainer_instance._stage7_reward(env_self)
            else:
                return trainer_instance._original_calculate_reward(env_self)
        
        # Appliquer le patch à la classe
        GameAIEnvironment._calculate_reward = curriculum_reward_wrapper
        print(f"📊 Système de récompenses configuré pour l'étape {stage}")
        
    def _stage1_reward(self, env) -> float:
        """🎯 ÉTAPE 1: Récompenses focalisées sur le TIR (simplifié)."""
        s = self._gather_env_state(env)
        reward = 0.1  # petite récompense de survie

        # Encourager le tir
        if s['projectiles_fired'] > 0:
            reward += s['projectiles_fired'] * 10.0
            env.projectiles_fired = getattr(env, 'projectiles_fired', 0) + s['projectiles_fired']

        # Bonus si vise globalement vers le plus proche ennemi
        if hasattr(env, 'last_action'):
            _, _, attack_x, attack_y, should_attack = env.last_action
            if should_attack > 0.5:
                ndx, ndy = s['closest_enemy_dir']
                dot = ndx * attack_x + ndy * attack_y
                if dot > 0.3:
                    reward += 5.0

        if s['p_health'] <= 0:
            reward -= 20.0

        return reward
    
    def _stage2_reward(self, env) -> float:
        """🎯 ÉTAPE 2: Récompenses focalisées sur la VISÉE (simplifié)."""
        s = self._gather_env_state(env)
        reward = 0.1

        # Récompenser la bonne orientation vers l'ennemi
        if hasattr(env, 'last_action'):
            _, _, attack_x, attack_y, should_attack = env.last_action
            ndx, ndy = s['closest_enemy_dir']
            dot = ndx * attack_x + ndy * attack_y
            if dot > 0.5:
                reward += dot * 8.0
            if should_attack > 0.5 and dot > 0.3:
                reward += 12.0

        # Tir et kills
        if s['projectiles_fired'] > 0:
            reward += s['projectiles_fired'] * 5.0

        reward += getattr(env, 'enemies_killed_by_projectiles', 0) * 30.0

        if s['p_health'] <= 0:
            reward -= 25.0

        return reward
    
    def _stage3_reward(self, env) -> float:
        """🏃 ÉTAPE 3: Récompenses focalisées sur le MOUVEMENT (simplifié)."""
        s = self._gather_env_state(env)
        reward = 0.2

        # Encourager le mouvement
        if hasattr(env, 'last_action'):
            move_x, move_y, _, _, _ = env.last_action
            is_moving = abs(move_x) > 0.1 or abs(move_y) > 0.1
            if is_moving:
                reward += 3.0
                # s'éloigner du plus proche ennemi
                ndx, ndy = s['closest_enemy_dir']
                # direction opposée à l'ennemi
                away_dot = (-ndx) * (move_x) + (-ndy) * (move_y)
                if away_dot > 0:
                    reward += away_dot * 2.0

        # Tir et kills conservés
        if s['projectiles_fired'] > 0:
            reward += s['projectiles_fired'] * 4.0
        reward += getattr(env, 'enemies_killed_by_projectiles', 0) * 20.0

        # Pénalité dégâts
        if s['health_lost'] > 0:
            reward -= s['health_lost'] * 2.0

        if s['p_health'] <= 0:
            reward -= 30.0

        return reward
    
    def _stage4_reward(self, env) -> float:
        """🛡️ ÉTAPE 4: Récompenses focalisées sur la SURVIE (simplifié)."""
        s = self._gather_env_state(env)
        reward = 0.5

        # Encourager survie et kills
        reward += getattr(env, 'enemies_killed_by_projectiles', 0) * 15.0

        # Mouvement simple
        if hasattr(env, 'last_action'):
            move_x, move_y, _, _, _ = env.last_action
            if abs(move_x) > 0.1 or abs(move_y) > 0.1:
                reward += 1.0

        # Tir contribute mais moins
        if s['projectiles_fired'] > 0:
            reward += s['projectiles_fired'] * 3.0

        # Pénalité dégâts et mort
        if s['health_lost'] > 0:
            reward -= s['health_lost'] * 5.0
        if s['p_health'] <= 0:
            reward -= 100.0

        # Position tactique approximée: pénaliser si trop proche des bords (si screen dims disponibles)
        try:
            px = s['px']
            py = s['py']
            sw = getattr(env, 'screen_width', None)
            sh = getattr(env, 'screen_height', None)
            if sw and sh:
                min_dist = min(px, sw - px, py, sh - py)
                if min_dist < 100:
                    reward -= 3.0
                else:
                    reward += 0.5
        except Exception:
            pass

        return reward
    
    # Note: duplicate _stage4_reward definition removed during simplification.
    
    def _stage5_reward(self, env) -> float:
        """💎 ÉTAPE 5: Récompenses pour collecte d'XP (simplifié)."""
        s = self._gather_env_state(env)
        reward = 0.4

        # Récompenser XP collecté
        if s['xp_gained'] > 0:
            reward += s['xp_gained'] * 5.0
            # petit bonus combo si collecte rapide (streak maintenue)
            if not hasattr(env, 'orb_collection_streak'):
                env.orb_collection_streak = 0
                env.last_collection_time = env.step_count
            if (env.step_count - getattr(env, 'last_collection_time', env.step_count)) < 100:
                env.orb_collection_streak = getattr(env, 'orb_collection_streak', 0) + 1
                reward += env.orb_collection_streak * 2.0
            else:
                env.orb_collection_streak = 1
            env.last_collection_time = env.step_count

        # Bonus kills and basic shooting
        reward += getattr(env, 'enemies_killed_by_projectiles', 0) * 25.0
        if s['projectiles_fired'] > 0:
            reward += s['projectiles_fired'] * 2.0

        # Pénalités
        if s['health_lost'] > 0:
            reward -= s['health_lost'] * 2.0
        if s['p_health'] <= 0:
            reward -= 60.0

        return reward
    
    def _stage6_reward(self, env) -> float:
        """🃏 ÉTAPE 6: Récompenses pour la sélection de cartes (simplifié)."""
        s = self._gather_env_state(env)
        reward = 0.4

        # Level-ups detection (simple)
        current_level = getattr(env.xp_system, 'level', 0)
        if not hasattr(env, 'last_level'):
            env.last_level = current_level
        if current_level > env.last_level:
            reward += 30.0
            env.last_cards_selected = getattr(env, 'last_cards_selected', 0) + 1
            env.last_level = current_level

        # XP and kills contribute
        if s['xp_gained'] > 0:
            reward += s['xp_gained'] * 1.5
        reward += getattr(env, 'enemies_killed_by_projectiles', 0) * 20.0

        # Shooting incentive maintained
        if s['projectiles_fired'] > 0:
            reward += s['projectiles_fired'] * 2.0

        # Penalties
        if s['health_lost'] > 0:
            reward -= s['health_lost'] * 4.0
        if s['p_health'] <= 0:
            reward -= 100.0

        return reward
    
    def _stage7_reward(self, env) -> float:
        """🏆 ÉTAPE 7: MAÎTRISE COMPLÈTE - Survie & performance (simplifié)."""
        s = self._gather_env_state(env)
        reward = 0.6

        # Kills and level
        reward += getattr(env, 'enemies_killed_by_projectiles', 0) * 30.0
        current_level = getattr(env.xp_system, 'level', 0)
        if current_level >= 5:
            reward += (current_level - 4) * 10.0

        # XP
        if s['xp_gained'] > 0:
            reward += s['xp_gained'] * 1.0

        # Shooting
        if s['projectiles_fired'] > 0:
            reward += s['projectiles_fired'] * 3.0

        # Movement bonus
        if hasattr(env, 'last_action'):
            move_x, move_y, _, _, _ = env.last_action
            if abs(move_x) > 0.1 or abs(move_y) > 0.1:
                reward += 1.5

        # Strong penalties for damage / death
        if s['health_lost'] > 0:
            reward -= s['health_lost'] * 8.0
        if s['p_health'] <= 0:
            reward -= 150.0

        # Tactical position approximation
        try:
            px = s['px']; py = s['py']
            sw = getattr(env, 'screen_width', None); sh = getattr(env, 'screen_height', None)
            if sw and sh:
                min_dist = min(px, sw - px, py, sh - py)
                if min_dist < 100:
                    reward -= 5.0
                elif min_dist > 200:
                    reward += 1.0
        except Exception:
            pass

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
            "kills": [],
            "xp_orbs_collected": [],
            "accuracy_scores": [],
            "cards_selected": [],
            "final_levels": []
        }
        
        for episode in range(5):  # Réduire le nombre d'épisodes pour aller plus vite
            obs, _ = env.reset()
            total_projectiles = 0
            total_movement = 0
            step_count = 0
            kills = 0
            last_projectile_count = 0
            xp_collected = 0
            last_xp = 0
            aimed_shots = 0
            total_shots = 0
            initial_level = env.xp_system.level
            
            while step_count < 1000:  # Réduire la durée max
                action, _ = self.trainer.model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = env.step(action)
                
                # Mesurer projectiles
                current_projectiles = len([p for p in env.player.projectiles if p.active])
                projectiles_fired = max(0, current_projectiles - last_projectile_count)
                total_projectiles += projectiles_fired
                total_shots += projectiles_fired
                last_projectile_count = current_projectiles
                
                # Mesurer précision de visée (étape 2)
                if projectiles_fired > 0 and len(env.enemy_spawner.enemies) > 0:
                    attack_x, attack_y = action[2], action[3]
                    closest_enemy = min(env.enemy_spawner.enemies,
                                      key=lambda e: ((e.rect.centerx - env.player.rect.centerx)**2 + 
                                                   (e.rect.centery - env.player.rect.centery)**2)**0.5)
                    dx = closest_enemy.rect.centerx - env.player.rect.centerx
                    dy = closest_enemy.rect.centery - env.player.rect.centery
                    length = (dx**2 + dy**2)**0.5
                    if length > 0:
                        dx /= length
                        dy /= length
                        dot_product = dx * attack_x + dy * attack_y
                        if dot_product > 0.3:
                            aimed_shots += 1
                
                # Mesurer mouvement
                move_x, move_y = action[0], action[1]
                movement = (move_x**2 + move_y**2)**0.5
                total_movement += movement
                
                # Mesurer collecte d'XP
                current_xp = env.xp_system.current_xp
                if current_xp > last_xp:
                    xp_collected += (current_xp - last_xp)
                last_xp = current_xp
                
                step_count += 1
                
                if terminated or truncated:
                    break
            
            metrics["projectiles_per_episode"].append(total_projectiles)
            metrics["survival_times"].append(step_count)
            metrics["movement_scores"].append(total_movement / step_count if step_count > 0 else 0)
            metrics["kills"].append(info.get('enemies_killed_by_projectiles', 0))
            metrics["xp_orbs_collected"].append(xp_collected / 10.0)  # Normaliser
            metrics["accuracy_scores"].append(aimed_shots / total_shots if total_shots > 0 else 0)
            metrics["cards_selected"].append(env.xp_system.level - initial_level)
            metrics["final_levels"].append(env.xp_system.level)
        
        # Afficher résultats
        avg_projectiles = np.mean(metrics["projectiles_per_episode"])
        avg_survival = np.mean(metrics["survival_times"])
        avg_movement = np.mean(metrics["movement_scores"])
        avg_kills = np.mean(metrics["kills"])
        avg_xp_collected = np.mean(metrics["xp_orbs_collected"])
        avg_accuracy = np.mean(metrics["accuracy_scores"])
        avg_cards = np.mean(metrics["cards_selected"])
        avg_level = np.mean(metrics["final_levels"])
        
        print(f"🎯 Projectiles/épisode: {avg_projectiles:.1f}")
        print(f"🎨 Précision visée: {avg_accuracy:.1%}")
        print(f"🏃 Score de mouvement: {avg_movement:.3f}")
        print(f"⏱️ Temps de survie: {avg_survival:.0f} steps")
        print(f"⚔️ Kills/épisode: {avg_kills:.1f}")
        print(f"💎 Orbes XP collectés: {avg_xp_collected:.1f}")
        print(f"🃏 Cartes obtenues: {avg_cards:.1f}")
        print(f"📊 Niveau moyen final: {avg_level:.1f}")
        
        # Stocker les métriques pour les graphiques
        self.stage_metrics["stage_names"].append(f"Étape {stage}")
        self.stage_metrics["projectiles"].append(avg_projectiles)
        self.stage_metrics["accuracy"].append(avg_accuracy * 100)  # En pourcentage
        self.stage_metrics["movement"].append(avg_movement)
        self.stage_metrics["survival"].append(avg_survival)
        self.stage_metrics["kills"].append(avg_kills)
        self.stage_metrics["xp_collected"].append(avg_xp_collected)
        self.stage_metrics["levels"].append(avg_level)
        
        # Vérifier critères de passage
        criteria = self.stage_criteria.get(stage, {})
        ready_for_next = True
        
        if "projectiles_per_episode" in criteria:
            if avg_projectiles < criteria["projectiles_per_episode"]:
                ready_for_next = False
                print(f"❌ Critère projectiles non atteint: {avg_projectiles:.1f}/{criteria['projectiles_per_episode']}")
        
        if "accuracy_score" in criteria:
            if avg_accuracy < criteria["accuracy_score"]:
                ready_for_next = False
                print(f"❌ Critère précision non atteint: {avg_accuracy:.1%}/{criteria['accuracy_score']:.1%}")
        
        if "movement_score" in criteria:
            if avg_movement < criteria["movement_score"]:
                ready_for_next = False
                print(f"❌ Critère mouvement non atteint: {avg_movement:.3f}/{criteria['movement_score']}")
        
        if "survival_time" in criteria:
            if avg_survival < criteria["survival_time"]:
                ready_for_next = False
                print(f"❌ Critère survie non atteint: {avg_survival:.0f}/{criteria['survival_time']}")
        
        if "xp_orbs_collected" in criteria:
            if avg_xp_collected < criteria["xp_orbs_collected"]:
                ready_for_next = False
                print(f"❌ Critère collecte XP non atteint: {avg_xp_collected:.1f}/{criteria['xp_orbs_collected']}")
        
        if "cards_selected" in criteria:
            if avg_cards < criteria["cards_selected"]:
                ready_for_next = False
                print(f"❌ Critère cartes non atteint: {avg_cards:.1f}/{criteria['cards_selected']}")
        
        if "kills" in criteria:
            if avg_kills < criteria["kills"]:
                ready_for_next = False
                print(f"❌ Critère kills non atteint: {avg_kills:.1f}/{criteria['kills']}")
        
        if ready_for_next and stage < 7:
            print(f"✅ PRÊT POUR L'ÉTAPE {stage + 1} !")
        elif stage == 7:
            print("🏆 CURRICULUM TERMINÉ !")
        else:
            print("⚠️ Besoin d'entraînement supplémentaire")
        
        env.close()
        return ready_for_next
    
    def run_full_curriculum(self):
        """Lance l'apprentissage complet par curriculum avec validation stricte."""
        print("\n" + "="*70)
        print("🎓 DÉMARRAGE DU CURRICULUM LEARNING - 7 ÉTAPES")
        print("="*70)
        print(f"\n📊 Configuration:")
        print(f"  • Étape 1 (Tir):      {self.stage_timesteps[1]:,} timesteps")
        print(f"  • Étape 2 (Visée):    {self.stage_timesteps[2]:,} timesteps")
        print(f"  • Étape 3 (Mouvement): {self.stage_timesteps[3]:,} timesteps")
        print(f"  • Étape 4 (Survie):   {self.stage_timesteps[4]:,} timesteps")
        print(f"  • Étape 5 (XP):       {self.stage_timesteps[5]:,} timesteps")
        print(f"  • Étape 6 (Cartes):   {self.stage_timesteps[6]:,} timesteps")
        print(f"  • Étape 7 (Maîtrise): {self.stage_timesteps[7]:,} timesteps")
        total_timesteps = sum(self.stage_timesteps.values())
        print(f"\n  📈 TOTAL: ~{total_timesteps:,} timesteps (~{total_timesteps/1000000:.1f}M)")
        estimated_time = total_timesteps / 7000 / 60  # Estimation: 7000 FPS, conversion en minutes
        print(f"  ⏱️ Temps estimé: ~{estimated_time:.0f} minutes ({estimated_time/60:.1f}h)")
        print("="*70 + "\n")
        
        start_total = time.time()
        successful_stages = 0
        stage_times = []
        
        for stage in [1, 2, 3, 4, 5, 6, 7]:
            stage_start = time.time()
            success = self.train_stage_with_validation(stage)
            stage_time = time.time() - stage_start
            stage_times.append(stage_time)
            self.stage_metrics["training_times"].append(stage_time / 60)  # En minutes
            
            if success:
                successful_stages += 1
            
            print(f"\n{'='*70}")
            print(f"📊 PROGRESSION: {successful_stages}/{stage} étapes validées")
            print(f"{'='*70}\n")
        
        total_time = time.time() - start_total
        
        print("\n" + "🎉"*35)
        print("🎉 CURRICULUM LEARNING TERMINÉ !")
        print("🎉"*35)
        print(f"\n📊 STATISTIQUES FINALES:")
        print(f"  ✅ Étapes validées: {successful_stages}/7")
        print(f"  ⏱️ Temps total: {total_time/60:.1f} minutes ({total_time/3600:.2f}h)")
        print(f"  💾 Modèle final: ai_models/curriculum_stage_7")
        print("\n" + "="*70 + "\n")
        
        # Générer les graphiques d'évolution
        self._generate_evolution_graphs()
    
    def _generate_evolution_graphs(self):
        """Génère des graphiques montrant l'évolution de l'IA à travers les étapes."""
        print("\n📊 Génération des graphiques d'évolution...")
        
        # Créer une figure avec 6 sous-graphiques (2 lignes x 3 colonnes)
        fig = plt.figure(figsize=(18, 10))
        fig.suptitle('Évolution de l\'IA à travers le Curriculum Learning', 
                     fontsize=16, fontweight='bold', y=0.98)
        
        stages = self.stage_metrics["stage_names"]
        x_pos = np.arange(len(stages))
        
        # Couleurs pour chaque étape
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DFE6E9', '#A29BFE']
        
        # 1. Projectiles tirés
        ax1 = plt.subplot(2, 3, 1)
        bars1 = ax1.bar(x_pos, self.stage_metrics["projectiles"], color=colors, alpha=0.8, edgecolor='black')
        ax1.set_xlabel('Étapes', fontweight='bold')
        ax1.set_ylabel('Projectiles par épisode', fontweight='bold')
        ax1.set_title('[TIR] Activité de Tir', fontweight='bold', pad=10)
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels([f'E{i+1}' for i in range(len(stages))], rotation=0)
        ax1.grid(axis='y', alpha=0.3, linestyle='--')
        # Ajouter les valeurs sur les barres
        for i, (bar, val) in enumerate(zip(bars1, self.stage_metrics["projectiles"])):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                    f'{val:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        # 2. Précision de visée
        ax2 = plt.subplot(2, 3, 2)
        bars2 = ax2.bar(x_pos, self.stage_metrics["accuracy"], color=colors, alpha=0.8, edgecolor='black')
        ax2.set_xlabel('Étapes', fontweight='bold')
        ax2.set_ylabel('Précision (%)', fontweight='bold')
        ax2.set_title('[VISEE] Précision de Visée', fontweight='bold', pad=10)
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels([f'E{i+1}' for i in range(len(stages))], rotation=0)
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        ax2.set_ylim(0, 100)
        for i, (bar, val) in enumerate(zip(bars2, self.stage_metrics["accuracy"])):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                    f'{val:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        # 3. Temps de survie
        ax3 = plt.subplot(2, 3, 3)
        bars3 = ax3.bar(x_pos, self.stage_metrics["survival"], color=colors, alpha=0.8, edgecolor='black')
        ax3.set_xlabel('Étapes', fontweight='bold')
        ax3.set_ylabel('Steps survivés', fontweight='bold')
        ax3.set_title('[SURVIE] Temps de Survie', fontweight='bold', pad=10)
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels([f'E{i+1}' for i in range(len(stages))], rotation=0)
        ax3.grid(axis='y', alpha=0.3, linestyle='--')
        for i, (bar, val) in enumerate(zip(bars3, self.stage_metrics["survival"])):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20, 
                    f'{val:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        # 4. Kills par épisode
        ax4 = plt.subplot(2, 3, 4)
        bars4 = ax4.bar(x_pos, self.stage_metrics["kills"], color=colors, alpha=0.8, edgecolor='black')
        ax4.set_xlabel('Étapes', fontweight='bold')
        ax4.set_ylabel('Kills par épisode', fontweight='bold')
        ax4.set_title('[COMBAT] Ennemis Éliminés', fontweight='bold', pad=10)
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels([f'E{i+1}' for i in range(len(stages))], rotation=0)
        ax4.grid(axis='y', alpha=0.3, linestyle='--')
        for i, (bar, val) in enumerate(zip(bars4, self.stage_metrics["kills"])):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, 
                    f'{val:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        # 5. XP collectée et niveau atteint
        ax5 = plt.subplot(2, 3, 5)
        width = 0.35
        bars5a = ax5.bar(x_pos - width/2, self.stage_metrics["xp_collected"], width, 
                        label='Orbes XP', color='#FFEAA7', alpha=0.8, edgecolor='black')
        bars5b = ax5.bar(x_pos + width/2, self.stage_metrics["levels"], width,
                        label='Niveau', color='#A29BFE', alpha=0.8, edgecolor='black')
        ax5.set_xlabel('Étapes', fontweight='bold')
        ax5.set_ylabel('Valeur', fontweight='bold')
        ax5.set_title('[XP] Progression XP et Niveau', fontweight='bold', pad=10)
        ax5.set_xticks(x_pos)
        ax5.set_xticklabels([f'E{i+1}' for i in range(len(stages))], rotation=0)
        ax5.legend(loc='upper left', framealpha=0.9)
        ax5.grid(axis='y', alpha=0.3, linestyle='--')
        
        # 6. Temps d'entraînement par étape
        ax6 = plt.subplot(2, 3, 6)
        bars6 = ax6.bar(x_pos, self.stage_metrics["training_times"], color=colors, alpha=0.8, edgecolor='black')
        ax6.set_xlabel('Étapes', fontweight='bold')
        ax6.set_ylabel('Temps (minutes)', fontweight='bold')
        ax6.set_title('[TEMPS] Temps d\'Entraînement', fontweight='bold', pad=10)
        ax6.set_xticks(x_pos)
        ax6.set_xticklabels([f'E{i+1}' for i in range(len(stages))], rotation=0)
        ax6.grid(axis='y', alpha=0.3, linestyle='--')
        for i, (bar, val) in enumerate(zip(bars6, self.stage_metrics["training_times"])):
            ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{val:.1f}m', ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        # Ajuster l'espacement
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        
        # Sauvegarder le graphique
        output_path = "ai_logs/training_evolution.png"
        os.makedirs("ai_logs", exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ Graphique sauvegardé : {output_path}")
        
        # Afficher le graphique
        plt.show()
        
        # Créer un second graphique : Évolution linéaire des métriques clés
        self._generate_line_evolution_graph()
    
    def _generate_line_evolution_graph(self):
        """Génère un graphique en ligne montrant l'évolution progressive des métriques."""
        fig, ax = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle('Progression Progressive de l\'IA', fontsize=16, fontweight='bold')
        
        stages = list(range(1, len(self.stage_metrics["stage_names"]) + 1))
        
        # 1. Compétences de combat (Projectiles + Kills)
        ax1 = ax[0, 0]
        ax1_twin = ax1.twinx()
        line1 = ax1.plot(stages, self.stage_metrics["projectiles"], 'o-', 
                        linewidth=3, markersize=10, color='#FF6B6B', label='Projectiles/épisode')
        line2 = ax1_twin.plot(stages, self.stage_metrics["kills"], 's-', 
                             linewidth=3, markersize=10, color='#4ECDC4', label='Kills/épisode')
        ax1.set_xlabel('Étape', fontweight='bold', fontsize=12)
        ax1.set_ylabel('Projectiles', fontweight='bold', fontsize=12, color='#FF6B6B')
        ax1_twin.set_ylabel('Kills', fontweight='bold', fontsize=12, color='#4ECDC4')
        ax1.set_title('[COMBAT] Évolution des Compétences de Combat', fontweight='bold', pad=10)
        ax1.tick_params(axis='y', labelcolor='#FF6B6B')
        ax1_twin.tick_params(axis='y', labelcolor='#4ECDC4')
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.set_xticks(stages)
        # Combiner les légendes
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left', framealpha=0.9)
        
        # 2. Précision et Mouvement
        ax2 = ax[0, 1]
        ax2_twin = ax2.twinx()
        line3 = ax2.plot(stages, self.stage_metrics["accuracy"], 'o-', 
                        linewidth=3, markersize=10, color='#A29BFE', label='Précision (%)')
        line4 = ax2_twin.plot(stages, self.stage_metrics["movement"], 's-', 
                             linewidth=3, markersize=10, color='#FD79A8', label='Mouvement')
        ax2.set_xlabel('Étape', fontweight='bold', fontsize=12)
        ax2.set_ylabel('Précision (%)', fontweight='bold', fontsize=12, color='#A29BFE')
        ax2_twin.set_ylabel('Score Mouvement', fontweight='bold', fontsize=12, color='#FD79A8')
        ax2.set_title('[VISEE] Précision et Mobilité', fontweight='bold', pad=10)
        ax2.tick_params(axis='y', labelcolor='#A29BFE')
        ax2_twin.tick_params(axis='y', labelcolor='#FD79A8')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_xticks(stages)
        lines = line3 + line4
        labels = [l.get_label() for l in lines]
        ax2.legend(lines, labels, loc='upper left', framealpha=0.9)
        
        # 3. Survie et Niveau
        ax3 = ax[1, 0]
        ax3_twin = ax3.twinx()
        line5 = ax3.plot(stages, self.stage_metrics["survival"], 'o-', 
                        linewidth=3, markersize=10, color='#00B894', label='Survie (steps)')
        line6 = ax3_twin.plot(stages, self.stage_metrics["levels"], 's-', 
                             linewidth=3, markersize=10, color='#FDCB6E', label='Niveau')
        ax3.set_xlabel('Étape', fontweight='bold', fontsize=12)
        ax3.set_ylabel('Temps de Survie', fontweight='bold', fontsize=12, color='#00B894')
        ax3_twin.set_ylabel('Niveau Atteint', fontweight='bold', fontsize=12, color='#FDCB6E')
        ax3.set_title('[SURVIE] Survie et Progression', fontweight='bold', pad=10)
        ax3.tick_params(axis='y', labelcolor='#00B894')
        ax3_twin.tick_params(axis='y', labelcolor='#FDCB6E')
        ax3.grid(True, alpha=0.3, linestyle='--')
        ax3.set_xticks(stages)
        lines = line5 + line6
        labels = [l.get_label() for l in lines]
        ax3.legend(lines, labels, loc='upper left', framealpha=0.9)
        
        # 4. Résumé global (Score composite)
        ax4 = ax[1, 1]
        # Créer un score composite normalisé (0-100)
        composite_scores = []
        for i in range(len(stages)):
            # Normaliser chaque métrique et créer un score composite
            proj_score = min(100, (self.stage_metrics["projectiles"][i] / 20) * 100)
            acc_score = self.stage_metrics["accuracy"][i]
            surv_score = min(100, (self.stage_metrics["survival"][i] / 2000) * 100)
            kill_score = min(100, (self.stage_metrics["kills"][i] / 10) * 100)
            level_score = min(100, (self.stage_metrics["levels"][i] / 5) * 100)
            
            composite = (proj_score + acc_score + surv_score + kill_score + level_score) / 5
            composite_scores.append(composite)
        
        bars = ax4.bar(stages, composite_scores, color='#6C5CE7', alpha=0.8, edgecolor='black', width=0.6)
        ax4.set_xlabel('Étape', fontweight='bold', fontsize=12)
        ax4.set_ylabel('Score Global (%)', fontweight='bold', fontsize=12)
        ax4.set_title('[GLOBAL] Performance Globale', fontweight='bold', pad=10)
        ax4.set_ylim(0, 100)
        ax4.grid(axis='y', alpha=0.3, linestyle='--')
        ax4.set_xticks(stages)
        
        # Ajouter les valeurs sur les barres
        for bar, score in zip(bars, composite_scores):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                    f'{score:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        # Ligne de tendance
        z = np.polyfit(stages, composite_scores, 2)
        p = np.poly1d(z)
        x_smooth = np.linspace(stages[0], stages[-1], 100)
        ax4.plot(x_smooth, p(x_smooth), "--", color='red', linewidth=2, alpha=0.7, label='Tendance')
        ax4.legend(loc='lower right', framealpha=0.9)
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.97])
        
        # Sauvegarder
        output_path = "ai_logs/training_progression.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ Graphique de progression sauvegardé : {output_path}")
        
        plt.show()
        print("\n📊 Tous les graphiques ont été générés avec succès!")
        print(f"   • ai_logs/training_evolution.png")
        print(f"   • ai_logs/training_progression.png")
def main():
    """Point d'entrée principal."""
    print("🎓 CURRICULUM LEARNING TRAINER - 7 ÉTAPES")
    print("Apprentissage progressif :")
    print("  1. 🎯 Tir")
    print("  2. 🎨 Visée")
    print("  3. 🏃 Mouvement")
    print("  4. 🛡️ Survie")
    print("  5. 💎 Collecte d'orbes XP")
    print("  6. 🃏 Sélection de cartes")
    print("  7. 🏆 Maîtrise complète")
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
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
        """� ÉTAPE 2: Récompenses focalisées sur la VISÉE."""
        reward = 0.0
        
        # OBJECTIF PRINCIPAL : VISER CORRECTEMENT LES ENNEMIS
        if hasattr(env, 'last_action') and len(env.enemy_spawner.enemies) > 0:
            move_x, move_y, attack_x, attack_y, should_attack = env.last_action
            
            # Trouver l'ennemi le plus proche
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
                
                # Récompenser la bonne visée (même sans tirer)
                if dot_product > 0.5:  # Bonne direction
                    reward += dot_product * 8.0  # TRÈS généreux pour bien viser
                
                # Bonus énorme si tire ET vise bien
                if should_attack > 0.5 and dot_product > 0.3:
                    reward += 12.0  # JACKPOT pour tir bien visé
        
        # Garder l'acquis de l'étape 1 (tirer) - AUGMENTÉ
        current_projectile_count = len([p for p in env.player.projectiles if p.active])
        projectiles_fired_this_step = max(0, current_projectile_count - env.last_projectile_count)
        if projectiles_fired_this_step > 0:
            reward += projectiles_fired_this_step * 5.0  # 🔥 Augmenté de 3.0 à 5.0
        env.last_projectile_count = current_projectile_count
        
        # Bonus pour kills (preuve de bonne visée) - AUGMENTÉ
        reward += env.enemies_killed_by_projectiles * 30.0  # 🔥 Augmenté de 20.0 à 30.0
        
        # Survie minimale
        reward += 0.1
        
        # Pénalité mort
        if env.player.health <= 0:
            reward -= 25.0
            
        return reward
    
    def _stage3_reward(self, env) -> float:
        """�🏃 ÉTAPE 3: Récompenses focalisées sur le MOUVEMENT."""
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
        
        # Garder les acquis précédents (tir et visée) - AUGMENTÉ
        current_projectile_count = len([p for p in env.player.projectiles if p.active])
        projectiles_fired_this_step = max(0, current_projectile_count - env.last_projectile_count)
        if projectiles_fired_this_step > 0:
            reward += projectiles_fired_this_step * 4.0  # 🔥 Augmenté de 2.0 à 4.0
        env.last_projectile_count = current_projectile_count
        
        # Bonus pour kills - AJOUTÉ
        reward += env.enemies_killed_by_projectiles * 20.0  # 🔥 Nouveau bonus
        
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
    
    def _stage4_reward(self, env) -> float:
        """🛡️ ÉTAPE 4: Récompenses focalisées sur la SURVIE."""
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
    
    def _stage4_reward(self, env) -> float:
        """🛡️ ÉTAPE 4: Récompenses focalisées sur la SURVIE."""
        reward = 0.0
        
        # OBJECTIF PRINCIPAL : SURVIVRE LONGTEMPS
        reward += 0.5  # Bonus de survie augmenté
        
        # Bonus pour kills (combinaison tir + survie)
        reward += env.enemies_killed_by_projectiles * 15.0
        
        # Garder les acquis (tir, visée, mouvement)
        if hasattr(env, 'last_action'):
            move_x, move_y, attack_x, attack_y, should_attack = env.last_action
            is_moving = abs(move_x) > 0.1 or abs(move_y) > 0.1
            if is_moving:
                reward += 1.0
        
        # TIR MAINTENU - AUGMENTÉ
        current_projectile_count = len([p for p in env.player.projectiles if p.active])
        projectiles_fired_this_step = max(0, current_projectile_count - env.last_projectile_count)
        if projectiles_fired_this_step > 0:
            reward += projectiles_fired_this_step * 3.0  # 🔥 Augmenté de 1.0 à 3.0
        env.last_projectile_count = current_projectile_count
        
        # Gestion des dégâts (critique pour survie)
        health_lost = env.last_player_health - env.player.health
        if health_lost > 0:
            reward -= health_lost * 5.0
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
            reward += 0.5
        
        # Pénalité mort massive
        if env.player.health <= 0:
            reward -= 100.0
            
        return reward
    
    def _stage5_reward(self, env) -> float:
        """💎 ÉTAPE 5: Récompenses AMÉLIORÉES pour COLLECTE D'ORBES D'XP."""
        reward = 0.0
        
        # ═══════════════════════════════════════════════════════
        # OBJECTIF PRINCIPAL : COLLECTER LES ORBES D'XP
        # ═══════════════════════════════════════════════════════
        
        # 1. RÉCOMPENSE MASSIVE POUR COLLECTE
        xp_gained = env.xp_system.current_xp - getattr(env, 'last_xp_count', env.xp_system.current_xp)
        if xp_gained > 0:
            reward += xp_gained * 5.0  # 🔥 Augmenté de 2.0 à 5.0 (250% plus!)
            
            # BONUS COMBO : Collecter plusieurs orbes dans un court laps de temps
            if not hasattr(env, 'orb_collection_streak'):
                env.orb_collection_streak = 0
                env.last_collection_time = 0
            
            # Si collecte rapide (< 100 steps depuis dernière)
            if (env.step_count - env.last_collection_time) < 100:
                env.orb_collection_streak += 1
                reward += env.orb_collection_streak * 10.0  # 🔥 COMBO MULTIPLIER!
            else:
                env.orb_collection_streak = 1
            
            env.last_collection_time = env.step_count
            env.last_xp_count = env.xp_system.current_xp
        
        # 2. RÉCOMPENSE POUR PROXIMITÉ AUX ORBES
        if len(env.xp_orbs) > 0:
            player_pos = (env.player.rect.centerx, env.player.rect.centery)
            
            # Trouver l'orbe le plus proche
            closest_orb = min(env.xp_orbs,
                             key=lambda orb: ((orb.x - player_pos[0])**2 + 
                                            (orb.y - player_pos[1])**2)**0.5)
            
            distance = ((closest_orb.x - player_pos[0])**2 + 
                       (closest_orb.y - player_pos[1])**2)**0.5
            
            # 🔥 BONUS DE PROXIMITÉ (plus proche = meilleur)
            if distance < 150:  # Rayon d'attraction magnétique
                proximity_bonus = (150 - distance) / 150 * 5.0
                reward += proximity_bonus  # Max +5 si très proche
            
            # 3. RÉCOMPENSE POUR SE DIRIGER VERS L'ORBE
            if hasattr(env, 'last_action') and distance > 10:
                # Direction vers l'orbe
                dx = closest_orb.x - player_pos[0]
                dy = closest_orb.y - player_pos[1]
                length = (dx**2 + dy**2)**0.5
                
                if length > 0:
                    dx /= length
                    dy /= length
                    
                    # Mouvement vers l'orbe
                    move_x, move_y, _, _, _ = env.last_action
                    dot_product = dx * move_x + dy * move_y
                    
                    if dot_product > 0.2:  # Plus tolérant (était 0.3)
                        reward += dot_product * 8.0  # 🔥 Augmenté de 3.0 à 8.0
            
            # 4. BONUS POUR NOMBRE D'ORBES DISPONIBLES
            # Plus il y a d'orbes, plus l'IA doit être motivée à les collecter
            num_orbs = len(env.xp_orbs)
            if num_orbs >= 3:
                reward += num_orbs * 0.5  # Incitation à aller nettoyer le terrain
        
        # ═══════════════════════════════════════════════════════
        # GARDER LES ACQUIS (mais avec moins de poids)
        # ═══════════════════════════════════════════════════════
        
        # Kills (important car créent des orbes!) - AUGMENTÉ
        reward += env.enemies_killed_by_projectiles * 25.0  # 🔥 Augmenté de 15 à 25
        
        # Tir (garder le comportement) - AUGMENTÉ
        current_projectile_count = len([p for p in env.player.projectiles if p.active])
        projectiles_fired_this_step = max(0, current_projectile_count - getattr(env, 'last_projectile_count', 0))
        if projectiles_fired_this_step > 0:
            reward += projectiles_fired_this_step * 2.0  # 🔥 Augmenté de 0.8 à 2.0
        env.last_projectile_count = current_projectile_count
        
        # Survie
        reward += 0.4  # Augmenté de 0.3
        
        # ═══════════════════════════════════════════════════════
        # PÉNALITÉS AJUSTÉES
        # ═══════════════════════════════════════════════════════
        
        # Pénalité dégâts RÉDUITE (collecter = risque acceptable)
        health_lost = getattr(env, 'last_player_health', env.player.health) - env.player.health
        if health_lost > 0:
            reward -= health_lost * 2.0  # RÉDUIT de 3.0 à 2.0 (risque acceptable)
            env.last_player_health = env.player.health
        
        # Pénalité mort RÉDUITE (encourager prise de risque calculée)
        if env.player.health <= 0:
            reward -= 60.0  # RÉDUIT de -80 à -60
            
        return reward
    
    def _stage6_reward(self, env) -> float:
        """🃏 ÉTAPE 6: Récompenses focalisées sur la SÉLECTION DE CARTES."""
        reward = 0.0
        
        # OBJECTIF PRINCIPAL : SÉLECTIONNER DES CARTES STRATÉGIQUEMENT
        # Vérifier si une carte a été sélectionnée
        if not hasattr(env, 'last_cards_selected'):
            env.last_cards_selected = 0
        
        # Simuler level ups et sélection de cartes
        current_level = env.xp_system.level
        if not hasattr(env, 'last_level'):
            env.last_level = current_level
        
        if current_level > env.last_level:
            # Level up! Récompense massive
            reward += 50.0
            env.last_cards_selected += 1
            env.last_level = current_level
        
        # Récompenser la collecte d'XP (pour atteindre les level ups)
        xp_gained = env.xp_system.current_xp - getattr(env, 'last_xp_count', env.xp_system.current_xp)
        if xp_gained > 0:
            reward += xp_gained * 1.5
        env.last_xp_count = env.xp_system.current_xp
        
        # Garder tous les acquis - AUGMENTÉ
        reward += env.enemies_killed_by_projectiles * 20.0  # 🔥 Augmenté de 12.0 à 20.0
        
        # TIR MAINTENU - AUGMENTÉ
        current_projectile_count = len([p for p in env.player.projectiles if p.active])
        projectiles_fired_this_step = max(0, current_projectile_count - env.last_projectile_count)
        if projectiles_fired_this_step > 0:
            reward += projectiles_fired_this_step * 2.0  # 🔥 Augmenté de 0.8 à 2.0
        env.last_projectile_count = current_projectile_count
        
        # Survie
        reward += 0.4
        
        # Pénalité dégâts
        health_lost = env.last_player_health - env.player.health
        if health_lost > 0:
            reward -= health_lost * 4.0
            env.last_player_health = env.player.health
        
        # Pénalité mort
        if env.player.health <= 0:
            reward -= 100.0
            
        return reward
    
    def _stage7_reward(self, env) -> float:
        """🏆 ÉTAPE 7: MAÎTRISE COMPLÈTE - Survie avec améliorations."""
        reward = 0.0
        
        # OBJECTIF FINAL : EXCELLENCE DANS TOUS LES DOMAINES
        
        # Survie longue durée
        reward += 0.6
        
        # Kills avec bonus croissant - AUGMENTÉ
        reward += env.enemies_killed_by_projectiles * 30.0  # 🔥 Augmenté de 20.0 à 30.0
        
        # Bonus pour niveau élevé (preuve d'améliorations)
        current_level = env.xp_system.level
        if current_level >= 5:
            reward += (current_level - 4) * 10.0  # Bonus exponentiel
        
        # Collecte d'XP
        xp_gained = env.xp_system.current_xp - getattr(env, 'last_xp_count', env.xp_system.current_xp)
        if xp_gained > 0:
            reward += xp_gained * 1.0
        env.last_xp_count = env.xp_system.current_xp
        
        # Maintien des compétences de base - AUGMENTÉ
        current_projectile_count = len([p for p in env.player.projectiles if p.active])
        projectiles_fired_this_step = max(0, current_projectile_count - env.last_projectile_count)
        if projectiles_fired_this_step > 0:
            reward += projectiles_fired_this_step * 3.0  # 🔥 Augmenté de 1.5 à 3.0
        env.last_projectile_count = current_projectile_count
        
        # Mouvement tactique
        if hasattr(env, 'last_action'):
            move_x, move_y, _, _, _ = env.last_action
            is_moving = abs(move_x) > 0.1 or abs(move_y) > 0.1
            if is_moving:
                reward += 1.5
        
        # Pénalité dégâts très forte
        health_lost = env.last_player_health - env.player.health
        if health_lost > 0:
            reward -= health_lost * 8.0
            env.last_player_health = env.player.health
        
        # Position tactique optimale
        player_x = env.player.rect.centerx
        player_y = env.player.rect.centery
        min_distance_to_edge = min(player_x, env.screen_width - player_x, 
                                 player_y, env.screen_height - player_y)
        if min_distance_to_edge < 100:
            reward -= 5.0
        elif min_distance_to_edge > 200:
            reward += 1.0
        
        # Pénalité mort MASSIVE
        if env.player.health <= 0:
            reward -= 150.0
            
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
        
        for stage in [1, 2, 3, 4, 5, 6, 7]:
            success = self.train_stage_with_validation(stage)
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
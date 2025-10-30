"""
Fonctions de récompense optimisées pour le curriculum learning.
Ces fonctions remplacent les calculs complexes par des versions plus rapides.
"""

def stage2_reward_optimized(env) -> float:
    """🎨 ÉTAPE 2: Récompenses focalisées sur la VISÉE (optimisé)."""
    reward = 0.1  # Survie de base
    
    # OBJECTIF PRINCIPAL : VISER CORRECTEMENT LES ENNEMIS
    if hasattr(env, 'last_action') and len(env.enemy_spawner.enemies) > 0:
        attack_x, attack_y, should_attack = env.last_action[2], env.last_action[3], env.last_action[4]
        
        # Utiliser premier ennemi (optimisation)
        enemy = env.enemy_spawner.enemies[0]
        dx = enemy.rect.centerx - env.player.rect.centerx
        dy = enemy.rect.centery - env.player.rect.centery
        dist_sq = dx*dx + dy*dy
        
        if dist_sq > 0:
            # Produit scalaire sans racine carrée ni normalisation complète
            dist = dist_sq ** 0.5
            dot = (dx * attack_x + dy * attack_y) / dist
            
            if dot > 0.5:
                reward += dot * 8.0
            
            if should_attack > 0.5 and dot > 0.3:
                reward += 12.0
    
    # Garder l'acquis de l'étape 1
    current_projectile_count = len([p for p in env.player.projectiles if p.active])
    projectiles_fired = max(0, current_projectile_count - env.last_projectile_count)
    if projectiles_fired > 0:
        reward += projectiles_fired * 5.0
    env.last_projectile_count = current_projectile_count
    
    # Bonus pour kills
    reward += env.enemies_killed_by_projectiles * 30.0
    
    # Pénalité mort
    if env.player.health <= 0:
        reward -= 25.0
        
    return reward


def stage3_reward_optimized(env) -> float:
    """🏃 ÉTAPE 3: Récompenses focalisées sur le MOUVEMENT (optimisé)."""
    reward = 0.2  # Survie de base
    
    # OBJECTIF PRINCIPAL : SE DÉPLACER
    if hasattr(env, 'last_action'):
        move_x, move_y = env.last_action[0], env.last_action[1]
        movement = move_x*move_x + move_y*move_y  # Pas besoin de racine carrée
        
        if movement > 0.01:  # Is moving
            reward += 3.0
            
            # S'éloigner des ennemis (simplifié)
            if len(env.enemy_spawner.enemies) > 0:
                enemy = env.enemy_spawner.enemies[0]
                dx = env.player.rect.centerx - enemy.rect.centerx
                dy = env.player.rect.centery - enemy.rect.centery
                
                # Produit scalaire simplifié (sans normalisation)
                dot = dx * move_x + dy * move_y
                if dot > 0:
                    reward += 2.0
    
    # Garder les acquis
    current_projectile_count = len([p for p in env.player.projectiles if p.active])
    projectiles_fired = max(0, current_projectile_count - env.last_projectile_count)
    if projectiles_fired > 0:
        reward += projectiles_fired * 4.0
    env.last_projectile_count = current_projectile_count
    
    reward += env.enemies_killed_by_projectiles * 20.0
    
    # Éviter les bords (simplifié)
    px, py = env.player.rect.centerx, env.player.rect.centery
    if px < 50 or px > env.screen_width - 50 or py < 50 or py > env.screen_height - 50:
        reward -= 2.0
    
    # Pénalité dégâts
    health_lost = env.last_player_health - env.player.health
    if health_lost > 0:
        reward -= health_lost * 2.0
        env.last_player_health = env.player.health
    
    # Pénalité mort
    if env.player.health <= 0:
        reward -= 30.0
        
    return reward


def stage4_reward_optimized(env) -> float:
    """🛡️ ÉTAPE 4: Récompenses focalisées sur la SURVIE (optimisé)."""
    reward = 0.5  # Survie augmentée
    
    # Bonus pour kills
    reward += env.enemies_killed_by_projectiles * 15.0
    
    # Mouvement basique
    if hasattr(env, 'last_action'):
        move_x, move_y = env.last_action[0], env.last_action[1]
        if abs(move_x) > 0.1 or abs(move_y) > 0.1:
            reward += 1.0
    
    # TIR MAINTENU
    current_projectile_count = len([p for p in env.player.projectiles if p.active])
    projectiles_fired = max(0, current_projectile_count - env.last_projectile_count)
    if projectiles_fired > 0:
        reward += projectiles_fired * 3.0
    env.last_projectile_count = current_projectile_count
    
    # Gestion des dégâts
    health_lost = env.last_player_health - env.player.health
    if health_lost > 0:
        reward -= health_lost * 5.0
        env.last_player_health = env.player.health
    
    # Position tactique (simplifié)
    px, py = env.player.rect.centerx, env.player.rect.centery
    min_edge = min(px, env.screen_width - px, py, env.screen_height - py)
    if min_edge < 100:
        reward -= 3.0
    elif min_edge > 200:
        reward += 0.5
    
    # Pénalité mort massive
    if env.player.health <= 0:
        reward -= 100.0
        
    return reward


def stage5_reward_optimized(env) -> float:
    """💎 ÉTAPE 5: Récompenses pour COLLECTE D'ORBES D'XP (optimisé)."""
    reward = 0.4  # Survie
    
    # COLLECTE D'XP (simplifié sans combo streak)
    xp_gained = env.xp_system.current_xp - getattr(env, 'last_xp_count', env.xp_system.current_xp)
    if xp_gained > 0:
        reward += xp_gained * 5.0
        env.last_xp_count = env.xp_system.current_xp
    
    # PROXIMITÉ AUX ORBES (simplifié)
    if len(env.xp_orbs) > 0:
        px, py = env.player.rect.centerx, env.player.rect.centery
        
        # Premier orbe au lieu du plus proche (optimisation)
        orb = env.xp_orbs[0]
        dist_sq = (orb.x - px)**2 + (orb.y - py)**2
        
        # Bonus proximité
        if dist_sq < 22500:  # 150^2
            reward += (22500 - dist_sq) / 22500 * 5.0
        
        # Direction vers l'orbe (simplifié)
        if hasattr(env, 'last_action') and dist_sq > 100:
            dx, dy = orb.x - px, orb.y - py
            move_x, move_y = env.last_action[0], env.last_action[1]
            dot = dx * move_x + dy * move_y
            
            if dot > 0:
                reward += 8.0
        
        # Bonus pour nombre d'orbes
        if len(env.xp_orbs) >= 3:
            reward += len(env.xp_orbs) * 0.5
    
    # Garder les acquis
    reward += env.enemies_killed_by_projectiles * 25.0
    
    current_projectile_count = len([p for p in env.player.projectiles if p.active])
    projectiles_fired = max(0, current_projectile_count - getattr(env, 'last_projectile_count', 0))
    if projectiles_fired > 0:
        reward += projectiles_fired * 2.0
    env.last_projectile_count = current_projectile_count
    
    # Pénalités réduites
    health_lost = getattr(env, 'last_player_health', env.player.health) - env.player.health
    if health_lost > 0:
        reward -= health_lost * 2.0
        env.last_player_health = env.player.health
    
    if env.player.health <= 0:
        reward -= 60.0
        
    return reward


def stage6_reward_optimized(env) -> float:
    """🃏 ÉTAPE 6: Récompenses pour SÉLECTION DE CARTES (optimisé)."""
    reward = 0.4  # Survie
    
    # Level ups
    current_level = env.xp_system.level
    if not hasattr(env, 'last_level'):
        env.last_level = current_level
    
    if current_level > env.last_level:
        reward += 50.0
        env.last_level = current_level
    
    # Collecte d'XP
    xp_gained = env.xp_system.current_xp - getattr(env, 'last_xp_count', env.xp_system.current_xp)
    if xp_gained > 0:
        reward += xp_gained * 1.5
        env.last_xp_count = env.xp_system.current_xp
    
    # Garder acquis
    reward += env.enemies_killed_by_projectiles * 20.0
    
    current_projectile_count = len([p for p in env.player.projectiles if p.active])
    projectiles_fired = max(0, current_projectile_count - env.last_projectile_count)
    if projectiles_fired > 0:
        reward += projectiles_fired * 2.0
    env.last_projectile_count = current_projectile_count
    
    # Pénalité dégâts
    health_lost = env.last_player_health - env.player.health
    if health_lost > 0:
        reward -= health_lost * 4.0
        env.last_player_health = env.player.health
    
    if env.player.health <= 0:
        reward -= 100.0
        
    return reward


def stage7_reward_optimized(env) -> float:
    """🏆 ÉTAPE 7: MAÎTRISE COMPLÈTE (optimisé)."""
    reward = 0.6  # Survie
    
    # Kills
    reward += env.enemies_killed_by_projectiles * 30.0
    
    # Bonus niveau
    current_level = env.xp_system.level
    if current_level >= 5:
        reward += (current_level - 4) * 10.0
    
    # Collecte d'XP
    xp_gained = env.xp_system.current_xp - getattr(env, 'last_xp_count', env.xp_system.current_xp)
    if xp_gained > 0:
        reward += xp_gained * 1.0
        env.last_xp_count = env.xp_system.current_xp
    
    # Tir
    current_projectile_count = len([p for p in env.player.projectiles if p.active])
    projectiles_fired = max(0, current_projectile_count - env.last_projectile_count)
    if projectiles_fired > 0:
        reward += projectiles_fired * 3.0
    env.last_projectile_count = current_projectile_count
    
    # Mouvement
    if hasattr(env, 'last_action'):
        move_x, move_y = env.last_action[0], env.last_action[1]
        if abs(move_x) > 0.1 or abs(move_y) > 0.1:
            reward += 1.5
    
    # Pénalité dégâts
    health_lost = env.last_player_health - env.player.health
    if health_lost > 0:
        reward -= health_lost * 8.0
        env.last_player_health = env.player.health
    
    # Position tactique
    px, py = env.player.rect.centerx, env.player.rect.centery
    min_edge = min(px, env.screen_width - px, py, env.screen_height - py)
    if min_edge < 100:
        reward -= 5.0
    elif min_edge > 200:
        reward += 1.0
    
    if env.player.health <= 0:
        reward -= 150.0
        
    return reward

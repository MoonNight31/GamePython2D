"""
Système d'IA Adaptative pour les Ennemis
Analyse les performances du joueur et adapte la difficulté des ennemis en conséquence.
"""

import time
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class PlayerMetrics:
    """Métriques de performance du joueur."""
    kills_per_minute: float = 0.0
    damage_taken_per_minute: float = 0.0
    survival_time: float = 0.0
    level: int = 1
    health_ratio: float = 1.0
    projectiles_fired: int = 0
    accuracy: float = 0.0
    xp_collected: int = 0
    

class AdaptiveEnemyAI:
    """
    Système d'IA qui adapte la difficulté des ennemis selon les performances du joueur.
    Plus le joueur est bon, plus les ennemis deviennent forts et intelligents.
    """
    
    def __init__(self):
        # Métriques du joueur
        self.metrics = PlayerMetrics()
        
        # Historique pour calculer les moyennes
        self.kills_history: List[float] = []
        self.damage_history: List[float] = []
        self.start_time = time.time()
        
        # Compteurs
        self.total_kills = 0
        self.total_damage_taken = 0
        self.total_projectiles_fired = 0
        self.total_hits = 0
        
        # Niveaux d'adaptation (0.0 à 2.0)
        self.difficulty_multiplier = 1.0
        self.adaptation_rate = 0.05  # Vitesse d'adaptation
        
        # Seuils de performance
        self.performance_thresholds = {
            'low': 0.5,      # Joueur en difficulté
            'medium': 1.0,   # Performance normale
            'high': 1.5,     # Joueur performant
            'expert': 2.0    # Joueur expert
        }
        
        # Buffs ennemis selon la difficulté
        self.enemy_buffs = {
            'health_multiplier': 1.0,
            'speed_multiplier': 1.0,
            'damage_multiplier': 1.0,
            'ai_intelligence': 1.0,  # Améliore le comportement
            'spawn_rate_multiplier': 1.0
        }
        
        # Temps depuis la dernière mise à jour
        self.last_update = time.time()
        self.update_interval = 5.0  # Mise à jour toutes les 5 secondes
        
    def update_player_metrics(self, player_health: int, player_max_health: int, 
                             player_level: int, xp_collected: int):
        """Met à jour les métriques du joueur."""
        current_time = time.time()
        elapsed_time = (current_time - self.start_time) / 60.0  # En minutes
        
        # Métriques de base
        self.metrics.survival_time = elapsed_time
        self.metrics.level = player_level
        self.metrics.health_ratio = player_health / player_max_health
        self.metrics.xp_collected = xp_collected
        
        # Calcul des taux
        if elapsed_time > 0:
            self.metrics.kills_per_minute = self.total_kills / elapsed_time
            self.metrics.damage_taken_per_minute = self.total_damage_taken / elapsed_time
            
            # Précision
            if self.total_projectiles_fired > 0:
                self.metrics.accuracy = self.total_hits / self.total_projectiles_fired
    
    def register_kill(self):
        """Enregistre un kill."""
        self.total_kills += 1
        self.kills_history.append(time.time())
        # Garder seulement les 20 derniers kills pour la moyenne
        if len(self.kills_history) > 20:
            self.kills_history.pop(0)
    
    def register_damage_taken(self, damage: int):
        """Enregistre des dégâts subis."""
        self.total_damage_taken += damage
        self.damage_history.append(time.time())
        if len(self.damage_history) > 20:
            self.damage_history.pop(0)
    
    def register_projectile_fired(self):
        """Enregistre un tir."""
        self.total_projectiles_fired += 1
    
    def register_hit(self):
        """Enregistre un tir réussi."""
        self.total_hits += 1
    
    def calculate_performance_score(self) -> float:
        """
        Calcule un score de performance du joueur (0.0 à 2.0+).
        Plus le score est élevé, plus le joueur est performant.
        """
        score = 1.0  # Score de base
        
        # Facteur 1: Kills par minute (cible: 5-10 kpm)
        if self.metrics.kills_per_minute > 0:
            kpm_factor = min(self.metrics.kills_per_minute / 7.5, 1.5)
            score *= kpm_factor
        
        # Facteur 2: Niveau (plus haut = meilleur)
        level_factor = 1.0 + (self.metrics.level - 1) * 0.05
        score *= min(level_factor, 1.5)
        
        # Facteur 3: Ratio de santé (encourage à rester en vie)
        health_factor = 0.7 + (self.metrics.health_ratio * 0.3)
        score *= health_factor
        
        # Facteur 4: Précision (bonus si >50%)
        if self.metrics.accuracy > 0.5:
            accuracy_factor = 1.0 + (self.metrics.accuracy - 0.5)
            score *= min(accuracy_factor, 1.3)
        
        # Facteur 5: Temps de survie (bonus progressif)
        survival_factor = 1.0 + min(self.metrics.survival_time * 0.02, 0.5)
        score *= survival_factor
        
        # Pénalité si beaucoup de dégâts subis
        if self.metrics.damage_taken_per_minute > 50:
            damage_penalty = max(0.7, 1.0 - (self.metrics.damage_taken_per_minute - 50) * 0.005)
            score *= damage_penalty
        
        return max(0.3, min(score, 2.5))  # Limiter entre 0.3 et 2.5
    
    def update_difficulty(self):
        """Met à jour le multiplicateur de difficulté basé sur les performances."""
        current_time = time.time()
        
        # Mettre à jour seulement tous les X secondes
        if current_time - self.last_update < self.update_interval:
            return
        
        self.last_update = current_time
        
        # Calculer le score de performance
        performance_score = self.calculate_performance_score()
        
        # Ajuster progressivement vers le score cible
        target_difficulty = performance_score
        diff = target_difficulty - self.difficulty_multiplier
        
        # Adaptation progressive (éviter les sauts brusques)
        self.difficulty_multiplier += diff * self.adaptation_rate
        
        # Limiter entre 0.5 et 2.5
        self.difficulty_multiplier = max(0.5, min(self.difficulty_multiplier, 2.5))
        
        # Mettre à jour les buffs ennemis
        self._calculate_enemy_buffs()
    
    def _calculate_enemy_buffs(self):
        """Calcule les buffs à appliquer aux ennemis selon la difficulté."""
        base = self.difficulty_multiplier
        
        # Santé augmente linéairement
        self.enemy_buffs['health_multiplier'] = 0.8 + (base * 0.4)  # 0.8x à 1.8x
        
        # Vitesse augmente modérément
        self.enemy_buffs['speed_multiplier'] = 0.9 + (base * 0.3)  # 0.9x à 1.65x
        
        # Dégâts augmentent significativement
        self.enemy_buffs['damage_multiplier'] = 0.85 + (base * 0.5)  # 0.85x à 2.1x
        
        # Intelligence augmente (comportement plus intelligent)
        # 1.0 = comportement de base, 2.0 = comportement très intelligent
        self.enemy_buffs['ai_intelligence'] = base
        
        # Taux de spawn augmente légèrement
        self.enemy_buffs['spawn_rate_multiplier'] = 0.95 + (base * 0.25)  # 0.95x à 1.57x
    
    def apply_buffs_to_enemy(self, enemy_stats: Dict) -> Dict:
        """
        Applique les buffs d'adaptation aux stats d'un ennemi.
        
        Args:
            enemy_stats: Dictionnaire avec 'health', 'speed', 'damage'
        
        Returns:
            Dictionnaire avec les stats modifiées
        """
        buffed_stats = {
            'health': int(enemy_stats.get('health', 30) * self.enemy_buffs['health_multiplier']),
            'speed': int(enemy_stats.get('speed', 80) * self.enemy_buffs['speed_multiplier']),
            'damage': int(enemy_stats.get('damage', 15) * self.enemy_buffs['damage_multiplier']),
            'xp_value': enemy_stats.get('xp_value', 10),  # XP reste identique
            'ai_intelligence': self.enemy_buffs['ai_intelligence']
        }
        
        return buffed_stats
    
    def get_spawn_interval_modifier(self) -> float:
        """Retourne le modificateur d'intervalle de spawn (plus bas = spawn plus rapide)."""
        return 1.0 / self.enemy_buffs['spawn_rate_multiplier']
    
    def should_use_advanced_ai(self) -> bool:
        """Détermine si les ennemis doivent utiliser une IA avancée."""
        return self.enemy_buffs['ai_intelligence'] >= 1.3
    
    def get_difficulty_level(self) -> str:
        """Retourne le niveau de difficulté actuel."""
        if self.difficulty_multiplier < 0.8:
            return "Très Facile"
        elif self.difficulty_multiplier < 1.2:
            return "Facile"
        elif self.difficulty_multiplier < 1.5:
            return "Normal"
        elif self.difficulty_multiplier < 1.8:
            return "Difficile"
        elif self.difficulty_multiplier < 2.2:
            return "Très Difficile"
        else:
            return "Expert"
    
    def get_stats_summary(self) -> Dict:
        """Retourne un résumé des statistiques pour l'affichage."""
        return {
            'difficulty_level': self.get_difficulty_level(),
            'difficulty_multiplier': f"{self.difficulty_multiplier:.2f}x",
            'performance_score': f"{self.calculate_performance_score():.2f}",
            'kills_per_minute': f"{self.metrics.kills_per_minute:.1f}",
            'accuracy': f"{self.metrics.accuracy * 100:.1f}%",
            'health_buff': f"+{(self.enemy_buffs['health_multiplier'] - 1) * 100:.0f}%",
            'speed_buff': f"+{(self.enemy_buffs['speed_multiplier'] - 1) * 100:.0f}%",
            'damage_buff': f"+{(self.enemy_buffs['damage_multiplier'] - 1) * 100:.0f}%",
        }
    
    def reset(self):
        """Réinitialise le système d'adaptation."""
        self.metrics = PlayerMetrics()
        self.kills_history.clear()
        self.damage_history.clear()
        self.start_time = time.time()
        self.total_kills = 0
        self.total_damage_taken = 0
        self.total_projectiles_fired = 0
        self.total_hits = 0
        self.difficulty_multiplier = 1.0
        self.last_update = time.time()

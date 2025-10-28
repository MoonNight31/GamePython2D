import math

class XPSystem:
    """Système de gestion de l'expérience et des niveaux."""
    
    def __init__(self):
        self.level = 1
        self.current_xp = 0
        
        # Configuration de la progression
        self.base_xp_requirement = 100
        self.xp_growth_factor = 1.5
        
        self.xp_to_next_level = self._calculate_xp_required(self.level + 1)
        
        # Statistiques
        self.total_xp_gained = 0
        self.levels_gained = 0
    
    def _calculate_xp_required(self, level: int) -> int:
        """Calcule l'XP total requis pour atteindre un niveau donné."""
        if level <= 1:
            return 0
        
        # Formule : base_xp * (growth_factor ^ (level - 1))
        return int(self.base_xp_requirement * (self.xp_growth_factor ** (level - 2)))
    
    def _calculate_xp_for_next_level(self) -> int:
        """Calcule l'XP nécessaire pour le prochain niveau."""
        current_level_xp = self._calculate_xp_required(self.level)
        next_level_xp = self._calculate_xp_required(self.level + 1)
        return next_level_xp - current_level_xp
    
    def gain_xp(self, amount: int) -> int:
        """Ajoute de l'XP et retourne l'XP réellement gagnée."""
        if amount <= 0:
            return 0
        
        self.current_xp += amount
        self.total_xp_gained += amount
        
        return amount
    
    def check_level_up(self) -> bool:
        """Vérifie si le joueur a suffisamment d'XP pour monter de niveau."""
        total_xp_for_current_level = self._calculate_xp_required(self.level)
        total_xp_for_next_level = self._calculate_xp_required(self.level + 1)
        
        current_total_xp = total_xp_for_current_level + self.current_xp
        
        if current_total_xp >= total_xp_for_next_level:
            # Level up !
            self.level += 1
            self.levels_gained += 1
            
            # Ajuster l'XP actuelle
            self.current_xp = current_total_xp - total_xp_for_next_level
            self.xp_to_next_level = self._calculate_xp_for_next_level()
            
            return True
        
        return False
    
    def get_xp_progress(self) -> float:
        """Retourne le pourcentage de progression vers le niveau suivant (0.0 à 1.0)."""
        xp_needed = self._calculate_xp_for_next_level()
        if xp_needed <= 0:
            return 1.0
        
        return min(1.0, self.current_xp / xp_needed)
    
    def get_xp_display_info(self) -> dict:
        """Retourne les informations d'affichage de l'XP."""
        xp_needed = self._calculate_xp_for_next_level()
        return {
            'level': self.level,
            'current_xp': self.current_xp,
            'xp_needed': xp_needed,
            'progress': self.get_xp_progress(),
            'total_xp': self.total_xp_gained
        }
    
    def get_stats(self) -> dict:
        """Retourne les statistiques complètes du système XP."""
        return {
            'level': self.level,
            'current_xp': self.current_xp,
            'total_xp_gained': self.total_xp_gained,
            'levels_gained': self.levels_gained,
            'xp_to_next_level': self._calculate_xp_for_next_level(),
            'progress_percentage': int(self.get_xp_progress() * 100)
        }
    
    def reset(self):
        """Remet à zéro le système XP (pour une nouvelle partie)."""
        self.level = 1
        self.current_xp = 0
        self.xp_to_next_level = self._calculate_xp_required(2)
        self.total_xp_gained = 0
        self.levels_gained = 0
    
    def add_bonus_xp(self, multiplier: float = 1.5):
        """Ajoute un bonus d'XP basé sur le niveau actuel."""
        bonus = int(self.level * 10 * multiplier)
        self.gain_xp(bonus)
        return bonus
    
    def simulate_level_up_rewards(self) -> list:
        """Simule les récompenses potentielles pour le niveau suivant."""
        next_level = self.level + 1
        
        # Les récompenses deviennent plus puissantes avec le niveau
        power_factor = 1 + (next_level - 1) * 0.1
        
        rewards = []
        
        # Types de récompenses basées sur le niveau
        if next_level % 5 == 0:
            # Tous les 5 niveaux : récompenses spéciales
            rewards.extend(['legendary_card', 'special_ability'])
        
        if next_level % 3 == 0:
            # Tous les 3 niveaux : récompenses rares
            rewards.extend(['rare_card', 'stat_boost'])
        
        # Récompenses standard
        rewards.extend(['common_card', 'minor_boost'])
        
        return rewards[:3]  # Limiter à 3 récompenses max
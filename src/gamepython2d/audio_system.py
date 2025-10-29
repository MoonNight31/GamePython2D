#!/usr/bin/env python3
"""
🔊 Système audio pour GamePython2D
Sons et musiques avec génération procédurale de sons
"""

import pygame
import numpy as np
import random
import math
from typing import Dict, Optional

class AudioSystem:
    """Système de gestion audio avec génération procédurale."""
    
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Cache des sons générés
        self.sound_cache: Dict[str, pygame.mixer.Sound] = {}
        
        # Configuration volume
        self.master_volume = 0.7
        self.sfx_volume = 0.8
        self.music_volume = 0.6
        
        # Sons par rareté de carte
        self.rarity_frequencies = {
            'common': 440,      # La
            'uncommon': 523,    # Do
            'rare': 659,        # Mi
            'epic': 784,        # Sol
            'legendary': 880    # La aigu
        }
        
        self._generate_all_sounds()
    
    def _generate_all_sounds(self):
        """Génère tous les sons nécessaires."""
        print("🔊 Génération des sons...")
        
        # Sons de cartes par rareté
        for rarity in self.rarity_frequencies:
            self._generate_card_selection_sound(rarity)
        
        # Sons d'effets
        self._generate_upgrade_sounds()
        self._generate_combat_sounds()
        
        print("✅ Sons générés!")
    
    def _generate_card_selection_sound(self, rarity: str):
        """Génère un son de sélection de carte selon la rareté."""
        base_freq = self.rarity_frequencies[rarity]
        duration = 0.5
        sample_rate = 22050
        
        # Complexité selon la rareté
        complexity = {
            'common': 1,
            'uncommon': 2,
            'rare': 3,
            'epic': 4,
            'legendary': 5
        }[rarity]
        
        # Génération du son
        samples = self._create_magical_chime(base_freq, duration, sample_rate, complexity)
        sound = pygame.sndarray.make_sound(samples)
        
        self.sound_cache[f'card_select_{rarity}'] = sound
    
    def _generate_upgrade_sounds(self):
        """Génère les sons d'application d'upgrades."""
        effects = {
            'speed_boost': (600, 0.3, 'sweep_up'),
            'damage_boost': (300, 0.4, 'power_chord'),
            'attack_speed_boost': (800, 0.2, 'rapid_beeps'),
            'health_boost': (400, 0.6, 'healing_tone'),
            'heal': (450, 0.5, 'heal_cascade'),
            'multi_shot': (500, 0.4, 'multiply_echo'),
            'all_stats': (440, 0.8, 'triumphant_chord')
        }
        
        for effect, (freq, duration, style) in effects.items():
            samples = self._create_effect_sound(freq, duration, style)
            self.sound_cache[f'upgrade_{effect}'] = pygame.sndarray.make_sound(samples)
    
    def _generate_combat_sounds(self):
        """Génère les sons de combat."""
        # Son de tir
        samples = self._create_laser_shot(800, 0.1)
        self.sound_cache['projectile_fire'] = pygame.sndarray.make_sound(samples)
        
        # Son d'impact
        samples = self._create_impact_sound(200, 0.2)
        self.sound_cache['projectile_impact'] = pygame.sndarray.make_sound(samples)
        
        # Son de mort d'ennemi
        samples = self._create_explosion_sound(150, 0.5)
        self.sound_cache['enemy_death'] = pygame.sndarray.make_sound(samples)
    
    def _create_magical_chime(self, base_freq: float, duration: float, sample_rate: int, complexity: int):
        """Crée un carillon magique avec harmoniques."""
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        # Fréquences harmoniques
        harmonics = [1.0, 1.5, 2.0, 2.5, 3.0][:complexity]
        
        for i, harmonic in enumerate(harmonics):
            freq = base_freq * harmonic
            amplitude = 0.3 / (i + 1)  # Amplitude décroissante
            
            # Envelope avec attack et decay
            envelope = np.ones(frames)
            attack_frames = int(frames * 0.1)
            decay_frames = int(frames * 0.3)
            
            # Attack
            for j in range(attack_frames):
                envelope[j] = j / attack_frames
            
            # Decay
            for j in range(decay_frames):
                envelope[-(j+1)] = j / decay_frames
            
            # Génération de la sinusoïde
            wave = amplitude * envelope * np.sin(2 * np.pi * freq * np.linspace(0, duration, frames))
            
            # Stéréo avec légère phase
            arr[:, 0] += wave
            arr[:, 1] += amplitude * envelope * np.sin(2 * np.pi * freq * np.linspace(0, duration, frames) + 0.1)
        
        return (arr * 32767).astype(np.int16)
    
    def _create_effect_sound(self, base_freq: float, duration: float, style: str):
        """Crée un son d'effet selon le style."""
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        if style == 'sweep_up':
            # Sweep de fréquence montant (vitesse)
            freq_end = base_freq * 2
            for i in range(frames):
                progress = i / frames
                freq = base_freq + (freq_end - base_freq) * progress
                amplitude = 0.4 * (1 - progress * 0.7)
                arr[i] = amplitude * np.sin(2 * np.pi * freq * i / sample_rate)
        
        elif style == 'power_chord':
            # Accord puissant (dégâts)
            freqs = [base_freq, base_freq * 1.25, base_freq * 1.5]
            for freq in freqs:
                wave = 0.2 * np.sin(2 * np.pi * freq * np.linspace(0, duration, frames))
                # Envelope avec sustain
                envelope = np.ones(frames)
                decay_start = int(frames * 0.7)
                for i in range(decay_start, frames):
                    envelope[i] = 1 - ((i - decay_start) / (frames - decay_start)) * 0.8
                arr[:, 0] += wave * envelope
                arr[:, 1] += wave * envelope
        
        elif style == 'rapid_beeps':
            # Bips rapides (vitesse d'attaque)
            beep_duration = 0.05
            beep_frames = int(beep_duration * sample_rate)
            num_beeps = int(duration / beep_duration)
            
            for beep in range(num_beeps):
                start = beep * beep_frames
                end = min(start + beep_frames, frames)
                if start < frames:
                    wave = 0.3 * np.sin(2 * np.pi * base_freq * np.linspace(0, beep_duration, end - start))
                    arr[start:end, 0] = wave[:end-start]
                    arr[start:end, 1] = wave[:end-start]
        
        elif style == 'healing_tone':
            # Ton apaisant (vie)
            wave = 0.3 * np.sin(2 * np.pi * base_freq * np.linspace(0, duration, frames))
            # Vibrato léger
            vibrato = 0.1 * np.sin(2 * np.pi * 6 * np.linspace(0, duration, frames))
            wave = wave * (1 + vibrato)
            
            # Envelope douce
            envelope = np.sin(np.pi * np.linspace(0, 1, frames))
            arr[:, 0] = wave * envelope
            arr[:, 1] = wave * envelope
        
        elif style == 'heal_cascade':
            # Cascade de guérison
            cascade_notes = [base_freq, base_freq * 1.2, base_freq * 1.4, base_freq * 1.6]
            note_duration = duration / len(cascade_notes)
            note_frames = int(note_duration * sample_rate)
            
            for i, freq in enumerate(cascade_notes):
                start = i * note_frames
                end = min(start + note_frames, frames)
                if start < frames:
                    wave = 0.25 * np.sin(2 * np.pi * freq * np.linspace(0, note_duration, end - start))
                    envelope = np.sin(np.pi * np.linspace(0, 1, end - start))
                    arr[start:end, 0] = wave * envelope
                    arr[start:end, 1] = wave * envelope
        
        else:  # Default
            wave = 0.3 * np.sin(2 * np.pi * base_freq * np.linspace(0, duration, frames))
            arr[:, 0] = wave
            arr[:, 1] = wave
        
        return (arr * 32767).astype(np.int16)
    
    def _create_laser_shot(self, start_freq: float, duration: float):
        """Crée un son de tir laser."""
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        # Sweep descendant rapide
        end_freq = start_freq * 0.3
        arr = np.zeros(frames)
        
        for i in range(frames):
            progress = i / frames
            freq = start_freq * (1 - progress * 0.7)
            amplitude = 0.4 * (1 - progress)
            arr[i] = amplitude * np.sin(2 * np.pi * freq * i / sample_rate)
        
        # Stéréo
        stereo = np.column_stack([arr, arr])
        return (stereo * 32767).astype(np.int16)
    
    def _create_impact_sound(self, freq: float, duration: float):
        """Crée un son d'impact."""
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        # Bruit blanc avec envelope
        noise = np.random.normal(0, 0.1, frames)
        
        # Envelope sharp attack, quick decay
        envelope = np.exp(-np.linspace(0, 10, frames))
        
        arr = noise * envelope * 0.3
        stereo = np.column_stack([arr, arr])
        return (stereo * 32767).astype(np.int16)
    
    def _create_explosion_sound(self, base_freq: float, duration: float):
        """Crée un son d'explosion."""
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        # Combinaison de bruit et de basses fréquences
        noise = np.random.normal(0, 0.2, frames)
        low_freq = 0.3 * np.sin(2 * np.pi * base_freq * np.linspace(0, duration, frames))
        
        # Envelope explosive
        envelope = np.exp(-np.linspace(0, 5, frames))
        
        arr = (noise + low_freq) * envelope * 0.4
        stereo = np.column_stack([arr, arr])
        return (stereo * 32767).astype(np.int16)
    
    def play_card_selection(self, rarity: str):
        """Joue le son de sélection de carte."""
        sound_key = f'card_select_{rarity}'
        if sound_key in self.sound_cache:
            sound = self.sound_cache[sound_key]
            sound.set_volume(self.sfx_volume * self.master_volume)
            sound.play()
    
    def play_upgrade_effect(self, effect_type: str):
        """Joue le son d'application d'upgrade."""
        sound_key = f'upgrade_{effect_type}'
        if sound_key in self.sound_cache:
            sound = self.sound_cache[sound_key]
            sound.set_volume(self.sfx_volume * self.master_volume * 0.7)
            sound.play()
    
    def play_combat_sound(self, sound_type: str):
        """Joue un son de combat."""
        if sound_type in self.sound_cache:
            sound = self.sound_cache[sound_type]
            sound.set_volume(self.sfx_volume * self.master_volume * 0.6)
            sound.play()
    
    def set_volume(self, master: float = None, sfx: float = None, music: float = None):
        """Ajuste les volumes."""
        if master is not None:
            self.master_volume = max(0.0, min(1.0, master))
        if sfx is not None:
            self.sfx_volume = max(0.0, min(1.0, sfx))
        if music is not None:
            self.music_volume = max(0.0, min(1.0, music))
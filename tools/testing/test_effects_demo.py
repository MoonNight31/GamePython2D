#!/usr/bin/env python3
"""
🎆 Démonstration des effets visuels et sonores
Test interactif des effets du jeu
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pygame
from gamepython2d.effects_system import EffectsSystem
from gamepython2d.audio_system import AudioSystem

def test_effects_demo():
    """Démo interactive des effets."""
    pygame.init()
    
    width, height = 1200, 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("🎆 Démo des Effets - GamePython2D")
    
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    # Initialiser les systèmes
    effects = EffectsSystem()
    audio = AudioSystem()
    
    running = True
    
    # Instructions
    instructions = [
        "Cliquez pour tester les effets:",
        "1 - Carte Common",
        "2 - Carte Uncommon", 
        "3 - Carte Rare",
        "4 - Carte Epic",
        "5 - Carte Legendary",
        "",
        "Q - Upgrade Vitesse",
        "W - Upgrade Dégâts",
        "E - Upgrade Cadence",
        "R - Upgrade Vie",
        "T - Heal",
        "Y - Multi-shot",
        "U - All Stats",
        "",
        "F - Projectile Fire",
        "G - Projectile Impact",
        "H - Enemy Death",
        "L - Level Up",
        "",
        "ESC - Quitter"
    ]
    
    print("🎆 Démonstration des Effets")
    print("=" * 50)
    print("\n".join(instructions))
    print("=" * 50)
    
    while running:
        dt = clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # Effets de cartes
                elif event.key == pygame.K_1:
                    print("🎴 Effet: Carte Common")
                    effects.create_card_selection_effect(mouse_pos[0], mouse_pos[1], 'common')
                    audio.play_card_selection('common')
                
                elif event.key == pygame.K_2:
                    print("🎴 Effet: Carte Uncommon")
                    effects.create_card_selection_effect(mouse_pos[0], mouse_pos[1], 'uncommon')
                    audio.play_card_selection('uncommon')
                
                elif event.key == pygame.K_3:
                    print("🎴 Effet: Carte Rare")
                    effects.create_card_selection_effect(mouse_pos[0], mouse_pos[1], 'rare')
                    audio.play_card_selection('rare')
                
                elif event.key == pygame.K_4:
                    print("🎴 Effet: Carte Epic")
                    effects.create_card_selection_effect(mouse_pos[0], mouse_pos[1], 'epic')
                    audio.play_card_selection('epic')
                
                elif event.key == pygame.K_5:
                    print("🎴 Effet: Carte Legendary")
                    effects.create_card_selection_effect(mouse_pos[0], mouse_pos[1], 'legendary')
                    audio.play_card_selection('legendary')
                
                # Effets d'upgrades
                elif event.key == pygame.K_q:
                    print("⚡ Effet: Speed Boost")
                    effects.create_upgrade_effect(mouse_pos[0], mouse_pos[1], 'speed_boost')
                    audio.play_upgrade_effect('speed_boost')
                
                elif event.key == pygame.K_w:
                    print("⚔️ Effet: Damage Boost")
                    effects.create_upgrade_effect(mouse_pos[0], mouse_pos[1], 'damage_boost')
                    audio.play_upgrade_effect('damage_boost')
                
                elif event.key == pygame.K_e:
                    print("⏱️ Effet: Attack Speed Boost")
                    effects.create_upgrade_effect(mouse_pos[0], mouse_pos[1], 'attack_speed_boost')
                    audio.play_upgrade_effect('attack_speed_boost')
                
                elif event.key == pygame.K_r:
                    print("❤️ Effet: Health Boost")
                    effects.create_upgrade_effect(mouse_pos[0], mouse_pos[1], 'health_boost')
                    audio.play_upgrade_effect('health_boost')
                
                elif event.key == pygame.K_t:
                    print("💚 Effet: Heal")
                    effects.create_upgrade_effect(mouse_pos[0], mouse_pos[1], 'heal')
                    audio.play_upgrade_effect('heal')
                
                elif event.key == pygame.K_y:
                    print("🎯 Effet: Multi-shot")
                    effects.create_upgrade_effect(mouse_pos[0], mouse_pos[1], 'multi_shot')
                    audio.play_upgrade_effect('multi_shot')
                
                elif event.key == pygame.K_u:
                    print("🌟 Effet: All Stats")
                    effects.create_upgrade_effect(mouse_pos[0], mouse_pos[1], 'all_stats')
                    audio.play_upgrade_effect('all_stats')
                
                # Effets de combat
                elif event.key == pygame.K_f:
                    print("💥 Effet: Projectile Fire")
                    effects.create_projectile_fire_effect(mouse_pos[0], mouse_pos[1])
                    audio.play_combat_sound('projectile_fire')
                
                elif event.key == pygame.K_g:
                    print("💢 Effet: Projectile Impact")
                    effects.create_projectile_impact_effect(mouse_pos[0], mouse_pos[1])
                    audio.play_combat_sound('projectile_impact')
                
                elif event.key == pygame.K_h:
                    print("💀 Effet: Enemy Death")
                    effects.create_enemy_death_effect(mouse_pos[0], mouse_pos[1])
                    audio.play_combat_sound('enemy_death')
                
                elif event.key == pygame.K_l:
                    print("🎉 Effet: Level Up")
                    effects.create_level_up_effect(mouse_pos[0], mouse_pos[1])
            
            # Clic souris pour effet aléatoire
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    import random
                    effects_list = [
                        ('common', lambda: effects.create_card_selection_effect(mouse_pos[0], mouse_pos[1], 'common')),
                        ('rare', lambda: effects.create_card_selection_effect(mouse_pos[0], mouse_pos[1], 'rare')),
                        ('legendary', lambda: effects.create_card_selection_effect(mouse_pos[0], mouse_pos[1], 'legendary')),
                        ('level_up', lambda: effects.create_level_up_effect(mouse_pos[0], mouse_pos[1]))
                    ]
                    
                    effect_name, effect_func = random.choice(effects_list)
                    print(f"🎲 Effet aléatoire: {effect_name}")
                    effect_func()
        
        # Mise à jour
        effects.update(dt / 1000.0)
        
        # Rendu
        screen.fill((20, 20, 30))
        
        # Dessiner les effets
        effects.draw(screen)
        
        # Dessiner le curseur
        pygame.draw.circle(screen, (255, 255, 255), mouse_pos, 3)
        pygame.draw.circle(screen, (255, 255, 255), mouse_pos, 10, 1)
        
        # Afficher le titre
        title = font.render("🎆 Démonstration des Effets", True, (255, 255, 255))
        screen.blit(title, (width // 2 - title.get_width() // 2, 20))
        
        # Afficher les instructions (plus compact)
        y_offset = 70
        for i, instruction in enumerate(instructions[:8]):  # Afficher seulement les premières lignes
            text = small_font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (20, y_offset + i * 25))
        
        # Info particules
        particle_info = small_font.render(
            f"Particules actives: {len(effects.particles)}", 
            True, 
            (100, 255, 100)
        )
        screen.blit(particle_info, (width - 250, height - 40))
        
        pygame.display.flip()
    
    pygame.quit()
    print("\n✅ Démo terminée!")

if __name__ == "__main__":
    test_effects_demo()

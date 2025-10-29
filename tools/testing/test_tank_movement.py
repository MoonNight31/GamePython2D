#!/usr/bin/env python3
"""
Test de déplacement des ennemis tanks
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pygame
from gamepython2d.enemy import Enemy

def test_tank_movement():
    """Teste le déplacement des tanks."""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Test Tank Movement")
    clock = pygame.time.Clock()
    
    # Créer un tank au coin
    tank = Enemy(100, 100, "tank")
    
    # Position du joueur (fixe)
    player_pos = (400, 300)
    
    print(f"🏁 Tank initial: position=({tank.rect.x}, {tank.rect.y}), speed={tank.speed}")
    print(f"🎯 Joueur à: {player_pos}")
    
    running = True
    step_count = 0
    
    while running and step_count < 300:  # 5 secondes à 60 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Mettre à jour le tank
        dt = 16.67  # Même que l'environnement IA
        old_pos = (tank.rect.x, tank.rect.y)
        tank.update(dt, player_pos)
        new_pos = (tank.rect.x, tank.rect.y)
        
        # Afficher le mouvement tous les 60 steps (1 seconde)
        if step_count % 60 == 0:
            distance_moved = ((new_pos[0] - old_pos[0])**2 + (new_pos[1] - old_pos[1])**2)**0.5
            total_distance = ((tank.rect.x - 100)**2 + (tank.rect.y - 100)**2)**0.5
            print(f"⏱️ Seconde {step_count//60}: position=({tank.rect.x:.1f}, {tank.rect.y:.1f}), distance_totale={total_distance:.1f}px")
        
        # Dessiner
        screen.fill((0, 0, 0))
        
        # Dessiner le joueur (bleu)
        pygame.draw.circle(screen, (0, 0, 255), player_pos, 15)
        
        # Dessiner le tank (rouge)
        pygame.draw.rect(screen, tank.color, tank.rect)
        
        # Dessiner une ligne vers la cible
        pygame.draw.line(screen, (100, 100, 100), tank.rect.center, player_pos, 1)
        
        pygame.display.flip()
        clock.tick(60)
        step_count += 1
    
    final_distance = ((tank.rect.x - 100)**2 + (tank.rect.y - 100)**2)**0.5
    time_elapsed = step_count / 60
    average_speed = final_distance / time_elapsed if time_elapsed > 0 else 0
    
    print(f"\n📊 RÉSULTATS:")
    print(f"   ⏱️ Temps: {time_elapsed:.1f} secondes")
    print(f"   📏 Distance parcourue: {final_distance:.1f} pixels")
    print(f"   🏃 Vitesse moyenne: {average_speed:.1f} px/s")
    print(f"   🎯 Vitesse théorique: {tank.speed} px/s")
    
    if average_speed < tank.speed * 0.1:  # Moins de 10% de la vitesse théorique
        print(f"   ❌ PROBLÈME: Le tank bouge très peu !")
    elif average_speed < tank.speed * 0.8:  # Moins de 80% de la vitesse
        print(f"   ⚠️ LENT: Le tank bouge mais c'est très lent")
    else:
        print(f"   ✅ OK: Le tank bouge normalement")
    
    pygame.quit()

if __name__ == "__main__":
    test_tank_movement()
#!/usr/bin/env python3
"""
✅ Script de Validation du Système d'Effets
Vérifie que tous les composants sont opérationnels
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_imports():
    """Test des imports."""
    print("📦 Test des imports...")
    try:
        from gamepython2d.effects_system import EffectsSystem, Particle
        print("   ✅ EffectsSystem importé")
        
        from gamepython2d.audio_system import AudioSystem
        print("   ✅ AudioSystem importé")
        
        from gamepython2d.game import Game
        print("   ✅ Game importé")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur d'import: {e}")
        return False

def test_effects_system():
    """Test du système d'effets."""
    print("\n🎨 Test du système d'effets...")
    try:
        from gamepython2d.effects_system import EffectsSystem
        
        effects = EffectsSystem()
        print(f"   ✅ EffectsSystem créé")
        print(f"   ℹ️  Particules initiales: {len(effects.particles)}")
        
        # Test de création d'effets
        effects.create_card_selection_effect(100, 100, 'common')
        print(f"   ✅ Effet carte créé: {len(effects.particles)} particules")
        
        effects.create_upgrade_effect(200, 200, 'speed_boost')
        print(f"   ✅ Effet upgrade créé: {len(effects.particles)} particules")
        
        effects.create_level_up_effect(300, 300)
        print(f"   ✅ Effet level up créé: {len(effects.particles)} particules")
        
        # Test update
        effects.update(0.016)  # ~1 frame à 60 FPS
        print(f"   ✅ Update fonctionne: {len(effects.particles)} particules restantes")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_audio_system():
    """Test du système audio."""
    print("\n🔊 Test du système audio...")
    try:
        from gamepython2d.audio_system import AudioSystem
        
        audio = AudioSystem()
        print(f"   ✅ AudioSystem créé")
        print(f"   ℹ️  Sons générés: {len(audio.sound_cache)}")
        
        # Vérifier les sons par catégorie
        card_sounds = [k for k in audio.sound_cache.keys() if 'card_select' in k]
        print(f"   ✅ Sons de cartes: {len(card_sounds)}")
        
        upgrade_sounds = [k for k in audio.sound_cache.keys() if 'upgrade' in k]
        print(f"   ✅ Sons d'upgrades: {len(upgrade_sounds)}")
        
        combat_sounds = [k for k in audio.sound_cache.keys() if k in ['projectile_fire', 'projectile_impact', 'enemy_death']]
        print(f"   ✅ Sons de combat: {len(combat_sounds)}")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_game_integration():
    """Test de l'intégration dans le jeu."""
    print("\n🎮 Test de l'intégration...")
    try:
        from gamepython2d.game import Game
        
        # Créer une instance de jeu (sans affichage)
        game = Game()
        print(f"   ✅ Instance Game créée")
        
        # Vérifier que les systèmes sont présents
        assert hasattr(game, 'effects'), "Attribut 'effects' manquant"
        print(f"   ✅ Système effects présent")
        
        assert hasattr(game, 'audio'), "Attribut 'audio' manquant"
        print(f"   ✅ Système audio présent")
        
        # Vérifier les particules
        particles_count = len(game.effects.particles)
        print(f"   ℹ️  Particules initiales: {particles_count}")
        
        # Vérifier les sons
        sounds_count = len(game.audio.sound_cache)
        print(f"   ℹ️  Sons disponibles: {sounds_count}")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_effects_types():
    """Test de tous les types d'effets."""
    print("\n🎯 Test des types d'effets...")
    try:
        from gamepython2d.effects_system import EffectsSystem
        
        effects = EffectsSystem()
        test_pos = (400, 300)
        
        # Test cartes
        rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary']
        for rarity in rarities:
            effects.create_card_selection_effect(*test_pos, rarity)
        print(f"   ✅ Effets de cartes: {len(rarities)} testés")
        
        # Test upgrades
        upgrade_types = ['speed_boost', 'damage_boost', 'attack_speed_boost', 
                        'health_boost', 'heal', 'multi_shot', 'all_stats']
        for upgrade in upgrade_types:
            effects.create_upgrade_effect(*test_pos, upgrade)
        print(f"   ✅ Effets d'upgrades: {len(upgrade_types)} testés")
        
        # Test combat
        effects.create_projectile_fire_effect(*test_pos)
        effects.create_projectile_impact_effect(*test_pos)
        effects.create_projectile_trail(*test_pos)
        effects.create_enemy_death_effect(*test_pos)
        print(f"   ✅ Effets de combat: 4 testés")
        
        # Test spéciaux
        effects.create_level_up_effect(*test_pos)
        print(f"   ✅ Effets spéciaux: 1 testé")
        
        total = len(rarities) + len(upgrade_types) + 5
        print(f"   🎉 Total: {total} types d'effets fonctionnels")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Exécute tous les tests."""
    print("=" * 60)
    print("🎆 VALIDATION DU SYSTÈME D'EFFETS - GamePython2D")
    print("=" * 60)
    
    results = []
    
    # Exécuter les tests
    results.append(("Imports", test_imports()))
    results.append(("Système d'effets", test_effects_system()))
    results.append(("Système audio", test_audio_system()))
    results.append(("Intégration jeu", test_game_integration()))
    results.append(("Types d'effets", test_effects_types()))
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    # Verdict final
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("Le système d'effets est entièrement opérationnel.")
        print("\nPour tester interactivement:")
        print("  python main.py")
        print("  python tools/testing/test_effects_demo.py")
    else:
        print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("Vérifiez les erreurs ci-dessus.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

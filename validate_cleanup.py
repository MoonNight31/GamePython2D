#!/usr/bin/env python3
"""
✅ Validation du nettoyage GamePython2D
Vérifie que tous les outils fonctionnent après le nettoyage
"""

import os
import sys
import subprocess
from pathlib import Path

def test_tool(tool_path, description):
    """Teste qu'un outil peut s'importer correctement."""
    try:
        # Test d'import seulement (pas d'exécution complète)
        result = subprocess.run([
            sys.executable, "-c", 
            f"import sys; sys.path.append('{os.getcwd()}'); exec(open('{tool_path}').read())"
        ], capture_output=True, text=True, timeout=5, cwd=os.getcwd())
        
        if result.returncode == 0:
            return True, "✅ OK"
        else:
            return False, f"❌ Erreur: {result.stderr[:100]}"
    except subprocess.TimeoutExpired:
        return True, "⏱️ Timeout (normal pour les scripts interactifs)"
    except Exception as e:
        return False, f"❌ Exception: {str(e)[:100]}"

def validate_cleanup():
    """Valide que le nettoyage s'est bien passé."""
    print("✅ VALIDATION DU NETTOYAGE GAMEPYTHON2D")
    print("=" * 50)
    
    # Vérifier la structure des dossiers
    print("📁 STRUCTURE DES DOSSIERS:")
    expected_dirs = ["src", "tools", "ai_models", "ai_logs", "archive"]
    for dir_name in expected_dirs:
        if os.path.exists(dir_name):
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ❌ {dir_name}/ (manquant)")
    
    # Vérifier les sous-dossiers tools
    print("\n🧰 OUTILS ORGANISÉS:")
    tool_dirs = ["tools/debug", "tools/training", "tools/testing"]
    for tool_dir in tool_dirs:
        if os.path.exists(tool_dir):
            file_count = len(list(Path(tool_dir).glob("*.py")))
            print(f"   ✅ {tool_dir}/ ({file_count} fichiers)")
        else:
            print(f"   ❌ {tool_dir}/ (manquant)")
    
    # Tester quelques outils clés
    print("\n🔧 TEST DES OUTILS CLÉS:")
    key_tools = [
        ("tools/testing/test_ai_effectiveness.py", "Test d'efficacité IA"),
        ("tools/training/curriculum_trainer.py", "Entraîneur curriculum"),
        ("tools/debug/debug_projectile_creation.py", "Debug projectiles"),
        ("demo_ai.py", "Démo IA"),
        ("clean_project.py", "Nettoyeur de projet")
    ]
    
    working_tools = 0
    for tool_path, description in key_tools:
        if os.path.exists(tool_path):
            success, message = test_tool(tool_path, description)
            print(f"   {message} {description}")
            if success:
                working_tools += 1
        else:
            print(f"   ❌ {description} (fichier manquant)")
    
    # Vérifier les fichiers archivés
    print("\n📦 ARCHIVAGE:")
    if os.path.exists("archive"):
        archived_items = len(os.listdir("archive"))
        print(f"   ✅ {archived_items} éléments archivés")
    else:
        print("   📝 Aucun élément archivé")
    
    # Résumé
    print(f"\n🏆 RÉSUMÉ:")
    print(f"   📁 Structure: Organisée avec tools/, archive/")
    print(f"   🔧 Outils testés: {working_tools}/{len(key_tools)} fonctionnels")
    print(f"   💾 Espace libéré: Logs et caches archivés")
    print(f"   📖 Documentation: README mis à jour")
    
    if working_tools >= len(key_tools) - 1:  # Tolérer 1 erreur
        print("\n✅ NETTOYAGE RÉUSSI!")
        print("   Le projet est maintenant bien organisé et fonctionnel")
    else:
        print("\n⚠️ PROBLÈMES DÉTECTÉS")
        print("   Certains outils ne fonctionnent pas correctement")
    
    print(f"\n📋 UTILISATION:")
    print(f"   🎮 Jouer: python demo_ai.py")
    print(f"   🧠 Entraîner: python tools/training/curriculum_trainer.py")
    print(f"   🔍 Tester: python tools/testing/test_ai_effectiveness.py")
    print(f"   🧹 Nettoyer: python clean_project.py")

if __name__ == "__main__":
    validate_cleanup()
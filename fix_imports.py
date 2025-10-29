#!/usr/bin/env python3
"""
🔧 Script de mise à jour des imports
Corrige les imports dans les outils déplacés
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path, relative_depth):
    """Corrige les imports dans un fichier selon sa profondeur relative."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern pour détecter les ajouts de path existants
        old_pattern = r"sys\.path\.insert\(0, os\.path\.join\(os\.path\.dirname\(__file__\), ['\"]src['\"]\)\)"
        
        # Nouveau pattern selon la profondeur
        if relative_depth == 1:  # tools/
            new_path = "sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))"
        elif relative_depth == 2:  # tools/subdir/
            new_path = "sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))"
        else:
            new_path = "sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))"
        
        # Remplacer l'ancien pattern
        content = re.sub(old_pattern, new_path, content)
        
        # Aussi chercher d'autres variantes
        old_pattern2 = r"sys\.path\.insert\(0, os\.path\.join\(os\.path\.dirname\(__file__\), ['\"]\.\.['\"]\)\)"
        content = re.sub(old_pattern2, new_path, content)
        
        # Écrire le fichier modifié
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Corrigé: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur {file_path}: {e}")
        return False

def fix_all_imports():
    """Corrige tous les imports dans les outils déplacés."""
    print("🔧 CORRECTION DES IMPORTS")
    print("=" * 30)
    
    project_root = Path(__file__).parent
    tools_dir = project_root / "tools"
    
    files_fixed = 0
    
    # Corriger les fichiers dans tools/ (profondeur 1)
    for file_path in tools_dir.glob("*.py"):
        if fix_imports_in_file(file_path, 1):
            files_fixed += 1
    
    # Corriger les fichiers dans tools/subdir/ (profondeur 2)
    for subdir in ["debug", "training", "testing"]:
        subdir_path = tools_dir / subdir
        if subdir_path.exists():
            for file_path in subdir_path.glob("*.py"):
                if fix_imports_in_file(file_path, 2):
                    files_fixed += 1
    
    print(f"\n✅ {files_fixed} fichiers corrigés")
    print("🎯 Les outils peuvent maintenant être utilisés depuis leur nouvelle location")

if __name__ == "__main__":
    fix_all_imports()
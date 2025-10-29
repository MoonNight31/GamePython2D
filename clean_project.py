#!/usr/bin/env python3
"""
🧹 Script de nettoyage GamePython2D
Nettoie les fichiers temporaires et anciens logs pour libérer de l'espace
"""

import os
import shutil
import time
from pathlib import Path

def get_folder_size(folder_path):
    """Calcule la taille d'un dossier en MB."""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except:
                    pass
    except:
        pass
    return total_size / (1024 * 1024)  # Convert to MB

def clean_project():
    """Nettoie le projet GamePython2D."""
    print("🧹 NETTOYAGE GAMEPYTHON2D")
    print("=" * 40)
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Analyser l'espace utilisé
    print("📊 ANALYSE DE L'ESPACE DISQUE:")
    
    folders_to_check = [
        "ai_logs",
        "ai_models", 
        "archive",
        ".venv",
        "src"
    ]
    
    total_space = 0
    for folder in folders_to_check:
        if os.path.exists(folder):
            size = get_folder_size(folder)
            total_space += size
            print(f"   {folder:<15}: {size:6.1f} MB")
    
    print(f"   {'TOTAL':<15}: {total_space:6.1f} MB")
    print()
    
    # Options de nettoyage
    print("🎯 OPTIONS DE NETTOYAGE:")
    print("1. 🗑️  Nettoyer les logs anciens (> 7 jours)")
    print("2. 🧽  Nettoyer les modèles intermédiaires")
    print("3. 🔄  Nettoyer le cache Python (__pycache__)")
    print("4. 📦  Archive complète des logs")
    print("5. ❌  Annuler")
    
    choice = input("\nChoisissez une option (1-5): ").strip()
    
    if choice == "1":
        clean_old_logs()
    elif choice == "2":
        clean_intermediate_models()
    elif choice == "3":
        clean_python_cache()
    elif choice == "4":
        archive_all_logs()
    elif choice == "5":
        print("❌ Nettoyage annulé")
    else:
        print("❌ Option invalide")

def clean_old_logs():
    """Nettoie les logs anciens."""
    print("\n🗑️ NETTOYAGE DES LOGS ANCIENS")
    print("-" * 30)
    
    if not os.path.exists("ai_logs"):
        print("✅ Aucun dossier ai_logs trouvé")
        return
    
    current_time = time.time()
    cutoff_time = current_time - (7 * 24 * 60 * 60)  # 7 jours
    
    removed_size = 0
    removed_count = 0
    
    for root, dirs, files in os.walk("ai_logs"):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                file_time = os.path.getmtime(file_path)
                if file_time < cutoff_time:
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    removed_size += file_size
                    removed_count += 1
            except:
                pass
    
    print(f"✅ {removed_count} fichiers supprimés")
    print(f"💾 {removed_size / (1024*1024):.1f} MB libérés")

def clean_intermediate_models():
    """Nettoie les modèles intermédiaires."""
    print("\n🧽 NETTOYAGE DES MODÈLES INTERMÉDIAIRES")
    print("-" * 40)
    
    if not os.path.exists("ai_models"):
        print("✅ Aucun dossier ai_models trouvé")
        return
    
    # Garder seulement les modèles importants
    keep_patterns = [
        "final",
        "curriculum_stage",
        "precision_shooting",
        "smart_shooting"
    ]
    
    removed_size = 0
    removed_count = 0
    
    for file in os.listdir("ai_models"):
        if file.endswith(".zip"):
            should_keep = any(pattern in file for pattern in keep_patterns)
            if not should_keep:
                file_path = os.path.join("ai_models", file)
                try:
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    removed_size += file_size
                    removed_count += 1
                    print(f"🗑️ Supprimé: {file}")
                except:
                    pass
    
    print(f"✅ {removed_count} modèles intermédiaires supprimés")
    print(f"💾 {removed_size / (1024*1024):.1f} MB libérés")

def clean_python_cache():
    """Nettoie le cache Python."""
    print("\n🔄 NETTOYAGE DU CACHE PYTHON")
    print("-" * 30)
    
    removed_size = 0
    removed_count = 0
    
    for root, dirs, files in os.walk("."):
        # Supprimer __pycache__ directories
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            try:
                cache_size = get_folder_size(pycache_path) * 1024 * 1024  # Convert back to bytes
                shutil.rmtree(pycache_path)
                removed_size += cache_size
                removed_count += 1
            except:
                pass
        
        # Supprimer .pyc files
        for file in files:
            if file.endswith(".pyc"):
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    removed_size += file_size
                    removed_count += 1
                except:
                    pass
    
    print(f"✅ {removed_count} fichiers cache supprimés")
    print(f"💾 {removed_size / (1024*1024):.1f} MB libérés")

def archive_all_logs():
    """Archive tous les logs."""
    print("\n📦 ARCHIVAGE COMPLET DES LOGS")
    print("-" * 30)
    
    if not os.path.exists("ai_logs"):
        print("✅ Aucun dossier ai_logs trouvé")
        return
    
    if not os.path.exists("archive"):
        os.makedirs("archive")
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    archive_name = f"archive/ai_logs_backup_{timestamp}"
    
    try:
        shutil.move("ai_logs", archive_name)
        os.makedirs("ai_logs")  # Recréer un dossier vide
        
        archived_size = get_folder_size(archive_name)
        print(f"✅ Logs archivés vers: {archive_name}")
        print(f"💾 {archived_size:.1f} MB archivés")
    except Exception as e:
        print(f"❌ Erreur lors de l'archivage: {e}")

if __name__ == "__main__":
    clean_project()
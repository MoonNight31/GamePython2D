#!/usr/bin/env python3
"""
Script de test pour vérifier le système de génération de graphiques.
"""

import matplotlib.pyplot as plt
import numpy as np
import os

# Données de test simulant 7 étapes d'entraînement
test_metrics = {
    "stage_names": [f"Étape {i}" for i in range(1, 8)],
    "projectiles": [2.5, 8.3, 12.1, 15.2, 18.5, 20.3, 22.7],
    "accuracy": [15.2, 28.5, 42.3, 51.8, 58.4, 63.2, 68.9],
    "movement": [0.12, 0.25, 0.48, 0.62, 0.71, 0.75, 0.78],
    "survival": [245, 412, 678, 892, 1123, 1345, 1567],
    "kills": [1.2, 2.8, 4.5, 5.9, 7.2, 8.5, 9.8],
    "xp_collected": [0.8, 1.5, 2.9, 4.2, 5.8, 7.1, 8.9],
    "levels": [1.0, 1.2, 2.1, 2.8, 3.5, 4.2, 5.1],
    "training_times": [12.5, 18.3, 24.7, 31.2, 38.9, 32.1, 52.4]
}

def generate_test_graphs():
    """Génère les graphiques de test."""
    print("📊 Génération des graphiques de test...")
    
    # Créer une figure avec 6 sous-graphiques
    fig = plt.figure(figsize=(18, 10))
    fig.suptitle('Évolution de l\'IA à travers le Curriculum Learning (TEST)', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    stages = test_metrics["stage_names"]
    x_pos = np.arange(len(stages))
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DFE6E9', '#A29BFE']
    
    # 1. Projectiles
    ax1 = plt.subplot(2, 3, 1)
    bars1 = ax1.bar(x_pos, test_metrics["projectiles"], color=colors, alpha=0.8, edgecolor='black')
    ax1.set_xlabel('Étapes', fontweight='bold')
    ax1.set_ylabel('Projectiles par épisode', fontweight='bold')
    ax1.set_title('[TIR] Activité de Tir', fontweight='bold', pad=10)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels([f'E{i+1}' for i in range(len(stages))], rotation=0)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 2. Précision
    ax2 = plt.subplot(2, 3, 2)
    bars2 = ax2.bar(x_pos, test_metrics["accuracy"], color=colors, alpha=0.8, edgecolor='black')
    ax2.set_xlabel('Étapes', fontweight='bold')
    ax2.set_ylabel('Précision (%)', fontweight='bold')
    ax2.set_title('[VISEE] Précision de Visée', fontweight='bold', pad=10)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels([f'E{i+1}' for i in range(len(stages))], rotation=0)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.set_ylim(0, 100)
    
    # 3. Survie
    ax3 = plt.subplot(2, 3, 3)
    bars3 = ax3.bar(x_pos, test_metrics["survival"], color=colors, alpha=0.8, edgecolor='black')
    ax3.set_xlabel('Étapes', fontweight='bold')
    ax3.set_ylabel('Steps survivés', fontweight='bold')
    ax3.set_title('[SURVIE] Temps de Survie', fontweight='bold', pad=10)
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels([f'E{i+1}' for i in range(len(stages))], rotation=0)
    ax3.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 4. Kills
    ax4 = plt.subplot(2, 3, 4)
    bars4 = ax4.bar(x_pos, test_metrics["kills"], color=colors, alpha=0.8, edgecolor='black')
    ax4.set_xlabel('Étapes', fontweight='bold')
    ax4.set_ylabel('Kills par épisode', fontweight='bold')
    ax4.set_title('[COMBAT] Ennemis Éliminés', fontweight='bold', pad=10)
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels([f'E{i+1}' for i in range(len(stages))], rotation=0)
    ax4.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 5. XP et Niveau
    ax5 = plt.subplot(2, 3, 5)
    width = 0.35
    bars5a = ax5.bar(x_pos - width/2, test_metrics["xp_collected"], width, 
                    label='Orbes XP', color='#FFEAA7', alpha=0.8, edgecolor='black')
    bars5b = ax5.bar(x_pos + width/2, test_metrics["levels"], width,
                    label='Niveau', color='#A29BFE', alpha=0.8, edgecolor='black')
    ax5.set_xlabel('Étapes', fontweight='bold')
    ax5.set_ylabel('Valeur', fontweight='bold')
    ax5.set_title('[XP] Progression XP et Niveau', fontweight='bold', pad=10)
    ax5.set_xticks(x_pos)
    ax5.set_xticklabels([f'E{i+1}' for i in range(len(stages))], rotation=0)
    ax5.legend(loc='upper left', framealpha=0.9)
    ax5.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 6. Temps d'entraînement
    ax6 = plt.subplot(2, 3, 6)
    bars6 = ax6.bar(x_pos, test_metrics["training_times"], color=colors, alpha=0.8, edgecolor='black')
    ax6.set_xlabel('Étapes', fontweight='bold')
    ax6.set_ylabel('Temps (minutes)', fontweight='bold')
    ax6.set_title('[TEMPS] Temps d\'Entraînement', fontweight='bold', pad=10)
    ax6.set_xticks(x_pos)
    ax6.set_xticklabels([f'E{i+1}' for i in range(len(stages))], rotation=0)
    ax6.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    
    # Sauvegarder
    os.makedirs("ai_logs", exist_ok=True)
    plt.savefig("ai_logs/test_evolution.png", dpi=150, bbox_inches='tight')
    print("✅ Graphique de test sauvegardé : ai_logs/test_evolution.png")
    
    plt.show()
    
    # Graphique de progression
    generate_progression_graph()

def generate_progression_graph():
    """Génère le graphique de progression."""
    fig, ax = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('Progression Progressive de l\'IA (TEST)', fontsize=16, fontweight='bold')
    
    stages = list(range(1, 8))
    
    # 1. Combat
    ax1 = ax[0, 0]
    ax1_twin = ax1.twinx()
    line1 = ax1.plot(stages, test_metrics["projectiles"], 'o-', 
                    linewidth=3, markersize=10, color='#FF6B6B', label='Projectiles/épisode')
    line2 = ax1_twin.plot(stages, test_metrics["kills"], 's-', 
                         linewidth=3, markersize=10, color='#4ECDC4', label='Kills/épisode')
    ax1.set_xlabel('Étape', fontweight='bold', fontsize=12)
    ax1.set_ylabel('Projectiles', fontweight='bold', fontsize=12, color='#FF6B6B')
    ax1_twin.set_ylabel('Kills', fontweight='bold', fontsize=12, color='#4ECDC4')
    ax1.set_title('[COMBAT] Compétences de Combat', fontweight='bold', pad=10)
    ax1.tick_params(axis='y', labelcolor='#FF6B6B')
    ax1_twin.tick_params(axis='y', labelcolor='#4ECDC4')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xticks(stages)
    
    # 2. Précision et Mouvement
    ax2 = ax[0, 1]
    ax2.plot(stages, test_metrics["accuracy"], 'o-', 
            linewidth=3, markersize=10, color='#A29BFE', label='Précision (%)')
    ax2.set_xlabel('Étape', fontweight='bold', fontsize=12)
    ax2.set_ylabel('Précision (%)', fontweight='bold', fontsize=12)
    ax2.set_title('[VISEE] Précision', fontweight='bold', pad=10)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_xticks(stages)
    ax2.legend(loc='upper left')
    
    # 3. Survie
    ax3 = ax[1, 0]
    ax3.plot(stages, test_metrics["survival"], 'o-', 
            linewidth=3, markersize=10, color='#00B894', label='Survie (steps)')
    ax3.set_xlabel('Étape', fontweight='bold', fontsize=12)
    ax3.set_ylabel('Temps de Survie', fontweight='bold', fontsize=12)
    ax3.set_title('[SURVIE] Survie', fontweight='bold', pad=10)
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.set_xticks(stages)
    ax3.legend(loc='upper left')
    
    # 4. Score global
    ax4 = ax[1, 1]
    composite_scores = []
    for i in range(len(stages)):
        proj_score = min(100, (test_metrics["projectiles"][i] / 20) * 100)
        acc_score = test_metrics["accuracy"][i]
        surv_score = min(100, (test_metrics["survival"][i] / 2000) * 100)
        kill_score = min(100, (test_metrics["kills"][i] / 10) * 100)
        level_score = min(100, (test_metrics["levels"][i] / 5) * 100)
        composite = (proj_score + acc_score + surv_score + kill_score + level_score) / 5
        composite_scores.append(composite)
    
    bars = ax4.bar(stages, composite_scores, color='#6C5CE7', alpha=0.8, edgecolor='black', width=0.6)
    ax4.set_xlabel('Étape', fontweight='bold', fontsize=12)
    ax4.set_ylabel('Score Global (%)', fontweight='bold', fontsize=12)
    ax4.set_title('[GLOBAL] Performance Globale', fontweight='bold', pad=10)
    ax4.set_ylim(0, 100)
    ax4.grid(axis='y', alpha=0.3, linestyle='--')
    ax4.set_xticks(stages)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.savefig("ai_logs/test_progression.png", dpi=150, bbox_inches='tight')
    print("✅ Graphique de progression sauvegardé : ai_logs/test_progression.png")
    plt.show()

if __name__ == "__main__":
    print("🧪 Test du système de génération de graphiques")
    print("=" * 60)
    generate_test_graphs()
    print("\n✅ Test terminé avec succès!")
    print("📊 Les graphiques ont été générés dans le dossier ai_logs/")

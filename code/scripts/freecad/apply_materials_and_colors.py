#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_materials_and_colors.py — Colorisation et Texturation Réelle de l'Assemblage FreeCAD
"""

import sys
import os
import FreeCAD
import FreeCADGui

DOC_PATH = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/01_Torse_et_Bassin/DBot_Torse_et_Bassin_Souverain.FCStd"
REPO_PATH = "/Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/DBot_Assembly_Sovereign.FCStd"
SHARED_COPY = "/Users/Shared/DBot_Assembly_Sovereign.FCStd"

print("=================================================================")
print("=== APPLICATION DES COULEURS ET TEXTURES RÉELLES D-BOT =========")
print("=================================================================")

doc = FreeCAD.openDocument(DOC_PATH)
print(f"Document ouvert : {doc.Label} ({len(doc.Objects)} objets)")

# Palette chromatique d'ingénierie D-Bot (RGB 0.0 - 1.0)
PALETTE = {
    "alu_7075":    (0.78, 0.79, 0.82),  # Aluminium aéronautique usiné satiné
    "pa12_cf":     (0.18, 0.18, 0.20),  # Carbone PA12-CF sombre mat
    "robstride":   (0.12, 0.13, 0.15),  # Boîtier moteur noir titane anodisé
    "bearing":     (0.85, 0.88, 0.92),  # Acier à roulement poli miroir
    "fasteners":   (0.40, 0.42, 0.45),  # Visserie Inox A4-80 / Acier zingué
    "copper_gold": (0.85, 0.65, 0.25),  # Cuivre / Laiton inserts
    "default":     (0.70, 0.70, 0.72)
}

colorized_count = 0

for obj in doc.Objects:
    # 1. Rendre le conteneur ou la pièce visible
    if hasattr(obj, "Visibility"):
        obj.Visibility = True

    if not hasattr(obj, "ViewObject") or not obj.ViewObject:
        continue

    # Masquer les repères d'axes et plans d'origine par défaut pour ne pas polluer la vue
    name_low = obj.Name.lower()
    label_low = obj.Label.lower()
    if any(k in name_low or k in label_low for k in ["plane", "x-axis", "y-axis", "z-axis", "origin"]):
        try:
            obj.ViewObject.Visibility = False
        except Exception:
            pass
        continue

    # 2. Ne traiter que les composants avec géométrie 3D
    if not hasattr(obj, "Shape") or obj.Shape.isNull() or len(obj.Shape.Solids) == 0:
        continue

    # Forcer la visibilité du solide dans l'interface graphique
    try:
        obj.ViewObject.Visibility = True
    except Exception:
        pass
        
    mat_name = getattr(obj, "MaterialName", "").lower()
    label = obj.Label.lower()
    
    # Détermination de la nuance
    color = PALETTE["default"]
    
    if any(k in label for k in ["rs04", "rs06", "el05", "moteur", "motor", "actuator"]):
        color = PALETTE["robstride"]
    elif "rb8016" in label or "roulement" in label or "bearing" in label:
        color = PALETTE["bearing"]
    elif any(k in label for k in ["vis", "screw", "rondelle", "washer", "ecrou", "écrou", "nut", "nylstop", "nord-lock", "fhc", "chc", "bhc", "goupille", "insert"]):
        color = PALETTE["fasteners"]
    elif any(k in mat_name for k in ["pa12", "carbone", "carbon", "gyroïde", "gyroide"]) or any(k in label for k in ["plastron", "carenage", "capot", "trappe"]):
        color = PALETTE["pa12_cf"]
    elif any(k in mat_name for k in ["alu", "7075", "6061", "dural"]) or any(k in label for k in ["waist_plate", "chassis", "traverse", "moyeu", "platine", "plaque"]):
        color = PALETTE["alu_7075"]
    elif "acier" in mat_name or "inox" in mat_name:
        color = PALETTE["fasteners"]
        
    try:
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.LineColor = (0.15, 0.15, 0.15)
        obj.ViewObject.LineWidth = 1.0
        colorized_count += 1
    except Exception as e:
        print(f"Erreur couleur sur {obj.Label}: {e}")

print(f"✅ {colorized_count} composants colorisés selon leurs matériaux réels.")

print("Sauvegarde du document avec les propriétés graphiques GUI...")
doc.save()
print(f"✅ Sauvegardé avec succès vers : {DOC_PATH}")

# Synchronisation dans le repo de travail
import shutil
try:
    shutil.copy2(DOC_PATH, REPO_PATH)
    print(f"✅ Copie miroir mise à jour dans : {REPO_PATH}")
    shutil.copy2(DOC_PATH, SHARED_COPY)
    print(f"✅ Copie conforme mise à jour dans : {SHARED_COPY}")
except Exception as err:
    print(f"Avertissement copie : {err}")

print("=================================================================")
print("=== APPLICATION DES TEXTURES TERMINÉE AVEC SUCCÈS ! =============")
print("=================================================================")
sys.exit(0)

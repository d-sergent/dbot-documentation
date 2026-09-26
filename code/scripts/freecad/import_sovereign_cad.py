#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
import_sovereign_cad.py — Reconstructeur d'Assemblage Souverain FreeCAD
=============================================================================
Ce script lit le manifeste JSON et les fichiers STEP extraits de Fusion 360,
recrée l'arbre hiérarchique d'assemblage (App::Part) et applique les matrices
de placement spatial 3D exactes à chaque pièce.
"""

import os
import sys
import json
import time
import shutil

print("=================================================================")
print("=== D-BOT : RECONSTRUCTION D'ASSEMBLAGE SOUVERAIN DANS FREECAD ==")
print("=================================================================")

try:
    import FreeCAD
    import Part
    from FreeCAD import Vector, Matrix, Placement
except ImportError as e:
    print(f"Erreur d'import FreeCAD: {e}")
    sys.exit(1)

EXPORT_DIR = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/Bibliotheque_Composants_STEP"
MANIFEST_FILE = os.path.join(EXPORT_DIR, "dbot_cad_manifest.json")
OUTPUT_FCSTD = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/01_Torse_et_Bassin/DBot_Torse_et_Bassin_Souverain.FCStd"
REPO_FCSTD = "/Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/DBot_Assembly_Sovereign.FCStd"
SHARED_COPY_FCSTD = "/Users/Shared/DBot_Assembly_Sovereign.FCStd"

def make_placement_from_data(origin, x_ax, y_ax, z_ax):
    """Construit un FreeCAD.Placement à partir de l'origine et des vecteurs directeurs."""
    mat = Matrix(
        x_ax[0], y_ax[0], z_ax[0], origin[0],
        x_ax[1], y_ax[1], z_ax[1], origin[1],
        x_ax[2], y_ax[2], z_ax[2], origin[2],
        0.0,     0.0,     0.0,     1.0
    )
    return Placement(mat)

def sanitize_name(name):
    """Nettoie une chaîne pour en faire un identifiant valide FreeCAD."""
    invalid = [":", " ", "-", "^", "(", ")", "[", "]", ".", "/", "\\", ",", "+", "*", "&", "~"]
    res = name
    for char in invalid:
        res = res.replace(char, "_")
    while "__" in res:
        res = res.replace("__", "_")
    return res.strip("_")

def main():
    start_total = time.time()
    
    if not os.path.exists(MANIFEST_FILE):
        print(f"❌ Erreur : Le fichier manifeste n'existe pas : {MANIFEST_FILE}")
        return 1

    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    meta = manifest.get("metadata", {})
    components = manifest.get("components", {})
    occurrences = manifest.get("occurrences", [])

    print(f"📂 Modèle source : {meta.get('source_document', 'Fusion 360')}")
    print(f"📦 Composants uniques répertoriés : {len(components)}")
    print(f"🎯 Total occurrences brutes : {len(occurrences)}")

    # 1. Création du document maître FreeCAD
    doc_name = "DBot_Sovereign"
    doc = FreeCAD.newDocument(doc_name)
    doc.Label = f"D-Bot — Assemblage Souverain ({meta.get('source_document', 'Torse v98')})"

    # 2. Création de l'arborescence structurelle principale
    root_asm = doc.addObject("App::Part", "DBot_Assembly")
    root_asm.Label = "D-Bot Robot Assembly"

    torse_part = doc.addObject("App::Part", "Torse_Superieur")
    torse_part.Label = "Torse Supérieur & Épaules [ASV1_100]"
    root_asm.addObject(torse_part)

    # Sous-groupes d'organisation pour le Torse
    torse_structure = doc.addObject("App::DocumentObjectGroup", "Structure_et_Plaques")
    torse_structure.Label = "01 - Structure & Plaques Usinées"
    torse_part.addObject(torse_structure)

    torse_actionneurs = doc.addObject("App::DocumentObjectGroup", "Actionneurs_Torse")
    torse_actionneurs.Label = "02 - Actionneurs QDD & Linéaires"
    torse_part.addObject(torse_actionneurs)

    torse_carenages = doc.addObject("App::DocumentObjectGroup", "Carenages_et_Habillage")
    torse_carenages.Label = "03 - Carénages & Habillage"
    torse_part.addObject(torse_carenages)

    torse_visserie = doc.addObject("App::DocumentObjectGroup", "Quincaillerie_Visserie")
    torse_visserie.Label = "04 - Quincaillerie & Visserie Normalisée"
    torse_part.addObject(torse_visserie)

    # Conteneur du Bassin
    bassin_part = doc.addObject("App::Part", "Bassin_Pelvis")
    bassin_part.Label = "Bassin Pelvis & Waist [ASV1_200]"
    root_asm.addObject(bassin_part)

    # Récupération du placement du Bassin dans le manifeste
    bassin_occ = None
    for occ in occurrences:
        if occ.get("instance_name") == "Bassin_Pelvis [ASV1_200]:1":
            bassin_occ = occ
            break

    if bassin_occ:
        p_bassin = make_placement_from_data(
            bassin_occ.get("origin_mm", [0, 0, 0]),
            bassin_occ.get("x_axis", [1, 0, 0]),
            bassin_occ.get("y_axis", [0, 1, 0]),
            bassin_occ.get("z_axis", [0, 0, 1])
        )
        bassin_part.Placement = p_bassin
        print(f"📍 Placement Bassin positionné à : X={p_bassin.Base.x:.2f}, Y={p_bassin.Base.y:.2f}, Z={p_bassin.Base.z:.2f} mm")

    # 3. Filtrage et sélection des occurrences à importer
    # - Les 14 composants directs de Bassin_Pelvis
    # - Les composants directs de Root (sauf Bassin_Pelvis lui-même dont les enfants sont importés)
    bassin_items = []
    root_items = []

    for occ in occurrences:
        p = occ.get("parent_instance")
        if p == "Bassin_Pelvis [ASV1_200]:1":
            bassin_items.append(occ)
        elif p == "Root" and occ.get("instance_name") != "Bassin_Pelvis [ASV1_200]:1":
            root_items.append(occ)

    total_to_import = len(bassin_items) + len(root_items)
    print(f"🚀 Occurrences à importer : {total_to_import} (Bassin: {len(bassin_items)}, Torse & Root: {len(root_items)})")

    # Cache des formes pour performance maximale
    shape_cache = {}
    success_count = 0
    missing_count = 0

    # Fonction auxiliaire pour ajouter une pièce
    def import_and_place_part(occ, parent_container, is_local_to_parent=True):
        nonlocal success_count, missing_count
        inst_name = occ.get("instance_name")
        comp_id = occ.get("component_id")
        comp_info = components.get(comp_id, {})
        step_filename = comp_info.get("step_file")

        if not step_filename:
            return False

        step_path = os.path.join(EXPORT_DIR, step_filename)
        if not os.path.exists(step_path):
            missing_count += 1
            print(f"  [!] Fichier STEP manquant : {step_filename}")
            return False

        # Lecture mise en cache
        if step_filename not in shape_cache:
            try:
                shape_cache[step_filename] = Part.read(step_path)
            except Exception as exp_err:
                print(f"  [!] Erreur lecture {step_filename}: {exp_err}")
                return False

        shape = shape_cache[step_filename].copy()
        clean_name = sanitize_name(inst_name)
        obj = doc.addObject("Part::Feature", clean_name)
        obj.Label = inst_name
        obj.Shape = shape

        # Placement spatial
        plc = make_placement_from_data(
            occ.get("origin_mm", [0, 0, 0]),
            occ.get("x_axis", [1, 0, 0]),
            occ.get("y_axis", [0, 1, 0]),
            occ.get("z_axis", [0, 0, 1])
        )
        obj.Placement = plc
        if hasattr(obj, "Visibility"):
            obj.Visibility = True

        # Enrichissement métadonnées techniques D-Bot
        try:
            mat_name = comp_info.get("material", "Aluminium 7075-T6")
            part_num = comp_info.get("part_number", "")
            mass_val = float(comp_info.get("mass_g", 0.0))

            obj.addProperty("App::PropertyString", "MaterialName", "D-Bot").MaterialName = mat_name
            obj.addProperty("App::PropertyString", "PartNumber", "D-Bot").PartNumber = part_num
            obj.addProperty("App::PropertyFloat", "Mass_g", "D-Bot").Mass_g = mass_val
            obj.addProperty("App::PropertyString", "SourceSTEP", "D-Bot").SourceSTEP = step_filename
        except Exception:
            pass

        parent_container.addObject(obj)
        success_count += 1
        return True

    # 4. Import des composants du Bassin
    print("\n--- [1/2] Importation des composants du Bassin Pelvis ---")
    for i, occ in enumerate(bassin_items, 1):
        name = occ.get("instance_name")
        c_info = components.get(occ.get("component_id"), {})
        import_and_place_part(occ, bassin_part, is_local_to_parent=True)
        print(f"  [{i:02d}/{len(bassin_items):02d}] {name:40} ({c_info.get('step_file')})")

    # 5. Import des composants du Torse
    print(f"\n--- [2/2] Importation des composants du Torse ({len(root_items)} pièces) ---")
    for i, occ in enumerate(root_items, 1):
        name = occ.get("instance_name")
        c_info = components.get(occ.get("component_id"), {})
        c_name = c_info.get("component_name", "")

        # Aiguillage intelligent vers le sous-groupe approprié
        if any(kw in c_name.lower() for kw in ["vis", "rondelle", "ecrou", "écrou", "nylstop", "nord-lock", "fhc", "chc", "bhc"]):
            target_grp = torse_visserie
        elif any(kw in c_name.lower() for kw in ["carenage", "plastron", "habillage", "capot"]):
            target_grp = torse_carenages
        elif any(kw in c_name.lower() for kw in ["rs04", "el05", "moteur", "actionneur"]):
            target_grp = torse_actionneurs
        else:
            target_grp = torse_structure

        import_and_place_part(occ, target_grp, is_local_to_parent=True)
        if i % 25 == 0 or i == len(root_items):
            print(f"  [{i:03d}/{len(root_items):03d}] Progression import Torse...")

    print(f"\n✅ {success_count}/{total_to_import} composants importés avec succès.")
    if missing_count > 0:
        print(f"⚠️ {missing_count} fichier(s) STEP introuvable(s).")

    # 6. Recalcul et Sauvegarde
    print("\nCalcul des dépendances et recalcul de l'arbre FreeCAD...")
    t_rec = time.time()
    doc.recompute()
    print(f"Recalcul achevé en {time.time() - t_rec:.2f} s.")

    print(f"Enregistrement du document maître souverain vers {OUTPUT_FCSTD}...")
    doc.saveAs(OUTPUT_FCSTD)
    file_size_mb = os.path.getsize(OUTPUT_FCSTD) / (1024 * 1024)
    print(f"✅ Fichier maître généré : {OUTPUT_FCSTD} ({file_size_mb:.2f} Mo)")

    # Copie dans le repo git et à la racine
    try:
        shutil.copy2(OUTPUT_FCSTD, REPO_FCSTD)
        print(f"✅ Copie conforme archivée dans : {REPO_FCSTD}")
        shutil.copy2(OUTPUT_FCSTD, SHARED_COPY_FCSTD)
        print(f"✅ Copie conforme archivée dans : {SHARED_COPY_FCSTD}")
    except Exception as copy_err:
        print(f"Avertissement copie : {copy_err}")

    elapsed = time.time() - start_total
    print("\n=================================================================")
    print(f"=== ASSEMBLAGE FREECAD SOUVERAIN ACHEVÉ EN {elapsed:.1f} SECONDES ! ===")
    print("=================================================================")
    return 0

# Lancement direct compatible freecadcmd
if __name__ in ["__main__", "import_sovereign_cad", "__freecad__"]:
    main()
elif True:
    main()

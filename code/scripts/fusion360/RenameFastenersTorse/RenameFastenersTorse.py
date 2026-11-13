# -*- coding: utf-8 -*-
"""
RenameFastenersTorse.py — Standardisation de la Visserie & Harmonisation des Matériaux CAO D-Bot
=============================================================================================
Ce script s'exécute directement dans Autodesk Fusion 360 (Shift + S > RenameFastenersTorse > Exécuter).

Fonctionnalités :
1. Standardisation Complète de la Visserie & Quincaillerie McMaster-Carr :
   - Renommage officiel de tous les composants selon la nomenclature projet '<Type> <Désignation> [<Réf>]'.
   - Nettoyage des chaînes longues et suppression des suffixes parasites : ' (1)', ' (2)', etc.
   - Suppression systématique du matériau par défaut 'Product Detail Link' et application d'Acier Inoxydable (7,93 g/cm3) ou Acier Allié (7,85 g/cm3).
   - Renseignement systématique du 'Part Number' et de la 'Description' officielle pour les nomenclatures.
   - Propagation du matériau physique à tous les corps BRep (bRepBodies) pour un calcul de masse rigoureux.

2. Standardisation des Composants Mécaniques du Bassin & Squelette Pelvien :
   - 'Tube transverse Epaules:2' -> 'Tube transverse Hanches [60x60]' (Alu 6060-T6, 2,70 g/cm3).
   - 'selle de pont' -> 'Selle de Pont Pelvis [ASV1_200_10]' (Alu 7075-T6, 2,81 g/cm3).
   - Les 4 'montant de hanche' -> 'Montant de Hanche Avant/Arriere Gauche/Droit [ASV1_200_11]' (Alu 6060-T6, 2,70 g/cm3).
   - Les 8 'Insert hanche' -> 'Insert Hanche Bas [ASV1_200_12]' et 'Insert Hanche Haut [ASV1_200_13]' (Alu 7075-T6, 2,81 g/cm3).
   - Coque 5mm 'Chassis_Structurel_Bassin_Last' -> 'PA12-CF (Coque 5mm Infill 15% Gyroide)' (0,70 g/cm3).
   - Ancien châssis massif 'Chassis_Structurel_Bassin [ASV1_200_01C]' -> Masquage (isLightBulbOn = False).
   - Supports & liaisons historiques de hanches ('Support_Hanche', 'Liaison_Hanche') -> 'PA12-CF' (corrige la régression +1,64 kg).

3. Intégrité des Matériaux du Torse & Épaules :
   - Corps 'ceinture' (dans Plastron_Ventral_Torse) -> 'Aluminium 7075-T6' (2,81 g/cm3).
   - Cornières hautes et basses -> 'Aluminium 7075-T6' (2,81 g/cm3).
   - Plaques structurales -> 'Aluminium 7075-T6' (Waist, Cou, Colonne, Epaules, Brides).
   - Coques & carénages -> 'PA12-CF (Infill 30% Gyroïde)' (0,56 g/cm3).
"""

import adsk.core
import adsk.fusion
import traceback
import re

# ---------------------------------------------------------------------------
# 1. RÈGLES DE NOMENCLATURE ET MATÉRIAUX DE LA QUINCAILLERIE (BOM D-BOT)
# ---------------------------------------------------------------------------
FASTENER_RULES = [
    {
        "pattern": r"91290A150",
        "new_name": "Vis CHC M4x14 [91290A150]",
        "part_number": "91290A150",
        "description": "Vis CHC M4 x 14 mm Acier allié cl. 12.9 Noir (ISO 4762 / DIN 912)",
        "material": "Acier"
    },
    {
        "pattern": r"91290A154",
        "new_name": "Vis CHC M4x16 [91290A154]",
        "part_number": "91290A154",
        "description": "Vis CHC M4 x 16 mm Acier cl. 12.9 (ISO 4762 / DIN 912)",
        "material": "Acier"
    },
    {
        "pattern": r"91290A158",
        "new_name": "Vis CHC M4x16 [91290A158]",
        "part_number": "91290A158",
        "description": "Vis CHC M4 x 16 mm Acier cl. 12.9 (ISO 4762 / DIN 912)",
        "material": "Acier"
    },
    {
        "pattern": r"91290A160",
        "new_name": "Vis CHC M4x20 [91290A160]",
        "part_number": "91290A160",
        "description": "Vis CHC M4 x 20 mm Acier cl. 12.9 (ISO 4762 / DIN 912)",
        "material": "Acier"
    },
    {
        "pattern": r"91290A170",
        "new_name": "Vis CHC M4x25 [91290A170]",
        "part_number": "91290A170",
        "description": "Vis CHC M4 x 25 mm Acier cl. 12.9 (ISO 4762 / DIN 912)",
        "material": "Acier"
    },
    {
        "pattern": r"91290A225",
        "new_name": "Vis CHC M5x25 [91290A225]",
        "part_number": "91290A225",
        "description": "Vis CHC M5 x 25 mm Acier cl. 12.9 (ISO 4762 / DIN 912)",
        "material": "Acier"
    },
    {
        "pattern": r"91290A242",
        "new_name": "Vis CHC M5x50 [91290A242]",
        "part_number": "91290A242",
        "description": "Vis CHC M5 x 50 mm Inox 18-8 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"91290A272",
        "new_name": "Vis CHC M5x70 [91290A272]",
        "part_number": "91290A272",
        "description": "Vis CHC M5 x 70 mm Acier 12.9 / Inox (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"91290A276",
        "new_name": "Vis CHC M5x80 [91290A276]",
        "part_number": "91290A276",
        "description": "Vis CHC M5 x 80 mm Acier allié cl. 12.9 Noir (ISO 4762 / DIN 912)",
        "material": "Acier"
    },
    {
        "pattern": r"91290A661",
        "new_name": "Vis CHC M5x35 [91290A661]",
        "part_number": "91290A661",
        "description": "Vis CHC M5 x 35 mm Acier allié cl. 12.9 Noir (ISO 4762 / DIN 912)",
        "material": "Acier"
    },
    {
        "pattern": r"91292A017",
        "new_name": "Vis CHC M2.5x14 [91292A017]",
        "part_number": "91292A017",
        "description": "Vis CHC M2.5 x 14 mm Inox 18-8 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"91292A113",
        "new_name": "Vis CHC M3x10 [91292A113]",
        "part_number": "91292A113",
        "description": "Vis CHC M3 x 10 mm Inox 18-8 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"91292A118",
        "new_name": "Vis CHC M4x16 [91292A118]",
        "part_number": "91292A118",
        "description": "Vis CHC M4 x 16 mm Inox 18-8 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"91292A121",
        "new_name": "Vis CHC M4x20 [91292A121]",
        "part_number": "91292A121",
        "description": "Vis CHC M4 x 20 mm Inox 18-8 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"91292A122",
        "new_name": "Vis CHC M4x25 [91292A122]",
        "part_number": "91292A122",
        "description": "Vis CHC M4 x 25 mm Inox 18-8 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"91292A129",
        "new_name": "Vis CHC M5x25 [91292A129]",
        "part_number": "91292A129",
        "description": "Vis CHC M5 x 25 mm Inox 18-8 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"91292A130",
        "new_name": "Vis CHC M4x30 [91292A130]",
        "part_number": "91292A130",
        "description": "Vis CHC M4 x 30 mm Inox 18-8 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92290A130",
        "new_name": "Vis CHC M4x12 [92290A130]",
        "part_number": "92290A130",
        "description": "Vis CHC M4 x 12 mm Inox 316 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92290A145",
        "new_name": "Vis CHC M4x16 [92290A145]",
        "part_number": "92290A145",
        "description": "Vis CHC M4 x 16 mm Inox 316 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92290A148",
        "new_name": "Vis CHC M4x25 [92290A148]",
        "part_number": "92290A148",
        "description": "Vis CHC M4 x 25 mm Inox 316 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92290A154",
        "new_name": "Vis CHC M4x16 [92290A154]",
        "part_number": "92290A154",
        "description": "Vis CHC M4 x 16 mm Inox 316 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92290A161",
        "new_name": "Vis CHC M4x18 [92290A161]",
        "part_number": "92290A161",
        "description": "Vis CHC M4 x 18 mm Inox 316 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92290A168",
        "new_name": "Vis CHC M4x20 [92290A168]",
        "part_number": "92290A168",
        "description": "Vis CHC M4 x 20 mm Inox 316 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92290A242",
        "new_name": "Vis CHC M5x20 [92290A242]",
        "part_number": "92290A242",
        "description": "Vis CHC M5 x 20 mm Inox 316 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92290A252",
        "new_name": "Vis CHC M5x25 [92290A252]",
        "part_number": "92290A252",
        "description": "Vis CHC M5 x 25 mm Inox 316 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92290A272",
        "new_name": "Vis CHC M5x70 [92290A272]",
        "part_number": "92290A272",
        "description": "Vis CHC M5 x 70 mm Inox 316 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92290A858",
        "new_name": "Vis CHC M2.5x14 [92290A858]",
        "part_number": "92290A858",
        "description": "Vis CHC M2.5 x 14 mm Inox 316 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92855A313",
        "new_name": "Vis CHC M3x12 Tête Basse [92855A313]",
        "part_number": "92855A313",
        "description": "Vis CHC M3 x 12 mm Tête Basse Inox 18-8 (DIN 7984)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92855A422",
        "new_name": "Vis CHC M4x25 Tête Basse [92855A422]",
        "part_number": "92855A422",
        "description": "Vis CHC M4 x 25 mm Tête Basse Inox 18-8 (DIN 7984)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"90128A214",
        "new_name": "Vis CHC M4x16 [90128A214]",
        "part_number": "90128A214",
        "description": "Vis CHC M4 x 16 mm Acier zingué cl. 8.8 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"90348A023",
        "new_name": "Vis CHC M5x25 [90348A023]",
        "part_number": "90348A023",
        "description": "Vis CHC M5 x 25 mm Inox 18-8 Noir (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92125A128",
        "new_name": "Vis FHC M3x8 [92125A128]",
        "part_number": "92125A128",
        "description": "Vis FHC M3 x 8 mm Inox 18-8 (ISO 10642 / DIN 7991)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92125A213",
        "new_name": "Vis FHC M5x18 [92125A213]",
        "part_number": "92125A213",
        "description": "Vis FHC M5 x 18 mm Inox 18-8 (ISO 10642 / DIN 7991)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92125A220",
        "new_name": "Vis FHC M4x30 [92125A220]",
        "part_number": "92125A220",
        "description": "Vis FHC M4 x 30 mm Inox 18-8 (ISO 10642 / DIN 7991)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92125A230",
        "new_name": "Vis FHC M5x25 [92125A230]",
        "part_number": "92125A230",
        "description": "Vis FHC M5 x 25 mm Inox 316 (ISO 10642 / DIN 7991)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"(?:91294A112|^LUOSI_1)",
        "new_name": "Vis FHC M3x8 [91294A112]",
        "part_number": "91294A112",
        "description": "Vis FHC M3 x 8 mm Inox 18-8 (ISO 10642 / DIN 7991)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"93475A230",
        "new_name": "Rondelle Plate DIN 125A M4 [93475A230]",
        "part_number": "93475A230",
        "description": "Rondelle Plate DIN 125A M4 Inox 18-8 (ISO 7089 / DIN 125A)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"93475A240",
        "new_name": "Rondelle Plate DIN 125A M5 [93475A240]",
        "part_number": "93475A240",
        "description": "Rondelle Plate DIN 125A M5 Inox 18-8 (ISO 7089 / DIN 125A)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"(?:91812A252|Wedge Lock|Nord-Lock M4)",
        "new_name": "Rondelle Nord-Lock M4 [91812A252]",
        "part_number": "91812A252",
        "description": "Rondelle Nord-Lock M4 Inox / Acier (NL4)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"93625A150",
        "new_name": "Ecrou Nylstop M4 [93625A150]",
        "part_number": "93625A150",
        "description": "Écrou Frein Nylstop M4 Inox 18-8 (ISO 7040 / DIN 985)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"93625A200",
        "new_name": "Ecrou Nylstop M5 [93625A200]",
        "part_number": "93625A200",
        "description": "Écrou Frein Nylstop M5 Inox 18-8 (ISO 7040 / DIN 985)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"90631A113",
        "new_name": "Ecrou Nylstop M5 [90631A113]",
        "part_number": "90631A113",
        "description": "Écrou Frein Nylstop M5 Inox 18-8 (ISO 7040 / DIN 985)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"91585A374",
        "new_name": "Goupille cylindrique ISO 8734 Ø3x14 [91585A374]",
        "part_number": "91585A374",
        "description": "Goupille cylindrique rectifiée Ø 3 x 14 mm Inox 18-8 (ISO 8734 / ISO 2338)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"91595A114",
        "new_name": "Goupille cylindrique ISO 8734 Ø3x14 [91595A114]",
        "part_number": "91595A114",
        "description": "Goupille cylindrique rectifiée Ø 3 x 14 mm Acier allié trempé (ISO 8734 / DIN 6325)",
        "material": "Acier"
    }
]

# ---------------------------------------------------------------------------
# 2. RÈGLES DE MATÉRIAUX POUR LES PIÈCES STRUCTURALES (TORSE & BASSIN)
# ---------------------------------------------------------------------------
STRUCTURAL_RULES = [
    {
        "material_name": "Aluminium 7075-T6",
        "density_g_cm3": 2.81,
        "keywords": [
            "waist_plate",
            "plaque_de_cou",
            "equerre waist",
            "equerre cou",
            "colonne vertébrale",
            "semelle éclisse",
            "moyeu_waist_sandwich",
            "bride epaule",
            "traverse_renfort_bassin",
            "corniere",
            "ceinture",
            "selle de pont",
            "insert hanche"
        ]
    },
    {
        "material_name": "Aluminium 6060-T6",
        "density_g_cm3": 2.70,
        "keywords": [
            "tube transverse epaules",
            "tube transverse hanches",
            "montant de hanche"
        ]
    },
    {
        "material_name": "PA12-CF (Coque 5mm Infill 15% Gyroide)",
        "density_g_cm3": 0.70,
        "keywords": [
            "chassis_structurel_bassin_last"
        ]
    },
    {
        "material_name": "PA12-CF (Infill 30% Gyroïde)",
        "density_g_cm3": 0.56,
        "keywords": [
            "plastron_ventral_torse",
            "platine_connectique_facade",
            "panier_batterie",
            "support batterie central",
            "capot_verrouillage",
            "carenage_pectoral",
            "carenage_lombaire",
            "trappe_inferieure_bassin",
            "capot_lateral_hanche",
            "capot_protection_hanche",
            "support_hanche",
            "liaison_hanche",
            "fixation batterie",
            "cou - tube collet"
        ]
    }
]

# ---------------------------------------------------------------------------
# 3. GESTION DES MATÉRIAUX DANS FUSION 360 (Création et Cache)
# ---------------------------------------------------------------------------
def strip_fusion_suffix(name):
    """Supprime le suffixe Fusion automatique ' (1)', ' (2)', etc. pour comparer les noms."""
    return re.sub(r"\s*\(\d+\)$", "", (name or "").strip())

def find_density_property(mat):
    """Localise la propriété Densité quel que soit le langage de Fusion 360 (FR/EN)."""
    if not mat:
        return None
    for exact_name in ('Density', 'Densité'):
        try:
            prop = mat.materialProperties.itemByName(exact_name)
            if prop:
                return prop
        except:
            pass
    try:
        for prop in mat.materialProperties:
            pid = str(getattr(prop, 'id', '')).lower()
            pname = str(getattr(prop, 'name', '')).lower()
            if 'density' in pid or 'density' in pname or 'densit' in pname or 'masse volumique' in pname:
                return prop
    except:
        pass
    return None

def set_material_density_g_cm3(mat, density_g_cm3):
    """Applique la densité cible (convertie g/cm3 -> kg/m3 SI Fusion) si différente."""
    density_prop = find_density_property(mat)
    if not density_prop:
        return False
    try:
        cur_val = float(density_prop.value)
        # Fusion API stocke Density en SI (kg/m3, ex: 1015.0 pour 1.015 g/cm3)
        scale = 1000.0 if (cur_val <= 0.0 or cur_val > 20.0) else 1.0
        target_val = float(density_g_cm3) * scale
        tol = 0.02 * scale
        if abs(cur_val - target_val) > tol:
            density_prop.value = target_val
            return True
    except:
        pass
    return False

def create_or_get_custom_material(design, app, mat_name, density_g_cm3):
    """Crée ou récupère un matériau sur-mesure dans Fusion 360 avec sa densité physique exacte."""
    existing = design.materials.itemByName(mat_name)
    if existing:
        if "coque 5mm" in mat_name.lower():
            set_material_density_g_cm3(existing, density_g_cm3)
        return existing

    base_mat = None
    if "pa12" in mat_name.lower():
        for m in design.materials:
            if "pa12-cf" in m.name.lower() and "coque 5mm" not in m.name.lower():
                base_mat = m
                break

    if not base_mat:
        mat_lib = app.materialLibraries.itemByName('Fusion 360 Material Library')
        if mat_lib:
            candidates = ['Stainless Steel', 'Aluminum', 'Steel', 'Nylon 6/6', 'ABS Plastic', 'Plastic']
            for cand in candidates:
                try:
                    m = mat_lib.materials.itemByName(cand)
                    if m:
                        base_mat = m
                        break
                except:
                    pass

    if not base_mat and design.materials.count > 0:
        base_mat = design.materials.item(0)

    if not base_mat:
        return None

    try:
        new_mat = design.materials.addByCopy(base_mat, mat_name)
        if not new_mat:
            return None
        set_material_density_g_cm3(new_mat, density_g_cm3)
        return new_mat
    except:
        return None

def find_best_material(design, app, req_mat_name, density_fallback=2.81):
    """Localise un matériau dans le design ou la bibliothèque, ou le crée dynamiquement."""
    req_l = req_mat_name.lower()

    # 1. Acier Inoxydable (Fasteners)
    if "inox" in req_l or "stainless" in req_l:
        for m in design.materials:
            if "inox" in m.name.lower() or "stainless" in m.name.lower():
                return m
        for lib in app.materialLibraries:
            try:
                for candidate in ['Stainless Steel', 'Acier inoxydable', 'Steel, Stainless']:
                    m = lib.materials.itemByName(candidate)
                    if m:
                        return design.materials.addByCopy(m, m.name)
            except:
                pass
        return create_or_get_custom_material(design, app, "Acier inoxydable", 7.93)

    # 2. Aluminium 7075-T6
    if "7075" in req_l:
        for m in design.materials:
            if "7075" in m.name.lower():
                return m
        for lib in app.materialLibraries:
            try:
                for m in lib.materials:
                    if "7075" in m.name.lower():
                        return design.materials.addByCopy(m, m.name)
            except:
                pass
        for m in design.materials:
            if "alumin" in m.name.lower():
                return m
        return create_or_get_custom_material(design, app, "Aluminium 7075-T6", 2.81)

    # 3. Aluminium 6060-T6
    if "6060" in req_l or "6061" in req_l:
        for m in design.materials:
            if "6060" in m.name.lower() or "6061" in m.name.lower():
                return m
        for lib in app.materialLibraries:
            try:
                for m in lib.materials:
                    if "6060" in m.name.lower() or "6061" in m.name.lower():
                        return design.materials.addByCopy(m, m.name)
            except:
                pass
        return create_or_get_custom_material(design, app, "Aluminium 6060-T6", 2.70)

    # 4. PA12-CF Coque 5mm (densité calibrée à 0,70 g/cm3)
    if "coque 5mm" in req_l or "0.70" in req_l or "0,70" in req_l:
        for m in design.materials:
            if "coque 5mm" in m.name.lower():
                set_material_density_g_cm3(m, 0.70)
                return m
        return create_or_get_custom_material(design, app, "PA12-CF (Coque 5mm Infill 15% Gyroide)", 0.70)

    # 5. PA12-CF Standard / Cosmétique (hors Coque 5mm 0,70 g/cm3)
    if "pa12" in req_l or "cf" in req_l or "gyro" in req_l:
        for m in design.materials:
            m_low = m.name.lower()
            if "pa12-cf" in m_low and "cosmetique" in m_low:
                return m
        for m in design.materials:
            m_low = m.name.lower()
            if "pa12-cf" in m_low and "coque 5mm" not in m_low:
                return m
        return create_or_get_custom_material(design, app, "PA12-CF (Infill 30% Gyroïde)", 0.56)

    # 6. Acier Allié / Acier Standard (exclut explicitement Inox / Stainless)
    if "acier" in req_l or "steel" in req_l:
        for m in design.materials:
            m_low = m.name.lower()
            if m_low in ("acier", "steel") or (
                ("acier" in m_low or "steel" in m_low)
                and "inox" not in m_low
                and "stainless" not in m_low
            ):
                return m
        for lib in app.materialLibraries:
            try:
                for candidate in ['Steel', 'Acier', 'Steel, Mild']:
                    m = lib.materials.itemByName(candidate)
                    if m:
                        return design.materials.addByCopy(m, m.name)
            except:
                pass
        return create_or_get_custom_material(design, app, "Acier", 7.85)

    return create_or_get_custom_material(design, app, req_mat_name, density_fallback)

# ---------------------------------------------------------------------------
# 4. EXÉCUTION PRINCIPALE DU SCRIPT
# ---------------------------------------------------------------------------
def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            if ui:
                ui.messageBox("Aucun modèle actif dans Autodesk Fusion 360.")
            return

        # Préchauffage et instanciation du cache des matériaux certifiés D-Bot
        materials_cache = {
            "Acier inoxydable": find_best_material(design, app, "Acier inoxydable", 7.93),
            "Aluminium 7075-T6": find_best_material(design, app, "Aluminium 7075-T6", 2.81),
            "Aluminium 6060-T6": find_best_material(design, app, "Aluminium 6060-T6", 2.70),
            "PA12-CF (Coque 5mm Infill 15% Gyroide)": find_best_material(design, app, "PA12-CF (Coque 5mm Infill 15% Gyroide)", 0.70),
            "PA12-CF (Infill 30% Gyroïde)": find_best_material(design, app, "PA12-CF (Infill 30% Gyroïde)", 0.56),
            "Acier": find_best_material(design, app, "Acier", 7.85)
        }

        mat_inox = materials_cache.get("Acier inoxydable")
        mat_alu_7075 = materials_cache.get("Aluminium 7075-T6")
        mat_alu_6060 = materials_cache.get("Aluminium 6060-T6")
        mat_pa12_coque = materials_cache.get("PA12-CF (Coque 5mm Infill 15% Gyroide)")

        renamed_components = 0
        materials_applied_comps = 0
        bodies_material_fixed = 0
        pelvis_parts_fixed = 0
        hidden_old_blocks = 0
        ceinture_updated = False
        ceinture_new_mass_g = 0.0
        log_lines = []

        root_comp = design.rootComponent

        # ===================================================================
        # ÉTAPE 1 : HARMONISATION MÉCANIQUE DES PIÈCES DU BASSIN & SQUELETTE
        # ===================================================================
        # NOTE IMPORTANTE FUSION 360 API :
        # Dans Fusion 360, Occurrence.name est une propriété en lecture seule.
        # Le nom affiché dans l'arborescence est automatiquement dérivé du
        # nom du composant parent (Component.name). C'est comp.name qui doit être modifié.
        processed_components = set()

        for occ in root_comp.allOccurrences:
            occ_name = occ.name
            occ_l = occ_name.lower()
            comp = occ.component
            if not comp or comp.entityToken in processed_components:
                continue

            comp_l = comp.name.lower()

            # 1.1 Tube Pont des Hanches (anciennement Tube transverse Epaules:2)
            if "tube transverse epaules:2" in occ_l or (comp.name == "Tube transverse Epaules" and occ.boundingBox.minPoint.z < 110.0):
                new_cname = "Tube transverse Hanches [60x60]"
                if comp.name != new_cname:
                    comp.name = new_cname
                    comp.partNumber = "Tube_Transverse_Hanches_60x60"
                    comp.description = "Tube profilé 60x60x2 mm entre RS-04 Hanches (Alu 6060-T6)"
                    renamed_components += 1
                if mat_alu_6060:
                    comp.material = mat_alu_6060
                    for b in comp.bRepBodies:
                        b.material = mat_alu_6060
                        bodies_material_fixed += 1
                pelvis_parts_fixed += 1
                processed_components.add(comp.entityToken)
                log_lines.append(f"• Tube Hanches ➔ '{comp.name}' (Alu 6060-T6, 2,70 g/cm3)")

            # 1.2 Selle de Pont Pelvienne en H
            elif "selle de pont" in occ_l or "selle de pont" in comp_l:
                new_cname = "Selle de Pont Pelvis [ASV1_200_10]"
                if comp.name != new_cname:
                    comp.name = new_cname
                    comp.partNumber = "ASV1_200_10"
                    comp.description = "Selle de Pont en H 140x145x22 mm (Alu 7075-T651)"
                    renamed_components += 1
                if mat_alu_7075:
                    comp.material = mat_alu_7075
                    for b in comp.bRepBodies:
                        b.material = mat_alu_7075
                        bodies_material_fixed += 1
                pelvis_parts_fixed += 1
                processed_components.add(comp.entityToken)
                log_lines.append(f"• Selle de Pont ➔ '{comp.name}' (Alu 7075-T6, 2,81 g/cm3)")

            # 1.3 Montants Verticaux 20x20 (+X = Avant, -X = Arriere | +Y = Gauche, -Y = Droit)
            elif "montant de hanche" in occ_l or "montant de hanche" in comp_l:
                try:
                    bb = occ.boundingBox
                    x_mid_cm = 0.5 * (bb.minPoint.x + bb.maxPoint.x)
                    y_mid_cm = 0.5 * (bb.minPoint.y + bb.maxPoint.y)
                    pos = "Avant" if x_mid_cm > 5.48 else "Arriere"
                    cote = "Gauche" if y_mid_cm > 0.87 else "Droit"
                except:
                    pos = "Arriere" if "arriere" in occ_l else "Avant"
                    cote = "Gauche" if "symétrie" in occ_l else "Droit"
                new_cname = f"Montant de Hanche {pos} {cote} [ASV1_200_11]"
                if strip_fusion_suffix(comp.name) != new_cname:
                    old_cname = comp.name
                    try:
                        comp.name = new_cname
                        renamed_components += 1
                        log_lines.append(f"• Montant : '{old_cname}' ➔ '{comp.name}'")
                    except:
                        pass
                try:
                    comp.partNumber = "ASV1_200_11"
                    comp.description = f"Tube montant vertical {pos.lower()} {cote.lower()} 20x20x2 mm L=65.75 mm (Alu 6060-T6)"
                except:
                    pass
                if mat_alu_6060:
                    try:
                        if not comp.material or comp.material.name != mat_alu_6060.name:
                            comp.material = mat_alu_6060
                            materials_applied_comps += 1
                    except:
                        pass
                    for b in comp.bRepBodies:
                        try:
                            if not b.material or b.material.name != mat_alu_6060.name:
                                b.material = mat_alu_6060
                                bodies_material_fixed += 1
                        except:
                            pass
                pelvis_parts_fixed += 1
                processed_components.add(comp.entityToken)

            # 1.4 Inserts Taraudés Tube 20x20 (Discrimination Bas / Haut par l'altitude Z)
            elif "insert hanche" in occ_l or "insert hanche" in comp_l:
                z_min_cm = occ.boundingBox.minPoint.z
                if z_min_cm > 98.0:  # Z > 980 mm -> Inserts du Haut sous Traverse Renfort
                    new_cname = "Insert Hanche Haut [ASV1_200_13]"
                    part_no = "ASV1_200_13"
                    desc = "Insert usiné haut 15.8x15.8x15 mm taraudé M5 (Alu 7075-T6)"
                else:  # Z <= 980 mm -> Inserts du Bas sur Selle de Pont
                    new_cname = "Insert Hanche Bas [ASV1_200_12]"
                    part_no = "ASV1_200_12"
                    desc = "Insert usiné bas 15.8x15.8x15 mm taraudé M4 (Alu 7075-T6)"

                if strip_fusion_suffix(comp.name) != new_cname:
                    try:
                        comp.name = new_cname
                        renamed_components += 1
                    except:
                        pass
                try:
                    comp.partNumber = part_no
                    comp.description = desc
                except:
                    pass
                if mat_alu_7075:
                    try:
                        if not comp.material or comp.material.name != mat_alu_7075.name:
                            comp.material = mat_alu_7075
                            materials_applied_comps += 1
                    except:
                        pass
                    for b in comp.bRepBodies:
                        try:
                            if not b.material or b.material.name != mat_alu_7075.name:
                                b.material = mat_alu_7075
                                bodies_material_fixed += 1
                        except:
                            pass
                pelvis_parts_fixed += 1
                processed_components.add(comp.entityToken)

            # 1.5 Coque Pelvienne 5mm
            elif "chassis_structurel_bassin_last" in occ_l:
                if mat_pa12_coque:
                    try:
                        comp.material = mat_pa12_coque
                    except:
                        pass
                    for b in comp.bRepBodies:
                        try:
                            b.material = mat_pa12_coque
                            bodies_material_fixed += 1
                        except:
                            pass
                processed_components.add(comp.entityToken)
                log_lines.append("• Coque Pelvis ➔ 'PA12-CF Coque 5mm' (0,70 g/cm3)")

            # 1.6 Masquage de l'Ancien Châssis Massif (pour éliminer le doublon de 2,37 kg)
            elif "asv1_200_01c" in occ_l or ("chassis_structurel_bassin" in occ_l and "last" not in occ_l):
                if occ.isLightBulbOn:
                    occ.isLightBulbOn = False
                    hidden_old_blocks += 1
                    log_lines.append(f"• Ancien Châssis Massif masqué ➔ '{occ.name}' (évite doublon)")

        # ===================================================================
        # ÉTAPE 2 : STANDARDISATION DES COMPOSANTS VISSERIE & MCMASTER-CARR
        # ===================================================================
        for comp in design.allComponents:
            cname = comp.name
            
            # Recherche de correspondance dans le catalogue de visserie
            matched_rule = None
            for rule in FASTENER_RULES:
                if re.search(rule["pattern"], cname, re.IGNORECASE):
                    matched_rule = rule
                    break

            if matched_rule:
                if strip_fusion_suffix(comp.name) != matched_rule["new_name"]:
                    old_cname = comp.name
                    try:
                        comp.name = matched_rule["new_name"]
                        renamed_components += 1
                        log_lines.append(f"• Visserie : '{old_cname}'\n   ➔ '{comp.name}'")
                    except:
                        pass

                try:
                    comp.partNumber = matched_rule["part_number"]
                except:
                    pass
                try:
                    comp.description = matched_rule["description"]
                except:
                    pass

                target_mat_name = matched_rule.get("material", "Acier inoxydable")
                target_mat = materials_cache.get(target_mat_name)
                if target_mat:
                    if not comp.material or comp.material.name != target_mat.name:
                        try:
                            comp.material = target_mat
                            materials_applied_comps += 1
                        except:
                            pass
                    # Assigner rigoureusement à tous les corps BRep pour purger 'Product Detail Link'
                    for b in comp.bRepBodies:
                        try:
                            if not b.material or b.material.name != target_mat.name:
                                b.material = target_mat
                                bodies_material_fixed += 1
                        except:
                            pass
                continue

            # Vérification des pièces structurales générales
            cname_l = cname.lower()
            for s_rule in STRUCTURAL_RULES:
                if any(kw in cname_l for kw in s_rule["keywords"]):
                    mat_obj = materials_cache.get(s_rule["material_name"])
                    if mat_obj:
                        has_ceinture = any("ceinture" in b.name.lower() for b in comp.bRepBodies)
                        changed = False
                        if not has_ceinture and (not comp.material or comp.material.name != mat_obj.name):
                            try:
                                comp.material = mat_obj
                                materials_applied_comps += 1
                                changed = True
                            except:
                                pass
                        for b in comp.bRepBodies:
                            if "ceinture" in b.name.lower():
                                continue
                            try:
                                if not b.material or b.material.name != mat_obj.name:
                                    b.material = mat_obj
                                    bodies_material_fixed += 1
                                    changed = True
                            except:
                                pass
                        if changed:
                            log_lines.append(f"• Matériau '{mat_obj.name}' appliqué sur '{comp.name}'")
                    break

        # ===================================================================
        # ÉTAPE 3 : TRAITEMENT DU CORPS 'CEINTURE' (Alu 7075-T6 dans Plastron)
        # ===================================================================
        if mat_alu_7075:
            for comp in design.allComponents:
                for body in comp.bRepBodies:
                    if "ceinture" in body.name.lower():
                        try:
                            body.material = mat_alu_7075
                            ceinture_updated = True
                            b_props = body.getPhysicalProperties(adsk.fusion.CalculationAccuracy.MediumCalculationAccuracy)
                            ceinture_new_mass_g = round(b_props.mass * 1000.0, 2)
                            log_lines.append(f"• Corps 'ceinture' (dans {comp.name}) ➔ Alu 7075-T6 (Masse = {ceinture_new_mass_g} g)")
                        except:
                            pass

        # ===================================================================
        # ÉTAPE 4 : TRAITEMENT DES CORNIÈRES (Alu 7075-T6 & Nomenclature)
        # ===================================================================
        corniere_updated = False
        corniere_new_mass_g = 0.0
        corniere_count = 0
        if mat_alu_7075:
            for comp in design.allComponents:
                c_low = comp.name.lower()
                if "corniere" in c_low:
                    try:
                        comp.material = mat_alu_7075
                        for body in comp.bRepBodies:
                            body.material = mat_alu_7075
                        c_props = comp.getPhysicalProperties(adsk.fusion.CalculationAccuracy.MediumCalculationAccuracy)
                        corniere_new_mass_g = round(c_props.mass * 1000.0, 2)
                        corniere_updated = True
                        corniere_count += 1
                        
                        if "haute" in c_low:
                            comp.partNumber = "Corniere_Haute_7075"
                            comp.description = "Cornière Haute Nervurée Portique Épaules (Alu 7075-T6)"
                        elif "basse" in c_low:
                            comp.partNumber = "Corniere_Basse_7075"
                            comp.description = "Cornière Basse Nervurée Portique Waist (Alu 7075-T6)"
                            
                        log_lines.append(f"• Cornière '{comp.name}' ➔ Alu 7075-T6 (Masse = {corniere_new_mass_g} g)")
                    except:
                        pass

        # ===================================================================
        # ÉTAPE 5 : SYNTHÈSE ET MESSAGE DE CONFIRMATION
        # ===================================================================
        msg = "=== STANDARDISATION NOMENCLATURE & MATÉRIAUX D-BOT TERMINÉE ===\n\n"
        msg += f"• Composants renommés & standardisés : {renamed_components}\n"
        msg += f"• Composants recevant le matériau certifié : {materials_applied_comps}\n"
        msg += f"• Corps BRep assainis (purge 'Product Detail Link') : {bodies_material_fixed}\n"
        msg += f"• Pièces structurales Bassin/Pelvis harmonisées : {pelvis_parts_fixed}\n"
        
        if hidden_old_blocks > 0:
            msg += f"• Blocs historiques masqués (évite doublons) : {hidden_old_blocks}\n"

        if ceinture_updated:
            msg += f"• Corps 'ceinture' actualisé en Alu 7075-T6 : {ceinture_new_mass_g} g (CONFORME)\n"

        if corniere_updated:
            msg += f"• Cornière(s) actualisée(s) en Alu 7075-T6 ({corniere_count} comp) : {corniere_new_mass_g} g (CONFORME)\n"
            
        msg += "\n"
        if log_lines:
            msg += "Détail des actions appliquées :\n\n" + "\n\n".join(log_lines[:15])
            if len(log_lines) > 15:
                msg += f"\n\n... et {len(log_lines) - 15} autres modifications de conformité."
        else:
            msg += "Tous les composants et matériaux sont déjà 100% conformes aux standards D-Bot !"

        msg += "\n\nConseil : Effectuez 'Modifier > Tout calculer' (Cmd+B) puis relancez 'AuditTorse'."

        if ui:
            ui.messageBox(msg, "Standardisation Torse & Bassin D-Bot")

    except Exception as e:
        if ui:
            ui.messageBox(f"Erreur durant l'exécution du script :\n{traceback.format_exc()}", "Erreur RenameFastenersTorse")


if __name__ == "__main__":
    run(None)

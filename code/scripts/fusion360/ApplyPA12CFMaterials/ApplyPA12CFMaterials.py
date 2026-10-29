# -*- coding: utf-8 -*-
"""
ApplyPA12CFMaterials.py — Script d'harmonisation des densités apparentes FDM & Calcul du Poids Réel
Projet : Robot Humanoïde D-Bot V1 (Torse & Bassin)
=============================================================================
Ce script s'exécute directement dans Fusion 360 (Raccourci Shift + S > Exécuter).
Il applique les 3 catégories de matériaux calibrés FDM (PA12-CF) aux géométries pleines :
  1. Catégorie A - Cosmétique (12-15% gyroïde) : 0,55 g/cm³ (Carénages, trappes, collet cou)
  2. Catégorie B - Semi-porteur (20-25% gyroïde) : 0,62 g/cm³ (Coque C1/C2, rack batterie)
  3. Catégorie C - Châssis Pelvien (70-80% lourd) : 0,85 g/cm³ (Châssis maître de bassin)

Protège rigoureusement la quincaillerie et les inserts métalliques (Alu 7075, visserie, roulement).
Calcule la masse totale réaliste de l'assemblage complet, la masse propre du Torse seul (hors batterie
et avec batterie), la masse propre du Bassin, ainsi que le nouveau Centre de Masse (CoM) Z au sternum.
Exporte automatiquement l'audit métrologique calibré en JSON.
"""

import adsk.core
import adsk.fusion
import os
import json
import traceback

# Barème des densités apparentes calibrées FDM (en g/cm³)
DENSITY_SPECS = {
    "COSMETIC": {
        "name": "PA12-CF (Cosmetique Infill 15% Gyroide)",
        "target_density_g_cm3": 0.55,
        "keywords": [
            "carenage_pectoral", "carenage_lombaire", "plastron_abdominal",
            "trappe_inferieure", "cou - tube collet", "hanche_gauche", "hanche_droite",
            "platine_connectique_facade", "trappe_pectorale", "trappe_abdominale",
            "coquille_hanche"
        ]
    },
    "TORSO": {
        "name": "PA12-CF (Torse Infill 25% Gyroide)",
        "target_density_g_cm3": 0.62,
        "keywords": [
            "plastron_ventral_torse", "panier_batterie_coulissant", "capot_verrouillage_batterie",
            "torse_haut_c1", "torse_haut_c2"
        ]
    },
    "PELVIS": {
        "name": "PA12-CF (Bassin Structurel Infill 75%)",
        "target_density_g_cm3": 0.85,
        "keywords": [
            "chassis_structurel_bassin", "bassin_pelvis"
        ]
    }
}

SOLID_PA12CF_DENSITY_REF = 1.015  # Densité nominale solide 100% (g/cm³)
JSON_EXPORT_PATH = "/Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/AUDIT_METROLOGIQUE_Torse_et_Bassin_Calibre.json"

def get_or_create_material(design, base_material, spec_name, target_density):
    """Récupère ou crée un matériau physique custom avec la densité calibrée."""
    # 1. Vérifier si le matériau existe déjà dans le document
    for mat in design.materials:
        if mat.name.strip().lower() == spec_name.strip().lower():
            return mat

    # 2. Créer une copie à partir du matériau de base (addByCopy ou addByCopying)
    new_mat = None
    try:
        new_mat = design.materials.addByCopy(base_material, spec_name)
    except Exception:
        try:
            new_mat = design.materials.addByCopying(base_material, spec_name)
        except Exception:
            pass

    if not new_mat:
        return base_material

    # 3. Ajustement de la densité physique proportionnellement au matériau de référence
    try:
        ref_density_prop = base_material.materialProperties.itemByName('Density')
        if not ref_density_prop:
            for prop in base_material.materialProperties:
                if "density" in prop.name.lower():
                    ref_density_prop = prop
                    break

        new_density_prop = new_mat.materialProperties.itemByName('Density')
        if not new_density_prop:
            for prop in new_mat.materialProperties:
                if "density" in prop.name.lower():
                    new_density_prop = prop
                    break

        if ref_density_prop and new_density_prop and ref_density_prop.value > 0:
            scale_ratio = target_density / SOLID_PA12CF_DENSITY_REF
            new_density_prop.value = ref_density_prop.value * scale_ratio
        elif new_density_prop:
            new_density_prop.value = float(target_density)
    except Exception:
        pass

    return new_mat

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            if ui:
                ui.messageBox("Veuillez exécuter ce script avec un assemblage 3D actif (Design).", "D-Bot Materials")
            return

        root_comp = design.rootComponent

        # -------------------------------------------------------------
        # 0. Mesure initiale globale de l'assemblage
        # -------------------------------------------------------------
        initial_assembly_mass_kg = root_comp.physicalProperties.mass
        com_init = root_comp.physicalProperties.centerOfMass
        com_init_mm = [com_init.x * 10.0, com_init.y * 10.0, com_init.z * 10.0]

        # -------------------------------------------------------------
        # 1. Recherche du matériau PA12-CF et apparence de référence
        # -------------------------------------------------------------
        ref_material = None
        ref_appearance = None

        # Recherche prioritaire dans les pièces composites existantes
        for comp in design.allComponents:
            c_name = comp.name.lower()
            if any(k in c_name for k in ["cou", "lombaire", "panier", "torse"]):
                for b in comp.bRepBodies:
                    if b.material and ("pa12" in b.material.name.lower() or "nylon" in b.material.name.lower()):
                        ref_material = b.material
                        if b.appearance:
                            ref_appearance = b.appearance
                        break
            if ref_material:
                break

        # Recherche secondaire dans la bibliothèque du document
        if not ref_material:
            for mat in design.materials:
                if "pa12" in mat.name.lower() or "nylon" in mat.name.lower() or "carbon" in mat.name.lower():
                    ref_material = mat
                    break

        if not ref_appearance:
            for app_item in design.appearances:
                if any(k in app_item.name.lower() for k in ["pa12", "carbon", "black", "noir"]):
                    ref_appearance = app_item
                    break

        # Fallback si aucun matériau PA12 trouvé : utiliser le premier matériau disponible
        if not ref_material and len(design.materials) > 0:
            ref_material = design.materials.item(0)

        if not ref_material:
            if ui:
                ui.messageBox(
                    "Aucun matériau physique n'a pu servir de base.\n"
                    "Veuillez affecter au moins un matériau physique à une pièce.",
                    "Erreur Initialisation"
                )
            return

        # -------------------------------------------------------------
        # 2. Création / Récupération des 3 matériaux calibrés FDM
        # -------------------------------------------------------------
        cat_materials = {}
        for cat_key, spec in DENSITY_SPECS.items():
            cat_materials[cat_key] = get_or_create_material(
                design, ref_material, spec["name"], spec["target_density_g_cm3"]
            )

        # -------------------------------------------------------------
        # 3. Application ciblée des matériaux et apparence
        # -------------------------------------------------------------
        modified_components = []
        total_delta_g = 0.0

        for comp in design.allComponents:
            c_name_lower = comp.name.lower()
            target_cat = None

            for cat_key, spec in DENSITY_SPECS.items():
                if any(k in c_name_lower for k in spec["keywords"]):
                    target_cat = cat_key
                    break

            if target_cat:
                target_mat = cat_materials[target_cat]
                mass_before_comp = comp.physicalProperties.mass * 1000.0
                body_count = 0

                for body in comp.bRepBodies:
                    b_name_lower = body.name.lower()
                    # Protection stricte des inserts et profilés internes métalliques
                    if any(m in b_name_lower for m in ["ceinture", "alu", "7075", "6060", "vis", "insert", "traverse", "spacer", "plate"]):
                        continue

                    try:
                        body.material = target_mat
                        if ref_appearance:
                            body.appearance = ref_appearance
                        body_count += 1
                    except Exception:
                        pass

                mass_after_comp = comp.physicalProperties.mass * 1000.0
                delta_comp = mass_after_comp - mass_before_comp
                total_delta_g += delta_comp

                modified_components.append({
                    "name": comp.name,
                    "category": target_cat,
                    "mat_name": target_mat.name,
                    "density_g_cm3": DENSITY_SPECS[target_cat]["target_density_g_cm3"],
                    "bodies_updated": body_count,
                    "mass_before_g": round(mass_before_comp, 1),
                    "mass_after_g": round(mass_after_comp, 1),
                    "delta_g": round(delta_comp, 1)
                })

        # -------------------------------------------------------------
        # 4. Calculs des masses réalistes par sous-ensemble
        # -------------------------------------------------------------
        final_assembly_mass_kg = root_comp.physicalProperties.mass
        com_final = root_comp.physicalProperties.centerOfMass
        com_final_mm = [round(com_final.x * 10.0, 2), round(com_final.y * 10.0, 2), round(com_final.z * 10.0, 2)]

        # Décomposition Torse Haut vs Bassin (frontière nominale Waist Z = 1033.4 mm)
        torse_mass_g = 0.0
        bassin_mass_g = 0.0
        battery_mass_g = 0.0

        for occ in root_comp.allOccurrences:
            try:
                comp = occ.component
                c_name_l = comp.name.lower()
                occ_mass = occ.physicalProperties.mass * 1000.0
                occ_com_z = occ.physicalProperties.centerOfMass.z * 10.0

                if any(k in c_name_l for k in ["panier_batterie", "batterie", "battery"]):
                    battery_mass_g += occ_mass

                if occ_com_z >= 1030.0 or any(k in c_name_l for k in ["torse", "carenage", "plastron", "cou", "colonne", "epaule"]):
                    torse_mass_g += occ_mass
                else:
                    bassin_mass_g += occ_mass
            except Exception:
                pass

        # Torse sans batterie
        torse_sans_batterie_kg = max(0.0, (torse_mass_g - battery_mass_g) / 1000.0)

        # -------------------------------------------------------------
        # 5. Export JSON de l'Audit Métrologique Calibré
        # -------------------------------------------------------------
        audit_data = {
            "metadata": {
                "document_name": design.rootComponent.name,
                "type": "AUDIT_METROLOGIQUE_CALIBRE_FDM",
                "methodology": "Densites Apparentes FDM Equivalentes (OrcaSlicer / Qidi Plus 4)"
            },
            "realistic_mass_summary": {
                "assembly_total_mass_kg": round(final_assembly_mass_kg, 2),
                "assembly_initial_mass_kg": round(initial_assembly_mass_kg, 2),
                "assembly_gain_net_kg": round(initial_assembly_mass_kg - final_assembly_mass_kg, 2),
                "torse_haut_avec_batterie_kg": round(torse_mass_g / 1000.0, 2),
                "torse_haut_hors_batterie_kg": round(torse_sans_batterie_kg, 2),
                "bassin_pelvis_total_kg": round(bassin_mass_g / 1000.0, 2),
                "pack_batterie_kg": round(battery_mass_g / 1000.0, 2)
            },
            "center_of_mass_mm": {
                "before": [round(x, 2) for x in com_init_mm],
                "after": com_final_mm,
                "delta_z_mm": round(com_final_mm[2] - com_init_mm[2], 2)
            },
            "calibrated_components": modified_components
        }

        try:
            os.makedirs(os.path.dirname(JSON_EXPORT_PATH), exist_ok=True)
            with open(JSON_EXPORT_PATH, "w", encoding="utf-8") as f:
                json.dump(audit_data, f, indent=2, ensure_ascii=False)
            json_status = f"✅ Fichier exporté : {os.path.basename(JSON_EXPORT_PATH)}"
        except Exception as e:
            json_status = f"⚠️ Erreur export JSON : {str(e)}"

        # -------------------------------------------------------------
        # 6. Message Box de Synthèse d'Ingénierie
        # -------------------------------------------------------------
        gain_kg = (initial_assembly_mass_kg - final_assembly_mass_kg)
        report_msg = (
            "=== BILAN MÉCIS DU POIDS RÉEL DU TORSE & BASSIN (D-BOT) ===\n\n"
            f"1. MASSE TOTALE ASSEMBLAGE : {final_assembly_mass_kg:.2f} kg  (au lieu de {initial_assembly_mass_kg:.2f} kg)\n"
            f"   ➔ Allègement effectif : -{gain_kg:.2f} kg (-{gain_kg * 1000:.0f} g)\n\n"
            "2. DÉCOMPOSITION RÉALISTE PAR SOUS-ENSEMBLE :\n"
            f"   • HAUT DU TORSE (seul, hors batterie) : {torse_sans_batterie_kg:.2f} kg\n"
            f"     (Squelette 7075 + RS-04 x2 + Peaux C1/C2 infill 25% + Carénages 15%)\n"
            f"   • PACK BATTERIE 12S + RACK GLISSIÈRE : {battery_mass_g / 1000.0:.2f} kg\n"
            f"   • TOTAL HAUT DU TORSE ÉQUIPÉ : {torse_mass_g / 1000.0:.2f} kg\n"
            f"   • BASSIN / BERCEAU PELVIEN : {bassin_mass_g / 1000.0:.2f} kg\n"
            f"     (Châssis PA12-CF infill 75% + Traverse 7075 + RB8016 + RS-06)\n\n"
            "3. CENTRE DE MASSE (CoM) RÉALISTE :\n"
            f"   • X = {com_final_mm[0]:.1f} mm, Y = {com_final_mm[1]:.1f} mm\n"
            f"   • Z = {com_final_mm[2]:.1f} mm  (Évolution Z : +{com_final_mm[2] - com_init_mm[2]:.1f} mm vers le sternum)\n\n"
            f"{json_status}\n"
            "Toutes les pièces polymères portent désormais la texture noire mat."
        )

        if ui:
            ui.messageBox(report_msg, "D-Bot V1 — Poids Réaliste du Torse")

    except Exception:
        if ui:
            ui.messageBox(f"Échec de l'exécution :\n{traceback.format_exc()}", "Erreur Python")

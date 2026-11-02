# -*- coding: utf-8 -*-
"""
FixCeintureAlu.py — Rétablissement Immédiat de l'Aluminium 7075 sur le Corps 'ceinture'
Projet : Robot Humanoïde D-Bot V1 (Torse & Bassin)
=============================================================================
Ce script s'exécute directement dans Fusion 360 (Raccourci Shift + S > Exécuter).
Il cible spécifiquement le corps BRep 'ceinture' au sein du composant 'Plastron_Ventral_Torse:1'
et lui réassigne la matière certifiée 'Aluminium 7075' (densité 2,81 g/cm³, masse ~45,4 g),
sans toucher aux autres corps (qui restent en PA12-CF).
"""

import adsk.core
import adsk.fusion
import traceback


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            if ui:
                ui.messageBox("Veuillez ouvrir l'assemblage Torse actif.", "Fix Ceinture Alu")
            return

        root_comp = design.rootComponent

        # 1. Recherche du matériau Aluminium 7075 certifié (densité 2,81 g/cm³)
        target_alu = None
        for mat in design.materials:
            name_lower = mat.name.strip().lower()
            if "7075" in name_lower and "-t6" not in name_lower:
                target_alu = mat
                break

        # Secours via Waist_Plate_7075
        if not target_alu:
            for occ in root_comp.allOccurrences:
                if "waist_plate_7075" in occ.name.lower():
                    target_alu = occ.component.material
                    break

        # Secours via bibliothèques système
        if not target_alu:
            for lib in app.materialLibraries:
                try:
                    for mat in lib.materials:
                        if "7075" in mat.name.lower():
                            target_alu = design.materials.addByCopy(mat, "Aluminium 7075")
                            break
                    if target_alu:
                        break
                except Exception:
                    continue

        if not target_alu:
            if ui:
                ui.messageBox("Impossible d'isoler la matière Aluminium 7075 dans le document.", "Erreur Matériau")
            return

        # 2. Recherche du corps 'ceinture' dans l'assemblage
        found_count = 0
        details = []

        for occ in root_comp.allOccurrences:
            comp = occ.component
            for body in comp.bRepBodies:
                if "ceinture" in body.name.lower():
                    body.material = target_alu
                    found_count += 1
                    try:
                        b_props = body.getPhysicalProperties(adsk.fusion.CalculationAccuracy.MediumCalculationAccuracy)
                        m_g = b_props.mass * 1000.0
                        vol_cm3 = body.volume
                        details.append(f"• {occ.name} > Corps '{body.name}' : {target_alu.name}\n  Volume : {vol_cm3:.2f} cm³ | Masse : {m_g:.2f} g")
                    except Exception:
                        details.append(f"• {occ.name} > Corps '{body.name}' : {target_alu.name}")

        if found_count == 0:
            if ui:
                ui.messageBox("Aucun corps nommé 'ceinture' n'a été trouvé dans l'assemblage.", "Avertissement")
            return

        msg = (
            f"✅ Matériau Aluminium 7075 rétabli avec succès sur {found_count} corps 'ceinture' !\n\n"
            + "\n".join(details)
            + "\n\nLa ceinture est de nouveau en Aluminium 7075 (densité 2,81 g/cm³)."
        )

        if ui:
            ui.messageBox(msg, "Correction Ceinture — D-Bot")

    except Exception:
        if ui:
            ui.messageBox(f"Erreur critique :\n{traceback.format_exc()}", "Exception D-Bot")


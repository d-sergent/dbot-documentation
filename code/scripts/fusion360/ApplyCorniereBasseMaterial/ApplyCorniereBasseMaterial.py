# -*- coding: utf-8 -*-
"""
ApplyCorniereBasseMaterial.py — Application du Matériau Aluminium 7075-T6 sur la Cornière Basse
Projet : Robot Humanoïde D-Bot V1 (Torse & Bassin)
=============================================================================
Ce script s'exécute directement dans Fusion 360 (Raccourci Shift + S > Exécuter).
Il assigne le matériau physique certifié 'Aluminium 7075-T6' à la pièce 'Corniere basse:1',
recalcule immédiatement sa masse réelle (passant de 143,3 g en acier à ~51,3 g en 7075)
et notifie l'utilisateur.
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
                ui.messageBox("Veuillez exécuter ce script avec le document d'assemblage actif (Torse).", "D-Bot Materials")
            return

        root_comp = design.rootComponent

        # 1. Recherche prioritaire du matériau Aluminium 7075 déjà présent dans le document
        target_material = None
        for mat in design.materials:
            name_lower = mat.name.strip().lower()
            if "7075" in name_lower:
                target_material = mat
                break

        # 2. Si non trouvé dans le document, recherche dans la bibliothèque standard Fusion 360
        if not target_material:
            for lib in app.materialLibraries:
                try:
                    for mat in lib.materials:
                        if "7075" in mat.name.lower():
                            target_material = design.materials.addByCopy(mat, "Aluminium 7075-T6")
                            break
                    if target_material:
                        break
                except Exception:
                    continue

        if not target_material:
            if ui:
                ui.messageBox("Impossible de trouver le matériau Aluminium 7075 dans les bibliothèques Fusion 360.", "Erreur Matériau")
            return

        # 3. Application du matériau sur l'occurrence 'Corniere basse'
        modified_count = 0
        target_occurrences = []

        for occ in root_comp.allOccurrences:
            if "corniere basse" in occ.name.lower():
                target_occurrences.append(occ)

        if not target_occurrences:
            if ui:
                ui.messageBox("Aucune occurrence 'Corniere basse' trouvée dans l'arbre d'assemblage.", "Avertissement")
            return

        for occ in target_occurrences:
            comp = occ.component
            # Assigner au composant ou à ses corps
            try:
                comp.material = target_material
                modified_count += 1
            except Exception:
                pass

            for body in comp.bRepBodies:
                try:
                    body.material = target_material
                    modified_count += 1
                except Exception:
                    pass

        # 4. Calcul de la nouvelle masse
        target_occ = target_occurrences[0]
        new_mass_g = target_occ.physicalProperties.mass * 1000.0
        new_vol_cm3 = target_occ.physicalProperties.volume

        msg = (
            f"✅ Matériau appliqué avec succès : {target_material.name}\n\n"
            f"Composant : {target_occ.name}\n"
            f"Volume : {new_vol_cm3:.2f} cm³\n"
            f"Nouvelle masse réelle (Alu 7075) : {new_mass_g:.2f} g\n"
            f"(Gain mesuré par rapport à l'acier : -{143.26 - new_mass_g:.2f} g sur le modèle 3D)"
        )

        if ui:
            ui.messageBox(msg, "Matériau Mis à Jour — D-Bot")

    except Exception:
        if ui:
            ui.messageBox(f"Erreur critique :\n{traceback.format_exc()}", "Exception D-Bot")


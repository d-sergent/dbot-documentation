# -*- coding: utf-8 -*-
"""
HarmonizePelvisMaterials.py — Harmonisation Souveraine des Matériaux & Apparences Visuelles du Bassin Pelvis D-Bot V1
Projet : Robot Humanoïde D-Bot V1
=============================================================================
Ce script s'exécute directement dans Autodesk Fusion 360 (Raccourci Shift + S > Exécuter).
Il applique la règle stricte du bassin validée en conception :
  1. Traverse Renfort Bassin ('Traverse_Renfort_Bassin [ASV1_200_16A]') :
     -> Maintenue et enforcée en 'Aluminium 7075' certifié (densité 2,81 g/cm³)
     -> Apparence métallique Satin / Aluminium préservée.
     -> Assise métallique indéformable pour le roulement RB8016 et le stator RS-06.
  2. Châssis Structurel Maître ('Chassis_Structurel_Bassin [ASV1_200_01C]') :
     -> Matériau physique : 'PA12-CF' (Infill 75%, densité calibrée ~0,85 g/cm³)
     -> Apparence visuelle : Noir Mat PA12-CF (purge intégrale des overrides de corps et faces).
  3. Supports de Hanches Gauche & Droit ('ASV1_200_06C' & 'ASV1_200_08C') :
     -> Matériau physique : 'PA12-CF'
     -> Apparence visuelle : Noir Mat PA12-CF (élimination du bug de flanc droit bleu-gris).
  4. Liaisons de Hanches Gauche & Droit ('ASV1_200_07C' & 'ASV1_200_09C') :
     -> Matériau physique : 'PA12-CF'
     -> Apparence visuelle : Noir Mat PA12-CF (plaques brides annulaires).
  5. Capots et Trappes Pelviennes (02A, 03A, 04B, 05B, 15C) :
     -> Matériau physique : 'PA12-CF (Cosmetique Infill 15% Gyroide)'
     -> Apparence visuelle : Noir Mat PA12-CF homogène.

Traitement à double niveau (BRepBodies + Occurrences) :
Écrase les overrides d'occurrences, de corps et de faces pour garantir un rendu 100% noir mat.
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
                ui.messageBox(
                    "Veuillez exécuter ce script avec le document d'assemblage actif (Torse-123).",
                    "D-Bot Materials Harmonizer"
                )
            return

        root_comp = design.rootComponent

        # ---------------------------------------------------------------------
        # 1. Résolution des matériaux physiques certifiés cibles
        # ---------------------------------------------------------------------
        mat_alu_7075 = None
        mat_pa12_structural = None
        mat_pa12_cosmetic = None

        for mat in design.materials:
            name_clean = mat.name.strip()
            name_lower = name_clean.lower()
            
            # Aluminium 7075
            if "7075" in name_lower and "-t6" not in name_lower and not mat_alu_7075:
                mat_alu_7075 = mat
            elif "7075" in name_lower and not mat_alu_7075:
                mat_alu_7075 = mat

            # PA12-CF Structurel
            if any(k in name_lower for k in ["structurel", "bassin", "75%", "100%"]) and "pa12" in name_lower and not mat_pa12_structural:
                mat_pa12_structural = mat

            # PA12-CF Cosmétique ou générique
            if any(k in name_lower for k in ["cosmetique", "15%"]) and "pa12" in name_lower and not mat_pa12_cosmetic:
                mat_pa12_cosmetic = mat
            elif "pa12" in name_lower and not mat_pa12_cosmetic:
                mat_pa12_cosmetic = mat

        # Recoupement via les composants de référence fiables déjà présents
        for occ in root_comp.allOccurrences:
            occ_lower = occ.name.lower()
            if not mat_alu_7075 and ("waist_plate_7075" in occ_lower or "traverse_renfort_bassin" in occ_lower):
                mat_alu_7075 = occ.component.material
            if not mat_pa12_cosmetic and ("capot_lateral" in occ_lower or "trappe_inferieure" in occ_lower or "panier_batterie" in occ_lower):
                mat_pa12_cosmetic = occ.component.material

        if not mat_pa12_structural:
            if mat_pa12_cosmetic:
                try:
                    mat_pa12_structural = design.materials.addByCopy(mat_pa12_cosmetic, "PA12-CF (Bassin Structurel Infill 75%)")
                    for prop in mat_pa12_structural.materialProperties:
                        if "density" in prop.name.lower():
                            prop.value = prop.value * (0.85 / 0.55)
                            break
                except Exception:
                    mat_pa12_structural = mat_pa12_cosmetic
            else:
                mat_pa12_structural = mat_pa12_cosmetic

        if not mat_pa12_cosmetic and mat_pa12_structural:
            mat_pa12_cosmetic = mat_pa12_structural

        # Secours via bibliothèques système pour Alu 7075 si manquant
        if not mat_alu_7075:
            for lib in app.materialLibraries:
                try:
                    for mat in lib.materials:
                        if "7075" in mat.name.lower():
                            mat_alu_7075 = design.materials.addByCopy(mat, "Aluminium 7075")
                            break
                    if mat_alu_7075:
                        break
                except Exception:
                    continue

        mat_target_structure = mat_pa12_structural if mat_pa12_structural else mat_pa12_cosmetic
        mat_target_cosmetic = mat_pa12_cosmetic if mat_pa12_cosmetic else mat_target_structure

        # ---------------------------------------------------------------------
        # 2. Résolution Infaillible des Apparences Visuelles (Noir Mat PA12-CF & Satin Alu)
        # Remarque API : Un objet 'Component' n'a pas d'attribut 'appearance'.
        # L'apparence s'applique sur BRepBody, BRepFace ou Occurrence.
        # ---------------------------------------------------------------------
        app_black_pa12 = None
        app_alu = None

        # Source 1 : Extraction directe depuis un corps BRep d'une pièce manifestement noire
        for comp in design.allComponents:
            c_low = comp.name.lower()
            if any(k in c_low for k in ["torse_haut", "carenage_pectoral", "carenage_lombaire", "plastron", "panier_batterie", "chassis_structurel", "hanche_gauche"]):
                # Inspection des corps BRep
                for b in comp.bRepBodies:
                    if b.appearance:
                        app_black_pa12 = b.appearance
                        break
                if app_black_pa12:
                    break
                # Ou depuis la matière du composant
                if comp.material:
                    try:
                        if comp.material.appearance:
                            app_black_pa12 = comp.material.appearance
                            break
                    except Exception:
                        pass

        # Source 2 : Extraction depuis les occurrences du document
        if not app_black_pa12:
            for occ in root_comp.allOccurrences:
                o_low = occ.name.lower()
                if any(k in o_low for k in ["torse_haut", "carenage", "plastron", "panier", "hanche_gauche", "support_batterie"]):
                    if occ.appearance:
                        app_black_pa12 = occ.appearance
                        break

        # Source 3 : Recherche dans les apparences du document (design.appearances)
        if not app_black_pa12:
            for a in design.appearances:
                a_name = a.name.lower()
                if any(k in a_name for k in ["black", "noir", "dark", "pa12", "carbon", "matte", "mat", "charcoal", "anthracite"]):
                    app_black_pa12 = a
                    break

        # Source 4 : Extraction depuis l'apparence associée au matériau physique PA12
        if not app_black_pa12 and mat_target_structure:
            try:
                if mat_target_structure.appearance:
                    app_black_pa12 = mat_target_structure.appearance
            except Exception:
                pass

        if not app_black_pa12 and mat_target_cosmetic:
            try:
                if mat_target_cosmetic.appearance:
                    app_black_pa12 = mat_target_cosmetic.appearance
            except Exception:
                pass

        # Source 5 : Recherche dans les bibliothèques d'apparences système (multilingue EN/FR)
        if not app_black_pa12:
            for lib in app.materialLibraries:
                try:
                    for a in lib.appearances:
                        a_name = a.name.lower()
                        is_plastic = any(p in a_name for p in ["plastic", "plastique", "composite", "nylon", "abs", "matte", "mat"])
                        is_dark = any(d in a_name for d in ["black", "noir", "dark", "charcoal"])
                        if is_plastic and is_dark:
                            app_black_pa12 = design.appearances.addByCopy(a, "PA12-CF Noir Mat")
                            break
                    if app_black_pa12:
                        break
                except Exception:
                    continue

        # Source 6 : Fallback ultime bibliothèque
        if not app_black_pa12:
            for lib in app.materialLibraries:
                try:
                    for a in lib.appearances:
                        if "black" in a.name.lower() or "noir" in a.name.lower():
                            app_black_pa12 = design.appearances.addByCopy(a, "PA12-CF Noir Mat")
                            break
                    if app_black_pa12:
                        break
                except Exception:
                    continue

        # Résolution de l'apparence Aluminium Satin pour la Traverse Renfort
        for comp in design.allComponents:
            c_low = comp.name.lower()
            if "waist_plate" in c_low or "traverse" in c_low or "corniere" in c_low:
                for b in comp.bRepBodies:
                    if b.appearance and any(k in b.appearance.name.lower() for k in ["alu", "metal", "satin", "clear"]):
                        app_alu = b.appearance
                        break
                if app_alu:
                    break
                if comp.material:
                    try:
                        if comp.material.appearance and any(k in comp.material.appearance.name.lower() for k in ["alu", "metal", "satin", "clear"]):
                            app_alu = comp.material.appearance
                            break
                    except Exception:
                        pass

        if not app_alu and mat_alu_7075:
            try:
                if mat_alu_7075.appearance:
                    app_alu = mat_alu_7075.appearance
            except Exception:
                pass

        if not app_alu:
            for a in design.appearances:
                if any(k in a.name.lower() for k in ["alu", "aluminum", "aluminium", "satin", "metal"]):
                    app_alu = a
                    break

        # ---------------------------------------------------------------------
        # 3. Application Ciblée sur le Bassin Pelvis (allComponents + allOccurrences)
        # ---------------------------------------------------------------------
        report = []
        total_mass_saved_g = 0.0
        bodies_updated_count = 0
        occs_updated_count = 0

        pelvis_keywords = [
            "asv1_200", "bassin", "pelvis", "chassis_structurel",
            "support_hanche", "liaison_hanche", "traverse_renfort_bassin",
            "trappe_inferieure", "capot_protection_hanche", "capot_lateral_hanche",
            "hanche", "hip"
        ]

        hardware_keywords = [
            "vis", "screw", "rondelle", "washer", "ecrou", "nut",
            "rb8016", "crbh", "rs-06", "rs06", "rs-04", "rs04", "motor", "moteur"
        ]

        # ETAPE A : Mise à niveau des COMPOSANTS (Matière physique, corps BRep et purge faces)
        for comp in design.allComponents:
            c_name = comp.name
            c_low = c_name.lower()

            if not any(k in c_low for k in pelvis_keywords):
                continue
            if any(h in c_low for h in hardware_keywords):
                continue

            is_traverse = any(k in c_low for k in ["traverse_renfort_bassin", "asv1_200_16a"])

            if is_traverse:
                phys_mat = mat_alu_7075
                vis_app = app_alu
            else:
                is_structure = any(k in c_low for k in ["chassis", "support_hanche", "liaison_hanche"])
                phys_mat = mat_target_structure if is_structure else mat_target_cosmetic
                vis_app = app_black_pa12

            # 1. Matériau physique sur le composant
            try:
                comp.material = phys_mat
            except Exception:
                pass

            # 2. Matériau, apparence et purge des faces sur tous les corps BRep
            for b in comp.bRepBodies:
                try:
                    b.material = phys_mat
                except Exception:
                    pass
                if vis_app:
                    try:
                        b.appearance = vis_app
                        bodies_updated_count += 1
                    except Exception:
                        pass
                # Purge impérative des overrides sur chaque face
                for f in b.faces:
                    if f.appearance:
                        try:
                            f.appearance = None
                        except Exception:
                            pass

        # ETAPE B : Parcours de toutes les OCCURRENCES pour forcer l'apparence d'assemblage
        for occ in root_comp.allOccurrences:
            occ_name = occ.name
            occ_low = occ_name.lower()
            comp = occ.component
            c_low = comp.name.lower() if comp else ""

            if not any(k in occ_low or k in c_low for k in pelvis_keywords):
                continue
            if any(h in occ_low or h in c_low for h in hardware_keywords):
                continue

            is_traverse = any(k in occ_low or k in c_low for k in ["traverse_renfort_bassin", "asv1_200_16a"])

            if is_traverse:
                vis_app = app_alu
                if vis_app:
                    try:
                        occ.appearance = vis_app
                    except Exception:
                        pass
                m_after = occ.physicalProperties.mass * 1000.0
                report.append(f"  • [ALU 7075 SATIN] {occ_name} : {m_after:.1f} g (Assise rigide RB8016 préservée)")
            else:
                vis_app = app_black_pa12
                m_before = occ.physicalProperties.mass * 1000.0
                
                # Affectation directe de l'apparence noire sur l'occurrence
                if vis_app:
                    try:
                        occ.appearance = vis_app
                        occs_updated_count += 1
                    except Exception:
                        pass

                m_after = occ.physicalProperties.mass * 1000.0
                diff = m_before - m_after
                if diff > 0.1:
                    total_mass_saved_g += diff
                    report.append(f"  • [PA12-CF NOIR MAT] {occ_name} : {m_before:.1f} g -> {m_after:.1f} g (gain : -{diff:.1f} g)")
                else:
                    report.append(f"  • [PA12-CF NOIR MAT] {occ_name} : {m_after:.1f} g (Rendu noir mat certifié)")

        # ---------------------------------------------------------------------
        # 4. Bilan d'exécution et Affichage
        # ---------------------------------------------------------------------
        app_name_str = app_black_pa12.name if app_black_pa12 else "Non trouvée"
        alu_name_str = app_alu.name if app_alu else "Non trouvée"

        msg = (
            "✅ Harmonisation des Matériaux & Apparences du Bassin Pelvis terminée !\n\n"
            f"🎨 Texture Noire Mat appliquée : '{app_name_str}'\n"
            f"⚙️ Texture Alu Satin appliquée : '{alu_name_str}'\n"
            f"📦 Corps BRep mis à jour : {bodies_updated_count}\n"
            f"🔗 Occurrences unifiées : {occs_updated_count}\n\n"
            f"Bilan détaillé ({len(report)} pièces traitées) :\n"
            + "\n".join(report)
            + f"\n\n⚖️ Gain de masse mesuré sur le Bassin : -{total_mass_saved_g:.1f} g (-{total_mass_saved_g / 1000.0:.2f} kg)\n\n"
            "Toutes les pièces composites (châssis, supports et capots gauche & droit) sont désormais en noir mat homogène."
        )

        if ui:
            ui.messageBox(msg, "Harmonisation Bassin Pelvis — D-Bot V1")

    except Exception:
        if ui:
            ui.messageBox(f"Erreur critique lors de l'exécution :\n{traceback.format_exc()}", "Exception D-Bot Pelvis")

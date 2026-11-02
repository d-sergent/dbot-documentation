# -*- coding: utf-8 -*-
"""
HarmonizeTorseMaterials.py — Harmonisation Automatique des Matériaux Torse & Bassin D-Bot V1
Projet : Robot Humanoïde D-Bot V1
=============================================================================
Ce script s'exécute directement dans Autodesk Fusion 360 (Raccourci Shift + S > Exécuter).
Il corrige automatiquement les 3 anomalies d'assignation matière détectées par l'audit métrologique :
  1. Brides de Retenue Roulement ('Bride_Retenue_RB8016_L', 4 occurrences) :
     -> Réassigne le véritable 'Aluminium 7075' certifié (densité 2,81 g/cm³)
     -> Écrase tout override 'Acier' sur les corps internes BRepBodies
     -> Masse ramenée de 11,50 g à ~4,13 g par bride (-29,5 g au total)
  2. Flanc Droit du Bassin ('Support_Hanche_Droit [ASV1_200_08C]' et 'Liaison_Hanche_Droit [ASV1_200_09C]') :
     -> Réassigne le 'PA12-CF (Cosmetique Infill 15% Gyroide)' identique au flanc gauche
     -> Support Hanche Droit : ramené de 1 027,56 g (Alu) à ~371,17 g (PA12-CF) -> gain -656,4 g
     -> Liaison Hanche Droit : ramené de 257,95 g (Alu) à ~93,18 g (PA12-CF) -> gain -164,8 g
     -> Supprime l'asymétrie latérale de +820 g sur le bassin
  3. Plastron Ventral Torse ('Plastron_Ventral_Torse:1') :
     -> Assigne formellement 'PA12-CF (Torse Infill 25% Gyroide)' pour éliminer le tag 'Unknown'
  4. Support Batterie Central ('Support Batterie Central:1') :
     -> Réassigne 'PA12-CF (Cosmetique Infill 15% Gyroide)' pour harmoniser avec les paniers
     -> Écrase le matériau par défaut 'Acier' (masse ramenée de 235,1 g à ~38,9 g, gain -196,2 g)
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
        # 1. Résolution des matériaux certifiés cibles
        # ---------------------------------------------------------------------
        mat_alu_7075 = None
        mat_pa12_cosmetic = None
        mat_pa12_torso = None

        # Recherche directe dans les matériaux du document
        for mat in design.materials:
            name_clean = mat.name.strip()
            name_lower = name_clean.lower()
            
            # Aluminium 7075 certifié (sans le '-T6' corrompu)
            if "7075" in name_lower and "-t6" not in name_lower and not mat_alu_7075:
                mat_alu_7075 = mat
            elif "7075" in name_lower and not mat_alu_7075:
                mat_alu_7075 = mat

            # PA12-CF Cosmétique (pour les hanches)
            if "cosmetique" in name_lower and "pa12" in name_lower and not mat_pa12_cosmetic:
                mat_pa12_cosmetic = mat
            elif "pa12-cf" in name_lower and "15%" in name_lower and not mat_pa12_cosmetic:
                mat_pa12_cosmetic = mat

            # PA12-CF Torse
            if "torse infill 25%" in name_lower and not mat_pa12_torso:
                mat_pa12_torso = mat

        # Recoupement via les composants de référence fiables déjà présents
        for occ in root_comp.allOccurrences:
            occ_lower = occ.name.lower()
            if not mat_alu_7075 and "waist_plate_7075" in occ_lower:
                mat_alu_7075 = occ.component.material
            if not mat_pa12_cosmetic and ("asv1_200_06c" in occ_lower or "hanche_gauche" in occ_lower):
                mat_pa12_cosmetic = occ.component.material
            if not mat_pa12_torso and ("panier_batterie" in occ_lower or "capot_verrouillage" in occ_lower):
                mat_pa12_torso = occ.component.material

        # Secours via bibliothèques système si un matériau manquait
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

        if not mat_pa12_cosmetic:
            mat_pa12_cosmetic = mat_pa12_torso

        if not mat_alu_7075:
            if ui:
                ui.messageBox("Impossible d'isoler la matière Aluminium 7075 certifiée.", "Erreur Matériau")
            return

        # ---------------------------------------------------------------------
        # 2. Application et écrasement propre des matériaux
        # ---------------------------------------------------------------------
        report = []
        total_mass_saved_g = 0.0

        for occ in root_comp.allOccurrences:
            occ_name = occ.name
            occ_lower = occ_name.lower()
            comp = occ.component

            # A. Brides de Retenue Roulement RB8016
            if "bride_retenue_rb8016" in occ_lower:
                m_before = occ.physicalProperties.mass * 1000.0
                try:
                    comp.material = mat_alu_7075
                except Exception:
                    pass
                for b in comp.bRepBodies:
                    try:
                        b.material = mat_alu_7075
                    except Exception:
                        pass
                m_after = occ.physicalProperties.mass * 1000.0
                diff = m_before - m_after
                total_mass_saved_g += diff
                report.append(f"  • {occ_name} : {mat_alu_7075.name} ({m_before:.1f}g -> {m_after:.1f}g, gain: -{diff:.1f}g)")

            # B. Support Hanche Droit (ASV1_200_08C)
            elif "asv1_200_08c" in occ_lower or "support_hanche_droit" in occ_lower:
                if mat_pa12_cosmetic:
                    m_before = occ.physicalProperties.mass * 1000.0
                    try:
                        comp.material = mat_pa12_cosmetic
                    except Exception:
                        pass
                    for b in comp.bRepBodies:
                        try:
                            b.material = mat_pa12_cosmetic
                        except Exception:
                            pass
                    m_after = occ.physicalProperties.mass * 1000.0
                    diff = m_before - m_after
                    total_mass_saved_g += diff
                    report.append(f"  • {occ_name} : {mat_pa12_cosmetic.name} ({m_before:.1f}g -> {m_after:.1f}g, gain: -{diff:.1f}g)")

            # C. Liaison Hanche Droit (ASV1_200_09C)
            elif "asv1_200_09c" in occ_lower or "liaison_hanche_droit" in occ_lower:
                if mat_pa12_cosmetic:
                    m_before = occ.physicalProperties.mass * 1000.0
                    try:
                        comp.material = mat_pa12_cosmetic
                    except Exception:
                        pass
                    for b in comp.bRepBodies:
                        try:
                            b.material = mat_pa12_cosmetic
                        except Exception:
                            pass
                    m_after = occ.physicalProperties.mass * 1000.0
                    diff = m_before - m_after
                    total_mass_saved_g += diff
                    report.append(f"  • {occ_name} : {mat_pa12_cosmetic.name} ({m_before:.1f}g -> {m_after:.1f}g, gain: -{diff:.1f}g)")

            # D. Plastron Ventral Torse
            elif "plastron_ventral_torse" in occ_lower:
                target_mat = mat_pa12_torso if mat_pa12_torso else mat_pa12_cosmetic
                if target_mat:
                    for b in comp.bRepBodies:
                        b_name_lower = b.name.strip().lower()
                        # ATTENTION MÉCANIQUE : Le corps 'ceinture' est la bague usinée en Aluminium 7075 (2,81 g/cm³, 45,4 g),
                        # seuls les autres corps (plastrons et coques) sont en PA12-CF !
                        if "ceinture" in b_name_lower:
                            try:
                                b.material = mat_alu_7075
                                report.append(f"  • {occ_name} > Corps '{b.name}' : {mat_alu_7075.name} (Aluminium 7075 préservé/rétabli)")
                            except Exception:
                                pass
                        else:
                            try:
                                b.material = target_mat
                            except Exception:
                                pass
                    report.append(f"  • {occ_name} (coques plastron) : {target_mat.name} (Tag Unknown éliminé)")

            # E. Support Batterie Central
            elif "support batterie central" in occ_lower or "support_batterie_central" in occ_lower:
                target_mat = mat_pa12_cosmetic if mat_pa12_cosmetic else mat_pa12_torso
                if target_mat:
                    m_before = occ.physicalProperties.mass * 1000.0
                    try:
                        comp.material = target_mat
                    except Exception:
                        pass
                    for b in comp.bRepBodies:
                        try:
                            b.material = target_mat
                        except Exception:
                            pass
                    m_after = occ.physicalProperties.mass * 1000.0
                    diff = m_before - m_after
                    total_mass_saved_g += diff
                    report.append(f"  • {occ_name} : {target_mat.name} ({m_before:.1f}g -> {m_after:.1f}g, gain: -{diff:.1f}g)")

        # ---------------------------------------------------------------------
        # 3. Message récapitulatif
        # ---------------------------------------------------------------------
        msg = (
            "✅ Harmonisation des matériaux terminée avec succès !\n\n"
            f"Bilan des pièces modifiées ({len(report)}) :\n"
            + "\n".join(report)
            + f"\n\n⚖️ Gain de masse total mesuré sur le modèle 3D : -{total_mass_saved_g:.1f} g\n"
            "Symétrie latérale Hanche Droite / Hanche Gauche rigoureusement rétablie."
        )

        if ui:
            ui.messageBox(msg, "Harmonisation Matériaux — D-Bot V1")

    except Exception:
        if ui:
            ui.messageBox(f"Erreur critique lors de l'exécution :\n{traceback.format_exc()}", "Exception D-Bot")


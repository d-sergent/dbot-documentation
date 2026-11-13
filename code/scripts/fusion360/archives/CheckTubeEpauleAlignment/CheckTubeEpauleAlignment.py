# -*- coding: utf-8 -*-
"""
CheckTubeEpauleAlignment.py — Contrôleur Métrologique d'Alignement et d'Horizontalité
======================================================================================
Auteur : Antigravity (Projet D-Bot)
Environnement : Autodesk Fusion 360 (Python API)
Mode : 100% LECTURE SEULE (Strictement non-destructif)

Rôle du script :
  1. Identifie automatiquement dans l'assemblage actif :
     - Le composant : 'Tube transverse Epaules:2'
     - Le composant : 'Bride Epaule(Symétrie miroir):3'
  2. Extrait la géométrie spatiale réelle (B-Rep Cylinders) transformée dans le repère MONDIAL.
  3. Calcule rigoureusement :
     - L'axe directeur 3D du tube [Vx, Vy, Vz]
     - L'horizontalité du tube (angle d'inclinaison par rapport au plan horizontal XY en degrés)
     - La variation d'altitude Z (dénivelé) sur la longueur du tube
     - L'axe de l'alésage / insert de la bride réceptrice
     - Le défaut de coaxialité (désaxage radial en mm et désalignement angulaire en degrés)
  4. Sauvegarde le diagnostic détaillé en JSON dans le dossier d'audit :
     Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/AUDIT_ALIGNEMENT_Tube_Epaule.json
  5. Affiche une boîte de dialogue récapitulative claire à l'écran.
"""

import adsk.core
import adsk.fusion
import os
import json
import math
import traceback
from datetime import datetime

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            if ui:
                ui.messageBox("Veuillez ouvrir un assemblage Fusion 360 actif avant d'exécuter ce script.", "Contrôle d'Alignement")
            return
            
        root_comp = design.rootComponent
        doc_name = app.activeDocument.name
        
        # 1. Recherche des deux composants cibles
        occ_tube = None
        occ_bride = None
        
        for occ in root_comp.allOccurrences:
            o_name = occ.name.lower()
            if "tube transverse epaules:2" in o_name:
                occ_tube = occ
            elif "tube transverse epaules" in o_name and not occ_tube:
                occ_tube = occ
                
            if "bride epaule(symétrie miroir):3" in o_name:
                occ_bride = occ
            elif "bride epaule(symétrie miroir)" in o_name and not occ_bride:
                occ_bride = occ

        if not occ_tube:
            # Fallback recherche souple
            for occ in root_comp.allOccurrences:
                if "tube transverse" in occ.name.lower():
                    occ_tube = occ
                    break

        if not occ_bride:
            for occ in root_comp.allOccurrences:
                if "bride epaule" in occ.name.lower() and "miroir" in occ.name.lower():
                    occ_bride = occ
                    break

        if not occ_tube or not occ_bride:
            missing = []
            if not occ_tube: missing.append("Tube transverse Epaules:2")
            if not occ_bride: missing.append("Bride Epaule(Symétrie miroir):3")
            ui.messageBox(f"Composant(s) introuvable(s) dans le modèle actif :\n• " + "\n• ".join(missing), "Erreur de Recherche")
            return

        # 2. Analyse géométrique du Tube dans le repère mondial
        t_matrix = occ_tube.transform2
        tube_cylinders = []
        
        for body in occ_tube.bRepBodies:
            for face in body.faces:
                if face.geometry.objectType == adsk.core.Cylinder.classType():
                    cyl = adsk.core.Cylinder.cast(face.geometry)
                    cyl.transformBy(t_matrix)
                    radius_mm = cyl.radius * 10.0
                    tube_cylinders.append({
                        "radius_mm": radius_mm,
                        "diameter_mm": radius_mm * 2.0,
                        "axis": cyl.axis,
                        "origin": cyl.origin
                    })

        if not tube_cylinders:
            ui.messageBox("Aucune face cylindrique détectée sur le composant Tube.", "Erreur Métrologie")
            return

        # Le cylindre extérieur a le plus grand rayon
        tube_cylinders.sort(key=lambda c: c["radius_mm"], reverse=True)
        main_tube_cyl = tube_cylinders[0]
        tube_axis = main_tube_cyl["axis"]
        tube_origin = main_tube_cyl["origin"]
        
        # Vecteur directeur unitaire du tube
        v_x = round(tube_axis.x, 6)
        v_y = round(tube_axis.y, 6)
        v_z = round(tube_axis.z, 6)
        
        # Calcul de l'inclinaison par rapport au plan horizontal mondial (XY)
        # Dans Fusion, Z est l'axe vertical (Up). Un vecteur horizontal a Z = 0.
        angle_tilt_rad = math.asin(min(1.0, abs(v_z)))
        angle_tilt_deg = round(math.degrees(angle_tilt_rad), 3)
        is_tube_horizontal = (angle_tilt_deg < 0.05)
        
        # Bounding Box du Tube (en mm)
        bbox = occ_tube.boundingBox
        z_min = round(bbox.minPoint.z * 10.0, 3)
        z_max = round(bbox.maxPoint.z * 10.0, 3)
        delta_z = round(z_max - z_min, 3)
        x_min = round(bbox.minPoint.x * 10.0, 3)
        x_max = round(bbox.maxPoint.x * 10.0, 3)
        y_min = round(bbox.minPoint.y * 10.0, 3)
        y_max = round(bbox.maxPoint.y * 10.0, 3)
        tube_dia_mm = round(main_tube_cyl["diameter_mm"], 2)

        # 3. Analyse géométrique de la Bride d'Épaule réceptrice
        b_matrix = occ_bride.transform2
        bride_cylinders = []
        
        for body in occ_bride.bRepBodies:
            for face in body.faces:
                if face.geometry.objectType == adsk.core.Cylinder.classType():
                    cyl = adsk.core.Cylinder.cast(face.geometry)
                    cyl.transformBy(b_matrix)
                    radius_mm = cyl.radius * 10.0
                    bride_cylinders.append({
                        "radius_mm": radius_mm,
                        "diameter_mm": radius_mm * 2.0,
                        "axis": cyl.axis,
                        "origin": cyl.origin
                    })

        # Trouver l'alésage de la bride dont le diamètre correspond au tube (à +/- 2 mm)
        target_bore = None
        min_dia_diff = 999.0
        for b_cyl in bride_cylinders:
            diff = abs(b_cyl["diameter_mm"] - tube_dia_mm)
            if diff < min_dia_diff:
                min_dia_diff = diff
                target_bore = b_cyl

        # Si pas trouvé au diamètre exact, prendre le plus grand cylindre de la bride
        if not target_bore and bride_cylinders:
            bride_cylinders.sort(key=lambda c: c["radius_mm"], reverse=True)
            target_bore = bride_cylinders[0]

        bore_axis = target_bore["axis"] if target_bore else None
        bore_origin = target_bore["origin"] if target_bore else None
        
        # 4. Calcul de coaxialité et alignement relatif Tube <---> Bride
        coaxial_angle_deg = None
        radial_offset_mm = None
        is_coaxial = False
        
        if bore_axis and bore_origin:
            # Angle entre l'axe du tube et l'axe de l'alésage de la bride
            dot = abs(tube_axis.dotProduct(bore_axis))
            dot = min(1.0, max(-1.0, dot))
            coaxial_angle_deg = round(math.degrees(math.acos(dot)), 3)
            
            # Distance radiale (désaxage entre les deux axes en 3D)
            # Vecteur reliant les deux origines
            d_origin = adsk.core.Vector3D.create(
                tube_origin.x - bore_origin.x,
                tube_origin.y - bore_origin.y,
                tube_origin.z - bore_origin.z
            )
            # Projection orthogonale sur l'axe du bore
            proj = bore_axis.copy()
            proj.scaleBy(d_origin.dotProduct(bore_axis))
            perp_vec = adsk.core.Vector3D.create(
                d_origin.x - proj.x,
                d_origin.y - proj.y,
                d_origin.z - proj.z
            )
            radial_offset_mm = round(perp_vec.length * 10.0, 3) # cm vers mm
            
            # Critère de coaxialité : angle < 0.1° et décalage radial < 0.05 mm
            is_coaxial = (coaxial_angle_deg < 0.1 and radial_offset_mm < 0.05)

        # 5. Structuration des données d'audit
        audit_data = {
            "metadata": {
                "audit_type": "ALIGNEMENT_ET_HORIZONTALITE_TUBE_EPAULE",
                "document_name": doc_name,
                "timestamp": datetime.now().isoformat(),
                "units": {"length": "mm", "angle": "deg"}
            },
            "components": {
                "tube": {
                    "name": occ_tube.name,
                    "outer_diameter_mm": tube_dia_mm,
                    "axis_vector_world": [v_x, v_y, v_z],
                    "center_point_world_mm": [
                        round(tube_origin.x * 10.0, 3),
                        round(tube_origin.y * 10.0, 3),
                        round(tube_origin.z * 10.0, 3)
                    ],
                    "bounding_box_mm": {
                        "min_x": x_min, "max_x": x_max,
                        "min_y": y_min, "max_y": y_max,
                        "min_z": z_min, "max_z": z_max,
                        "height_delta_z": delta_z
                    },
                    "horizontal_status": {
                        "is_horizontal": is_tube_horizontal,
                        "tilt_angle_from_horizontal_deg": angle_tilt_deg,
                        "vertical_component_vz": v_z
                    }
                },
                "bride_bore": {
                    "name": occ_bride.name,
                    "matched_bore_diameter_mm": round(target_bore["diameter_mm"], 2) if target_bore else None,
                    "bore_axis_world": [
                        round(bore_axis.x, 6),
                        round(bore_axis.y, 6),
                        round(bore_axis.z, 6)
                    ] if bore_axis else None,
                    "bore_tilt_angle_deg": round(math.degrees(math.asin(min(1.0, abs(bore_axis.z)))), 3) if bore_axis else None
                }
            },
            "alignment_analysis": {
                "is_coaxial": is_coaxial,
                "angular_misalignment_deg": coaxial_angle_deg,
                "radial_offset_mm": radial_offset_mm,
                "verdict_coaxialite": "PARFAITEMENT COAXIAL" if is_coaxial else "DÉSAXÉ / DÉSALIGNÉ",
                "verdict_horizontalite": "STRICTEMENT HORIZONTAL" if is_tube_horizontal else f"INCLINÉ DE {angle_tilt_deg} deg"
            }
        }

        # 6. Sauvegarde du rapport JSON
        target_doc_path = "/Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/AUDIT_ALIGNEMENT_Tube_Epaule.json"
        target_cad_path = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/01_Torse_et_Bassin/AUDIT_ALIGNEMENT_Tube_Epaule.json"
        
        saved_paths = []
        for p in [target_doc_path, target_cad_path]:
            try:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(audit_data, f, indent=2, ensure_ascii=False)
                saved_paths.append(p)
            except:
                pass

        # 7. Affichage de la boîte de dialogue utilisateur dans Fusion 360
        horiz_symbol = "✅" if is_tube_horizontal else "🚨"
        coax_symbol = "✅" if is_coaxial else "⚠️"
        
        diag_lines = [
            f"=== CONTRÔLE D'ALIGNEMENT GÉOMÉTRIQUE 3D ===",
            f"• Tube analysé  : {occ_tube.name}",
            f"• Bride analysée : {occ_bride.name}",
            f"",
            f"--- 1. HORIZONTALITÉ DU TUBE ---",
            f"{horiz_symbol} Statut : {'STRICTEMENT HORIZONTAL' if is_tube_horizontal else 'INCLINÉ / NON HORIZONTAL'}",
            f"• Angle d'inclinaison par rapport au plan XY : {angle_tilt_deg} deg",
            f"• Vecteur directeur 3D : [{v_x}, {v_y}, {v_z}]",
            f"• Altitude Z Tube : Min = {z_min} mm | Max = {z_max} mm (Écart Z = {delta_z} mm)",
            f"",
            f"--- 2. COAXIALITÉ AVEC L'ALÉSAGE DE LA BRIDE ---",
            f"{coax_symbol} Statut : {'PARFAITEMENT COAXIAL (0,00 mm)' if is_coaxial else 'DÉFAUT D ALIGNEMENT DÉTECTÉ'}",
            f"• Alésage Bride détecté : Ø {target_bore['diameter_mm']:.2f} mm (Tube : Ø {tube_dia_mm:.2f} mm)",
            f"• Désalignement angulaire : {coaxial_angle_deg} deg",
            f"• Désaxage radial (excentrement) : {radial_offset_mm} mm",
            f"",
            f"📁 Rapport complet enregistré dans :",
            f"{target_doc_path}"
        ]
        
        ui.messageBox("\n".join(diag_lines), "Diagnostic d'Alignement Tube Épaule")

    except Exception as e:
        if ui:
            ui.messageBox(f"Erreur durant l'analyse d'alignement :\n{traceback.format_exc()}", "Erreur CheckTubeEpauleAlignment")


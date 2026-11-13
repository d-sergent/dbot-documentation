# -*- coding: utf-8 -*-
"""
CheckHipVerticality.py — Audit 3D de Verticalité de l'Ensemble Hanche, Bassin & Colonne
======================================================================================
Auteur : Antigravity (Projet D-Bot)
Environnement : Autodesk Fusion 360 (Python API)
Mode : 100% LECTURE SEULE (Strictement non-destructif)

Rôle du script :
  1. Inspecte les matrices spatiales mondiales (Matrix3D transform2) des composants clés :
     - 'colonne vertébrale:1' (référence verticale haute du torse)
     - 'Bassin_Pelvis [ASV1_200]:1' (référence structurelle basse)
     - 'Traverse_Renfort_Bassin [ASV1_200_16A]:1' (platine d'assise supérieure)
     - 'selle de pont:1' (bloc pont de hanches sous traverse)
     - Moteur RS-06 Waist / Hanches
     - 'Tube transverse Epaules:2' & Brides d'épaules
  2. Calcule pour chaque pièce :
     - Son vecteur d'axe Z local dans le repère mondial
     - Son inclinaison angulaire par rapport à la verticale absolue Z (en degrés)
     - Son inclinaison par rapport au plan horizontal XY
     - L'écart angulaire relatif par rapport à la colonne vertébrale
  3. Sauvegarde l'audit complet en JSON dans :
     Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/AUDIT_VERTICALITE_HANCHE_ET_BASSIN.json
  4. Présente le diagnostic immédiat dans une boîte de dialogue Fusion 360.
"""

import adsk.core
import adsk.fusion
import os
import json
import math
import traceback
from datetime import datetime

def clamp(val, min_v=-1.0, max_v=1.0):
    return max(min_v, min(max_v, val))

def get_matrix_data(occ):
    """Extrait les vecteurs directeurs locaux et la position d'une occurrence dans le monde."""
    m = occ.transform2
    # Colonne 0 = Axe X local
    vx = [m.getCell(0, 0), m.getCell(1, 0), m.getCell(2, 0)]
    # Colonne 1 = Axe Y local
    vy = [m.getCell(0, 1), m.getCell(1, 1), m.getCell(2, 1)]
    # Colonne 2 = Axe Z local
    vz = [m.getCell(0, 2), m.getCell(1, 2), m.getCell(2, 2)]
    # Colonne 3 = Origine en cm -> conversion en mm
    origin_mm = [
        round(m.getCell(0, 3) * 10.0, 3),
        round(m.getCell(1, 3) * 10.0, 3),
        round(m.getCell(2, 3) * 10.0, 3)
    ]
    
    # Angle d'inclinaison de l'axe Z local par rapport à l'axe Z mondial [0, 0, 1]
    # Si local Z est parallèle à mondial Z, abs(vz[2]) == 1.0 -> angle = 0.0 deg
    cos_z = clamp(abs(vz[2]))
    tilt_z_deg = round(math.degrees(math.acos(cos_z)), 3)
    
    # Bounding Box en mm
    bbox = occ.boundingBox
    bbox_dict = {
        "min": [round(bbox.minPoint.x * 10.0, 2), round(bbox.minPoint.y * 10.0, 2), round(bbox.minPoint.z * 10.0, 2)],
        "max": [round(bbox.maxPoint.x * 10.0, 2), round(bbox.maxPoint.y * 10.0, 2), round(bbox.maxPoint.z * 10.0, 2)],
        "size": [
            round((bbox.maxPoint.x - bbox.minPoint.x) * 10.0, 2),
            round((bbox.maxPoint.y - bbox.minPoint.y) * 10.0, 2),
            round((bbox.maxPoint.z - bbox.minPoint.z) * 10.0, 2)
        ]
    }
    
    return {
        "name": occ.name,
        "is_grounded": occ.isGrounded,
        "origin_world_mm": origin_mm,
        "axis_x_world": [round(c, 6) for c in vx],
        "axis_y_world": [round(c, 6) for c in vy],
        "axis_z_world": [round(c, 6) for c in vz],
        "tilt_from_world_z_deg": tilt_z_deg,
        "is_vertical": (tilt_z_deg < 0.05),
        "bounding_box_mm": bbox_dict
    }

def compute_relative_angle(data_a, data_b):
    """Calcule l'angle relatif (en degrés) entre les repères locaux de deux composants."""
    za = data_a["axis_z_world"]
    zb = data_b["axis_z_world"]
    dot_z = clamp(abs(za[0]*zb[0] + za[1]*zb[1] + za[2]*zb[2]))
    angle_z = round(math.degrees(math.acos(dot_z)), 3)
    
    ya = data_a["axis_y_world"]
    yb = data_b["axis_y_world"]
    dot_y = clamp(abs(ya[0]*yb[0] + ya[1]*yb[1] + ya[2]*yb[2]))
    angle_y = round(math.degrees(math.acos(dot_y)), 3)
    
    return {
        "angle_between_z_axes_deg": angle_z,
        "angle_between_y_axes_deg": angle_y
    }

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            if ui:
                ui.messageBox("Veuillez ouvrir un document Fusion 360 actif.", "Contrôle Verticalité")
            return
            
        root_comp = design.rootComponent
        doc_name = app.activeDocument.name
        
        # Mots-clés des composants cibles prioritaires
        targets_found = {}
        
        for occ in root_comp.allOccurrences:
            name_low = occ.name.lower()
            if "colonne" in name_low and "vertébrale" in name_low and "colonne" not in targets_found:
                targets_found["colonne"] = occ
            elif "selle de pont" in name_low and "selle_de_pont" not in targets_found:
                targets_found["selle_de_pont"] = occ
            elif "traverse_renfort_bassin" in name_low and "traverse" not in targets_found:
                targets_found["traverse"] = occ
            elif "bassin_pelvis" in name_low and "pelvis" not in targets_found:
                targets_found["pelvis"] = occ
            elif "tube transverse epaules:2" in name_low and "tube_epaule" not in targets_found:
                targets_found["tube_epaule"] = occ
            elif any(k in name_low for k in ["rs06", "rs-06", "00_1-1305"]) and "moteur_rs06" not in targets_found:
                targets_found["moteur_rs06"] = occ
            elif "chassis_structurel_bassin" in name_low and "chassis_pelvis" not in targets_found:
                targets_found["chassis_pelvis"] = occ

        # Extraction des caractéristiques matricielles
        components_data = {}
        for key, occ in targets_found.items():
            components_data[key] = get_matrix_data(occ)

        # Calculs relatifs par rapport à la Colonne Vertébrale (référence torse)
        colonne_ref = components_data.get("colonne")
        relative_comparisons = {}
        
        if colonne_ref:
            for key, c_data in components_data.items():
                if key != "colonne":
                    relative_comparisons[key] = compute_relative_angle(colonne_ref, c_data)

        # Rapport global
        audit_payload = {
            "metadata": {
                "audit_type": "AUDIT_VERTICALITE_ENSEMBLE_HANCHE_ET_BASSIN",
                "document_name": doc_name,
                "timestamp": datetime.now().isoformat(),
                "units": {"length": "mm", "angle": "deg"}
            },
            "components": components_data,
            "relative_to_colonne_vertebrale": relative_comparisons
        }

        # Sauvegarde JSON
        save_path = "/Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/AUDIT_VERTICALITE_HANCHE_ET_BASSIN.json"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(audit_payload, f, indent=2, ensure_ascii=False)

        # Synthèse textuelle pour boîte de dialogue
        lines = [
            "=== AUDIT DE VERTICALITÉ DE L'ENSEMBLE HANCHE & BASSIN ===",
            f"Document analysé : {doc_name}",
            ""
        ]

        # 1. Colonne
        if "colonne" in components_data:
            c = components_data["colonne"]
            lines.append(f"• Colonne Vertébrale : Inclinaison Z = {c['tilt_from_world_z_deg']} deg (Grounded: {c['is_grounded']})")
        else:
            lines.append("• Colonne Vertébrale : Non trouvée")

        # 2. Selle de pont
        if "selle_de_pont" in components_data:
            s = components_data["selle_de_pont"]
            rel = relative_comparisons.get("selle_de_pont", {}).get("angle_between_z_axes_deg", "?")
            lines.append(f"• Selle de Pont       : Inclinaison Z = {s['tilt_from_world_z_deg']} deg | Écart vs Colonne = {rel} deg")

        # 3. Traverse Bassin
        if "traverse" in components_data:
            t = components_data["traverse"]
            rel = relative_comparisons.get("traverse", {}).get("angle_between_z_axes_deg", "?")
            lines.append(f"• Traverse Renfort    : Inclinaison Z = {t['tilt_from_world_z_deg']} deg | Écart vs Colonne = {rel} deg")

        # 4. Bassin Pelvis
        if "pelvis" in components_data:
            p = components_data["pelvis"]
            rel = relative_comparisons.get("pelvis", {}).get("angle_between_z_axes_deg", "?")
            lines.append(f"• Bassin Pelvis       : Inclinaison Z = {p['tilt_from_world_z_deg']} deg (Grounded: {p['is_grounded']})")

        # 5. Moteur RS-06
        if "moteur_rs06" in components_data:
            m = components_data["moteur_rs06"]
            lines.append(f"• Moteur RS-06        : Inclinaison Z = {m['tilt_from_world_z_deg']} deg")

        # 6. Tube Épaule
        if "tube_epaule" in components_data:
            te = components_data["tube_epaule"]
            lines.append(f"• Tube Transverse Ép. : Inclinaison Z = {te['tilt_from_world_z_deg']} deg")

        lines.append("")
        lines.append(f"📁 Rapport JSON complet enregistré dans :")
        lines.append(f"{save_path}")

        ui.messageBox("\n".join(lines), "Audit de Verticalité Hanche & Pelvis")

    except Exception as e:
        if ui:
            ui.messageBox(f"Erreur durant l'audit de verticalité :\n{traceback.format_exc()}", "Erreur CheckHipVerticality")


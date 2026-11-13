# -*- coding: utf-8 -*-
"""
AuditTorse.py — Script Maître Unifié d'Audit CAO Fusion 360 (Métrologie, Cinématique, Alignement & Vision)
Projet : Robot Humanoïde D-Bot V1
===========================================================================================================
Point d'entrée unique dans Fusion 360 (Raccourci Shift + S > AuditTorse > Exécuter).
Exécute en une seule passe :
  1. Audit métrologique & B-Rep complet -> `Audits/AUDIT_METROLOGIQUE_<SousEnsemble>.json`
     + Synthèse Markdown RAG           -> `SYNTHESE_METROLOGIQUE_<SousEnsemble>.md`
  2. Audit cinématique & DDL unifié     -> `Audits/AUDIT_CINEMATIQUE_<SousEnsemble>.json`
  3. Audit d'alignement & coaxialité    -> `Audits/AUDIT_ALIGNEMENT_<SousEnsemble>.json`
  4. Captures visuelles multi-vues PNG  -> `Exports_CAO_DBot/<SousEnsemble>/Visual_Snapshots/`
     (et DXF 1:1 CNC / plans cotés FreeCAD si activés).

Tous les JSON bruts sont écrits exclusivement dans `Audits/` (hors Git dans `Documentation/`
via `.gitignore`, et sauvegardés côté souverain dans `Exports_CAO_DBot/`).
"""

import adsk.core
import adsk.fusion
import importlib
import json
import math
import os
import re
import shutil
import sys
import traceback
from datetime import datetime

# ==============================================================================
# CONFIGURATION DU TEST VISUEL ET LIVRABLES 2D (MODE UNITAIRE VS MODE TOTALITÉ)
# ==============================================================================
# TEST_MODE_SINGLE_PIECE :
#   - True  : Teste le pipeline sur une seule pièce ciblée (ex: 'waist_plate')
#   - False : Exécute l'exportation complète sur l'ensemble des pièces structurelles (Mode Production).
TEST_MODE_SINGLE_PIECE = False
TARGET_TEST_PIECE_NAME = "waist_plate"
SKIP_ASSEMBLY_VIEWS_IN_TEST = False

# GESTION DES CAPTURES VISUELLES PNG :
# OVERWRITE_EXISTING_SNAPSHOTS :
#   - True  : Écrase et régénère systématiquement toutes les captures visuelles PNG pour refléter la CAO active (Par défaut).
#   - False : Conserve les images saines (> 12 Ko) déjà générées (Mode Reprise Rapide / Débogage).
OVERWRITE_EXISTING_SNAPSHOTS = True
SKIP_EXISTING_SNAPSHOTS = not OVERWRITE_EXISTING_SNAPSHOTS
AUTO_CLEAN_ORPHAN_SNAPSHOTS = True  # Purge automatiquement les dossiers de pièces orphelines (renommées ou supprimées de la CAO)

# LIVRABLES 2D BOUT EN BOUT AUTOMATISÉS (FREECAD / DXF) :
ENABLE_AUTO_CNC_DXF = False     # Désactivé par défaut pour accélérer les rendus visuels PNG
ENABLE_AUTO_DRAFTING = False    # Désactivé par défaut (évite les appels lourds subprocess FreeCAD pour chaque pièce)
FREECAD_BIN = "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
FREECAD_DRAFTING_SCRIPT = "/Users/Shared/Mon Google Drive Physique/Documentation/Code/scripts/cad_tools/generate_freecad_draft_drawings.py"




def resolve_export_targets(doc_name):
    """Résout le sous-ensemble actif et ses dossiers cibles (Exports_CAO_DBot & Documentation)."""
    doc_lower = (doc_name or "").lower()
    base_exports = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot"
    base_docs = "/Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis"

    if any(k in doc_lower for k in ("torse", "bassin", "waist")):
        sub_label = "Torse_et_Bassin"
        sovereign_dir = os.path.join(base_exports, "01_Torse_et_Bassin")
        doc_folder_rel = "Torse_et_Bassin"
        doc_dir = os.path.join(base_docs, doc_folder_rel)
    elif any(k in doc_lower for k in ("tete", "tête", "cou", "neck", "head")):
        sub_label = "Tete_et_Cou"
        sovereign_dir = os.path.join(base_exports, "02_Tete_et_Cou")
        doc_folder_rel = "Tete_et_Cou"
        doc_dir = os.path.join(base_docs, doc_folder_rel)
    elif any(k in doc_lower for k in ("bras", "epaule", "épaule", "avant_bras")):
        sub_label = "Bras_et_Epaules"
        sovereign_dir = os.path.join(base_exports, "03_Bras_et_Epaules")
        doc_folder_rel = "Bras_et_Mains"
        doc_dir = os.path.join(base_docs, doc_folder_rel)
    elif any(k in doc_lower for k in ("main", "d-hand", "dhand")):
        sub_label = "Mains_DHand"
        sovereign_dir = os.path.join(base_exports, "04_Mains_DHand")
        doc_folder_rel = "Bras_et_Mains"
        doc_dir = os.path.join(base_docs, doc_folder_rel)
    elif any(k in doc_lower for k in ("jambe", "pied", "cuisse", "tibia", "genou", "cheville")):
        sub_label = "Jambes_et_Hanches"
        sovereign_dir = os.path.join(base_exports, "05_Jambes_et_Hanches")
        doc_folder_rel = "Jambes_et_Pieds"
        doc_dir = os.path.join(base_docs, doc_folder_rel)
    else:
        sub_label = sanitize_filename(doc_name or "Assemblage")
        sovereign_dir = os.path.join(base_exports, "00_Robot_Complet")
        doc_folder_rel = sub_label
        doc_dir = os.path.join(base_docs, doc_folder_rel)

    return {
        "sub_label": sub_label,
        "doc_folder_rel": doc_folder_rel,
        "sovereign_dir": sovereign_dir,
        "sovereign_audit_dir": os.path.join(sovereign_dir, "Audits"),
        "doc_dir": doc_dir,
        "doc_audit_dir": os.path.join(doc_dir, "Audits"),
    }


def sanitize_filename(name):
    """Nettoie le nom d'un corps ou composant pour en faire un nom de fichier image/json valide."""
    clean = re.sub(r'[\\/*?:"<>| \(\)\[\]:]', '_', name)
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean or "element"

def get_world_bbox(local_bbox, transform):
    """Calcule la boîte englobante d'un corps en coordonnées globales d'assemblage (mm)."""
    try:
        min_pt = local_bbox.minPoint
        max_pt = local_bbox.maxPoint
        corners = [
            adsk.core.Point3D.create(min_pt.x, min_pt.y, min_pt.z),
            adsk.core.Point3D.create(min_pt.x, min_pt.y, max_pt.z),
            adsk.core.Point3D.create(min_pt.x, max_pt.y, min_pt.z),
            adsk.core.Point3D.create(min_pt.x, max_pt.y, max_pt.z),
            adsk.core.Point3D.create(max_pt.x, min_pt.y, min_pt.z),
            adsk.core.Point3D.create(max_pt.x, min_pt.y, max_pt.z),
            adsk.core.Point3D.create(max_pt.x, max_pt.y, min_pt.z),
            adsk.core.Point3D.create(max_pt.x, max_pt.y, max_pt.z),
        ]
        xs, ys, zs = [], [], []
        for pt in corners:
            pt.transformBy(transform)
            xs.append(pt.x * 10.0)
            ys.append(pt.y * 10.0)
            zs.append(pt.z * 10.0)
        return {
            "min": [round(min(xs), 2), round(min(ys), 2), round(min(zs), 2)],
            "max": [round(max(xs), 2), round(max(ys), 2), round(max(zs), 2)],
            "size": [round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2), round(max(zs) - min(zs), 2)]
        }
    except:
        try:
            return {
                "min": [round(local_bbox.minPoint.x * 10.0, 2), round(local_bbox.minPoint.y * 10.0, 2), round(local_bbox.minPoint.z * 10.0, 2)],
                "max": [round(local_bbox.maxPoint.x * 10.0, 2), round(local_bbox.maxPoint.y * 10.0, 2), round(local_bbox.maxPoint.z * 10.0, 2)],
                "size": [round((local_bbox.maxPoint.x - local_bbox.minPoint.x) * 10.0, 2),
                         round((local_bbox.maxPoint.y - local_bbox.minPoint.y) * 10.0, 2),
                         round((local_bbox.maxPoint.z - local_bbox.minPoint.z) * 10.0, 2)]
            }
        except:
            return None

_HARDWARE_ACTUATOR_PATTERNS = (
    "vis ", "ecrou ", "rondelle ", "goupille ", "rb8016", "zyd", "luosi",
    "000_", "00_", "1_1_", "1_2_", "1_3_", "100_", "1000_", "3_1_",
    "_2025_", "_gyos", "_pis", "d19_", "dianjiban", "fl82blw",
    "eb1203", "eb1201", "eb823", "rs04", "rs06", "el05",
    "screw", "bolt", "nut", "washer", "bearing",
)


def _is_hardware_or_actuator(comp_name):
    """Indique si un composant est une visserie standard ou sous-pièce actionneur importée."""
    low = (comp_name or "").lower()
    return any(pat in low for pat in _HARDWARE_ACTUATOR_PATTERNS)


def _transform_point_mm(pt3d, transform):
    """Transforme un Point3D local (cm) en coordonnées globales d'assemblage (mm)."""
    pt = adsk.core.Point3D.create(pt3d.x, pt3d.y, pt3d.z)
    pt.transformBy(transform)
    return [round(pt.x * 10.0, 2), round(pt.y * 10.0, 2), round(pt.z * 10.0, 2)]


def _transform_axis_vec(vec3d, transform):
    """Transforme un Vector3D local unitaire vers le repère global d'assemblage."""
    vec = adsk.core.Vector3D.create(vec3d.x, vec3d.y, vec3d.z)
    vec.transformBy(transform)
    vec.normalize()
    return [round(vec.x, 3), round(vec.y, 3), round(vec.z, 3)]


def _is_internal_cylinder(face, cyl):
    """Détecte si une face cylindrique est concave (alésage interne = True) ou convexe (False)."""
    try:
        ev = face.evaluator
        ok_rng, rng = ev.parameterRange()
        if not ok_rng:
            return None
        u_mid = (rng.minPoint.x + rng.maxPoint.x) * 0.5
        v_mid = (rng.minPoint.y + rng.maxPoint.y) * 0.5
        prm = adsk.core.Point2D.create(u_mid, v_mid)
        ok_pt, p_surf = ev.getPointAtParameter(prm)
        ok_nm, n_surf = ev.getNormalAtParameter(prm)
        if not (ok_pt and ok_nm):
            return None
        # Produit scalaire entre vecteur radial local (P_surf - Orig) et normale sortante
        vx = p_surf.x - cyl.origin.x
        vy = p_surf.y - cyl.origin.y
        vz = p_surf.z - cyl.origin.z
        ax, ay, az = cyl.axis.x, cyl.axis.y, cyl.axis.z
        dot_ax = vx * ax + vy * ay + vz * az
        rx = vx - dot_ax * ax
        ry = vy - dot_ax * ay
        rz = vz - dot_ax * az
        radial_dot = rx * n_surf.x + ry * n_surf.y + rz * n_surf.z
        return radial_dot < 0.0
    except Exception:
        return None


def _canonical_axis_signature(origin_mm, axis_vec, use_perp=True):
    """Signature géométrique canonique pour dédoublonner les demi-faces d'un même perçage."""
    norm = math.sqrt(axis_vec[0] ** 2 + axis_vec[1] ** 2 + axis_vec[2] ** 2) or 1.0
    ux, uy, uz = axis_vec[0] / norm, axis_vec[1] / norm, axis_vec[2] / norm
    for c in (ux, uy, uz):
        if abs(c) > 1e-3:
            if c < 0.0:
                ux, uy, uz = -ux, -uy, -uz
            break
    if use_perp:
        dot = origin_mm[0] * ux + origin_mm[1] * uy + origin_mm[2] * uz
        px = origin_mm[0] - dot * ux
        py = origin_mm[1] - dot * uy
        pz = origin_mm[2] - dot * uz
    else:
        px, py, pz = origin_mm[0], origin_mm[1], origin_mm[2]
    return (round(ux, 2), round(uy, 2), round(uz, 2), round(px, 1), round(py, 1), round(pz, 1))


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        
        if not design:
            ui.messageBox("Aucun modèle actif détecté dans Fusion 360.\nVeuillez ouvrir le modèle du Torse D-Bot.")
            return
            
        root_comp = design.rootComponent
        doc_name = app.activeDocument.name
        
        # -------------------------------------------------------------
        # 1. Structure générale et métadonnées
        # -------------------------------------------------------------
        audit_data = {
            "metadata": {
                "document_name": doc_name,
                "timestamp": datetime.now().isoformat(),
                "units": {
                    "length": "mm",
                    "mass": "g",
                    "volume": "cm3",
                    "angle": "deg"
                },
                "fusion_default_length_units": design.unitsManager.defaultLengthUnits
            },
            "assembly_summary": {},
            "user_parameters": [],
            "components": [],
            "holes_summary": {
                "dowel_pins_dia_3mm": [],
                "countersinks_90deg_fhc_m4": [],
                "clearance_holes_m4_dia_4_5mm": [],
                "clearance_holes_m5_dia_5_5mm": [],
                "large_bores": []
            },
            "hardware_bom": {}
        }
        
        # -------------------------------------------------------------
        # 2. Propriétés globales de l'assemblage racine
        # -------------------------------------------------------------
        try:
            root_props = root_comp.getPhysicalProperties(adsk.fusion.CalculationAccuracy.MediumCalculationAccuracy)
            root_mass_g = root_props.mass * 1000.0  # kg -> g
            root_volume_cm3 = root_props.volume     # cm3
            root_cog = root_props.centerOfMass      # cm -> mm
            root_cog_mm = [round(root_cog.x * 10.0, 3), round(root_cog.y * 10.0, 3), round(root_cog.z * 10.0, 3)]
            
            root_bbox = root_comp.boundingBox
            dx = round((root_bbox.maxPoint.x - root_bbox.minPoint.x) * 10.0, 2)
            dy = round((root_bbox.maxPoint.y - root_bbox.minPoint.y) * 10.0, 2)
            dz = round((root_bbox.maxPoint.z - root_bbox.minPoint.z) * 10.0, 2)
            
            audit_data["assembly_summary"] = {
                "total_mass_g": round(root_mass_g, 2),
                "total_volume_cm3": round(root_volume_cm3, 2),
                "center_of_mass_mm": root_cog_mm,
                "bounding_box_mm": {
                    "min": [round(root_bbox.minPoint.x * 10.0, 2), round(root_bbox.minPoint.y * 10.0, 2), round(root_bbox.minPoint.z * 10.0, 2)],
                    "max": [round(root_bbox.maxPoint.x * 10.0, 2), round(root_bbox.maxPoint.y * 10.0, 2), round(root_bbox.maxPoint.z * 10.0, 2)],
                    "size": [dx, dy, dz]
                }
            }
        except Exception as e_props:
            audit_data["assembly_summary"]["error"] = str(e_props)
            
        # -------------------------------------------------------------
        # 3. Paramètres utilisateur (User Parameters)
        # -------------------------------------------------------------
        for param in design.userParameters:
            param_val_mm = None
            try:
                # Si unité de longueur, convertir en mm
                param_val_mm = round(param.value * 10.0, 3)
            except:
                pass
                
            audit_data["user_parameters"].append({
                "name": param.name,
                "expression": param.expression,
                "value_internal": param.value,
                "value_mm": param_val_mm,
                "unit": param.unit,
                "comment": param.comment
            })

        # -------------------------------------------------------------
        # 4. Parcours récursif de toutes les occurrences & composants
        # -------------------------------------------------------------
        all_occurrences = root_comp.allOccurrences
        
        for occ in all_occurrences:
            if not occ.isLightBulbOn:
                continue
                
            comp = occ.component
            comp_name = comp.name
            part_number = comp.partNumber
            desc = comp.description
            
            # Quincaillerie / BOM tracking
            bom_key = part_number if part_number else comp_name
            if bom_key not in audit_data["hardware_bom"]:
                audit_data["hardware_bom"][bom_key] = {
                    "component_name": comp_name,
                    "part_number": part_number,
                    "description": desc,
                    "quantity": 0
                }
            audit_data["hardware_bom"][bom_key]["quantity"] += 1
            
            # Matrice monde complète (occ.transform2 inclut toute la hiérarchie parente)
            transform = getattr(occ, "transform2", None) or occ.transform
            origin, xAxis, yAxis, zAxis = transform.getAsCoordinateSystem()
            comp_origin_mm = [round(origin.x * 10.0, 3), round(origin.y * 10.0, 3), round(origin.z * 10.0, 3)]
            is_container = (comp.bRepBodies.count == 0)
            is_hw_or_motor = _is_hardware_or_actuator(comp_name)
            
            # Propriétés physiques du composant
            comp_mass_g = 0.0
            comp_vol_cm3 = 0.0
            comp_cog_mm = [0.0, 0.0, 0.0]
            try:
                c_props = occ.getPhysicalProperties(adsk.fusion.CalculationAccuracy.MediumCalculationAccuracy)
                comp_mass_g = round(c_props.mass * 1000.0, 2)
                comp_vol_cm3 = round(c_props.volume, 2)
                c_cog = c_props.centerOfMass
                comp_cog_mm = [round(c_cog.x * 10.0, 3), round(c_cog.y * 10.0, 3), round(c_cog.z * 10.0, 3)]
            except:
                pass
                
            # Bounding box du composant
            c_bbox = occ.boundingBox
            c_dx = round((c_bbox.maxPoint.x - c_bbox.minPoint.x) * 10.0, 2)
            c_dy = round((c_bbox.maxPoint.y - c_bbox.minPoint.y) * 10.0, 2)
            c_dz = round((c_bbox.maxPoint.z - c_bbox.minPoint.z) * 10.0, 2)
            
            comp_entry = {
                "instance_name": occ.name,
                "component_name": comp_name,
                "part_number": part_number,
                "description": desc,
                "material": comp.material.name if comp.material else "Unknown",
                "is_container": is_container,
                "is_hardware_or_actuator": is_hw_or_motor,
                "mass_g": comp_mass_g,
                "volume_cm3": comp_vol_cm3,
                "center_of_mass_mm": comp_cog_mm,
                "bounding_box_mm": {
                    "min": [round(c_bbox.minPoint.x * 10.0, 2), round(c_bbox.minPoint.y * 10.0, 2), round(c_bbox.minPoint.z * 10.0, 2)],
                    "max": [round(c_bbox.maxPoint.x * 10.0, 2), round(c_bbox.maxPoint.y * 10.0, 2), round(c_bbox.maxPoint.z * 10.0, 2)],
                    "size": [c_dx, c_dy, c_dz]
                },
                "bodies": [],
                "hole_features": [],
                "cylindrical_faces": [],
                "conical_faces": []
            }
            
            # --- 4.A Extraction des HoleFeatures natives ---
            for hole in comp.features.holeFeatures:
                try:
                    hole_info = {
                        "name": hole.name,
                        "type": str(hole.holeType),
                        "diameter_mm": round(hole.holeDiameter.value * 10.0, 3) if hole.holeDiameter else None,
                        "depth_mm": round(hole.depth.value * 10.0, 3) if hasattr(hole, 'depth') and hole.depth else None,
                        "is_threaded": hole.isThreaded if hasattr(hole, 'isThreaded') else False
                    }
                    if hasattr(hole, 'countersinkAngle') and hole.countersinkAngle:
                        hole_info["countersink_angle_deg"] = round(math.degrees(hole.countersinkAngle.value), 2)
                    if hasattr(hole, 'countersinkDiameter') and hole.countersinkDiameter:
                        hole_info["countersink_diameter_mm"] = round(hole.countersinkDiameter.value * 10.0, 3)
                    if hasattr(hole, 'counterboreDiameter') and hole.counterboreDiameter:
                        hole_info["counterbore_diameter_mm"] = round(hole.counterboreDiameter.value * 10.0, 3)
                    if hasattr(hole, 'counterboreDepth') and hole.counterboreDepth:
                        hole_info["counterbore_depth_mm"] = round(hole.counterboreDepth.value * 10.0, 3)
                        
                    comp_entry["hole_features"].append(hole_info)
                except:
                    pass

            # --- 4.B Analyse B-Rep de tous les corps (BRepBodies) ---
            for body in comp.bRepBodies:
                # 4.B.1 Métrologie du corps individuel et barycentre
                try:
                    b_bbox = get_world_bbox(body.boundingBox, transform)
                    b_vol = round(body.volume, 2) if hasattr(body, 'volume') else 0.0
                    b_mass = 0.0
                    b_cog_world = None
                    cog_offset = None
                    try:
                        b_props = body.getPhysicalProperties(adsk.fusion.CalculationAccuracy.MediumCalculationAccuracy)
                        b_mass = round(b_props.mass * 1000.0, 2)
                        raw_cog = b_props.centerOfMass
                        pt_cog = adsk.core.Point3D.create(raw_cog.x, raw_cog.y, raw_cog.z)
                        pt_cog.transformBy(transform)
                        b_cog_world = [round(pt_cog.x * 10.0, 2), round(pt_cog.y * 10.0, 2), round(pt_cog.z * 10.0, 2)]
                        
                        if b_bbox:
                            b_center = [
                                round((b_bbox["min"][0] + b_bbox["max"][0]) / 2.0, 2),
                                round((b_bbox["min"][1] + b_bbox["max"][1]) / 2.0, 2),
                                round((b_bbox["min"][2] + b_bbox["max"][2]) / 2.0, 2)
                            ]
                            cog_offset = [
                                round(b_cog_world[0] - b_center[0], 2),
                                round(b_cog_world[1] - b_center[1], 2),
                                round(b_cog_world[2] - b_center[2], 2)
                            ]
                    except:
                        pass
                        
                    comp_entry["bodies"].append({
                        "name": body.name,
                        "is_visible": body.isLightBulbOn,
                        "volume_cm3": b_vol,
                        "mass_g": b_mass,
                        "center_of_mass_mm": b_cog_world,
                        "cog_offset_from_bbox_center_mm": cog_offset,
                        "bounding_box_mm": b_bbox,
                        "faces_count": body.faces.count if hasattr(body, 'faces') else 0
                    })
                except:
                    pass

                if not body.isLightBulbOn:
                    continue
                    
                seen_cyl_keys = set()
                seen_cone_keys = set()
                for face in body.faces:
                    geom = face.geometry
                    
                    # Cylindres (Perçages, Alésages, Tourillons)
                    if geom.objectType == adsk.core.Cylinder.classType():
                        try:
                            cyl = adsk.core.Cylinder.cast(geom)
                            radius_mm = cyl.radius * 10.0
                            dia_mm = round(radius_mm * 2.0, 2)
                            origin_mm = _transform_point_mm(cyl.origin, transform)
                            axis = _transform_axis_vec(cyl.axis, transform)
                            is_hole = _is_internal_cylinder(face, cyl)
                            
                            cyl_info = {
                                "diameter_mm": dia_mm,
                                "radius_mm": round(radius_mm, 2),
                                "origin_global_mm": origin_mm,
                                "axis": axis,
                                "is_hole": is_hole
                            }
                            comp_entry["cylindrical_faces"].append(cyl_info)
                            
                            # Classification structurelle (hors visserie/moteurs, dédoublonnée par axe coaxial)
                            if not is_hw_or_motor and is_hole is not False:
                                sig = _canonical_axis_signature(origin_mm, axis, use_perp=True)
                                dedup_key = (round(dia_mm, 1), sig)
                                if dedup_key not in seen_cyl_keys:
                                    seen_cyl_keys.add(dedup_key)
                                    hole_entry = {
                                        "component": comp_name,
                                        "instance": occ.name,
                                        "diameter_mm": dia_mm,
                                        "origin_mm": origin_mm,
                                        "axis": axis
                                    }
                                    if 2.9 <= dia_mm <= 3.1:
                                        audit_data["holes_summary"]["dowel_pins_dia_3mm"].append(hole_entry)
                                    elif 4.0 <= dia_mm <= 4.8:
                                        audit_data["holes_summary"]["clearance_holes_m4_dia_4_5mm"].append(hole_entry)
                                    elif 5.3 <= dia_mm <= 5.7:
                                        audit_data["holes_summary"]["clearance_holes_m5_dia_5_5mm"].append(hole_entry)
                                    elif dia_mm >= 60.0:
                                        audit_data["holes_summary"]["large_bores"].append(hole_entry)
                        except:
                            pass
                            
                    # Cônes (Fraisures coniques 90° type FHC)
                    elif geom.objectType == adsk.core.Cone.classType():
                        try:
                            cone = adsk.core.Cone.cast(geom)
                            half_angle_deg = round(math.degrees(cone.halfAngle), 1)
                            full_angle_deg = round(half_angle_deg * 2.0, 1)
                            origin_mm = _transform_point_mm(cone.origin, transform)
                            axis = _transform_axis_vec(cone.axis, transform)
                            
                            cone_info = {
                                "half_angle_deg": half_angle_deg,
                                "full_angle_deg": full_angle_deg,
                                "origin_global_mm": origin_mm,
                                "axis": axis
                            }
                            comp_entry["conical_faces"].append(cone_info)
                            
                            if not is_hw_or_motor and 88.0 <= full_angle_deg <= 92.0:
                                sig = _canonical_axis_signature(origin_mm, axis, use_perp=False)
                                dedup_key = (round(full_angle_deg, 1), sig)
                                if dedup_key not in seen_cone_keys:
                                    seen_cone_keys.add(dedup_key)
                                    audit_data["holes_summary"]["countersinks_90deg_fhc_m4"].append({
                                        "component": comp_name,
                                        "instance": occ.name,
                                        "angle_deg": full_angle_deg,
                                        "origin_mm": origin_mm,
                                        "axis": axis
                                    })
                        except:
                            pass
                            
            audit_data["components"].append(comp_entry)

        # -------------------------------------------------------------
        # 4b. Calcul de la boîte englobante physique réelle des composants feuilles
        # (Élimine les esquisses, occurrences vides et conteneurs à 0 corps type Ensemble hanche:1)
        # -------------------------------------------------------------
        valid_bbox_comps = []
        excluded_zero_bbox = []
        excluded_containers = []
        for c in audit_data["components"]:
            bbox = c.get("bounding_box_mm")
            if not bbox:
                continue
            sz = bbox.get("size", [0, 0, 0])
            if sz[0] <= 0.01 and sz[1] <= 0.01 and sz[2] <= 0.01:
                excluded_zero_bbox.append(c.get("instance_name", c.get("component_name", "?")))
            elif c.get("is_container") or not any(b.get("is_visible", True) for b in c.get("bodies", [])):
                excluded_containers.append(c.get("instance_name", c.get("component_name", "?")))
            else:
                valid_bbox_comps.append(c)

        all_min_x = [c["bounding_box_mm"]["min"][0] for c in valid_bbox_comps]
        all_max_x = [c["bounding_box_mm"]["max"][0] for c in valid_bbox_comps]
        all_min_y = [c["bounding_box_mm"]["min"][1] for c in valid_bbox_comps]
        all_max_y = [c["bounding_box_mm"]["max"][1] for c in valid_bbox_comps]
        all_min_z = [c["bounding_box_mm"]["min"][2] for c in valid_bbox_comps]
        all_max_z = [c["bounding_box_mm"]["max"][2] for c in valid_bbox_comps]

        if all_min_x:
            p_min = [round(min(all_min_x), 2), round(min(all_min_y), 2), round(min(all_min_z), 2)]
            p_max = [round(max(all_max_x), 2), round(max(all_max_y), 2), round(max(all_max_z), 2)]
            p_size = [round(p_max[0] - p_min[0], 2), round(p_max[1] - p_min[1], 2), round(p_max[2] - p_min[2], 2)]
            audit_data["assembly_summary"]["physical_components_bounding_box_mm"] = {
                "min": p_min,
                "max": p_max,
                "size": p_size,
                "physical_height_mm": p_size[2],
                "excluded_zero_bbox_components": excluded_zero_bbox,
                "excluded_containers": excluded_containers,
                "note": "Boîte englobante réelle des pièces physiques feuilles visibles (exclut esquisses, occurrences vides et conteneurs)"
            }

        # -------------------------------------------------------------
        # 5. Sauvegarde des résultats (Métrologie JSON dans Audits/ & Synthèse MD RAG)
        # -------------------------------------------------------------
        targets = resolve_export_targets(doc_name)
        sub_label = targets["sub_label"]
        doc_folder_rel = targets["doc_folder_rel"]
        sovereign_torse_dir = targets["sovereign_dir"]
        sovereign_audit_dir = targets["sovereign_audit_dir"]
        doc_dir = targets["doc_dir"]
        doc_audit_dir = targets["doc_audit_dir"]

        os.makedirs(sovereign_audit_dir, exist_ok=True)
        if os.path.exists(doc_dir):
            os.makedirs(doc_audit_dir, exist_ok=True)

        sovereign_json_path = os.path.join(sovereign_audit_dir, f"AUDIT_METROLOGIQUE_{sub_label}.json")
        sovereign_md_path = os.path.join(sovereign_audit_dir, f"SYNTHESE_METROLOGIQUE_{sub_label}.md")
        doc_json_path = os.path.join(doc_audit_dir, f"AUDIT_METROLOGIQUE_{sub_label}.json")
        doc_md_path = os.path.join(doc_dir, f"SYNTHESE_METROLOGIQUE_{sub_label}.md")

        json_content = json.dumps(audit_data, indent=2, ensure_ascii=False)
        saved_paths = []

        # Écriture dans Exports_CAO_DBot/.../Audits
        try:
            with open(sovereign_json_path, "w", encoding="utf-8") as f:
                f.write(json_content)
            saved_paths.append(sovereign_json_path)
        except Exception:
            pass

        # Écriture miroir dans Documentation/.../Audits (ignoré par Git, centralisé)
        try:
            if os.path.exists(doc_dir):
                with open(doc_json_path, "w", encoding="utf-8") as f:
                    f.write(json_content)
                saved_paths.append(doc_json_path)
        except Exception:
            pass

        # Génération du Markdown de synthèse pour le RAG et Exports
        script_dir = os.path.dirname(os.path.realpath(__file__))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)

        try:
            import metrology_markdown
            importlib.reload(metrology_markdown)
            md_content = metrology_markdown.build_markdown_summary(
                audit_data, sub_label=sub_label, doc_folder_rel=doc_folder_rel
            )
            with open(sovereign_md_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            saved_paths.append(sovereign_md_path)

            if os.path.exists(doc_dir):
                with open(doc_md_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                saved_paths.append(doc_md_path)
        except Exception:
            pass

        # -------------------------------------------------------------
        # 5b. Audits Unifiés Cinématique & Alignement (Même passe Fusion 360)
        # -------------------------------------------------------------
        kine_summary_str = "Non exécuté"
        align_summary_str = "Non exécuté"
        design_obj = adsk.fusion.Design.cast(app.activeProduct)

        kine_targets = [os.path.join(sovereign_audit_dir, f"AUDIT_CINEMATIQUE_{sub_label}.json")]
        align_targets = [os.path.join(sovereign_audit_dir, f"AUDIT_ALIGNEMENT_{sub_label}.json")]
        if os.path.exists(doc_audit_dir):
            kine_targets.append(os.path.join(doc_audit_dir, f"AUDIT_CINEMATIQUE_{sub_label}.json"))
            align_targets.append(os.path.join(doc_audit_dir, f"AUDIT_ALIGNEMENT_{sub_label}.json"))

        try:
            import kinematic_audit
            importlib.reload(kinematic_audit)
            k_data, k_saved, k_errs = kinematic_audit.run_kinematic_audit(
                app, design_obj, root_comp, doc_name, sub_label, kine_targets
            )
            saved_paths.extend(k_saved)
            ks = k_data.get("summary", {})
            kine_summary_str = (
                f"{ks.get('total_joints', 0)} Joints + {ks.get('total_as_built_joints', 0)} AsBuilt "
                f"| {ks.get('mobile_joints_active', 0)}/{ks.get('mobile_joints_total', 0)} DDL libres "
                f"| Anomalies : {ks.get('health_warnings', 0) + ks.get('broken_assembly_constraints', 0)}"
            )
        except Exception as k_err:
            kine_summary_str = f"Erreur module cinématique : {k_err}"

        try:
            import alignment_audit
            importlib.reload(alignment_audit)
            a_data, a_saved, a_errs = alignment_audit.run_alignment_audit(
                app, design_obj, root_comp, doc_name, sub_label, audit_data["components"], align_targets
            )
            saved_paths.extend(a_saved)
            als = a_data.get("summary", {})
            align_summary_str = (
                f"Waist={als.get('waist_concentricity_status')} (Δr={als.get('waist_max_radial_offset_mm')} mm) "
                f"| Hanches={als.get('hip_bridge_status')} (tilt={als.get('hip_max_montant_tilt_deg')} deg) "
                f"| Symétrie={als.get('symmetry_pairs_ok')}/{als.get('symmetry_pairs_checked')}"
            )
        except Exception as a_err:
            align_summary_str = f"Erreur module alignement : {a_err}"

        # -------------------------------------------------------------
        # 6. Prises de vue visuelles automatiques (Snapshots multi-angles)
        # -------------------------------------------------------------
        snapshots_count = 0
        valid_count = 0
        empty_count = 0
        empty_samples = []
        dxf_count = 0
        drafting_count = 0
        snapshots_err_msg = ""
        try:
            saved_snapshots, valid_captures, empty_captures, saved_dxf, saved_draft = generate_cad_visual_snapshots(app, root_comp, sovereign_torse_dir)
            snapshots_count = len(saved_snapshots)
            valid_count = len(valid_captures)
            empty_count = len(empty_captures)
            empty_samples = empty_captures[:5]
            dxf_count = len(saved_dxf)
            drafting_count = len(saved_draft)
        except Exception:
            snapshots_err_msg = f"\n⚠️ ERREUR DANS LE MODULE DE CAPTURE VISUELLE :\n{traceback.format_exc()}\n"
            
        # Message récapitulatif utilisateur
        mode_str = f"MODE TEST UNITAIRE ACTIF (Cible : '{TARGET_TEST_PIECE_NAME}')" if TEST_MODE_SINGLE_PIECE else "MODE COMPLET (Toutes pièces)"
        qc_str = f"Contrôle Qualité Images : {valid_count} vues certifiées (> 12 Ko)"
        if empty_count > 0:
            qc_str += f"\nATTENTION : {empty_count} vues suspectes (< 12 Ko) :\n" + "\n".join(f"  - {s}" for s in empty_samples)
        if snapshots_err_msg:
            qc_str += f"\n{snapshots_err_msg}"
            
        dxf_str = f"Fichiers DXF 1:1 CNC générés : {dxf_count} profils machine\n" if ENABLE_AUTO_CNC_DXF else ""
        draft_str = f"Plans 2D Cotés générés (PDF/SVG) : {drafting_count} liasses officielles\n" if ENABLE_AUTO_DRAFTING else ""

        msg = (
            f"=== AUDIT UNIFIÉ D-BOT V2 (MÉTROLOGIE + CINÉMATIQUE + ALIGNEMENT + VISION) ===\n\n"
            f"Statut : {mode_str}\n"
            f"Modèle : {doc_name} ({sub_label})\n"
            f"Masse totale extraite : {audit_data['assembly_summary'].get('total_mass_g', 0)} g\n"
            f"Hauteur physique réelle : {audit_data['assembly_summary'].get('physical_components_bounding_box_mm', {}).get('physical_height_mm', 'N/A')} mm\n"
            f"Composants analysés : {len(audit_data['components'])}\n"
            f"Goupilles Ø3 mm : {len(audit_data['holes_summary']['dowel_pins_dia_3mm'])} | "
            f"Fraisures 90° : {len(audit_data['holes_summary']['countersinks_90deg_fhc_m4'])} | "
            f"Alésages majeurs : {len(audit_data['holes_summary']['large_bores'])}\n"
            f"Cinématique : {kine_summary_str}\n"
            f"Alignement  : {align_summary_str}\n"
            f"Captures d'écran générées : {snapshots_count} vues\n"
            f"{dxf_str}"
            f"{draft_str}"
            f"{qc_str}\n\n"
            f"Tous les JSON (Métrologie, Cinématique, Alignement) + Synthèse MD mis à jour :\n"
            f"→ {sovereign_audit_dir}\n"
            f"→ {doc_audit_dir}\n"
            f"→ {os.path.join(sovereign_torse_dir, 'Visual_Snapshots')}\n\n"
            f"Pipeline unifié 100% automatisé exécuté avec succès !"
        )
        
        ui.messageBox(msg, "Audit Unifié D-Bot")

    except Exception:
        if ui:
            ui.messageBox(f"Erreur durant l'audit :\n{traceback.format_exc()}", "Erreur AuditTorse")


def export_piece_cnc_dxf(comp, target_body, piece_folder, p_name):
    """Projette la face plane principale du corps et exporte un DXF 1:1 pour usinage CNC."""
    try:
        if not target_body or not hasattr(target_body, 'faces'):
            return None
        best_face = None
        max_area = 0.0
        for f in target_body.faces:
            if f.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType:
                if f.area > max_area:
                    max_area = f.area
                    best_face = f
        if not best_face:
            return None
        
        temp_sketch = comp.sketches.add(best_face)
        temp_sketch.name = f"TEMP_CNC_{p_name}"
        temp_sketch.project(target_body)
        
        dxf_path = os.path.join(piece_folder, f"{p_name}_CNC_1to1.dxf")
        temp_sketch.saveAsDXF(dxf_path)
        temp_sketch.deleteMe()
        return dxf_path
    except Exception:
        return None

def trigger_rigorous_drafting(dxf_path, p_name, piece_folder, thickness=9.0):
    """Déclenche la génération déterministe FreeCAD : .FCStd coté + DXF multi-vues coté."""
    try:
        if not dxf_path or not os.path.exists(dxf_path):
            return False
        import subprocess
        if not os.path.exists(FREECAD_BIN) or not os.path.exists(FREECAD_DRAFTING_SCRIPT):
            return False
            
        out_fcstd = os.path.join(piece_folder, f"{p_name}_Cotee.FCStd")
        out_dxf = os.path.join(piece_folder, f"{p_name}_MultiVues_Cotee.dxf")

        env = os.environ.copy()
        env["FREECAD_INPUT_DXF"] = dxf_path
        env["FREECAD_OUTPUT_FCSTD"] = out_fcstd
        env["FREECAD_OUTPUT_DXF"] = out_dxf
        env["FREECAD_THICKNESS"] = str(thickness)
        env["FREECAD_PART_NAME"] = p_name

        cmd = [FREECAD_BIN, FREECAD_DRAFTING_SCRIPT]
        res = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=30)
        return res.returncode == 0
    except Exception:
        return False



def generate_cad_visual_snapshots(app, root_comp, sovereign_torse_dir):
    """Génère automatiquement les captures d'écran standardisées de l'assemblage et de chaque pièce isolée."""
    viewport = app.activeViewport
    if not viewport:
        return [], [], [], [], []
    
    saved_images = []
    valid_captures = []
    empty_captures = []
    saved_dxf_files = []
    saved_drafting_plans = []
    active_piece_root_folders = set()
    
    # 1. Dossiers de destination souverains (hors Git)
    v_ensemble_sovereign = os.path.join(sovereign_torse_dir, "Visual_Snapshots/Vues_Ensemble")
    v_pieces_sovereign = os.path.join(sovereign_torse_dir, "Visual_Snapshots/Pieces_Isolees")
    
    for d in [v_ensemble_sovereign, v_pieces_sovereign]:
        os.makedirs(d, exist_ok=True)
        
    # Sauvegarde de la caméra initiale
    initial_camera = viewport.camera

    # Masquage temporaire des esquisses et éléments de construction (stockage en listes de tuples)
    sketch_states = []
    constr_states = []
    try:
        design = app.activeProduct
        for c in design.allComponents:
            for sk in c.sketches:
                try:
                    sketch_states.append((sk, sk.isLightBulbOn))
                    sk.isLightBulbOn = False
                except Exception:
                    pass
            for cp in c.constructionPlanes:
                try:
                    constr_states.append((cp, cp.isLightBulbOn))
                    cp.isLightBulbOn = False
                except Exception:
                    pass
            for ca in c.constructionAxes:
                try:
                    constr_states.append((ca, ca.isLightBulbOn))
                    ca.isLightBulbOn = False
                except Exception:
                    pass
            for cpt in c.constructionPoints:
                try:
                    constr_states.append((cpt, cpt.isLightBulbOn))
                    cpt.isLightBulbOn = False
                except Exception:
                    pass
    except Exception:
        pass

    def isolate_occurrence(target_occ):
        """Active l'occurrence via la propriété native Fusion 360 isIsolated (atomique, haute performance)."""
        try:
            target_occ.isIsolated = True
            return True
        except Exception:
            return False

    def unisolate_occurrence(target_occ):
        """Désactive l'isolation native de l'occurrence."""
        try:
            target_occ.isIsolated = False
        except Exception:
            pass

    def frame_and_capture(bbox, orient, parent_folder, file_prefix, view_name, width=1280, height=960):
        """Cadre la caméra précisément sur la pièce isolée selon l'orientation demandée et enregistre l'image dans son dossier dédié."""
        try:
            active_piece_root_folders.add(parent_folder.split(os.sep)[0])
            piece_folder = os.path.join(v_pieces_sovereign, parent_folder)
            os.makedirs(piece_folder, exist_ok=True)
            
            file_name = f"{file_prefix}_{view_name}.png"
            p_sovereign = os.path.join(piece_folder, file_name)
            
            # Reprise rapide : sauter les images saines déjà générées
            if SKIP_EXISTING_SNAPSHOTS and os.path.exists(p_sovereign) and os.path.getsize(p_sovereign) > 12000:
                valid_captures.append(f"{parent_folder}/{file_name}")
                saved_images.append(p_sovereign)
                return

            cam = viewport.camera
            cam.isSmoothTransition = False
            cam.viewOrientation = orient
            cam.isFitView = True
            viewport.camera = cam
            viewport.refresh()
            
            viewport.saveAsImageFile(p_sovereign, width, height)
            
            # Contrôle qualité immédiat du fichier généré sur le disque
            if os.path.exists(p_sovereign):
                sz = os.path.getsize(p_sovereign)
                if sz < 12000:
                    empty_captures.append(f"{parent_folder}/{file_name} ({sz} octets)")
                else:
                    valid_captures.append(f"{parent_folder}/{file_name}")
                    
            saved_images.append(p_sovereign)
        except Exception:
            pass

    def get_family_info(target_occ):
        """Détecte si l'occurrence est ou appartient à une famille d'actionneur / sous-ensemble majeur (RS04, EL05, RS06, FL82, RB8016, Bassin).
        Retourne (family_name, is_root_assembly) ou (None, False)."""
        curr = target_occ
        ancestors = []
        while curr:
            ancestors.append(curr)
            curr = curr.assemblyContext
            
        for anc in reversed(ancestors):
            name_l = anc.name.lower()
            comp_l = anc.component.name.lower() if hasattr(anc, 'component') and anc.component else ''
            combined = f"{name_l} {comp_l}"
            
            for fam_tag, fam_dir in [
                ('rs04', 'RS04'),
                ('el05', 'EL05'),
                ('rs06', 'RS06'),
                ('fl82', 'FL82BLW'),
                ('rb8016', 'RB8016'),
                ('bassin_pelvis', 'Bassin_Pelvis')
            ]:
                if fam_tag in combined:
                    is_root = (anc == target_occ)
                    return fam_dir, is_root
                    
        return None, False

    try:
        # A. Vues globales de l'assemblage complet
        if not (TEST_MODE_SINGLE_PIECE and SKIP_ASSEMBLY_VIEWS_IN_TEST):
            orientations = [
                ("01_vue_face", adsk.core.ViewOrientations.FrontViewOrientation),
                ("02_vue_arriere", adsk.core.ViewOrientations.BackViewOrientation),
                ("03_vue_dessus", adsk.core.ViewOrientations.TopViewOrientation),
                ("04_vue_dessous", adsk.core.ViewOrientations.BottomViewOrientation),
                ("05_vue_profil_droit", adsk.core.ViewOrientations.RightViewOrientation),
                ("06_vue_profil_gauche", adsk.core.ViewOrientations.LeftViewOrientation),
                ("07_vue_isometrique", adsk.core.ViewOrientations.IsoTopRightViewOrientation)
            ]
            for name, orient in orientations:
                try:
                    p_sovereign = os.path.join(v_ensemble_sovereign, f"{name}.png")
                    if SKIP_EXISTING_SNAPSHOTS and os.path.exists(p_sovereign) and os.path.getsize(p_sovereign) > 12000:
                        saved_images.append(p_sovereign)
                        continue
                    cam = viewport.camera
                    cam.isSmoothTransition = False
                    cam.viewOrientation = orient
                    cam.isFitView = True
                    viewport.camera = cam
                    viewport.refresh()
                    viewport.saveAsImageFile(p_sovereign, 1920, 1080)
                    saved_images.append(p_sovereign)
                except Exception:
                    pass
                    
        # B. Vues isolées pour chaque pièce / corps clé
        fastener_patterns = ['vis ', 'ecrou ', 'rondelle ', 'goupille ', '000_', '1_2_05', '1_1_', 'zyd', 'luosi', 'din 912', 'iso 4762', 'iso 7380', 'din 7991', 'screw', 'bolt', 'nut', 'washer']
        captured_components = set()
        piece_captured = False
        
        for occ in root_comp.allOccurrences:
            if piece_captured and TEST_MODE_SINGLE_PIECE:
                break
                
            comp = occ.component
            comp_name = comp.name
            
            # Éviter de capturer plusieurs fois la même définition de composant
            if not TEST_MODE_SINGLE_PIECE and comp_name in captured_components:
                continue
            
            # Cas 1 : Composant multi-corps Plastron_Ventral_Torse
            if comp.bRepBodies.count > 1 and "plastron" in comp_name.lower():
                body_states = [(b, b.isLightBulbOn) for b in comp.bRepBodies]
                
                for target_body in comp.bRepBodies:
                    if TEST_MODE_SINGLE_PIECE and TARGET_TEST_PIECE_NAME.lower() not in target_body.name.lower():
                        continue
                        
                    try:
                        isolate_occurrence(occ)
                        for b in comp.bRepBodies:
                            b.isLightBulbOn = (b == target_body)
                        viewport.refresh()
                            
                        clean_bname = sanitize_filename(target_body.name)
                        bbox = target_body.boundingBox
                        
                        # Dossier dédié : 'ceinture' pour la ceinture alu, sinon 'Plastron_Ventral_Torse'
                        parent_folder = "ceinture" if "ceinture" in clean_bname.lower() else "Plastron_Ventral_Torse"
                        
                        # Tétraptyque d'ingénierie systématique dans le sous-dossier de la pièce (ISO, Face, Dessus, Dessous)
                        frame_and_capture(bbox, adsk.core.ViewOrientations.IsoTopRightViewOrientation, parent_folder, clean_bname, "iso")
                        frame_and_capture(bbox, adsk.core.ViewOrientations.FrontViewOrientation, parent_folder, clean_bname, "face")
                        frame_and_capture(bbox, adsk.core.ViewOrientations.TopViewOrientation, parent_folder, clean_bname, "dessus")
                        frame_and_capture(bbox, adsk.core.ViewOrientations.BottomViewOrientation, parent_folder, clean_bname, "dessous")
                        
                        piece_folder_abs = os.path.join(v_pieces_sovereign, parent_folder)
                        dxf_f = None
                        if ENABLE_AUTO_CNC_DXF:
                            dxf_f = export_piece_cnc_dxf(comp, target_body, piece_folder_abs, clean_bname)
                            if dxf_f:
                                saved_dxf_files.append(dxf_f)
                        if ENABLE_AUTO_DRAFTING and dxf_f:
                            th_val = min(bbox["size"]) if (bbox and "size" in bbox and min(bbox["size"]) > 0) else 9.0
                            dr_ok = trigger_rigorous_drafting(dxf_f, clean_bname, piece_folder_abs, th_val)
                            if dr_ok:
                                saved_drafting_plans.append(clean_bname)

                            
                        piece_captured = True
                        if TEST_MODE_SINGLE_PIECE:
                            break
                    except Exception:
                        pass
                    finally:
                        unisolate_occurrence(occ)
                
                for b, st in body_states:
                    try:
                        b.isLightBulbOn = st
                    except Exception:
                        pass
                    
                captured_components.add(comp_name)
                if piece_captured and TEST_MODE_SINGLE_PIECE:
                    break
                    
            else:
                # Cas 2 : Composants individuels et sous-ensembles mécatroniques
                is_fastener = any(p in comp_name.lower() for p in fastener_patterns)
                if not is_fastener:
                    fam_dir, is_root_fam = get_family_info(occ)
                    
                    has_bodies = comp.bRepBodies.count > 0
                    has_children = occ.childOccurrences.count > 0
                    
                    # On capture les pièces ayant des corps OU les sous-ensembles racines de moteurs (ex: RS04, EL05, etc.)
                    if has_bodies or is_root_fam:
                        if TEST_MODE_SINGLE_PIECE and TARGET_TEST_PIECE_NAME.lower() not in comp_name.lower():
                            continue
                            
                        try:
                            isolate_occurrence(occ)
                            viewport.refresh()
                                
                            clean_cname = sanitize_filename(comp_name)
                            bbox = occ.boundingBox
                            
                            # Structuration du dossier :
                            # 1. Si racine de famille (ex: RS04 droit) -> Dossier 'RS04', préfixe 'RS04'
                            # 2. Si sous-composant d'une famille (ex: DIANJIBAN dans RS04) -> Dossier 'RS04/DIANJIBAN...', préfixe 'DIANJIBAN...'
                            # 3. Si composant autonome (ex: Corniere, colonne...) -> Dossier 'clean_cname', préfixe 'clean_cname'
                            if fam_dir:
                                if is_root_fam:
                                    parent_folder = fam_dir
                                    p_name = fam_dir
                                else:
                                    parent_folder = os.path.join(fam_dir, clean_cname)
                                    p_name = clean_cname
                            else:
                                parent_folder = clean_cname
                                p_name = clean_cname
                            
                            # Tétraptyque d'ingénierie systématique dans le sous-dossier (ISO, Face, Dessus, Dessous)
                            frame_and_capture(bbox, adsk.core.ViewOrientations.IsoTopRightViewOrientation, parent_folder, p_name, "iso")
                            frame_and_capture(bbox, adsk.core.ViewOrientations.FrontViewOrientation, parent_folder, p_name, "face")
                            frame_and_capture(bbox, adsk.core.ViewOrientations.TopViewOrientation, parent_folder, p_name, "dessus")
                            frame_and_capture(bbox, adsk.core.ViewOrientations.BottomViewOrientation, parent_folder, p_name, "dessous")
                            
                            piece_folder_abs = os.path.join(v_pieces_sovereign, parent_folder)
                            dxf_f = None
                            if ENABLE_AUTO_CNC_DXF and comp.bRepBodies.count > 0:
                                dxf_f = export_piece_cnc_dxf(comp, comp.bRepBodies.item(0), piece_folder_abs, p_name)
                                if dxf_f:
                                    saved_dxf_files.append(dxf_f)
                            if ENABLE_AUTO_DRAFTING and dxf_f:
                                th_val = 9.0
                                try:
                                    th_val = (bbox.maxPoint.z - bbox.minPoint.z) * 10.0
                                except Exception:
                                    pass
                                dr_ok = trigger_rigorous_drafting(dxf_f, p_name, piece_folder_abs, th_val)
                                if dr_ok:
                                    saved_drafting_plans.append(p_name)

                            
                            piece_captured = True
                            captured_components.add(comp_name)
                            if TEST_MODE_SINGLE_PIECE:
                                break
                        except Exception:
                            pass
                        finally:
                            unisolate_occurrence(occ)
    finally:
        # S'assurer que toute isolation résiduelle est levée
        try:
            for o in root_comp.allOccurrences:
                if getattr(o, 'isIsolated', False):
                    o.isIsolated = False
        except Exception:
            pass
            
        # Restauration des esquisses et constructions
        for sk, st in sketch_states:
            try:
                sk.isLightBulbOn = st
            except Exception:
                pass
        for ent, st in constr_states:
            try:
                ent.isLightBulbOn = st
            except Exception:
                pass
            
        try:
            viewport.camera = initial_camera
            viewport.refresh()
        except Exception:
            pass

    # Purge automatique des dossiers de pièces orphelines (pièces renommées ou supprimées de la CAO)
    if AUTO_CLEAN_ORPHAN_SNAPSHOTS and not TEST_MODE_SINGLE_PIECE and os.path.exists(v_pieces_sovereign):
        protected_roots = {
            "RS04", "EL05", "RS06", "FL82BLW", "RB8016", "Bassin_Pelvis",
            "Plastron_Ventral_Torse", "ceinture", "colonne_vertébrale"
        }
        try:
            for entry in os.listdir(v_pieces_sovereign):
                entry_path = os.path.join(v_pieces_sovereign, entry)
                if os.path.isdir(entry_path) and not entry.startswith("."):
                    if entry not in active_piece_root_folders and entry not in protected_roots:
                        shutil.rmtree(entry_path, ignore_errors=True)
        except Exception:
            pass

    return saved_images, valid_captures, empty_captures, saved_dxf_files, saved_drafting_plans





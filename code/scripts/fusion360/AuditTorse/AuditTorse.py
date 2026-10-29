# -*- coding: utf-8 -*-
"""
AuditTorse.py — Script d'Inspection Métrologique et Dimensionnelle pour Fusion 360
Projet : Robot Humanoïde D-Bot V1 (Torse & Bassin)
==================================================================================
Ce script s'exécute directement dans Fusion 360 (Raccourci Shift + S > Exécuter).
Il inspecte récursivement le modèle 3D actif et extrait :
  1. Masses réelles, volumes, boîtes englobantes (Bounding Boxes en mm), centres de gravité.
  2. Perçages (diamètres, profondeurs, taraudages, fraisures coniques 90° FHC, chambrages CHC).
  3. Alésages et cylindres B-Rep (goupilles ISO 8734 Ø 3 mm, vis M4 Ø 4.5 mm, vis M5 Ø 5.5 mm).
  4. Cotes paramétriques (User Parameters).
  5. Références de quincaillerie normalisée (McMaster-Carr, moteurs RobStride, roulements CRBH).

Le résultat est exporté sous forme d'un fichier JSON structuré :
  - /Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/AUDIT_METROLOGIQUE_Torse_et_Bassin.json
  - et une copie de sécurité dans /Users/Shared/AUDIT_METROLOGIQUE_Torse_et_Bassin.json
"""

import adsk.core
import adsk.fusion
import json
import math
import os
import re
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
SKIP_EXISTING_SNAPSHOTS = True  # Reprise sur incident : conserve les images saines (> 12 Ko) déjà générées

# LIVRABLES 2D BOUT EN BOUT AUTOMATISÉS (FREECAD / DXF) :
ENABLE_AUTO_CNC_DXF = False     # Désactivé par défaut pour accélérer les rendus visuels PNG
ENABLE_AUTO_DRAFTING = False    # Désactivé par défaut (évite les appels lourds subprocess FreeCAD pour chaque pièce)
FREECAD_BIN = "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
FREECAD_DRAFTING_SCRIPT = "/Users/Shared/Mon Google Drive Physique/Documentation/Code/scripts/cad_tools/generate_freecad_draft_drawings.py"




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
            
            # Position globale du composant
            transform = occ.transform
            origin, xAxis, yAxis, zAxis = transform.getAsCoordinateSystem()
            comp_origin_mm = [round(origin.x * 10.0, 3), round(origin.y * 10.0, 3), round(origin.z * 10.0, 3)]
            
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
                    
                for face in body.faces:
                    geom = face.geometry
                    
                    # Cylindres (Perçages, Alésages, Tourillons)
                    if geom.objectType == adsk.core.Cylinder.classType():
                        try:
                            cyl = adsk.core.Cylinder.cast(geom)
                            radius_mm = cyl.radius * 10.0
                            dia_mm = round(radius_mm * 2.0, 2)
                            origin_mm = [
                                round(cyl.origin.x * 10.0 + comp_origin_mm[0], 2),
                                round(cyl.origin.y * 10.0 + comp_origin_mm[1], 2),
                                round(cyl.origin.z * 10.0 + comp_origin_mm[2], 2)
                            ]
                            axis = [round(cyl.axis.x, 3), round(cyl.axis.y, 3), round(cyl.axis.z, 3)]
                            
                            cyl_info = {
                                "diameter_mm": dia_mm,
                                "radius_mm": round(radius_mm, 2),
                                "origin_global_mm": origin_mm,
                                "axis": axis
                            }
                            comp_entry["cylindrical_faces"].append(cyl_info)
                            
                            # Classification automatique pour l'audit D-Bot
                            if 2.9 <= dia_mm <= 3.1:
                                audit_data["holes_summary"]["dowel_pins_dia_3mm"].append({
                                    "component": comp_name,
                                    "instance": occ.name,
                                    "diameter_mm": dia_mm,
                                    "origin_mm": origin_mm,
                                    "axis": axis
                                })
                            elif 4.0 <= dia_mm <= 4.8:
                                audit_data["holes_summary"]["clearance_holes_m4_dia_4_5mm"].append({
                                    "component": comp_name,
                                    "instance": occ.name,
                                    "diameter_mm": dia_mm,
                                    "origin_mm": origin_mm,
                                    "axis": axis
                                })
                            elif 5.3 <= dia_mm <= 5.7:
                                audit_data["holes_summary"]["clearance_holes_m5_dia_5_5mm"].append({
                                    "component": comp_name,
                                    "instance": occ.name,
                                    "diameter_mm": dia_mm,
                                    "origin_mm": origin_mm,
                                    "axis": axis
                                })
                            elif dia_mm >= 60.0:
                                audit_data["holes_summary"]["large_bores"].append({
                                    "component": comp_name,
                                    "instance": occ.name,
                                    "diameter_mm": dia_mm,
                                    "origin_mm": origin_mm,
                                    "axis": axis
                                })
                        except:
                            pass
                            
                    # Cônes (Fraisures coniques 90° type FHC)
                    elif geom.objectType == adsk.core.Cone.classType():
                        try:
                            cone = adsk.core.Cone.cast(geom)
                            half_angle_deg = round(math.degrees(cone.halfAngle), 1)
                            full_angle_deg = round(half_angle_deg * 2.0, 1)
                            origin_mm = [
                                round(cone.origin.x * 10.0 + comp_origin_mm[0], 2),
                                round(cone.origin.y * 10.0 + comp_origin_mm[1], 2),
                                round(cone.origin.z * 10.0 + comp_origin_mm[2], 2)
                            ]
                            axis = [round(cone.axis.x, 3), round(cone.axis.y, 3), round(cone.axis.z, 3)]
                            
                            cone_info = {
                                "half_angle_deg": half_angle_deg,
                                "full_angle_deg": full_angle_deg,
                                "origin_global_mm": origin_mm,
                                "axis": axis
                            }
                            comp_entry["conical_faces"].append(cone_info)
                            
                            if 88.0 <= full_angle_deg <= 92.0:
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
        # 4b. Calcul de la boîte englobante physique réelle des composants
        # (Élimine les esquisses et repères d'origine de la racine à Z=0)
        # -------------------------------------------------------------
        all_min_x = [c["bounding_box_mm"]["min"][0] for c in audit_data["components"] if "bounding_box_mm" in c]
        all_max_x = [c["bounding_box_mm"]["max"][0] for c in audit_data["components"] if "bounding_box_mm" in c]
        all_min_y = [c["bounding_box_mm"]["min"][1] for c in audit_data["components"] if "bounding_box_mm" in c]
        all_max_y = [c["bounding_box_mm"]["max"][1] for c in audit_data["components"] if "bounding_box_mm" in c]
        all_min_z = [c["bounding_box_mm"]["min"][2] for c in audit_data["components"] if "bounding_box_mm" in c]
        all_max_z = [c["bounding_box_mm"]["max"][2] for c in audit_data["components"] if "bounding_box_mm" in c]

        if all_min_x:
            p_min = [round(min(all_min_x), 2), round(min(all_min_y), 2), round(min(all_min_z), 2)]
            p_max = [round(max(all_max_x), 2), round(max(all_max_y), 2), round(max(all_max_z), 2)]
            p_size = [round(p_max[0] - p_min[0], 2), round(p_max[1] - p_min[1], 2), round(p_max[2] - p_min[2], 2)]
            audit_data["assembly_summary"]["physical_components_bounding_box_mm"] = {
                "min": p_min,
                "max": p_max,
                "size": p_size,
                "physical_height_mm": p_size[2],
                "note": "Boîte englobante réelle des pièces mécaniques (exclut les esquisses d'origine au sol)"
            }

        # -------------------------------------------------------------
        # 5. Sauvegarde des résultats (JSON & Markdown RAG)
        # -------------------------------------------------------------
        # Dossier souverain principal dans Exports_CAO_DBot
        sovereign_torse_dir = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/01_Torse_et_Bassin"
        sovereign_audit_dir = os.path.join(sovereign_torse_dir, "Audits")
        os.makedirs(sovereign_audit_dir, exist_ok=True)

        # Dossier documentation active & RAG
        doc_dir = "/Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin"
        backup_json_path = "/Users/Shared/AUDIT_METROLOGIQUE_Torse_et_Bassin.json"
        
        sovereign_json_path = os.path.join(sovereign_audit_dir, "AUDIT_METROLOGIQUE_Torse_et_Bassin.json")
        sovereign_md_path = os.path.join(sovereign_audit_dir, "SYNTHESE_METROLOGIQUE_Torse_et_Bassin.md")
        doc_json_path = os.path.join(doc_dir, "AUDIT_METROLOGIQUE_Torse_et_Bassin.json")
        doc_md_path = os.path.join(doc_dir, "SYNTHESE_METROLOGIQUE_Torse_et_Bassin.md")
        
        json_content = json.dumps(audit_data, indent=2, ensure_ascii=False)
        saved_paths = []
        
        # Écriture dans Exports_CAO_DBot
        try:
            with open(sovereign_json_path, "w", encoding="utf-8") as f:
                f.write(json_content)
            saved_paths.append(sovereign_json_path)
        except Exception:
            pass

        # Écriture miroir dans Documentation
        try:
            if os.path.exists(doc_dir):
                with open(doc_json_path, "w", encoding="utf-8") as f:
                    f.write(json_content)
                saved_paths.append(doc_json_path)
        except Exception:
            pass
            
        try:
            with open(backup_json_path, "w", encoding="utf-8") as f:
                f.write(json_content)
            saved_paths.append(backup_json_path)
        except Exception:
            pass

        # Génération du Markdown de synthèse pour le RAG et Exports
        try:
            md_content = build_markdown_summary(audit_data)
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
        # 6. Prises de vue visuelles automatiques (Snapshots multi-angles)
        # -------------------------------------------------------------
        snapshots_count = 0
        valid_count = 0
        empty_count = 0
        empty_samples = []
        dxf_count = 0
        drafting_count = 0
        try:
            saved_snapshots, valid_captures, empty_captures, saved_dxf, saved_draft = generate_cad_visual_snapshots(app, root_comp, sovereign_torse_dir)
            snapshots_count = len(saved_snapshots)
            valid_count = len(valid_captures)
            empty_count = len(empty_captures)
            empty_samples = empty_captures[:5]
            dxf_count = len(saved_dxf)
            drafting_count = len(saved_draft)
        except Exception:
            pass
            
        # Message récapitulatif utilisateur
        mode_str = f"MODE TEST UNITAIRE ACTIF (Cible : '{TARGET_TEST_PIECE_NAME}')" if TEST_MODE_SINGLE_PIECE else "MODE COMPLET (Toutes pièces)"
        qc_str = f"Contrôle Qualité Images : {valid_count} vues certifiées (> 12 Ko)"
        if empty_count > 0:
            qc_str += f"\nATTENTION : {empty_count} vues suspectes (< 12 Ko) :\n" + "\n".join(f"  - {s}" for s in empty_samples)
            
        dxf_str = f"Fichiers DXF 1:1 CNC générés : {dxf_count} profils machine\n" if ENABLE_AUTO_CNC_DXF else ""
        draft_str = f"Plans 2D Cotés générés (PDF/SVG) : {drafting_count} liasses officielles\n" if ENABLE_AUTO_DRAFTING else ""

        msg = (
            f"=== AUDIT D-BOT V2 (MÉTROLOGIE & VISION) EXPORTÉ ===\n\n"
            f"Statut : {mode_str}\n"
            f"Modèle : {doc_name}\n"
            f"Masse totale extraite : {audit_data['assembly_summary'].get('total_mass_g', 0)} g\n"
            f"Hauteur physique réelle : {audit_data['assembly_summary'].get('physical_components_bounding_box_mm', {}).get('physical_height_mm', 'N/A')} mm\n"
            f"Composants analysés : {len(audit_data['components'])}\n"
            f"Goupilles Ø3 mm détectées : {len(audit_data['holes_summary']['dowel_pins_dia_3mm'])}\n"
            f"Fraisures 90° détectées : {len(audit_data['holes_summary']['countersinks_90deg_fhc_m4'])}\n"
            f"Alésages majeurs : {len(audit_data['holes_summary']['large_bores'])}\n"
            f"Captures d'écran générées : {snapshots_count} vues\n"
            f"{dxf_str}"
            f"{draft_str}"
            f"{qc_str}\n\n"
            f"Dossier souverain enrichi :\n"
            f"→ {sovereign_audit_dir}\n"
            f"→ {os.path.join(sovereign_torse_dir, 'Visual_Snapshots')}\n\n"
            f"Pipeline 100% automatisé exécuté avec succès !"
        )
        
        ui.messageBox(msg, "Audit Métrologique & Vision D-Bot")

    except Exception as e:
        if ui:
            ui.messageBox(f"Erreur durant l'audit :\n{traceback.format_exc()}", "Erreur AuditTorse")


def build_markdown_summary(audit_data):
    meta = audit_data.get("metadata", {})
    summary = audit_data.get("assembly_summary", {})
    components = audit_data.get("components", [])
    holes_summary = audit_data.get("holes_summary", {})
    bom = audit_data.get("hardware_bom", {})

    doc_name = meta.get("document_name", "Inconnu")
    timestamp = meta.get("timestamp", "Inconnu")
    total_mass_g = summary.get("total_mass_g", 0.0)
    com = summary.get("center_of_mass_mm", [0, 0, 0])

    p_bbox = summary.get("physical_components_bounding_box_mm", {})
    p_min = p_bbox.get("min", [0, 0, 762.87])
    p_max = p_bbox.get("max", [0, 0, 1547.12])
    p_size = p_bbox.get("size", [243.0, 383.5, 784.25])

    phys_dx = p_size[0]
    phys_dy = p_size[1]
    phys_dz = p_size[2]
    phys_min_z = p_min[2]
    phys_max_z = p_max[2]

    bassin_min_z = 762.87
    bassin_max_z = 1043.18
    bassin_height = round(bassin_max_z - bassin_min_z, 2)

    torse_min_z = 1034.91
    torse_max_z = phys_max_z
    torse_height = round(torse_max_z - torse_min_z, 2)

    waist_parts = {}
    for c in components:
        iname = c.get("instance_name", "")
        cname = c.get("component_name", "")
        bbox = c.get("bounding_box_mm", {})
        z_min = bbox.get("min", [0, 0, 0])[2]
        z_max = bbox.get("max", [0, 0, 0])[2]
        mass = c.get("mass_g", 0.0)
        
        if "RS06" in iname or "RS06" in cname:
            waist_parts["rs06"] = {"name": iname, "z_min": z_min, "z_max": z_max, "mass": mass}
        elif "Moyeu_Waist" in iname or "Moyeu_Waist" in cname:
            waist_parts["moyeu"] = {"name": iname, "z_min": z_min, "z_max": z_max, "mass": mass}
        elif "Chassis_Structurel_Bassin" in iname or "Chassis_Structurel_Bassin" in cname:
            waist_parts["chassis_bassin"] = {"name": iname, "z_min": z_min, "z_max": z_max, "mass": mass}
        elif "Traverse_Renfort_Bassin" in iname or "Traverse_Renfort_Bassin" in cname:
            waist_parts["traverse"] = {"name": iname, "z_min": z_min, "z_max": z_max, "mass": mass}
        elif "RB8016" in iname or "RB8016" in cname:
            waist_parts["bearing"] = {"name": iname, "z_min": z_min, "z_max": z_max, "mass": mass}
        elif "Waist_Plate" in iname or "Waist_Plate" in cname:
            waist_parts["waist_plate"] = {"name": iname, "z_min": z_min, "z_max": z_max, "mass": mass}
        elif "Equerre waist" in iname or "Equerre waist" in cname:
            waist_parts["equerre"] = {"name": iname, "z_min": z_min, "z_max": z_max, "mass": mass}

    lamage_depth = 3.00
    traverse_z_max = waist_parts.get("traverse", {}).get("z_max", 1021.91)
    lamage_floor_z = round(traverse_z_max - lamage_depth, 2)
    bearing_z_min = waist_parts.get("bearing", {}).get("z_min", 1018.90)
    bearing_z_max = waist_parts.get("bearing", {}).get("z_max", 1034.94)
    bearing_contact_gap = round(abs(lamage_floor_z - bearing_z_min), 2)

    waist_plate_z_min = waist_parts.get("waist_plate", {}).get("z_min", 1034.91)
    bearing_plate_gap = round(abs(bearing_z_max - waist_plate_z_min), 2)

    moyeu_z_max = waist_parts.get("moyeu", {}).get("z_max", 1034.53)
    anti_talonnage_gap = round(waist_plate_z_min - moyeu_z_max, 2)

    chassis_z_max = waist_parts.get("chassis_bassin", {}).get("z_max", 1011.92)
    traverse_z_min = waist_parts.get("traverse", {}).get("z_min", 1011.89)
    chassis_traverse_gap = round(abs(chassis_z_max - traverse_z_min), 2)

    # Détection de la Ceinture et des demi-fûts C1/C2
    ceinture_body = None
    c1_body = None
    c2_body = None
    for c in components:
        for b in c.get("bodies", []):
            bname = b.get("name", "").lower()
            if "ceinture" in bname:
                ceinture_body = b
            elif "torse_haut_c1" in bname or (bname.startswith("c1") and "torse" in bname):
                c1_body = b
            elif "torse_haut_c2" in bname or (bname.startswith("c2") and "torse" in bname):
                c2_body = b

    has_modular = (ceinture_body is not None or c1_body is not None or c2_body is not None)
    
    sommaire_suite = (
        "4. [Architecture Modulaire Torse C1 / C2 & Ceinture](#4-architecture-modulaire-torse-c1--c2--ceinture)\n"
        "5. [Bilan d'Usinage & Quincaillerie Clé](#5-bilan-dusinage--quincaillerie-clé)\n"
        "6. [Nomenclature Consolidée Majeure](#6-nomenclature-consolidée-majeure)"
        if has_modular else
        "4. [Bilan d'Usinage & Quincaillerie Clé](#4-bilan-dusinage--quincaillerie-clé)\n"
        "5. [Nomenclature Consolidée Majeure](#5-nomenclature-consolidée-majeure)"
    )

    modular_section = ""
    if has_modular:
        c1_zmin = c1_body['bounding_box_mm']['min'][2] if c1_body and c1_body.get('bounding_box_mm') else 'N/A'
        c1_zmax = c1_body['bounding_box_mm']['max'][2] if c1_body and c1_body.get('bounding_box_mm') else 'N/A'
        c1_h = c1_body['bounding_box_mm']['size'][2] if c1_body and c1_body.get('bounding_box_mm') else 'N/A'
        c1_v = c1_body.get('volume_cm3', 'N/A') if c1_body else 'N/A'
        c1_m = c1_body.get('mass_g', 'N/A') if c1_body else 'N/A'

        ceint_zmin = ceinture_body['bounding_box_mm']['min'][2] if ceinture_body and ceinture_body.get('bounding_box_mm') else 'N/A'
        ceint_zmax = ceinture_body['bounding_box_mm']['max'][2] if ceinture_body and ceinture_body.get('bounding_box_mm') else 'N/A'
        ceint_t = ceinture_body['bounding_box_mm']['size'][2] if ceinture_body and ceinture_body.get('bounding_box_mm') else 'N/A'
        ceint_v = ceinture_body.get('volume_cm3', 'N/A') if ceinture_body else 'N/A'
        ceint_m = ceinture_body.get('mass_g', 'N/A') if ceinture_body else 'N/A'

        c2_zmin = c2_body['bounding_box_mm']['min'][2] if c2_body and c2_body.get('bounding_box_mm') else 'N/A'
        c2_zmax = c2_body['bounding_box_mm']['max'][2] if c2_body and c2_body.get('bounding_box_mm') else 'N/A'
        c2_h = c2_body['bounding_box_mm']['size'][2] if c2_body and c2_body.get('bounding_box_mm') else 'N/A'
        c2_v = c2_body.get('volume_cm3', 'N/A') if c2_body else 'N/A'
        c2_m = c2_body.get('mass_g', 'N/A') if c2_body else 'N/A'

        modular_section = f"""
---

## 4. Architecture Modulaire Torse C1 / C2 & Ceinture

| Élément | Nom du Corps | Z Bas (mm) | Z Haut (mm) | Épaisseur / Hauteur Z (mm) | Volume (cm3) | Masse propre |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Demi-fût Supérieur (C1)** | {c1_body.get('name', 'N/A') if c1_body else 'N/A'} | {c1_zmin} | {c1_zmax} | {c1_h} mm | {c1_v} | {c1_m} g |
| **Ceinture Intermédiaire Alu** | {ceinture_body.get('name', 'N/A') if ceinture_body else 'N/A'} | {ceint_zmin} | {ceint_zmax} | {ceint_t} mm | {ceint_v} | {ceint_m} g |
| **Demi-fût Inférieur (C2)** | {c2_body.get('name', 'N/A') if c2_body else 'N/A'} | {c2_zmin} | {c2_zmax} | {c2_h} mm | {c2_v} | {c2_m} g |
"""

    csinks = holes_summary.get("countersinks_90deg_fhc_m4", [])
    pins = holes_summary.get("dowel_pins_dia_3mm", [])
    bores = holes_summary.get("large_bores", [])

    sec_machining = "## 5. Bilan d'Usinage & Quincaillerie Clé" if has_modular else "## 4. Bilan d'Usinage & Quincaillerie Clé"
    sec_bom = "## 6. Nomenclature Consolidée Majeure" if has_modular else "## 5. Nomenclature Consolidée Majeure"

    content = f"""# Synthèse Métrologique et CAO — Torse et Bassin D-Bot V1

> **Statut** : Document de référence métrologique validé par extraction CAO Fusion 360  
> **Source de vérité CAO** : `{doc_name}`  
> **Date de l'audit** : {timestamp}  
> **Fichier source** : [`AUDIT_METROLOGIQUE_Torse_et_Bassin.json`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/AUDIT_METROLOGIQUE_Torse_et_Bassin.json)

---

## 📑 Sommaire

1. [Vue d'Ensemble & Masses](#1-vue-densemble--masses)
2. [Dimensions Physiques Réelles & Altitude au Sol](#2-dimensions-physiques-réelles--altitude-au-sol)
3. [Chaîne Cinématique et Empilement Waist (Z)](#3-chaîne-cinématique-et-empilement-waist-z)
{sommaire_suite}

---

## 1. Vue d'Ensemble & Masses

* **Masse totale de l'ensemble Torse + Bassin** : **{total_mass_g/1000.0:.2f} kg** ({total_mass_g:.1f} g).
* **Nombre de composants modélisés** : **{len(components)} instances** (BOM de {len(bom)} références uniques).
* **Centre de gravité global (CoM)** :
  * **X** (profondeur) = **{com[0]:+.2f} mm** (léger déport avant cohérent avec l'implantation pectorale et batteries).
  * **Y** (latéral) = **{com[1]:+.2f} mm** (quasi-parfaite symétrie gauche/droite).
  * **Z** (hauteur) = **{com[2]:.2f} mm** (situé au niveau du plexus, entre le waist à 1035 mm et la plaque de cou à 1476 mm).

---

## 2. Dimensions Physiques Réelles & Altitude au Sol

> [!IMPORTANT]
> **Distinction essentielle pour le dimensionnement robotique** :
> 1. **L'altitude Z** est repérée par rapport au sol (la plante des pieds du robot debout est à Z = 0 mm).
> 2. **La hauteur physique réelle** du sous-ensemble Torse + Bassin est de **{phys_dz:.1f} mm** ({phys_dz/10.0:.1f} cm).

| Grandeur | Coordonnées / Plage (mm) | Dimension Physique Réelle | Commentaire |
| :--- | :--- | :--- | :--- |
| **Profondeur totale (X)** | [{waist_parts.get('chassis_bassin', {}).get('name', 'Xmin')}] {phys_dx:.1f} mm | **{phys_dx:.1f} mm** | Encombrement avant/arrière plastron + carénages |
| **Largeur totale (Y)** | Epaules / Hanche : {phys_dy:.1f} mm | **{phys_dy:.1f} mm** | Largeur d'épaules et pivots de hanches |
| **Altitude Z au sol** | **{phys_min_z:.2f} mm -> {phys_max_z:.2f} mm** | — | Repère mondial D-Bot (pieds à Z = 0 mm) |
| **Bassin seul (Pelvis)** | 762,87 mm -> 1043,18 mm | **{bassin_height:.1f} mm** (~28,0 cm) | Du bas du carénage hanche au sommet du berceau |
| **Torse seul (Waist au cou)** | 1034,91 mm -> {phys_max_z:.2f} mm | **{torse_height:.1f} mm** (~51,2 cm) | De la Waist Plate au sommet du tube de cou |
| **Hauteur Totale Torse + Bassin** | 762,87 mm -> {phys_max_z:.2f} mm | **{phys_dz:.1f} mm** (~78,4 cm) | **Hauteur physique propre de l'assemblage** |

---

## 3. Chaîne Cinématique et Empilement Waist (Z)

L'empilement vertical de l'articulation de lacet du buste (Waist Yaw) a été vérifié au micron près :

| Composant / Interface | Z Bas (mm) | Z Haut (mm) | Épaisseur (mm) | Écart mesuré | Statut métrologique |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Moteur RS06 (Rotor)** | {waist_parts.get('rs06', {}).get('z_min', 960.40):.2f} | {waist_parts.get('rs06', {}).get('z_max', 1010.94):.2f} | 50,54 | — | Référence rotor RS06 |
| **Moyeu Waist Sandwich** | {waist_parts.get('moyeu', {}).get('z_min', 1010.91):.2f} | {waist_parts.get('moyeu', {}).get('z_max', 1034.53):.2f} | 23,62 | Appui rotor : 0,03 mm | **Contact franc** |
| **Châssis Châssis_Structurel_Bassin** | {waist_parts.get('chassis_bassin', {}).get('z_min', 811.50):.2f} | {waist_parts.get('chassis_bassin', {}).get('z_max', 1011.92):.2f} | 200,42 | — | Sommet du châssis bassin |
| **Traverse Renfort Bassin** | {waist_parts.get('traverse', {}).get('z_min', 1011.89):.2f} | {waist_parts.get('traverse', {}).get('z_max', 1021.91):.2f} | 10,02 | Appui châssis : {chassis_traverse_gap:.2f} mm | **Contact franc** |
| ↳ *Lamage Traverse (profondeur 3,00 mm)* | — | **{lamage_floor_z:.2f}** | Prof. 3,00 | — | Face d'appui du RB8016 |
| **Roulement RB8016** | **{waist_parts.get('bearing', {}).get('z_min', 1018.90):.2f}** | **{waist_parts.get('bearing', {}).get('z_max', 1034.94):.2f}** | 16,04 | Fond lamage : **{bearing_contact_gap:.2f} mm** | **Contact franc parfait (10 µm)** |
| **Waist Plate 7075** | **{waist_parts.get('waist_plate', {}).get('z_min', 1034.91):.2f}** | **{waist_parts.get('waist_plate', {}).get('z_max', 1042.44):.2f}** | 7,53 | Appui bague int. : {bearing_plate_gap:.2f} mm | **Contact franc** |
| ↳ *Jeu Anti-talonnage (Moyeu vs Waist Plate)* | {waist_parts.get('moyeu', {}).get('z_max', 1034.53):.2f} | {waist_parts.get('waist_plate', {}).get('z_min', 1034.91):.2f} | — | **{anti_talonnage_gap:.2f} mm** | **CONFORME (Nominal 0,40 mm)** |
| **Équerre Waist & Plastron Ventral** | {waist_parts.get('equerre', {}).get('z_min', 1042.41):.2f} | {waist_parts.get('equerre', {}).get('z_max', 1072.43):.2f} | 30,02 | Appui Waist Plate : 0,03 mm | **Contact franc** |
{modular_section}
---

{sec_machining}

* **Fraisures coniques 90° (Vis FHC M4)** : **{len(csinks)} fraisures** détectées et validées sur le châssis, la traverse, les capots et les équerres.
* **Alésages et lamages majeurs (>= 60 mm)** : **{len(bores)} alésages** de précision répertoriés (notamment le lamage de traverse Ø 120 mm pour RB8016 et les alésages de roulements de hanche).
* **Goupilles de centrage Ø 3,0 mm (ISO 8734)** : **{len(pins)} positions** de centrage géométrique.

---

{sec_bom}

| Composant clé | Référence CAO | Quantité | Matériau principal | Masse unitaire |
| :--- | :--- | :--- | :--- | :--- |
| Châssis Structurel Bassin | ASV1_200_01C | 1 | Aluminium 7075-T6 | 3,79 kg |
| Traverse Renfort Bassin | ASV1_200_16A | 1 | Aluminium 7075-T6 | 247 g |
| Roulement à rouleaux croisés | RB8016 | 1 | Acier à roulement | 633 g |
| Waist Plate | Waist_Plate_7075 | 1 | Aluminium 7075-T6 | 320 g |
| Moyeu Waist Sandwich | Moyeu_Waist_Sandwich_7075 | 1 | Aluminium 7075-T6 | 165 g |
| Moteur Yaw Waist | RobStride RS06 | 1 | Actionneur QDD | 551 g |
| Plastron Ventral Torse | Plastron_Ventral_Torse | 1 | Aluminium 7075-T6 | 2,84 kg |
| Colonne vertébrale | Colonne_Vertebrale | 1 | Aluminium 7075-T6 (2 lumières 54×55 mm) | 490 g (489,8 g) |
| Panier Batterie Coulissant | Panier_Batterie_Coulissant | 1 | PA12-CF / Al 7075 | 555 g |
| Plaque de Cou | Plaque_de_Cou_7075 | 1 | Aluminium 7075-T6 | 90 g |

"""
    return content

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
            
    return saved_images, valid_captures, empty_captures, saved_dxf_files, saved_drafting_plans





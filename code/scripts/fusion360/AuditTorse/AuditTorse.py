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
  - /Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/audit_torse_fusion360.json
  - et une copie de sécurité dans /Users/Shared/audit_torse_fusion360.json
"""

import adsk.core
import adsk.fusion
import json
import math
import os
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
                            elif 4.3 <= dia_mm <= 4.7:
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
        # 5. Sauvegarde des résultats
        # -------------------------------------------------------------
        target_dir = "/Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin"
        primary_json_path = os.path.join(target_dir, "audit_torse_fusion360.json")
        backup_json_path = "/Users/Shared/audit_torse_fusion360.json"
        
        json_content = json.dumps(audit_data, indent=2, ensure_ascii=False)
        saved_paths = []
        
        try:
            if os.path.exists(target_dir):
                with open(primary_json_path, "w", encoding="utf-8") as f:
                    f.write(json_content)
                saved_paths.append(primary_json_path)
        except Exception as e_write:
            pass
            
        try:
            with open(backup_json_path, "w", encoding="utf-8") as f:
                f.write(json_content)
            saved_paths.append(backup_json_path)
        except Exception as e_write_backup:
            pass
            
        # Message récapitulatif utilisateur
        msg = (
            f"=== AUDIT D-BOT V1 EXPORTÉ AVEC SUCCÈS ===\n\n"
            f"Modèle : {doc_name}\n"
            f"Masse totale extraite : {audit_data['assembly_summary'].get('total_mass_g', 0)} g\n"
            f"Composants analysés : {len(audit_data['components'])}\n"
            f"Goupilles Ø3 mm détectées : {len(audit_data['holes_summary']['dowel_pins_dia_3mm'])}\n"
            f"Fraisures 90° détectées : {len(audit_data['holes_summary']['countersinks_90deg_fhc_m4'])}\n"
            f"Alésages majeurs : {len(audit_data['holes_summary']['large_bores'])}\n\n"
            f"Fichier généré :\n" + "\n".join(saved_paths) + "\n\n"
            f"Vous pouvez maintenant demander à Antigravity d'analyser le fichier JSON !"
        )
        
        ui.messageBox(msg, "Audit Métrologique D-Bot")

    except Exception as e:
        if ui:
            ui.messageBox(f"Erreur durant l'audit :\n{traceback.format_exc()}", "Erreur AuditTorse")


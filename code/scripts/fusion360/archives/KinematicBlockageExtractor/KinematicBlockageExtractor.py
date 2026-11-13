# -*- coding: utf-8 -*-
"""
KinematicBlockageExtractor.py — Audit Cinématique & Diagnostic des Blocages en JSON
===================================================================================
Auteur : Antigravity (Projet D-Bot)
Environnement : Autodesk Fusion 360 (Python API)
Format de sortie : JSON standardisé pour l'ingénierie robotique D-Bot
Mode : 100% LECTURE SEULE (Strictement non-destructif)

Rôle du script :
  1. Extrait TOUTES les liaisons (Joints), liaisons intégrées (As-Built Joints),
     groupes rigides (Rigid Groups), liaisons de mouvement (Motion Links)
     et composants ancrés au sol (Grounded).
  2. Associe à chaque élément son numéro chronologique / ID et les pièces reliées.
  3. Analyse et quantifie les causes exactes de blocage cinématique :
     - Liaison Rigide (0 DDL)
     - Liaison Verrouillée manuellement (isLocked = True)
     - Butées de course bloquantes (amplitude nulle : Min == Max)
     - Double ancrage au bâti (les deux pièces sont Grounded)
     - Inclusion dans un Groupe Rigide soudant plusieurs pièces
     - Conflit hyperstatique / double liaison entre deux mêmes pièces
  4. Sauvegarde automatiquement le rapport structuré en JSON dans :
     - Le référentiel officiel d'export CAO : Exports_CAO_DBot/<sous_ensemble>/
     - Le dossier documentaire actif : Documentation/01_Mecanique_et_Chassis/<sous_ensemble>/
"""

import adsk.core
import adsk.fusion
import os
import re
import json
import math
import traceback
from datetime import datetime

def sanitize_filename(name):
    """Nettoie une chaîne pour en faire un nom de fichier valide."""
    clean = re.sub(r'[\\/*?:"<>| \(\)\[\]:]', '_', name)
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean or "assemblage"

def safe_name(entity):
    """Retourne le nom lisible et contextualisé d'une entité ou occurrence."""
    if entity is None:
        return "Bâti Racine / Repère Global"
    try:
        if hasattr(entity, 'name') and entity.name:
            return entity.name
        if hasattr(entity, 'assemblyContext') and entity.assemblyContext:
            return entity.assemblyContext.name
        if hasattr(entity, 'parentComponent') and entity.parentComponent:
            return entity.parentComponent.name
        return str(entity)
    except:
        return "<Inconnu>"

def get_joint_type_info(joint_type_enum):
    """Traduit le type de liaison Fusion en identifiant textuel, libellé et DDL."""
    mapping = {
        adsk.fusion.JointTypes.RigidJointType: ("Rigid", "Rigide (Rigid)", 0),
        adsk.fusion.JointTypes.RevoluteJointType: ("Revolute", "Pivot (Revolute)", 1),
        adsk.fusion.JointTypes.SliderJointType: ("Slider", "Glissière (Slider)", 1),
        adsk.fusion.JointTypes.CylindricalJointType: ("Cylindrical", "Cylindrique (Cylindrical)", 2),
        adsk.fusion.JointTypes.PinSlotJointType: ("PinSlot", "Pivot glissant (Pin-Slot)", 2),
        adsk.fusion.JointTypes.PlanarJointType: ("Planar", "Plan sur plan (Planar)", 3),
        adsk.fusion.JointTypes.BallJointType: ("Ball", "Rotule sphérique (Ball)", 3)
    }
    return mapping.get(joint_type_enum, ("Unknown", "Inconnu / Non spécifié", -1))

def resolve_export_targets(doc_name, root_comp_name):
    """
    Identifie le sous-ensemble D-Bot actif et détermine les chemins de destination judicieux :
    1. Dans Exports_CAO_DBot/<sous_ensemble>/
    2. Dans Documentation/01_Mecanique_et_Chassis/<sous_ensemble>/
    """
    combined_name = f"{doc_name} {root_comp_name}".lower()
    
    if any(k in combined_name for k in ["torse", "bassin", "waist", "pelvis"]):
        sub_folder_cad = "01_Torse_et_Bassin"
        sub_folder_doc = "Torse_et_Bassin"
        base_filename = "AUDIT_CINEMATIQUE_Torse_et_Bassin.json"
    elif any(k in combined_name for k in ["bras", "epaule", "coude", "shoulder", "arm"]):
        sub_folder_cad = "03_Bras_et_Epaules"
        sub_folder_doc = "Bras_et_Mains"
        base_filename = "AUDIT_CINEMATIQUE_Bras_et_Epaules.json"
    elif any(k in combined_name for k in ["main", "dhand", "doigt", "hand"]):
        sub_folder_cad = "04_Mains_DHand"
        sub_folder_doc = "Bras_et_Mains"
        base_filename = "AUDIT_CINEMATIQUE_Mains_DHand.json"
    elif any(k in combined_name for k in ["jambe", "hanche", "pied", "genou", "leg", "foot"]):
        sub_folder_cad = "05_Jambes_et_Hanches"
        sub_folder_doc = "Jambes_et_Pieds"
        base_filename = "AUDIT_CINEMATIQUE_Jambes_et_Hanches.json"
    elif any(k in combined_name for k in ["tete", "cou", "head", "neck"]):
        sub_folder_cad = "02_Tete_et_Cou"
        sub_folder_doc = "Tete_et_Cou"
        base_filename = "AUDIT_CINEMATIQUE_Tete_et_Cou.json"
    else:
        sub_folder_cad = "00_Robot_Complet"
        sub_folder_doc = "Torse_et_Bassin"
        clean_name = sanitize_filename(root_comp_name)
        base_filename = f"AUDIT_CINEMATIQUE_{clean_name}.json"

    targets = []
    
    # Cible 1 : Référentiel Exports_CAO_DBot
    cad_base = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot"
    cad_dir = os.path.join(cad_base, sub_folder_cad)
    targets.append(os.path.join(cad_dir, base_filename))
    
    # Cible 2 : Référentiel Documentation / 01_Mecanique_et_Chassis
    doc_base = "/Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis"
    doc_dir = os.path.join(doc_base, sub_folder_doc)
    targets.append(os.path.join(doc_dir, base_filename))

    return targets, base_filename

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            if ui:
                ui.messageBox("Veuillez ouvrir un document Fusion 360 actif avant d'exécuter ce script.", "Audit Cinématique")
            return
            
        root_comp = design.rootComponent
        doc_name = app.activeDocument.name
        
        # --- 1. COMPOSANTS FIXÉS AU BÂTI (GROUNDED) ---
        grounded_components = []
        grounded_set = set()
        for occ in root_comp.allOccurrences:
            try:
                if occ.isGrounded:
                    o_name = occ.name
                    grounded_set.add(o_name)
                    grounded_components.append({
                        "occurrence_name": o_name,
                        "full_path": getattr(occ, 'fullPathName', o_name),
                        "is_grounded": True
                    })
            except:
                pass

        # --- 2. EXTRACTION DES LIAISONS STANDARDS (JOINTS) ---
        joints_data = []
        pair_constraint_map = {}
        blocking_joints_summary = []
        
        # Récupération de tous les joints
        all_joints_list = []
        try:
            for j in root_comp.allJoints:
                all_joints_list.append(j)
        except:
            for comp in design.allComponents:
                for j in comp.joints:
                    all_joints_list.append(j)

        for idx, joint in enumerate(all_joints_list, start=1):
            try:
                j_name = joint.name
                is_suppressed = getattr(joint, 'isSuppressed', False)
                is_locked = getattr(joint, 'isLocked', False)
                health = getattr(joint, 'healthState', 0)
                
                tl_idx = joint.timelineObject.index if joint.timelineObject else idx
                
                occ1 = getattr(joint, 'occurrenceOne', None)
                occ2 = getattr(joint, 'occurrenceTwo', None)
                n1 = safe_name(occ1)
                n2 = safe_name(occ2)
                
                occ1_grounded = n1 in grounded_set
                occ2_grounded = n2 in grounded_set
                
                # Traçage des paires pour identifier les surcontraintes
                pair_key = tuple(sorted([n1, n2]))
                pair_constraint_map[pair_key] = pair_constraint_map.get(pair_key, 0) + 1
                
                motion = getattr(joint, 'jointMotion', None)
                motion_key, motion_label, dof_count = ("Indeterminate", "Indéterminé", -1)
                
                limits_obj = {
                    "has_limits": False,
                    "unit": "",
                    "min": None,
                    "max": None,
                    "range": None,
                    "rest": None,
                    "is_zero_range": False
                }
                
                if motion:
                    motion_key, motion_label, dof_count = get_joint_type_info(motion.jointType)
                    
                    if motion.jointType == adsk.fusion.JointTypes.RevoluteJointType:
                        rev_motion = adsk.fusion.RevoluteJointMotion.cast(motion)
                        if rev_motion:
                            limits = rev_motion.rotationLimits
                            if limits and (limits.isMinimumValueEnabled or limits.isMaximumValueEnabled):
                                min_deg = limits.minimumValue * (180.0 / math.pi) if limits.isMinimumValueEnabled else None
                                max_deg = limits.maximumValue * (180.0 / math.pi) if limits.isMaximumValueEnabled else None
                                span_deg = (max_deg - min_deg) if (min_deg is not None and max_deg is not None) else None
                                is_zero = (span_deg is not None and abs(span_deg) < 1e-4)
                                rest_deg = limits.restValue * (180.0 / math.pi) if limits.isRestValueEnabled else None
                                
                                limits_obj = {
                                    "has_limits": True,
                                    "unit": "deg",
                                    "min": round(min_deg, 3) if min_deg is not None else None,
                                    "max": round(max_deg, 3) if max_deg is not None else None,
                                    "range": round(span_deg, 3) if span_deg is not None else None,
                                    "rest": round(rest_deg, 3) if rest_deg is not None else None,
                                    "is_zero_range": is_zero
                                }
                                
                    elif motion.jointType == adsk.fusion.JointTypes.SliderJointType:
                        slide_motion = adsk.fusion.SliderJointMotion.cast(motion)
                        if slide_motion:
                            limits = slide_motion.slideLimits
                            if limits and (limits.isMinimumValueEnabled or limits.isMaximumValueEnabled):
                                min_mm = limits.minimumValue * 10.0 if limits.isMinimumValueEnabled else None
                                max_mm = limits.maximumValue * 10.0 if limits.isMaximumValueEnabled else None
                                span_mm = (max_mm - min_mm) if (min_mm is not None and max_mm is not None) else None
                                is_zero = (span_mm is not None and abs(span_mm) < 1e-4)
                                rest_mm = limits.restValue * 10.0 if limits.isRestValueEnabled else None
                                
                                limits_obj = {
                                    "has_limits": True,
                                    "unit": "mm",
                                    "min": round(min_mm, 3) if min_mm is not None else None,
                                    "max": round(max_mm, 3) if max_mm is not None else None,
                                    "range": round(span_mm, 3) if span_mm is not None else None,
                                    "rest": round(rest_mm, 3) if rest_mm is not None else None,
                                    "is_zero_range": is_zero
                                }

                # Extraction de l'alignement et des décalages (Offsets et Angle)
                alignment_obj = {
                    "is_flipped": False,
                    "has_offset": False,
                    "angle_deg": 0.0,
                    "angle_expression": "0 deg",
                    "offset_mm": 0.0,
                    "offset_expression": "0 mm"
                }
                try:
                    if hasattr(joint, 'isFlipped'):
                        alignment_obj["is_flipped"] = bool(joint.isFlipped)
                except:
                    pass
                try:
                    if hasattr(joint, 'angle') and joint.angle:
                        ang_val = joint.angle.value * (180.0 / math.pi)
                        alignment_obj["angle_deg"] = round(ang_val, 3)
                        alignment_obj["angle_expression"] = str(joint.angle.expression)
                        if abs(ang_val) > 1e-4:
                            alignment_obj["has_offset"] = True
                except:
                    pass
                try:
                    if hasattr(joint, 'offset') and joint.offset:
                        off_val = joint.offset.value * 10.0
                        alignment_obj["offset_mm"] = round(off_val, 3)
                        alignment_obj["offset_expression"] = str(joint.offset.expression)
                        if abs(off_val) > 1e-4:
                            alignment_obj["has_offset"] = True
                except:
                    pass

                # Diagnostic de blocage
                block_reasons = []
                is_blocking = False
                
                if is_suppressed:
                    status_label = "INACTIF (Supprimé / Suppressed)"
                elif is_locked:
                    is_blocking = True
                    status_label = "BLOQUÉ (Liaison Verrouillée manuellement)"
                    block_reasons.append("Verrouillage manuel actif (isLocked = True)")
                elif dof_count == 0:
                    is_blocking = True
                    status_label = "BLOQUÉ (Liaison Rigide / 0 DDL)"
                    block_reasons.append("Type Rigide : supprime les 6 degrés de liberté relatifs")
                elif limits_obj["is_zero_range"]:
                    is_blocking = True
                    status_label = "BLOQUÉ (Course nulle / Butées Min == Max)"
                    block_reasons.append(f"Butées de course identiques ({limits_obj['min']} {limits_obj['unit']}) : débattement nul")
                else:
                    status_label = f"MOBILE ({dof_count} DDL libre(s))"
                    
                if occ1_grounded and occ2_grounded and not is_suppressed:
                    is_blocking = True
                    block_reasons.append("Les deux pièces reliées sont ancrées au sol (Grounded) : mouvement relatif impossible")
                    status_label = "BLOQUÉ (Double ancrage Bâti)"
                    
                if is_blocking:
                    blocking_joints_summary.append({
                        "id": idx,
                        "name": j_name,
                        "category": "Joint Standard",
                        "motion_type": motion_key,
                        "part_one": n1,
                        "part_two": n2,
                        "status": status_label,
                        "reasons": block_reasons
                    })
                    
                joints_data.append({
                    "id": idx,
                    "timeline_index": tl_idx,
                    "name": j_name,
                    "category": "Joint Standard",
                    "motion_type": motion_key,
                    "motion_type_label": motion_label,
                    "degrees_of_freedom": dof_count,
                    "is_suppressed": is_suppressed,
                    "is_locked": is_locked,
                    "health_state": health,
                    "part_one": {
                        "name": n1,
                        "is_grounded": occ1_grounded
                    },
                    "part_two": {
                        "name": n2,
                        "is_grounded": occ2_grounded
                    },
                    "limits": limits_obj,
                    "alignment": alignment_obj,
                    "diagnostic": {
                        "is_blocking": is_blocking,
                        "status_label": status_label,
                        "block_reasons": block_reasons
                    }
                })
            except Exception as e_j:
                joints_data.append({
                    "id": idx,
                    "name": getattr(joint, 'name', f"Joint_{idx}"),
                    "error": str(e_j)
                })

        # --- 3. EXTRACTION DES LIAISONS AS-BUILT ---
        as_built_data = []
        all_abj_list = []
        try:
            for abj in root_comp.allAsBuiltJoints:
                all_abj_list.append(abj)
        except:
            for comp in design.allComponents:
                for abj in comp.asBuiltJoints:
                    all_abj_list.append(abj)

        for idx, abj in enumerate(all_abj_list, start=1):
            try:
                j_name = abj.name
                is_suppressed = getattr(abj, 'isSuppressed', False)
                is_locked = getattr(abj, 'isLocked', False)
                health = getattr(abj, 'healthState', 0)
                tl_idx = abj.timelineObject.index if abj.timelineObject else idx
                
                occ1 = getattr(abj, 'occurrenceOne', None)
                occ2 = getattr(abj, 'occurrenceTwo', None)
                n1 = safe_name(occ1)
                n2 = safe_name(occ2)
                
                occ1_grounded = n1 in grounded_set
                occ2_grounded = n2 in grounded_set
                
                pair_key = tuple(sorted([n1, n2]))
                pair_constraint_map[pair_key] = pair_constraint_map.get(pair_key, 0) + 1
                
                motion = getattr(abj, 'jointMotion', None)
                motion_key, motion_label, dof_count = ("Indeterminate", "Indéterminé", -1)
                if motion:
                    motion_key, motion_label, dof_count = get_joint_type_info(motion.jointType)
                    
                block_reasons = []
                is_blocking = False
                
                if is_suppressed:
                    status_label = "INACTIF (Supprimé / Suppressed)"
                elif is_locked:
                    is_blocking = True
                    status_label = "BLOQUÉ (Liaison Verrouillée manuellement)"
                    block_reasons.append("Verrouillage manuel actif (isLocked = True)")
                elif dof_count == 0:
                    is_blocking = True
                    status_label = "BLOQUÉ (Liaison Rigide / 0 DDL)"
                    block_reasons.append("Type Rigide As-Built : verrouille la géométrie telle quelle")
                else:
                    status_label = f"MOBILE ({dof_count} DDL libre(s))"
                    
                if occ1_grounded and occ2_grounded and not is_suppressed:
                    is_blocking = True
                    block_reasons.append("Les deux pièces reliées sont ancrées au sol (Grounded)")
                    status_label = "BLOQUÉ (Double ancrage Bâti)"
                    
                if is_blocking:
                    blocking_joints_summary.append({
                        "id": idx,
                        "name": j_name,
                        "category": "As-Built Joint",
                        "motion_type": motion_key,
                        "part_one": n1,
                        "part_two": n2,
                        "status": status_label,
                        "reasons": block_reasons
                    })

                as_built_data.append({
                    "id": idx,
                    "timeline_index": tl_idx,
                    "name": j_name,
                    "category": "As-Built Joint",
                    "motion_type": motion_key,
                    "motion_type_label": motion_label,
                    "degrees_of_freedom": dof_count,
                    "is_suppressed": is_suppressed,
                    "is_locked": is_locked,
                    "health_state": health,
                    "part_one": {
                        "name": n1,
                        "is_grounded": occ1_grounded
                    },
                    "part_two": {
                        "name": n2,
                        "is_grounded": occ2_grounded
                    },
                    "diagnostic": {
                        "is_blocking": is_blocking,
                        "status_label": status_label,
                        "block_reasons": block_reasons
                    }
                })
            except Exception as e_abj:
                as_built_data.append({
                    "id": idx,
                    "name": getattr(abj, 'name', f"AsBuilt_{idx}"),
                    "error": str(e_abj)
                })

        # --- 4. EXTRACTION DES GROUPES RIGIDES (RIGID GROUPS) ---
        rigid_groups_data = []
        try:
            for idx, rg in enumerate(root_comp.rigidGroups, start=1):
                members = [safe_name(m) for m in rg.occurrences]
                rigid_groups_data.append({
                    "id": idx,
                    "name": rg.name,
                    "is_suppressed": rg.isSuppressed,
                    "members_count": len(members),
                    "members": members,
                    "diagnostic": "INACTIF" if rg.isSuppressed else f"BLOQUE_ENSEMBLE ({len(members)} composants solidaires)"
                })
        except:
            pass

        # --- 5. EXTRACTION DES MOTION LINKS ---
        motion_links_data = []
        try:
            for idx, ml in enumerate(root_comp.motionLinks, start=1):
                motion_links_data.append({
                    "id": idx,
                    "name": ml.name,
                    "is_suppressed": ml.isSuppressed,
                    "joint_one": safe_name(ml.jointOne),
                    "joint_two": safe_name(ml.jointTwo),
                    "status": "INACTIF" if ml.isSuppressed else "ACTIF"
                })
        except:
            pass

        # --- 6. IDENTIFICATION DES SURCONTRAINTES / PAIRES REDONDANTES ---
        redundant_pairs = []
        for pair, count in pair_constraint_map.items():
            if count > 1 and pair[0] != pair[1]:
                redundant_pairs.append({
                    "part_one": pair[0],
                    "part_two": pair[1],
                    "simultaneous_constraints_count": count,
                    "warning": f"{count} liaisons relient directement cette même paire de composants"
                })

        # --- BILAN STATISTIQUE GLOBAL ---
        total_joints = len(joints_data)
        total_abj = len(as_built_data)
        total_rg = len(rigid_groups_data)
        
        blocked_joints = sum(1 for j in joints_data if j.get("diagnostic", {}).get("is_blocking", False))
        blocked_abj = sum(1 for j in as_built_data if j.get("diagnostic", {}).get("is_blocking", False))
        mobile_joints = sum(1 for j in joints_data if not j.get("diagnostic", {}).get("is_blocking", False) and not j.get("is_suppressed", False))
        mobile_abj = sum(1 for j in as_built_data if not j.get("diagnostic", {}).get("is_blocking", False) and not j.get("is_suppressed", False))

        # --- STRUCTURATION DU MANIFESTE JSON COMPLET ---
        export_targets, base_filename = resolve_export_targets(doc_name, root_comp.name)
        
        manifest_data = {
            "metadata": {
                "audit_type": "AUDIT_CINEMATIQUE_ET_BLOCAGES",
                "document_name": doc_name,
                "root_component": root_comp.name,
                "timestamp": datetime.now().isoformat(),
                "fusion_version": app.version,
                "units": {
                    "length": "mm",
                    "angle": "deg"
                },
                "target_filename": base_filename,
                "written_paths": []
            },
            "summary": {
                "total_constraints_analyzed": total_joints + total_abj + total_rg,
                "total_joints": total_joints,
                "blocked_joints_count": blocked_joints,
                "mobile_joints_count": mobile_joints,
                "total_as_built_joints": total_abj,
                "blocked_as_built_count": blocked_abj,
                "mobile_as_built_count": mobile_abj,
                "total_rigid_groups": total_rg,
                "grounded_components_count": len(grounded_components),
                "redundant_pairs_count": len(redundant_pairs)
            },
            "diagnostics": {
                "critical_blockages": blocking_joints_summary,
                "grounded_anchors": list(grounded_set),
                "redundant_kinematic_conflicts": redundant_pairs
            },
            "grounded_components": grounded_components,
            "rigid_groups": rigid_groups_data,
            "redundant_pairs": redundant_pairs,
            "joints": joints_data,
            "as_built_joints": as_built_data,
            "motion_links": motion_links_data
        }

        # --- SAUVEGARDE EN JSON DANS LES EMPLACEMENTS JUDICIEUX ---
        successful_paths = []
        for target_path in export_targets:
            try:
                target_dir = os.path.dirname(target_path)
                os.makedirs(target_dir, exist_ok=True)
                with open(target_path, "w", encoding="utf-8") as f:
                    manifest_data["metadata"]["written_paths"].append(target_path)
                    json.dump(manifest_data, f, indent=2, ensure_ascii=False)
                successful_paths.append(target_path)
            except Exception as e_write:
                pass

        # Fallback de secours sur le Bureau si aucun dossier n'a pu être écrit
        if not successful_paths:
            fallback_path = os.path.expanduser(f"~/Desktop/{base_filename}")
            with open(fallback_path, "w", encoding="utf-8") as f:
                json.dump(manifest_data, f, indent=2, ensure_ascii=False)
            successful_paths.append(fallback_path)

        # Message de confirmation interactif dans Fusion 360
        paths_str = "\n".join([f"• {p}" for p in successful_paths])
        ui_msg = (
            f"✅ AUDIT CINÉMATIQUE JSON EXPORTÉ AVEC SUCCÈS !\n\n"
            f"Modèle analysé : {root_comp.name}\n"
            f"• Liaisons Standards (Joints) : {total_joints} (dont {blocked_joints} bloquantes)\n"
            f"• Liaisons As-Built           : {total_abj} (dont {blocked_abj} bloquantes)\n"
            f"• Groupes Rigides             : {total_rg}\n"
            f"• Pièces ancrées (Grounded)   : {len(grounded_components)}\n"
            f"• Surcontraintes potentielles : {len(redundant_pairs)}\n\n"
            f"📁 Emplacements d'enregistrement judicieux :\n{paths_str}"
        )
        if ui:
            ui.messageBox(ui_msg, "Audit Cinématique & Diagnostic des Blocages")

    except Exception as e:
        if ui:
            ui.messageBox(f"Erreur durant l'extraction cinématique JSON :\n{traceback.format_exc()}", "Erreur KinematicBlockageExtractor")

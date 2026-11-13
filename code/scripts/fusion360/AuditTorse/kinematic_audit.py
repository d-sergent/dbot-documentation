# -*- coding: utf-8 -*-
"""
kinematic_audit.py — Sous-module d'extraction cinématique unifiée pour AuditTorse (Fusion 360)
Projet : Robot Humanoïde D-Bot V1
=================================================================================================
Inspecte l'ensemble des liaisons (Joints, AsBuiltJoints), groupes rigides (RigidGroups),
contraintes d'assemblage et liens cinématiques (MotionLinks) du modèle actif, identifie les
degrés de liberté effectifs ainsi que les blocages éventuels, et écrit le rapport JSON
`AUDIT_CINEMATIQUE_<SousEnsemble>.json`.
"""

import adsk.fusion
import json
import math
import os
from datetime import datetime


MOTION_TYPE_MAP = {
    adsk.fusion.JointTypes.RigidJointType: ("Rigid", "Rigide (Rigid)", 0),
    adsk.fusion.JointTypes.RevoluteJointType: ("Revolute", "Pivot / Révolution (Revolute)", 1),
    adsk.fusion.JointTypes.SliderJointType: ("Slider", "Glissière (Slider)", 1),
    adsk.fusion.JointTypes.CylindricalJointType: ("Cylindrical", "Pivot Glissant (Cylindrical)", 2),
    adsk.fusion.JointTypes.PinSlotJointType: ("PinSlot", "Doigt dans Rainure (Pin-Slot)", 2),
    adsk.fusion.JointTypes.PlanarJointType: ("Planar", "Appui Plan (Planar)", 3),
    adsk.fusion.JointTypes.BallJointType: ("Ball", "Rotule (Ball)", 3),
}


def _safe_occ_info(occ):
    """Retourne le nom et l'état Grounded d'une occurrence Fusion 360."""
    if not occ:
        return {"name": "Root / Inconnu", "is_grounded": False}
    try:
        return {
            "name": occ.name,
            "is_grounded": bool(getattr(occ, "isGrounded", False)),
        }
    except Exception:
        return {"name": "Inconnu", "is_grounded": False}


def _safe_timeline_index(entity):
    """Récupère l'index dans la timeline Fusion 360 sans lever d'exception."""
    try:
        tl_obj = getattr(entity, "timelineObject", None)
        if tl_obj is not None:
            return tl_obj.index
    except Exception:
        pass
    return None


def _extract_limit_block(lim_obj, is_angle):
    """Extrait min/max/rest/range d'un objet JointLimits en deg ou mm."""
    if not lim_obj:
        return {
            "has_limits": False,
            "unit": "deg" if is_angle else "mm",
            "min": None,
            "max": None,
            "range": None,
            "rest": None,
            "is_zero_range": False,
        }

    scale_fn = math.degrees if is_angle else (lambda v: v * 10.0)
    unit = "deg" if is_angle else "mm"

    try:
        min_en = bool(getattr(lim_obj, "isMinimumValueEnabled", False))
        max_en = bool(getattr(lim_obj, "isMaximumValueEnabled", False))
        rest_en = bool(getattr(lim_obj, "isRestValueEnabled", False))

        min_val = round(scale_fn(lim_obj.minimumValue), 3) if min_en else None
        max_val = round(scale_fn(lim_obj.maximumValue), 3) if max_en else None
        rest_val = round(scale_fn(lim_obj.restValue), 3) if rest_en else None

        has_limits = min_en or max_en
        rng = None
        is_zero_range = False
        if min_val is not None and max_val is not None:
            rng = round(max_val - min_val, 3)
            is_zero_range = abs(rng) < 1e-3

        return {
            "has_limits": has_limits,
            "unit": unit,
            "min": min_val,
            "max": max_val,
            "range": rng,
            "rest": rest_val,
            "is_zero_range": is_zero_range,
        }
    except Exception:
        return {
            "has_limits": False,
            "unit": unit,
            "min": None,
            "max": None,
            "range": None,
            "rest": None,
            "is_zero_range": False,
        }


def _extract_joint_limits(motion, motion_code):
    """Extrait les limites primaires (et secondaires le cas échéant) d'un JointMotion."""
    empty_limits = {
        "has_limits": False,
        "unit": "",
        "min": None,
        "max": None,
        "range": None,
        "rest": None,
        "is_zero_range": False,
    }
    if not motion or motion_code == "Rigid":
        return empty_limits, None

    primary = empty_limits
    secondary = None

    if motion_code in ("Revolute", "Cylindrical", "PinSlot"):
        rot_lim = getattr(motion, "rotationLimits", None)
        if rot_lim is not None:
            primary = _extract_limit_block(rot_lim, is_angle=True)
        if motion_code in ("Cylindrical", "PinSlot"):
            slide_lim = getattr(motion, "slideLimits", None)
            if slide_lim is not None:
                secondary = _extract_limit_block(slide_lim, is_angle=False)
    elif motion_code == "Slider":
        slide_lim = getattr(motion, "slideLimits", None)
        if slide_lim is not None:
            primary = _extract_limit_block(slide_lim, is_angle=False)

    return primary, secondary


def _extract_joint_alignment(joint):
    """Extrait angle/offset/isFlipped d'un Joint standard."""
    is_flipped = False
    angle_deg = 0.0
    angle_expr = "0.0 deg"
    offset_mm = 0.0
    offset_expr = "0.00 mm"

    try:
        is_flipped = bool(getattr(joint, "isFlipped", False))
    except Exception:
        pass

    try:
        ang_param = getattr(joint, "angle", None)
        if ang_param is not None:
            angle_deg = round(math.degrees(ang_param.value), 3)
            angle_expr = getattr(ang_param, "expression", None) or f"{angle_deg} deg"
    except Exception:
        pass

    try:
        off_param = getattr(joint, "offset", None)
        if off_param is not None:
            offset_mm = round(off_param.value * 10.0, 3)
            offset_expr = getattr(off_param, "expression", None) or f"{offset_mm} mm"
    except Exception:
        pass

    has_offset = abs(angle_deg) > 1e-4 or abs(offset_mm) > 1e-4
    return {
        "is_flipped": is_flipped,
        "has_offset": has_offset,
        "angle_deg": angle_deg,
        "angle_expression": angle_expr,
        "offset_mm": offset_mm,
        "offset_expression": offset_expr,
    }


def _diagnose_joint(motion_code, dof, is_suppressed, is_locked, health_state,
                    part_one, part_two, limits, secondary_limits, is_as_built,
                    in_rigid_group_pair):
    """Construit le diagnostic de mobilité ou de blocage d'une liaison."""
    reasons = []
    if motion_code == "Rigid" or dof == 0:
        if is_as_built:
            reasons.append("Type Rigide As-Built : verrouille la géométrie telle quelle")
        else:
            reasons.append("Type Rigide : supprime les 6 degrés de liberté relatifs")
    if is_suppressed:
        reasons.append("Liaison désactivée / supprimée dans la timeline (isSuppressed = True)")
    if is_locked:
        reasons.append("Liaison verrouillée manuellement (isLocked = True)")
    if health_state != 0:
        reasons.append(f"Anomalie ou conflit solveur Fusion 360 (healthState = {health_state})")
    if part_one["is_grounded"] and part_two["is_grounded"]:
        reasons.append("Double ancrage Grounded simultané sur les deux pièces")
    if limits.get("is_zero_range"):
        reasons.append("Plage de butées primaires nulle (min == max)")
    if secondary_limits and secondary_limits.get("is_zero_range"):
        reasons.append("Plage de butées secondaires nulle (min == max)")
    if in_rigid_group_pair and dof > 0:
        reasons.append("Surcontrainte probable : les deux occurrences appartiennent au même RigidGroup actif")

    is_blocking = len(reasons) > 0
    if motion_code == "Rigid" or dof == 0:
        status_label = "BLOQUÉ (Liaison Rigide / 0 DDL)"
    elif is_blocking:
        status_label = f"BLOQUÉ / ANOMALIE ({motion_code} / {dof} DDL nominaux)"
    else:
        status_label = f"LIBRE / ACTIF ({motion_code} / {dof} DDL)"

    return {
        "is_blocking": is_blocking,
        "status_label": status_label,
        "block_reasons": reasons,
    }


def _collect_rigid_groups(design):
    """Collecte les RigidGroups actifs et l'index des paires d'occurrences liées."""
    rigid_groups = []
    pair_set = set()
    seen_tokens = set()

    for comp in design.allComponents:
        rgs = getattr(comp, "rigidGroups", None)
        if not rgs:
            continue
        for rg in rgs:
            try:
                tok = getattr(rg, "entityToken", None)
                if tok and tok in seen_tokens:
                    continue
                if tok:
                    seen_tokens.add(tok)

                is_supp = bool(getattr(rg, "isSuppressed", False))
                occ_names = []
                occ_tokens = []
                occs = getattr(rg, "occurrences", None)
                if occs:
                    for o in occs:
                        occ_names.append(o.name)
                        otok = getattr(o, "entityToken", None) or o.name
                        occ_tokens.append(otok)

                if not is_supp and len(occ_tokens) >= 2:
                    for i in range(len(occ_tokens)):
                        for j in range(i + 1, len(occ_tokens)):
                            a, b = occ_tokens[i], occ_tokens[j]
                            pair_set.add((a, b) if a <= b else (b, a))

                rigid_groups.append({
                    "name": rg.name,
                    "component": comp.name,
                    "timeline_index": _safe_timeline_index(rg),
                    "is_suppressed": is_supp,
                    "occurrence_count": len(occ_names),
                    "occurrences": occ_names[:30],
                })
            except Exception:
                continue

    return rigid_groups, pair_set


def _collect_assembly_constraints(design):
    """Inspecte les AssemblyConstraints (santé du solveur)."""
    constraints = []
    seen_tokens = set()

    for comp in design.allComponents:
        ac_list = getattr(comp, "assemblyConstraints", None)
        if not ac_list:
            continue
        for i in range(ac_list.count):
            try:
                c = ac_list.item(i)
                tok = getattr(c, "entityToken", None)
                if tok and tok in seen_tokens:
                    continue
                if tok:
                    seen_tokens.add(tok)
                health = int(getattr(c, "healthState", 0))
                is_valid = bool(getattr(c, "isValid", True))
                constraints.append({
                    "name": getattr(c, "name", f"Constraint_{i}"),
                    "component": comp.name,
                    "timeline_index": _safe_timeline_index(c),
                    "health_state": health,
                    "is_valid": is_valid,
                })
            except Exception:
                continue

    return constraints


def _collect_motion_links(root_comp):
    """Collecte les MotionLinks de couplage cinématique."""
    links = []
    ml_col = getattr(root_comp, "motionLinks", None)
    if not ml_col:
        return links
    for ml in ml_col:
        try:
            j1 = getattr(ml, "jointOne", None)
            j2 = getattr(ml, "jointTwo", None)
            links.append({
                "name": getattr(ml, "name", "MotionLink"),
                "joint_one": j1.name if j1 else None,
                "joint_two": j2.name if j2 else None,
                "is_suppressed": bool(getattr(ml, "isSuppressed", False)),
                "is_reversed": bool(getattr(ml, "isReversed", False)),
            })
        except Exception:
            continue
    return links


def run_kinematic_audit(app, design, root_comp, doc_name, sub_label, target_json_paths):
    """Exécute l'audit cinématique complet et écrit les fichiers JSON cibles."""
    rigid_groups, rigid_pair_set = _collect_rigid_groups(design)
    assembly_constraints = _collect_assembly_constraints(design)
    motion_links = _collect_motion_links(root_comp)

    joints_list = []
    as_built_list = []
    mobile_overview = []
    seen_joint_tokens = set()
    seen_abj_tokens = set()

    j_counter = 0
    abj_counter = 0

    for comp in design.allComponents:
        # 1. Joints standards
        for j in getattr(comp, "joints", []):
            try:
                tok = getattr(j, "entityToken", None)
                if tok and tok in seen_joint_tokens:
                    continue
                if tok:
                    seen_joint_tokens.add(tok)
                j_counter += 1

                motion = getattr(j, "jointMotion", None)
                jtype = getattr(motion, "jointType", None) if motion else None
                motion_code, motion_label, dof = MOTION_TYPE_MAP.get(
                    jtype, ("Unknown", "Inconnu (Unknown)", 0)
                )

                is_supp = bool(getattr(j, "isSuppressed", False))
                is_locked = bool(getattr(j, "isLocked", False))
                health_state = int(getattr(j, "healthState", 0))

                occ1 = getattr(j, "occurrenceOne", None)
                occ2 = getattr(j, "occurrenceTwo", None)
                part_one = _safe_occ_info(occ1)
                part_two = _safe_occ_info(occ2)

                in_rg_pair = False
                if occ1 and occ2:
                    t1 = getattr(occ1, "entityToken", None) or occ1.name
                    t2 = getattr(occ2, "entityToken", None) or occ2.name
                    pair = (t1, t2) if t1 <= t2 else (t2, t1)
                    in_rg_pair = pair in rigid_pair_set

                limits, secondary_limits = _extract_joint_limits(motion, motion_code)
                alignment = _extract_joint_alignment(j)
                diag = _diagnose_joint(
                    motion_code, dof, is_supp, is_locked, health_state,
                    part_one, part_two, limits, secondary_limits, False, in_rg_pair
                )

                entry = {
                    "id": j_counter,
                    "timeline_index": _safe_timeline_index(j),
                    "name": j.name,
                    "category": "Joint Standard",
                    "motion_type": motion_code,
                    "motion_type_label": motion_label,
                    "degrees_of_freedom": dof,
                    "is_suppressed": is_supp,
                    "is_locked": is_locked,
                    "health_state": health_state,
                    "part_one": part_one,
                    "part_two": part_two,
                    "limits": limits,
                    "alignment": alignment,
                    "diagnostic": diag,
                }
                if secondary_limits is not None:
                    entry["secondary_limits"] = secondary_limits
                joints_list.append(entry)

                if dof > 0:
                    mobile_overview.append({
                        "category": "Joint Standard",
                        "name": j.name,
                        "motion_type": motion_code,
                        "degrees_of_freedom": dof,
                        "part_one": part_one["name"],
                        "part_two": part_two["name"],
                        "limits": limits,
                        "is_locked": is_locked,
                        "is_suppressed": is_supp,
                        "health_state": health_state,
                        "status_label": diag["status_label"],
                        "block_reasons": diag["block_reasons"],
                    })
            except Exception:
                continue

        # 2. As-Built Joints
        for abj in getattr(comp, "asBuiltJoints", []):
            try:
                tok = getattr(abj, "entityToken", None)
                if tok and tok in seen_abj_tokens:
                    continue
                if tok:
                    seen_abj_tokens.add(tok)
                abj_counter += 1

                motion = getattr(abj, "jointMotion", None)
                jtype = getattr(motion, "jointType", None) if motion else None
                motion_code, motion_label, dof = MOTION_TYPE_MAP.get(
                    jtype, ("Unknown", "Inconnu (Unknown)", 0)
                )

                is_supp = bool(getattr(abj, "isSuppressed", False))
                is_locked = bool(getattr(abj, "isLocked", False))
                health_state = int(getattr(abj, "healthState", 0))

                occ1 = getattr(abj, "occurrenceOne", None)
                occ2 = getattr(abj, "occurrenceTwo", None)
                part_one = _safe_occ_info(occ1)
                part_two = _safe_occ_info(occ2)

                in_rg_pair = False
                if occ1 and occ2:
                    t1 = getattr(occ1, "entityToken", None) or occ1.name
                    t2 = getattr(occ2, "entityToken", None) or occ2.name
                    pair = (t1, t2) if t1 <= t2 else (t2, t1)
                    in_rg_pair = pair in rigid_pair_set

                limits, secondary_limits = _extract_joint_limits(motion, motion_code)
                diag = _diagnose_joint(
                    motion_code, dof, is_supp, is_locked, health_state,
                    part_one, part_two, limits, secondary_limits, True, in_rg_pair
                )

                entry = {
                    "id": abj_counter,
                    "timeline_index": _safe_timeline_index(abj),
                    "name": abj.name,
                    "category": "As-Built Joint",
                    "motion_type": motion_code,
                    "motion_type_label": motion_label,
                    "degrees_of_freedom": dof,
                    "is_suppressed": is_supp,
                    "is_locked": is_locked,
                    "health_state": health_state,
                    "part_one": part_one,
                    "part_two": part_two,
                    "diagnostic": diag,
                }
                if dof > 0:
                    entry["limits"] = limits
                if secondary_limits is not None:
                    entry["secondary_limits"] = secondary_limits
                as_built_list.append(entry)

                if dof > 0:
                    mobile_overview.append({
                        "category": "As-Built Joint",
                        "name": abj.name,
                        "motion_type": motion_code,
                        "degrees_of_freedom": dof,
                        "part_one": part_one["name"],
                        "part_two": part_two["name"],
                        "limits": limits,
                        "is_locked": is_locked,
                        "is_suppressed": is_supp,
                        "health_state": health_state,
                        "status_label": diag["status_label"],
                        "block_reasons": diag["block_reasons"],
                    })
            except Exception:
                continue

    all_joint_entries = joints_list + as_built_list
    health_warnings = sum(1 for e in all_joint_entries if e["health_state"] != 0)
    broken_constraints = sum(
        1 for c in assembly_constraints if c["health_state"] != 0 or not c["is_valid"]
    )
    active_mobile_count = sum(
        1 for m in mobile_overview if not m["block_reasons"]
    )
    blocked_mobile_count = sum(
        1 for m in mobile_overview if m["block_reasons"]
    )

    kinematic_data = {
        "metadata": {
            "document_name": doc_name,
            "subassembly": sub_label,
            "timestamp": datetime.now().isoformat(),
            "generator": "AuditTorse (kinematic_audit.py)",
            "units": {"angle": "deg", "length": "mm"},
        },
        "summary": {
            "total_joints": len(joints_list),
            "total_as_built_joints": len(as_built_list),
            "total_rigid_groups": len(rigid_groups),
            "total_assembly_constraints": len(assembly_constraints),
            "broken_assembly_constraints": broken_constraints,
            "total_motion_links": len(motion_links),
            "mobile_joints_total": len(mobile_overview),
            "mobile_joints_active": active_mobile_count,
            "mobile_joints_blocked": blocked_mobile_count,
            "health_warnings": health_warnings,
            "mobile_joints_overview": mobile_overview,
        },
        "joints": joints_list,
        "as_built_joints": as_built_list,
        "rigid_groups": rigid_groups,
        "assembly_constraints": assembly_constraints,
        "motion_links": motion_links,
    }

    payload = json.dumps(kinematic_data, indent=2, ensure_ascii=False)
    saved_paths = []
    errors = []
    for out_path in target_json_paths:
        try:
            parent_dir = os.path.dirname(out_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(payload)
            saved_paths.append(out_path)
        except Exception as err:
            errors.append(f"{out_path}: {err}")

    return kinematic_data, saved_paths, errors


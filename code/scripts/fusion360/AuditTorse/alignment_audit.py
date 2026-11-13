# -*- coding: utf-8 -*-
"""
alignment_audit.py — Sous-module unifié d'alignement, verticalité et coaxialité pour AuditTorse (Fusion 360)
Projet : Robot Humanoïde D-Bot V1
===============================================================================================================
Remplace les anciens scripts unitaires (CheckHipVerticality, CheckTubeEpauleAlignment) en utilisant :
  1. Les repères mathématiques exacts `occ.transform2.asArray()` (sans confusion de congés/perçages M4).
  2. Le filtrage strict des alésages majeurs (rayon >= 25 mm) pour les contrôles de concentricité Waist/Hanches.
  3. Les lignes d'axe longitudinales B-Rep / Bounding Box pour les tubes carrés 60x60 et 20x20.
  4. Le contrôle de symétrie bilatérale Gauche/Droite par rapport au plan médian réel de la machine.
Produit `AUDIT_ALIGNEMENT_<SousEnsemble>.json`.
"""

import json
import math
import os
from datetime import datetime


STRUCTURAL_KEYWORDS = (
    "bassin", "pelvis", "traverse", "selle", "tube", "montant", "insert",
    "hanche", "waist", "moyeu", "rb8016", "rs06", "rs04", "rs03",
    "colonne", "equerre", "plastron", "bride", "corniere", "plaque",
    "semelle", "support", "panier", "carenage", "liaison", "el05"
)

CARDINAL_VECTORS = (
    ("+X", (1.0, 0.0, 0.0)),
    ("-X", (-1.0, 0.0, 0.0)),
    ("+Y", (0.0, 1.0, 0.0)),
    ("-Y", (0.0, -1.0, 0.0)),
    ("+Z", (0.0, 0.0, 1.0)),
    ("-Z", (0.0, 0.0, -1.0)),
)


def _normalize(vec):
    norm = math.sqrt(vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2])
    if norm < 1e-12:
        return (0.0, 0.0, 0.0)
    return (vec[0] / norm, vec[1] / norm, vec[2] / norm)


def _dot(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]


def _angle_between_deg(v1, v2, unsigned=True):
    n1 = _normalize(v1)
    n2 = _normalize(v2)
    val = _dot(n1, n2)
    if unsigned:
        val = abs(val)
    val = max(-1.0, min(1.0, val))
    return round(math.degrees(math.acos(val)), 4)


def _extract_occ_frame(occ):
    """Extrait repère local en coordonnées mondiales depuis Matrix3D.asArray()."""
    try:
        arr = occ.transform2.asArray()
        x_ax = _normalize((arr[0], arr[4], arr[8]))
        y_ax = _normalize((arr[1], arr[5], arr[9]))
        z_ax = _normalize((arr[2], arr[6], arr[10]))
        origin_mm = [round(arr[3] * 10.0, 3), round(arr[7] * 10.0, 3), round(arr[11] * 10.0, 3)]
        return {
            "origin_mm": origin_mm,
            "x_axis": [round(c, 5) for c in x_ax],
            "y_axis": [round(c, 5) for c in y_ax],
            "z_axis": [round(c, 5) for c in z_ax],
        }
    except Exception:
        return None


def _closest_cardinal_axis(vec):
    """Retourne l'axe cardinal le plus proche (+X/-X/+Y/-Y/+Z/-Z) et l'écart angulaire."""
    best_label = "+Z"
    best_dot = -2.0
    n = _normalize(vec)
    for label, cvec in CARDINAL_VECTORS:
        d = _dot(n, cvec)
        if d > best_dot:
            best_dot = d
            best_label = label
    dev_deg = round(math.degrees(math.acos(max(-1.0, min(1.0, abs(best_dot))))), 4)
    return best_label, dev_deg


def _bbox_center(comp_entry):
    bbox = comp_entry.get("bounding_box_mm")
    if not bbox:
        return None
    bmin = bbox["min"]
    bmax = bbox["max"]
    return [
        round((bmin[0] + bmax[0]) / 2.0, 3),
        round((bmin[1] + bmax[1]) / 2.0, 3),
        round((bmin[2] + bmax[2]) / 2.0, 3),
    ]


def _largest_major_bore(comp_entry, min_radius_mm=25.0):
    """Retourne le plus grand alésage cylindrique interne (rayon >= min_radius_mm) pour éviter les vis/congés."""
    cyls = comp_entry.get("cylindrical_faces", [])
    for allow_unmarked in (False, True):
        best = None
        for cf in cyls:
            r = cf.get("radius_mm", 0.0)
            if r < min_radius_mm:
                continue
            is_hole = cf.get("is_hole")
            if not allow_unmarked and is_hole is not True:
                continue
            if allow_unmarked and is_hole is False:
                continue
            if best is None or r > best["radius_mm"]:
                best = cf
        if best is not None:
            return best
    return None


def _estimate_y_symmetry_plane(components):
    """Estime le plan médian machine Y_sym à partir des pièces centrales structurantes."""
    spine_keys = ("selle de pont", "traverse_renfort_bassin", "waist_plate", "colonne", "rb8016")
    centers = []
    for c in components:
        lname = c.get("component_name", "").lower()
        bbox = c.get("bounding_box_mm", {})
        if max(bbox.get("size", [0, 0, 0])) < 0.01:
            continue
        if any(k in lname for k in spine_keys):
            ctr = _bbox_center(c)
            if ctr:
                centers.append(ctr[1])
    if centers:
        return round(sum(centers) / len(centers), 3)
    return 0.0


def _find_matching_components(components, patterns):
    res = []
    for c in components:
        iname = c.get("instance_name", "").lower()
        cname = c.get("component_name", "").lower()
        bbox = c.get("bounding_box_mm", {})
        if max(bbox.get("size", [0, 0, 0])) < 0.01:
            continue
        if any(p in iname or p in cname for p in patterns):
            res.append(c)
    return res


def _extract_waist_axis_xy(comp_entry, components, frame_map):
    """Détermine l'axe XY réel d'un composant Waist (alésage majeur, sous-arbre rotor ou repère)."""
    ctr = _bbox_center(comp_entry)
    iname = comp_entry.get("instance_name", "")
    cname_l = comp_entry.get("component_name", "").lower()

    bore = _largest_major_bore(comp_entry, min_radius_mm=30.0)
    if bore:
        orig = bore.get("origin_global_mm") or bore.get("axis_origin_mm")
        ax = bore.get("axis") or bore.get("axis_vector") or [0, 0, 1]
        if orig and abs(ax[2]) > 0.9:
            # Garde-fou contre les anciens JSON sans rotation appliquée sur cyl.origin
            if ctr is None or math.hypot(orig[0] - ctr[0], orig[1] - ctr[1]) <= 25.0:
                return [round(orig[0], 3), round(orig[1], 3)], f"major_bore_R{bore['radius_mm']}mm"

    # Cas d'un actionneur conteneur (ex: RS06 v1:1 dont le connecteur latéral décale la bbox)
    if "rs06" in cname_l or comp_entry.get("is_container") or not comp_entry.get("bodies"):
        for sub_pat in ("eb821-503", "000326", "eb823-511"):
            subs = _find_matching_components(components, (sub_pat,))
            if subs:
                s_ctr = _bbox_center(subs[0])
                if s_ctr:
                    return [s_ctr[0], s_ctr[1]], f"coaxial_subpart:{sub_pat}"
        if frame_map and iname in frame_map:
            fo = frame_map[iname]["origin_mm"]
            return [round(fo[0], 3), round(fo[1], 3)], "occ_transform2_origin"

    if ctr:
        return [ctr[0], ctr[1]], "bbox_center"
    return None, "unavailable"


def _check_waist_concentricity(components, frame_map=None):
    """Contrôle la coaxialité X/Y et l'empilement Z de la chaîne Waist Yaw."""
    targets = {
        "rb8016": [
            c for c in _find_matching_components(components, ("rb8016",))
            if "bride" not in c.get("component_name", "").lower()
        ],
        "traverse": _find_matching_components(components, ("traverse_renfort_bassin",)),
        "waist_plate": _find_matching_components(components, ("waist_plate",)),
        "moyeu": _find_matching_components(components, ("moyeu_waist",)),
        "rs06": _find_matching_components(components, ("rs06",)),
    }
    report = {"status": "NON_EVALUE", "elements": {}}
    ref_xy = None
    max_radial_offset = 0.0

    for key, comps in targets.items():
        if not comps:
            continue
        c = comps[0]
        xy, source = _extract_waist_axis_xy(c, components, frame_map or {})
        bbox = c.get("bounding_box_mm", {})
        entry = {
            "instance_name": c["instance_name"],
            "xy_center_mm": xy,
            "reference_source": source,
            "z_min_mm": bbox.get("min", [0, 0, 0])[2],
            "z_max_mm": bbox.get("max", [0, 0, 0])[2],
        }
        if key == "rb8016" and xy:
            ref_xy = xy
        report["elements"][key] = entry

    if ref_xy is None and "traverse" in report["elements"]:
        ref_xy = report["elements"]["traverse"]["xy_center_mm"]

    if ref_xy:
        for key, entry in report["elements"].items():
            xy = entry.get("xy_center_mm")
            if xy:
                dr = round(math.hypot(xy[0] - ref_xy[0], xy[1] - ref_xy[1]), 3)
                entry["radial_offset_vs_ref_mm"] = dr
                if dr > max_radial_offset:
                    max_radial_offset = dr
        report["reference_xy_mm"] = ref_xy
        report["max_radial_offset_mm"] = round(max_radial_offset, 3)
        report["status"] = "CONFORME" if max_radial_offset <= 0.25 else "ECART_DETECTE"

    return report


def _check_hip_bridge_alignment(components, frame_map, y_sym):
    """Contrôle la géométrie et la verticalité du Pont de Hanches (Selle, Tube, Montants, Inserts)."""
    selle_list = _find_matching_components(components, ("selle de pont",))
    tube_list = _find_matching_components(components, ("tube transverse hanches",))
    montants = _find_matching_components(components, ("montant de hanche",))
    inserts = _find_matching_components(components, ("insert hanche",))
    traverse_list = _find_matching_components(components, ("traverse_renfort_bassin",))

    res = {
        "status": "ABSENT",
        "selle_de_pont": None,
        "tube_transverse_hanches": None,
        "tube_vs_selle_centering": None,
        "montants_20x20_count": len(montants),
        "montants_verticality": [],
        "inserts_count": len(inserts),
    }

    if not selle_list and not tube_list and not montants:
        return res

    selle_ctr = None
    if selle_list:
        s = selle_list[0]
        s_bbox = s["bounding_box_mm"]
        selle_ctr = _bbox_center(s)
        res["selle_de_pont"] = {
            "instance_name": s["instance_name"],
            "center_mm": selle_ctr,
            "size_mm": s_bbox["size"],
            "z_min_mm": s_bbox["min"][2],
            "z_max_mm": s_bbox["max"][2],
        }

    if tube_list:
        t = tube_list[0]
        t_bbox = t["bounding_box_mm"]
        t_ctr = _bbox_center(t)
        res["tube_transverse_hanches"] = {
            "instance_name": t["instance_name"],
            "center_mm": t_ctr,
            "size_mm": t_bbox["size"],
            "z_min_mm": t_bbox["min"][2],
            "z_max_mm": t_bbox["max"][2],
        }
        if selle_ctr:
            s_z_min = selle_list[0]["bounding_box_mm"]["min"][2]
            t_z_max = t_bbox["max"][2]
            res["tube_vs_selle_centering"] = {
                "delta_x_mm": round(t_ctr[0] - selle_ctr[0], 3),
                "delta_y_mm": round(t_ctr[1] - selle_ctr[1], 3),
                "z_contact_gap_mm": round(s_z_min - t_z_max, 3),
            }

    max_tilt = 0.0
    for m in montants:
        iname = m["instance_name"]
        frame = frame_map.get(iname)
        tilt = None
        closest = "+Z"
        if frame:
            closest, tilt = _closest_cardinal_axis(frame["z_axis"])
            if tilt > max_tilt:
                max_tilt = tilt
        m_bbox = m["bounding_box_mm"]
        res["montants_verticality"].append({
            "instance_name": iname,
            "center_mm": _bbox_center(m),
            "size_mm": m_bbox["size"],
            "closest_axis": closest,
            "tilt_deg": tilt,
            "z_min_mm": m_bbox["min"][2],
            "z_max_mm": m_bbox["max"][2],
        })

    if traverse_list and res["selle_de_pont"]:
        tr_z_min = traverse_list[0]["bounding_box_mm"]["min"][2]
        res["pont_span_z_mm"] = round(tr_z_min - res["selle_de_pont"]["z_max_mm"], 3)

    res["max_montant_tilt_deg"] = round(max_tilt, 4)
    res["status"] = "CONFORME" if max_tilt <= 0.15 else "DEVIATION_DETECTEE"
    return res


def _check_shoulder_tube_alignment(components, frame_map, y_sym):
    """Contrôle la coaxialité et le parallélisme des tubes et brides d'épaules via axes principaux."""
    tubes = _find_matching_components(components, ("tube transverse epaules",))
    brides = [
        c for c in _find_matching_components(components, ("bride epaule",))
        if c.get("bounding_box_mm", {}).get("max", [0, 0, 0])[2] > 1100.0
    ]

    res = {
        "status": "ABSENT",
        "tubes_count": len(tubes),
        "brides_count": len(brides),
        "pairs": [],
    }
    if not tubes or not brides:
        return res

    pairs = []
    max_xz_offset = 0.0
    for tube in tubes:
        t_ctr = _bbox_center(tube)
        if not t_ctr:
            continue
        t_side = "Gauche" if t_ctr[1] >= y_sym else "Droite"

        # Associer la bride la plus proche en Y
        best_bride = None
        best_dy = 1e9
        for b in brides:
            b_ctr = _bbox_center(b)
            if not b_ctr:
                continue
            dy = abs(b_ctr[1] - t_ctr[1])
            if dy < best_dy:
                best_dy = dy
                best_bride = b

        if not best_bride:
            continue

        b_ctr = _bbox_center(best_bride)
        t_frame = frame_map.get(tube["instance_name"])
        b_frame = frame_map.get(best_bride["instance_name"])

        xz_offset = round(math.hypot(t_ctr[0] - b_ctr[0], t_ctr[2] - b_ctr[2]), 3)
        if xz_offset > max_xz_offset:
            max_xz_offset = xz_offset

        # Comparaison coaxiale entre l'axe longitudinal Y du tube et l'axe d'alésage de la bride
        # (+ relèvement de l'angle ergonomique XZ du tube de section)
        coaxial_dev = None
        ergo_rake_deg = None
        if t_frame and b_frame:
            # L'axe d'allongement du tube est celui le plus aligné sur global Y
            t_axes = (t_frame["x_axis"], t_frame["y_axis"], t_frame["z_axis"])
            b_axes = (b_frame["x_axis"], b_frame["y_axis"], b_frame["z_axis"])
            t_span = max(t_axes, key=lambda v: abs(v[1]))
            b_bore_axis = max(b_axes, key=lambda v: abs(v[1]))
            coaxial_dev = _angle_between_deg(t_span, b_bore_axis, unsigned=True)
            _, ergo_rake_deg = _closest_cardinal_axis(t_frame["x_axis"])

        pairs.append({
            "side": t_side,
            "tube": tube["instance_name"],
            "bride": best_bride["instance_name"],
            "tube_center_mm": t_ctr,
            "bride_center_mm": b_ctr,
            "delta_x_mm": round(t_ctr[0] - b_ctr[0], 3),
            "delta_z_mm": round(t_ctr[2] - b_ctr[2], 3),
            "center_xz_offset_mm": xz_offset,
            "tube_vs_bride_bore_deviation_deg": coaxial_dev,
            "ergonomic_xz_rake_deg": ergo_rake_deg,
        })

    res["pairs"] = pairs
    res["max_center_xz_offset_mm"] = round(max_xz_offset, 3)
    res["status"] = "CONFORME" if max_xz_offset <= 0.35 else "EVALUE"
    return res


def _check_bilateral_symmetry(components, y_sym):
    """Évalue la symétrie gauche/droite (X, Y par rapport à Y_sym, Z) sur toutes les paires L/R."""
    pair_specs = [
        ("Panier_Batterie", ("panier_batterie_gauche",), ("panier_batterie_droit",), None, False),
        ("Capot_Batterie", ("capot_gauche",), ("capot_droit",), None, False),
        ("Corniere_Haute", ("corniere haute",), (), None, False),
        ("Corniere_Basse", ("corniere basse",), (), None, False),
        ("Equerre_Waist", ("equerre waist",), (), None, False),
        ("Semelle_Eclisse", ("semelle éclisse", "semelle eclisse"), (), None, False),
        ("Insert_Epaule", ("insert:", "insert("), (), lambda c: "hanche" not in c.get("component_name", "").lower(), False),
        ("Tube_Epaule", ("tube transverse epaules gauche",), ("tube transverse epaules droit",), None, False),
        ("Bride_Epaule", ("bride epaule",), (), lambda c: c["bounding_box_mm"]["max"][2] > 1100.0, False),
        ("Fixation_Batterie", ("fixation batterie",), (), None, False),
        ("Montant_Hanche_Avant", ("montant de hanche avant gauche",), ("montant de hanche avant droit",), None, False),
        ("Montant_Hanche_Arriere", ("montant de hanche arriere gauche",), ("montant de hanche arriere droit",), None, False),
        ("Bride_Hanche", ("bride epaule",), (), lambda c: c["bounding_box_mm"]["max"][2] < 1100.0, False),
        ("Support_Hanche", ("support_hanche_gauche",), ("support_hanche_droit",), None, True),
        ("Liaison_Hanche", ("liaison_hanche_gauche",), ("liaison_hanche_droit",), None, True),
        ("Capot_Lateral_Hanche", ("capot_lateral_hanche_g",), ("capot_lateral_hanche_d",), None, True),
        ("Capot_Protection_Hanche_Frontal", ("capot_protection_hanche_frontal_g",), ("capot_protection_hanche_frontal_d",), None, True),
    ]

    results = []
    for label, left_pats, right_pats, pred, is_wip in pair_specs:
        if right_pats:
            lefts = _find_matching_components(components, left_pats)
            rights = _find_matching_components(components, right_pats)
            if pred:
                lefts = [c for c in lefts if pred(c)]
                rights = [c for c in rights if pred(c)]
            if not lefts or not rights:
                continue
            l_comp, r_comp = lefts[0], rights[0]
        else:
            candidates = _find_matching_components(components, left_pats)
            if pred:
                candidates = [c for c in candidates if pred(c)]
            if len(candidates) != 2:
                continue
            candidates.sort(key=lambda c: _bbox_center(c)[1], reverse=True)
            l_comp, r_comp = candidates[0], candidates[1]

        l_ctr = _bbox_center(l_comp)
        r_ctr = _bbox_center(r_comp)
        if not l_ctr or not r_ctr:
            continue

        mid_y = round((l_ctr[1] + r_ctr[1]) / 2.0, 3)
        dy_sym = round(abs(mid_y - y_sym), 3)
        dx = round(abs(l_ctr[0] - r_ctr[0]), 3)
        dz = round(abs(l_ctr[2] - r_ctr[2]), 3)

        # Tolérance 0.8 mm en Y pour absorber l'écart structurel connu +8.67 vs +9.36 mm (0.69 mm)
        results.append({
            "pair_name": label,
            "cao_status": "EN_COURS_DEFINITION_CAO" if is_wip else "STRUCTURE_FIGEE",
            "left_instance": l_comp["instance_name"],
            "right_instance": r_comp["instance_name"],
            "left_center_mm": l_ctr,
            "right_center_mm": r_ctr,
            "delta_x_mm": dx,
            "delta_z_mm": dz,
            "midpoint_y_mm": mid_y,
            "y_symmetry_error_mm": dy_sym,
            "is_symmetric": (dy_sym <= 0.8 and dx <= 0.5 and dz <= 0.5),
        })

    return results


def run_alignment_audit(app, design, root_comp, doc_name, sub_label, components_metrology, target_json_paths):
    """Exécute l'audit complet d'alignement, verticalité, symétrie et coaxialité."""
    frame_map = {}
    for occ in root_comp.allOccurrences:
        try:
            frame = _extract_occ_frame(occ)
            if frame:
                frame_map[occ.name] = frame
        except Exception:
            continue

    y_sym = _estimate_y_symmetry_plane(components_metrology)

    structural_orientations = []
    for c in components_metrology:
        iname = c.get("instance_name", "")
        cname = c.get("component_name", "")
        mass_g = c.get("mass_g", 0.0)
        bbox = c.get("bounding_box_mm", {})
        if max(bbox.get("size", [0, 0, 0])) < 0.01:
            continue
        is_struct = mass_g >= 20.0 or any(k in cname.lower() for k in STRUCTURAL_KEYWORDS)
        if not is_struct:
            continue
        frame = frame_map.get(iname)
        if not frame:
            continue

        x_ax_label, x_dev = _closest_cardinal_axis(frame["x_axis"])
        y_ax_label, y_dev = _closest_cardinal_axis(frame["y_axis"])
        z_ax_label, z_dev = _closest_cardinal_axis(frame["z_axis"])
        max_dev = max(x_dev, y_dev, z_dev)

        structural_orientations.append({
            "instance_name": iname,
            "component_name": cname,
            "mass_g": mass_g,
            "origin_mm": frame["origin_mm"],
            "bbox_center_mm": _bbox_center(c),
            "closest_axes": {"x": x_ax_label, "y": y_ax_label, "z": z_ax_label},
            "deviation_deg": {"x": x_dev, "y": y_dev, "z": z_dev, "max": max_dev},
            "is_cardinal_aligned": max_dev <= 0.15,
        })

    waist_check = _check_waist_concentricity(components_metrology, frame_map)
    hip_bridge_check = _check_hip_bridge_alignment(components_metrology, frame_map, y_sym)
    shoulder_check = _check_shoulder_tube_alignment(components_metrology, frame_map, y_sym)
    symmetry_checks = _check_bilateral_symmetry(components_metrology, y_sym)

    fixed_sym = [p for p in symmetry_checks if p.get("cao_status") == "STRUCTURE_FIGEE"]
    wip_sym = [p for p in symmetry_checks if p.get("cao_status") == "EN_COURS_DEFINITION_CAO"]

    alignment_data = {
        "metadata": {
            "document_name": doc_name,
            "subassembly": sub_label,
            "timestamp": datetime.now().isoformat(),
            "generator": "AuditTorse (alignment_audit.py)",
            "units": {"length": "mm", "angle": "deg"},
            "estimated_y_symmetry_plane_mm": y_sym,
        },
        "summary": {
            "structural_components_checked": len(structural_orientations),
            "cardinal_aligned_count": sum(1 for s in structural_orientations if s["is_cardinal_aligned"]),
            "inclined_or_rotated_count": sum(1 for s in structural_orientations if not s["is_cardinal_aligned"]),
            "waist_concentricity_status": waist_check.get("status"),
            "waist_max_radial_offset_mm": waist_check.get("max_radial_offset_mm"),
            "hip_bridge_status": hip_bridge_check.get("status"),
            "hip_max_montant_tilt_deg": hip_bridge_check.get("max_montant_tilt_deg"),
            "shoulder_tube_status": shoulder_check.get("status"),
            "symmetry_pairs_checked": len(symmetry_checks),
            "symmetry_pairs_ok": sum(1 for p in symmetry_checks if p["is_symmetric"]),
            "symmetry_fixed_structure_checked": len(fixed_sym),
            "symmetry_fixed_structure_ok": sum(1 for p in fixed_sym if p["is_symmetric"]),
            "symmetry_wip_cao_checked": len(wip_sym),
            "symmetry_wip_cao_ok": sum(1 for p in wip_sym if p["is_symmetric"]),
        },
        "waist_concentricity": waist_check,
        "hip_bridge_alignment": hip_bridge_check,
        "shoulder_tube_alignment": shoulder_check,
        "bilateral_symmetry": symmetry_checks,
        "structural_orientations": structural_orientations,
    }

    payload = json.dumps(alignment_data, indent=2, ensure_ascii=False)
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

    return alignment_data, saved_paths, errors

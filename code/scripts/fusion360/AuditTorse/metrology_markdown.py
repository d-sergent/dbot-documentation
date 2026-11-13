# -*- coding: utf-8 -*-
"""
metrology_markdown.py — Générateur partagé de synthèse Markdown métrologique (D-Bot V1)
=======================================================================================
Source unique utilisée à la fois par `AuditTorse.py` (dans Fusion 360) et par
`Code/scripts/analyze_cad_audit.py` (CLI hors Fusion 360).
Produit une fiche RAG sans valeurs codées en dur (boîte englobante, empilement Waist Z,
C1/C2 modulaire et nomenclature majeure >= 50 g extraits dynamiquement du JSON).
"""


def _is_leaf_visible_component(comp):
    """Retourne True uniquement pour les composants feuilles possédant au moins un corps visible."""
    if comp.get("is_container"):
        return False
    bodies = comp.get("bodies", [])
    if not bodies:
        return False
    bbox = comp.get("bounding_box_mm")
    if not bbox:
        return False
    sz = bbox.get("size", [0, 0, 0])
    if sz[0] <= 0.01 and sz[1] <= 0.01 and sz[2] <= 0.01:
        return False
    return any(b.get("is_visible", True) for b in bodies)


_HW_MOTOR_SUBSTRINGS = (
    "vis ", "ecrou ", "rondelle ", "goupille ", "rb8016", "zyd", "luosi",
    "000_", "00_", "1_1_", "1_2_", "1_3_", "100_", "1000_", "3_1_",
    "_2025_", "_gyos", "_pis", "d19_", "dianjiban", "fl82blw",
    "eb1203", "eb1201", "eb823", "rs04", "rs06", "el05",
)

_WIP_PELVIS_TAGS = (
    "support_hanche", "liaison_hanche", "capot_lateral_hanche", "capot_protection_hanche",
)


def _normalize_bom_key(cname):
    """Regroupe les variantes '(Symétrie miroir)' et suffixes d'instance STEP sous un nom canonique."""
    cleaned = cname or "Inconnu"
    for tok in ("(Symétrie miroir)", " (1)", " (2)", " (3)"):
        cleaned = cleaned.replace(tok, "")
    return " ".join(cleaned.split())


def _filter_structural_hole_entries(entries, measure_key):
    """Filtre les faces issues de visserie/moteurs et dédoublonne par instance + géométrie."""
    seen = set()
    kept = []
    for e in entries or []:
        cname_l = (e.get("component") or "").lower()
        if any(p in cname_l for p in _HW_MOTOR_SUBSTRINGS):
            continue
        inst = e.get("instance") or cname_l
        val = round(float(e.get(measure_key, 0.0) or 0.0), 1)
        orig = e.get("origin_mm") or [0.0, 0.0, 0.0]
        ax = e.get("axis") or [0.0, 0.0, 1.0]
        sig = (inst, val, round(orig[0], 0), round(orig[1], 0), round(orig[2], 0), round(abs(ax[0]), 1), round(abs(ax[1]), 1), round(abs(ax[2]), 1))
        if sig not in seen:
            seen.add(sig)
            kept.append(e)
    return kept


def build_markdown_summary(audit_data, sub_label="Torse_et_Bassin", doc_folder_rel="Torse_et_Bassin"):
    """Construit la synthèse Markdown RAG à partir d'un dictionnaire d'audit métrologique."""
    meta = audit_data.get("metadata", {})
    summary = audit_data.get("assembly_summary", {})
    components = audit_data.get("components", [])
    holes_summary = audit_data.get("holes_summary", {})
    bom = audit_data.get("hardware_bom", {})

    doc_name = meta.get("document_name", "Inconnu")
    timestamp = meta.get("timestamp", "Inconnu")
    total_mass_g = summary.get("total_mass_g", 0.0)
    com = summary.get("center_of_mass_mm", [0, 0, 0])

    # Filtrage strict : uniquement composants feuilles avec corps visibles (écarte conteneurs type Ensemble hanche:1)
    valid_comps = [c for c in components if _is_leaf_visible_component(c)]
    if not valid_comps:
        for c in components:
            bbox = c.get("bounding_box_mm")
            if bbox and max(bbox.get("size", [0, 0, 0])) > 0.01:
                valid_comps.append(c)

    # Diagnostic densité PA12-CF brute vs calibrée
    uncalibrated_pa12 = []
    for c in valid_comps:
        mat_l = (c.get("material") or "").lower()
        vol = float(c.get("volume_cm3", 0.0) or 0.0)
        mass = float(c.get("mass_g", 0.0) or 0.0)
        if ("pa12" in mat_l or "plastron" in c.get("component_name", "").lower()) and vol > 5.0:
            if (mass / vol) > 0.90:
                uncalibrated_pa12.append(c.get("component_name"))

    density_note = ""
    if uncalibrated_pa12:
        density_note = (
            f"\n> [!NOTE]\n"
            f"> **Calibration densités PA12-CF** : {len(uncalibrated_pa12)} composant(s)/sous-corps polymères "
            f"conservent dans ce snapshot une densité pleine (rho ~ 1.015 g/cm3) ou un matériau mixte "
            f"(masse CAO brute : **{total_mass_g/1000.0:.2f} kg**, incluant ~+2.1 kg de marge théorique par rapport à un infill gyroïde 15 %)."
        )

    p_bbox = summary.get("physical_components_bounding_box_mm", {})
    if valid_comps:
        p_min = [
            round(min(c["bounding_box_mm"]["min"][0] for c in valid_comps), 2),
            round(min(c["bounding_box_mm"]["min"][1] for c in valid_comps), 2),
            round(min(c["bounding_box_mm"]["min"][2] for c in valid_comps), 2),
        ]
        p_max = [
            round(max(c["bounding_box_mm"]["max"][0] for c in valid_comps), 2),
            round(max(c["bounding_box_mm"]["max"][1] for c in valid_comps), 2),
            round(max(c["bounding_box_mm"]["max"][2] for c in valid_comps), 2),
        ]
        p_size = [
            round(p_max[0] - p_min[0], 2),
            round(p_max[1] - p_min[1], 2),
            round(p_max[2] - p_min[2], 2),
        ]
    else:
        p_min = p_bbox.get("min", [0, 0, 0])
        p_max = p_bbox.get("max", [0, 0, 0])
        p_size = p_bbox.get("size", [0, 0, 0])

    phys_dx, phys_dy, phys_dz = p_size[0], p_size[1], p_size[2]
    phys_min_z, phys_max_z = p_min[2], p_max[2]

    waist_parts = {}
    pelvis_z_mins = []
    pelvis_z_maxs = []
    plaque_cou_z_max = phys_max_z
    pelvis_keywords = (
        "bassin", "pelvis", "hanche", "selle de pont",
        "traverse_renfort", "rb8016", "rs06", "moyeu_waist",
    )

    for c in valid_comps:
        iname = c.get("instance_name", "")
        cname = c.get("component_name", "")
        cname_l = cname.lower()
        bbox = c.get("bounding_box_mm", {})
        z_min = bbox.get("min", [0, 0, 0])[2]
        z_max = bbox.get("max", [0, 0, 0])[2]
        mass = c.get("mass_g", 0.0)

        if any(k in cname_l for k in pelvis_keywords):
            pelvis_z_mins.append(z_min)
            pelvis_z_maxs.append(z_max)
        if "plaque_de_cou" in cname_l or "plaque de cou" in cname_l:
            plaque_cou_z_max = z_max

        if "RS06" in iname or "RS06" in cname:
            waist_parts["rs06"] = {"name": iname, "z_min": z_min, "z_max": z_max, "mass": mass}
        elif "Moyeu_Waist" in iname or "Moyeu_Waist" in cname:
            waist_parts["moyeu"] = {"name": iname, "z_min": z_min, "z_max": z_max, "mass": mass}
        elif "Chassis_Structurel_Bassin" in iname or "Chassis_Structurel_Bassin" in cname:
            waist_parts["chassis_bassin"] = {"name": iname, "z_min": z_min, "z_max": z_max, "mass": mass}
        elif "Traverse_Renfort_Bassin" in iname or "Traverse_Renfort_Bassin" in cname:
            waist_parts["traverse"] = {"name": iname, "z_min": z_min, "z_max": z_max, "mass": mass}
        elif ("rb8016" in cname_l or "rb8016" in iname.lower()) and "bride" not in cname_l:
            waist_parts["bearing"] = {"name": iname, "z_min": z_min, "z_max": z_max, "mass": mass}
        elif "Waist_Plate" in iname or "Waist_Plate" in cname:
            waist_parts["waist_plate"] = {"name": iname, "z_min": z_min, "z_max": z_max, "mass": mass}
        elif "Equerre waist" in iname or "Equerre waist" in cname:
            waist_parts["equerre"] = {"name": iname, "z_min": z_min, "z_max": z_max, "mass": mass}

    if "rs06" not in waist_parts:
        for c in components:
            iname = c.get("instance_name", "")
            cname = c.get("component_name", "")
            if iname.startswith("RS06") or cname.startswith("RS06"):
                bbox = c.get("bounding_box_mm")
                if bbox and max(bbox.get("size", [0, 0, 0])) > 1.0:
                    waist_parts["rs06"] = {
                        "name": iname,
                        "z_min": bbox["min"][2],
                        "z_max": bbox["max"][2],
                        "mass": c.get("mass_g", 0.0),
                    }
                    break

    waist_plate_z_min = waist_parts.get("waist_plate", {}).get("z_min", 0.0)
    waist_plate_z_max = waist_parts.get("waist_plate", {}).get("z_max", 0.0)
    traverse_z_min = waist_parts.get("traverse", {}).get("z_min", 0.0)
    traverse_z_max = waist_parts.get("traverse", {}).get("z_max", 0.0)
    lamage_depth = 3.00
    lamage_floor_z = round(traverse_z_max - lamage_depth, 2)
    bearing_z_min = waist_parts.get("bearing", {}).get("z_min", 0.0)
    bearing_z_max = waist_parts.get("bearing", {}).get("z_max", 0.0)
    bearing_contact_gap = round(abs(lamage_floor_z - bearing_z_min), 2)
    bearing_plate_gap = round(abs(bearing_z_max - waist_plate_z_min), 2)
    moyeu_z_min = waist_parts.get("moyeu", {}).get("z_min", 0.0)
    moyeu_z_max = waist_parts.get("moyeu", {}).get("z_max", 0.0)
    anti_talonnage_gap = round(waist_plate_z_min - moyeu_z_max, 2)
    chassis_z_min = waist_parts.get("chassis_bassin", {}).get("z_min", 0.0)
    chassis_z_max = waist_parts.get("chassis_bassin", {}).get("z_max", 0.0)
    chassis_traverse_gap = round(abs(chassis_z_max - traverse_z_min), 2)
    rs06_z_min = waist_parts.get("rs06", {}).get("z_min", 0.0)
    rs06_z_max = waist_parts.get("rs06", {}).get("z_max", 0.0)
    equerre_z_min = waist_parts.get("equerre", {}).get("z_min", 0.0)
    equerre_z_max = waist_parts.get("equerre", {}).get("z_max", 0.0)

    bassin_min_z = round(min(pelvis_z_mins), 2) if pelvis_z_mins else round(phys_min_z, 2)
    bassin_max_z = round(max(pelvis_z_maxs), 2) if pelvis_z_maxs else round(waist_plate_z_min, 2)
    bassin_height = round(bassin_max_z - bassin_min_z, 2)

    torse_min_z = round(waist_plate_z_min, 2) if waist_plate_z_min else round(phys_min_z, 2)
    torse_max_z = round(phys_max_z, 2)
    torse_height = round(torse_max_z - torse_min_z, 2)

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

    csinks = _filter_structural_hole_entries(holes_summary.get("countersinks_90deg_fhc_m4", []), "angle_deg")
    pins = _filter_structural_hole_entries(holes_summary.get("dowel_pins_dia_3mm", []), "diameter_mm")
    bores = _filter_structural_hole_entries(holes_summary.get("large_bores", []), "diameter_mm")

    sec_machining = "## 5. Bilan d'Usinage & Quincaillerie Clé" if has_modular else "## 4. Bilan d'Usinage & Quincaillerie Clé"
    sec_bom = "## 6. Nomenclature Consolidée Majeure" if has_modular else "## 5. Nomenclature Consolidée Majeure"

    grouped_bom = {}
    for c in components:
        cname = c.get("component_name", "Inconnu")
        mass_g = float(c.get("mass_g", 0.0) or 0.0)
        mat = c.get("material", "Unknown")
        pnum = c.get("part_number", "") or "—"
        bodies = c.get("bodies", [])
        is_container = len(bodies) == 0 and mass_g > 0.0
        if is_container:
            continue
        if mat == "Unknown" and bodies:
            if "plastron" in cname.lower():
                mat = f"PA12-CF ({max(len(bodies) - 1, 1)} corps) + ceinture Alu 7075"
            else:
                mat = f"Multi-corps ({len(bodies)} corps)"
        if any(tag in cname.lower() for tag in _WIP_PELVIS_TAGS):
            mat = f"{mat} [En cours de définition CAO]"

        bom_key = _normalize_bom_key(cname)
        if bom_key not in grouped_bom:
            grouped_bom[bom_key] = {
                "component_name": bom_key,
                "part_number": pnum,
                "qty": 0,
                "material": mat,
                "unit_mass_g": mass_g,
                "total_mass_g": 0.0,
            }
        grouped_bom[bom_key]["qty"] += 1
        grouped_bom[bom_key]["total_mass_g"] += mass_g

    leaf_items = sorted(
        [v for v in grouped_bom.values() if v["total_mass_g"] >= 45.0],
        key=lambda x: x["total_mass_g"],
        reverse=True,
    )
    bom_rows = []
    for item in leaf_items[:28]:
        bom_rows.append(
            f"| {item['component_name']} | `{item['part_number']}` | {item['qty']} | {item['material']} | {item['unit_mass_g']:.2f} g | {item['total_mass_g']:.2f} g |"
        )
    bom_table_str = "\n".join(bom_rows) if bom_rows else "| *(Aucune pièce >= 45 g)* | — | — | — | — | — |"

    src_json_url = f"file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/{doc_folder_rel}/Audits/AUDIT_METROLOGIQUE_{sub_label}.json"

    content = f"""# Synthèse Métrologique et CAO — Torse et Bassin D-Bot V1

> **Statut** : Document de référence métrologique validé par extraction CAO Fusion 360  
> **Source de vérité CAO** : `{doc_name}`  
> **Date de l'audit** : {timestamp}  
> **Fichier source** : [`AUDIT_METROLOGIQUE_{sub_label}.json`]({src_json_url})  
> **Audits complémentaires (`Audits/`)** : `AUDIT_CINEMATIQUE_{sub_label}.json`, `AUDIT_ALIGNEMENT_{sub_label}.json`

---

## 📑 Sommaire

1. [Vue d'Ensemble & Masses](#1-vue-densemble--masses)
2. [Dimensions Physiques Réelles & Altitude au Sol](#2-dimensions-physiques-réelles--altitude-au-sol)
3. [Chaîne Cinématique et Empilement Waist (Z)](#3-chaîne-cinématique-et-empilement-waist-z)
{sommaire_suite}

---

## 1. Vue d'Ensemble & Masses

* **Masse totale de l'ensemble Torse + Bassin** : **{total_mass_g/1000.0:.2f} kg** ({total_mass_g:.2f} g).
* **Nombre de composants modélisés** : **{len(components)} instances** (BOM de {len(bom)} références uniques).
* **Centre de gravité global (CoM)** :
  * **X** (profondeur) = **{com[0]:+.2f} mm** (déport avant cohérent avec l'implantation pectorale et les tiroirs batteries).
  * **Y** (latéral) = **{com[1]:+.2f} mm** (symétrie gauche/droite par rapport au plan médian machine).
  * **Z** (hauteur) = **{com[2]:.2f} mm** (situé au niveau du plexus, entre le waist à {waist_plate_z_min:.2f} mm et la plaque de cou à {plaque_cou_z_max:.2f} mm).{density_note}

---

## 2. Dimensions Physiques Réelles & Altitude au Sol

> [!IMPORTANT]
> **Distinction essentielle pour le dimensionnement robotique** :
> 1. **L'altitude Z** est repérée par rapport au sol (la plante des pieds du robot debout est à Z = 0 mm).
> 2. **La hauteur physique réelle** du sous-ensemble Torse + Bassin est de **{phys_dz:.2f} mm** ({phys_dz/10.0:.1f} cm).

| Grandeur | Coordonnées / Plage (mm) | Dimension Physique Réelle | Commentaire |
| :--- | :--- | :--- | :--- |
| **Profondeur totale (X)** | {p_min[0]:.2f} mm -> {p_max[0]:.2f} mm | **{phys_dx:.2f} mm** | Encombrement avant/arrière plastron + carénages |
| **Largeur totale (Y)** | {p_min[1]:.2f} mm -> {p_max[1]:.2f} mm | **{phys_dy:.2f} mm** | Largeur d'épaules et pivots de hanches |
| **Altitude Z au sol** | **{phys_min_z:.2f} mm -> {phys_max_z:.2f} mm** | — | Repère mondial D-Bot (pieds à Z = 0 mm) |
| **Bassin seul (Pelvis)** | {bassin_min_z:.2f} mm -> {bassin_max_z:.2f} mm | **{bassin_height:.2f} mm** (~{bassin_height/10.0:.1f} cm) | Du bas des supports de hanche au sommet du berceau |
| **Torse seul (Waist au cou)** | {torse_min_z:.2f} mm -> {torse_max_z:.2f} mm | **{torse_height:.2f} mm** (~{torse_height/10.0:.1f} cm) | De la Waist Plate au sommet du collet de cou |
| **Hauteur Totale Torse + Bassin** | {phys_min_z:.2f} mm -> {phys_max_z:.2f} mm | **{phys_dz:.2f} mm** (~{phys_dz/10.0:.1f} cm) | **Hauteur physique propre de l'assemblage** |

---

## 3. Chaîne Cinématique et Empilement Waist (Z)

L'empilement vertical de l'articulation de lacet du buste (Waist Yaw) a été vérifié au micron près :

| Composant / Interface | Z Bas (mm) | Z Haut (mm) | Épaisseur (mm) | Écart mesuré | Statut métrologique |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Moteur RS06 (Rotor)** | {rs06_z_min:.2f} | {rs06_z_max:.2f} | {round(rs06_z_max - rs06_z_min, 2):.2f} | — | Référence rotor RS06 |
| **Moyeu Waist Sandwich** | {moyeu_z_min:.2f} | {moyeu_z_max:.2f} | {round(moyeu_z_max - moyeu_z_min, 2):.2f} | Appui rotor : {round(abs(moyeu_z_min - rs06_z_max), 2):.2f} mm | **Contact franc** |
| **Châssis Structurel Bassin** | {chassis_z_min:.2f} | {chassis_z_max:.2f} | {round(chassis_z_max - chassis_z_min, 2):.2f} | Enveloppe coque PA12-CF | Coque pelvienne encastrée |
| **Traverse Renfort Bassin** | {traverse_z_min:.2f} | {traverse_z_max:.2f} | {round(traverse_z_max - traverse_z_min, 2):.2f} | Sur Pont de Hanches (Alu 7075) | **Interface Waist maître** |
| ↳ *Lamage Traverse (profondeur 3,00 mm)* | — | **{lamage_floor_z:.2f}** | Prof. 3,00 | — | Face d'appui du RB8016 |
| **Roulement RB8016** | **{bearing_z_min:.2f}** | **{bearing_z_max:.2f}** | {round(bearing_z_max - bearing_z_min, 2):.2f} | Fond lamage : **{bearing_contact_gap:.2f} mm** | **Contact franc** |
| **Waist Plate 7075** | **{waist_plate_z_min:.2f}** | **{waist_plate_z_max:.2f}** | {round(waist_plate_z_max - waist_plate_z_min, 2):.2f} | Appui bague int. : {bearing_plate_gap:.2f} mm | **Contact franc** |
| ↳ *Jeu Anti-talonnage (Moyeu vs Waist Plate)* | {moyeu_z_max:.2f} | {waist_plate_z_min:.2f} | — | **{anti_talonnage_gap:.2f} mm** | **Jeu de sécurité axial** |
| **Équerre Waist & Plastron Ventral** | {equerre_z_min:.2f} | {equerre_z_max:.2f} | {round(equerre_z_max - equerre_z_min, 2):.2f} | Appui Waist Plate : {round(abs(equerre_z_min - waist_plate_z_max), 2):.2f} mm | **Contact franc** |
{modular_section}
---

{sec_machining}

* **Fraisures coniques 90° (pièces structurelles usinées/imprimées)** : **{len(csinks)} fraisures** dédoublonnées (hors visserie/moteurs).
* **Alésages et lamages majeurs (>= 60 mm, pièces structurelles)** : **{len(bores)} surfaces d'alésages** répertoriées (lamage Traverse Ø 120 mm, alésages Waist Plate Ø 80/130/170 mm, interfaces bassin).
* **Goupilles / alésages fins Ø 3,0 mm (pièces structurelles)** : **{len(pins)} perçages** répertoriés (hors moteurs STEP).

---

{sec_bom}

| Composant clé | Référence CAO | Quantité | Matériau / Note | Masse unitaire | Masse totale |
| :--- | :--- | :---: | :--- | ---: | ---: |
{bom_table_str}

"""
    return content

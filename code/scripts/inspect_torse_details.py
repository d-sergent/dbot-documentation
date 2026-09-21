# -*- coding: utf-8 -*-
"""
inspect_torse_details.py — Inspection fine des pièces Torse & Bassin D-Bot V1
"""

import json
import os

JSON_PATH = "/Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/AUDIT_METROLOGIQUE_Torse_et_Bassin.json"

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    components = data.get("components", [])
    holes_summary = data.get("holes_summary", {})

    print("=== 1. TOUTES LES PIÈCES UNIQUES ET LEURS MASSES ===")
    unique_comps = {}
    for c in components:
        name = c["component_name"]
        if name not in unique_comps:
            unique_comps[name] = {
                "count": 0,
                "mass_g": c.get("mass_g", 0),
                "vol_cm3": c.get("volume_cm3", 0),
                "material": c.get("material", "N/A"),
                "bbox": c.get("bounding_box_mm", {}).get("size", [])
            }
        unique_comps[name]["count"] += 1

    # Trier par masse décroissante
    for name, info in sorted(unique_comps.items(), key=lambda x: x[1]["mass_g"], reverse=True):
        print(f"[{info['count']}x] {name} : {info['mass_g']:.2f} g | {info['material']} | BBox: {info['bbox']}")

    print("\n=== 2. LOCALISATION PRÉCISE DES GOUPILLES Ø 3.0 mm (ISO 8734) ===")
    pins = holes_summary.get("dowel_pins_dia_3mm", [])
    pins_by_comp = {}
    for p in pins:
        pins_by_comp.setdefault(p["component"], []).append(p)
    for cname, plist in pins_by_comp.items():
        print(f"\n* {cname} ({len(plist)} goupilles) :")
        for p in plist:
            print(f"  - Ø {p['diameter_mm']} mm @ Pos {p['origin_mm']} (axe {p['axis']})")

    print("\n=== 3. FOCUS PIÈCES MAÎTRESSES DU TORSE ===")
    focus_names = ["colonne", "semelle", "insert", "platine", "bride", "rb8016", "moyeu", "waist", "cou"]
    for c in components:
        cname_lower = c["component_name"].lower()
        if any(fn in cname_lower for fn in focus_names):
            print(f"\n=======================================================")
            print(f"PIÈCE : {c['component_name']} (Instance: {c['instance_name']})")
            print(f"Masse : {c.get('mass_g')} g | Matériau : {c.get('material')}")
            bbox = c.get("bounding_box_mm", {})
            print(f"Dimensions : L={bbox.get('size', [0,0,0])[0]} mm, l={bbox.get('size', [0,0,0])[1]} mm, h={bbox.get('size', [0,0,0])[2]} mm")
            print(f"Min: {bbox.get('min')} | Max: {bbox.get('max')}")
            
            # Perçages
            holes = c.get("hole_features", [])
            if holes:
                print(f"HoleFeatures ({len(holes)}) :")
                for h in holes:
                    print(f"  - {h.get('name')}: dia={h.get('diameter_mm')} mm, type={h.get('type')}, c-sink={h.get('countersink_diameter_mm')} mm @ {h.get('countersink_angle_deg')} deg")
            
            # Cylindres
            cyls = c.get("cylindrical_faces", [])
            if cyls:
                # Regrouper par diamètre
                dias = {}
                for cyl in cyls:
                    d = cyl["diameter_mm"]
                    dias.setdefault(d, []).append(cyl["origin_global_mm"])
                print(f"Cylindres ({len(cyls)}) par diamètres :")
                for d, coords in sorted(dias.items()):
                    print(f"  - Ø {d} mm : {len(coords)} occurrences. Exemple coords: {coords[:3]}")

            # Cônes / Fraisures
            cones = c.get("conical_faces", [])
            if cones:
                angles = {}
                for cn in cones:
                    a = cn["full_angle_deg"]
                    angles.setdefault(a, []).append(cn["origin_global_mm"])
                print(f"Cônes/Fraisures ({len(cones)}) :")
                for a, coords in sorted(angles.items()):
                    print(f"  - Angle {a} deg : {len(coords)} occurrences. Exemple coords: {coords[:3]}")

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
inspect_full_audit.py — Analyse complète des 171 composants du Torse & Bassin D-Bot V1
"""

import json
import os

JSON_PATH = "/Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/audit_torse_fusion360.json"

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    comps = data.get("components", [])
    print(f"=== ANALYSE GLOBALE : {len(comps)} COMPOSANTS RÉVÉLÉS ===\n")

    # 1. Regroupement par composant unique
    unique_comps = {}
    for c in comps:
        name = c["component_name"]
        if name not in unique_comps:
            unique_comps[name] = {
                "instances": [],
                "mass_g": c.get("mass_g", 0),
                "material": c.get("material", "N/A"),
                "bbox": c.get("bounding_box_mm", {}).get("size", []),
                "min_z": c.get("bounding_box_mm", {}).get("min", [0,0,0])[2],
                "max_z": c.get("bounding_box_mm", {}).get("max", [0,0,0])[2],
                "holes": c.get("hole_features", []),
                "cyls": c.get("cylindrical_faces", []),
                "cones": c.get("conical_faces", [])
            }
        unique_comps[name]["instances"].append(c["instance_name"])

    print(f"Nombre total de pièces uniques : {len(unique_comps)}\n")
    print("--- 1. LISTE DE TOUTES LES PIÈCES UNIQUES (Triées par position Z) ---")
    sorted_by_z = sorted(unique_comps.items(), key=lambda x: x[1]["min_z"])
    for name, info in sorted_by_z:
        qty = len(info["instances"])
        print(f"- [{qty:2d}x] {name:<35} | Z=[{info['min_z']:6.1f}..{info['max_z']:6.1f}] | Masse: {info['mass_g']:6.1f} g | BBox: {info['bbox']}")

    print("\n--- 2. FOCUS PIÈCES MAÎTRESSES DU TORSE & BASSIN ---")
    keywords = ["plaque", "plate", "waist", "equerre", "corniere", "cou", "neck", "butee", "doigt", "platine", "spine", "colonne", "bride", "hub", "moyeu"]
    matched = []
    for name, info in unique_comps.items():
        if any(k in name.lower() for k in keywords):
            matched.append((name, info))

    print(f"Composants identifiés par mots-clés ({len(matched)}) :")
    for name, info in matched:
        print(f"\n* PIÈCE : {name} ({len(info['instances'])} instance(s))")
        print(f"  - Matériau : {info['material']} | Masse unitaire : {info['mass_g']} g")
        print(f"  - Dimensions (L x l x h) : {info['bbox']} mm")
        print(f"  - Étendue Z : [{info['min_z']:.2f} .. {info['max_z']:.2f}] mm")
        if info["holes"]:
            print(f"  - HoleFeatures ({len(info['holes'])}) :")
            for h in info["holes"]:
                print(f"    * {h.get('name')}: dia={h.get('diameter_mm')} mm, type={h.get('type')}, c-sink={h.get('countersink_diameter_mm')} mm @ {h.get('countersink_angle_deg')} deg")
        if info["cyls"]:
            dia_counts = {}
            for cy in info["cyls"]:
                d = cy["diameter_mm"]
                dia_counts[d] = dia_counts.get(d, 0) + 1
            print(f"  - Cylindres : {dict(sorted(dia_counts.items()))}")
        if info["cones"]:
            angle_counts = {}
            for cn in info["cones"]:
                a = cn["full_angle_deg"]
                angle_counts[a] = angle_counts.get(a, 0) + 1
            print(f"  - Cônes/Fraisures : {dict(sorted(angle_counts.items()))}")

    print("\n--- 3. ZONE INTERMÉDIAIRE WAIST (Z = 1000 à 1060 mm) ---")
    for name, info in unique_comps.items():
        if (1000 <= info["min_z"] <= 1060) or (1000 <= info["max_z"] <= 1060):
            print(f"- {name} : Z=[{info['min_z']:.1f} .. {info['max_z']:.1f}] mm | BBox: {info['bbox']}")

    print("\n--- 4. ZONE HAUTE COU (Z = 1450 à 1530 mm) ---")
    for name, info in unique_comps.items():
        if (1450 <= info["min_z"] <= 1530) or (1450 <= info["max_z"] <= 1530):
            print(f"- {name} : Z=[{info['min_z']:.1f} .. {info['max_z']:.1f}] mm | BBox: {info['bbox']}")

if __name__ == "__main__":
    main()

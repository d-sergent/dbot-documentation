# -*- coding: utf-8 -*-
"""
inspect_chamfers.py — Contrôle métrologique des chanfreins et fraisures CAO vs Spécifications
"""

import json
import os

JSON_PATH = "/Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/AUDIT_METROLOGIQUE_Torse_et_Bassin.json"

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    target_names = [
        "colonne vertébrale",
        "semelle éclisse",
        "Waist_Plate_7075",
        "Plaque_de_Cou_7075",
        "Equerre waist",
        "Equerre cou",
        "Moyeu_Waist_Sandwich_7075",
        "Bride Epaule"
    ]

    print("================================================================================")
    print("CONTRÔLE DES CHANFREINS, FRAISURES ET ÉBAVURAGES DANS LE MODÈLE CAO")
    print("================================================================================\n")

    for c in data["components"]:
        cname = c["component_name"]
        if cname in target_names:
            print(f"--------------------------------------------------------------------------------")
            print(f"PIÈCE : {cname}")
            holes = c.get("hole_features", [])
            cones = c.get("conical_faces", [])
            
            # Fraisures via HoleFeatures
            if holes:
                print(f"  * Fonctions de perçage natives (HoleFeatures) : {len(holes)}")
                for h in holes:
                    cs_dia = h.get("countersink_diameter_mm")
                    cs_ang = h.get("countersink_angle_deg")
                    print(f"    - {h.get('name')}: perçage Ø {h.get('diameter_mm')} mm | fraisure {cs_ang} deg (Ø sup {cs_dia} mm)")
            else:
                print("  * Aucune fonction HoleFeature native (perçages réalisés par esquisse/extrusion ou import)")

            # Surfaces coniques B-Rep (Chanfreins & Fraisures modélisés)
            print(f"  * Surfaces coniques modélisées en 3D (Cônes B-Rep) : {len(cones)}")
            if cones:
                # Regrouper par angle
                by_angle = {}
                for cn in cones:
                    ang = cn["full_angle_deg"]
                    by_angle.setdefault(ang, []).append(cn)
                for ang, clist in sorted(by_angle.items()):
                    print(f"    - Cône angle total {ang:.1f} deg (demi-angle {ang/2.0:.1f} deg) : {len(clist)} occurrence(s)")
                    for idx, item in enumerate(clist[:4]):
                        print(f"      [{idx+1}] Pos: {item['origin_global_mm']} | Axe: {item['axis']}")
                    if len(clist) > 4:
                        print(f"      ... et {len(clist)-4} autre(s) occurrence(s)")
            else:
                print("    - Aucun chanfrein ou fraisure conique modélisé en 3D sur ce solide.")

            print()

if __name__ == "__main__":
    main()

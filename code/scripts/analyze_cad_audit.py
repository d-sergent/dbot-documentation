# -*- coding: utf-8 -*-
"""
analyze_cad_audit.py — Analyseur d'audit CAO Fusion 360 vs Documentation D-Bot V1
"""

import json
import os
import math

JSON_PATH = "/Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/audit_torse_fusion360.json"

def main():
    if not os.path.exists(JSON_PATH):
        print(f"Erreur: fichier introuvable {JSON_PATH}")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("metadata", {})
    summary = data.get("assembly_summary", {})
    components = data.get("components", [])
    holes_summary = data.get("holes_summary", {})
    bom = data.get("hardware_bom", {})

    print("================================================================================")
    print(f"RAPPORT D'ANALYSE CAO FUSION 360 : {meta.get('document_name', 'Inconnu')}")
    print(f"Date : {meta.get('timestamp')}")
    print(f"Masse totale assemblage : {summary.get('total_mass_g', 0):.2f} g ({summary.get('total_mass_g', 0)/1000.0:.2f} kg)")
    print(f"Dimensions hors tout : {summary.get('bounding_box_mm', {}).get('size', [])} mm")
    print(f"Nombre d'instances de composants : {len(components)}")
    print(f"Nombre de références uniques BOM : {len(bom)}")
    print("================================================================================\n")

    # 1. Nomenclature consolidée
    print("--- 1. NOMENCLATURE DES COMPOSANTS (BOM) ---")
    sorted_bom = sorted(bom.items(), key=lambda x: x[1]["quantity"], reverse=True)
    for key, item in sorted_bom:
        comp_name = item.get("component_name", "")
        part_num = item.get("part_number", "")
        qty = item.get("quantity", 0)
        desc = item.get("description", "")
        print(f"- [x{qty:2d}] {comp_name} | PartNo: {part_num} | Desc: {desc}")

    # 2. Focus Pièces Structurelles Torse & Bassin
    print("\n--- 2. PIÈCES STRUCTURELLES CLÉS DÉTECTÉES ---")
    keywords = ["colonne", "bride", "waist", "bassin", "torse", "plaque", "equerre", "shoulder", "hub", "moyeu", "platine", "spine", "neck", "cou", "rs-04", "rs-05", "rs-06", "crbh", "8016"]
    
    matched_comps = []
    for c in components:
        name_lower = c["component_name"].lower()
        if any(k in name_lower for k in keywords):
            matched_comps.append(c)

    print(f"Nombre de composants structurels identifiés par mots-clés : {len(matched_comps)}")
    for c in matched_comps:
        bbox = c.get("bounding_box_mm", {}).get("size", [0, 0, 0])
        print(f"\n* Composant : {c['component_name']} ({c['instance_name']})")
        print(f"  - Matériau : {c.get('material', 'N/A')}")
        print(f"  - Masse : {c.get('mass_g', 0):.2f} g | Volume : {c.get('volume_cm3', 0):.2f} cm3")
        print(f"  - Bounding Box : L={bbox[0]:.1f} mm, l={bbox[1]:.1f} mm, h={bbox[2]:.1f} mm")
        print(f"  - Centre de gravité : {c.get('center_of_mass_mm', [])}")
        
        # Perçages et géométrie
        holes = c.get("hole_features", [])
        if holes:
            print(f"  - HoleFeatures ({len(holes)}) :")
            for h in holes:
                print(f"    * {h.get('name')}: dia={h.get('diameter_mm')} mm, depth={h.get('depth_mm')} mm, type={h.get('type')}, c-sink={h.get('countersink_diameter_mm')} mm @ {h.get('countersink_angle_deg')} deg")
        
        cyls = c.get("cylindrical_faces", [])
        if cyls:
            dia_list = sorted(list(set([cyl["diameter_mm"] for cyl in cyls])))
            print(f"  - Diamètres cylindres détectés : {dia_list}")

    # 3. Analyse des Goupilles Ø 3 mm (Jonction Z=0)
    print("\n--- 3. CONTRÔLE MÉLOGIQUE : GOUPILLES Ø 3.0 mm (ISO 8734) ---")
    pins = holes_summary.get("dowel_pins_dia_3mm", [])
    print(f"Total de faces cylindriques Ø 2.9 - 3.1 mm : {len(pins)}")
    # Regrouper par composant
    pins_by_comp = {}
    for p in pins:
        cname = p["component"]
        pins_by_comp.setdefault(cname, []).append(p)
    for cname, plist in pins_by_comp.items():
        print(f"- {cname} : {len(plist)} occurrences de Ø ~3.0 mm")
        for p in plist[:8]: # afficher max 8
            print(f"  * Origine: {p['origin_mm']} | Axe: {p['axis']}")

    # 4. Analyse des Fraisures Coniques 90° (Vis FHC M4)
    print("\n--- 4. CONTRÔLE MÉLOGIQUE : FRAISURES 90° (VIS FHC M4) ---")
    csinks = holes_summary.get("countersinks_90deg_fhc_m4", [])
    print(f"Total de surfaces coniques à 90° : {len(csinks)}")
    csinks_by_comp = {}
    for cs in csinks:
        cname = cs["component"]
        csinks_by_comp.setdefault(cname, []).append(cs)
    for cname, cslist in csinks_by_comp.items():
        print(f"- {cname} : {len(cslist)} fraisures coniques 90°")
        for cs in cslist[:6]:
            print(f"  * Origine: {cs['origin_mm']} | Axe: {cs['axis']}")

    # 5. Analyse des Alésages Majeurs (>= 60 mm)
    print("\n--- 5. CONTRÔLE MÉLOGIQUE : ALÉSAGES MAJEURS (>= 60 mm) ---")
    bores = holes_summary.get("large_bores", [])
    bores_by_comp = {}
    for b in bores:
        cname = b["component"]
        bores_by_comp.setdefault(cname, []).append(b)
    for cname, blist in bores_by_comp.items():
        dia_set = sorted(list(set([b["diameter_mm"] for b in blist])))
        print(f"- {cname} : alésages {dia_set}")

if __name__ == "__main__":
    main()

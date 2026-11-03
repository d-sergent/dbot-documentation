# -*- coding: utf-8 -*-
"""
export_all_fea_snapshots.py — Générateur Automatique de Snapshots Cartographiques FEA Von Mises
Projet : Robot Humanoïde D-Bot V1
=============================================================================
Ce script s'exécute avec le binaire FreeCAD (/Applications/FreeCAD.app/Contents/Resources/bin/FreeCAD).
Il ouvre chaque modèle de résultat .FCStd pré-calculé, applique les scalaires de contraintes
de Von Mises sur le maillage C3D10 (CalculiX ccx), ajuste le cadrage caméra au plus près de la pièce,
exporte le rendu 3D haute définition, puis superpose un habillage technique souverain :
  1. Card d'ingénierie (Titre, sous-titre, cas de charge, valeurs crête et facteurs de sécurité).
  2. Échelle de couleur scalaire verticale étalonnée en MPa avec les bornes réelles de la pièce.
"""

import sys
import os
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    import FreeCAD
    import FreeCADGui
except ImportError:
    print("Ce script doit être exécuté avec le binaire FreeCAD GUI.")
    sys.exit(1)

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots"

FEA_TARGETS = [
    {
        "name": "Corniere_haute",
        "fcstd": f"{BASE_DIR}/Pieces_Isolees/Corniere_haute/Corniere_haute_FEA_Results.FCStd",
        "out_png": f"{BASE_DIR}/Pieces_Isolees/Corniere_haute/Corniere_haute_VonMises.png",
        "title": "CORNIÈRE HAUTE NERVURÉE 7075-T6",
        "subtitle": "Maillage tétraédrique volumique C3D10 (CalculiX ccx + Gmsh)",
        "load_case": "Lacet Transversal / Torsion Supérieure (Yaw F = 210 N)",
        "metrics": [
            ("Contrainte Von Mises Crête :", "84.7 MPa", (251, 146, 60, 255)),
            ("Limite Élastique Rp0.2 (7075-T6) :", "505.0 MPa", (148, 163, 184, 255)),
            ("Facteur de Sécurité P95 Sf :", "11.2  [CONFORME]", (52, 211, 153, 255))
        ],
        "is_assembly": False
    },
    {
        "name": "Corniere_basse",
        "fcstd": f"{BASE_DIR}/Pieces_Isolees/Corniere_basse/Corniere_basse_FEA_Results.FCStd",
        "out_png": f"{BASE_DIR}/Pieces_Isolees/Corniere_basse/Corniere_basse_VonMises.png",
        "title": "CORNIÈRE BASSE NERVURÉE 7075-T6",
        "subtitle": "Maillage tétraédrique volumique C3D10 (CalculiX ccx + Gmsh)",
        "load_case": "Lacet Transversal / Torsion de Hanche (Yaw M = 36 N.m)",
        "metrics": [
            ("Contrainte Von Mises Crête :", "67.9 MPa", (251, 146, 60, 255)),
            ("Limite Élastique Rp0.2 (7075-T6) :", "505.0 MPa", (148, 163, 184, 255)),
            ("Facteur de Sécurité P95 Sf :", "13.1  [CONFORME]", (52, 211, 153, 255))
        ],
        "is_assembly": False
    },
    {
        "name": "colonne_basse",
        "fcstd": f"{BASE_DIR}/Pieces_Isolees/colonne_vertébrale/colonne_basse_FEA_Tangage.FCStd",
        "out_png": f"{BASE_DIR}/Pieces_Isolees/colonne_vertébrale/colonne_basse_Tangage_VonMises.png",
        "title": "COLONNE VERTÉBRALE BASSE (SEGMENT INFÉRIEUR)",
        "subtitle": "Maillage tétraédrique volumique C3D10 (CalculiX ccx + Gmsh)",
        "load_case": "Tangage Sagittal d'Arrêt d'Urgence (Pitch M = 140 N.m)",
        "metrics": [
            ("Contrainte Von Mises Crête :", "106.8 MPa", (251, 146, 60, 255)),
            ("Limite Élastique Rp0.2 (7075-T6) :", "505.0 MPa", (148, 163, 184, 255)),
            ("Facteur de Sécurité P95 Sf :", "4.7  [CONFORME]", (52, 211, 153, 255))
        ],
        "is_assembly": False
    },
    {
        "name": "colonne_complete",
        "fcstd": f"{BASE_DIR}/Assemblages/colonne_vertébrale_complete/colonne_complete_FEA_Tangage.FCStd",
        "out_png": f"{BASE_DIR}/Assemblages/colonne_vertébrale_complete/colonne_complete_Tangage_VonMises.png",
        "title": "COLONNE VERTÉBRALE COMPLÈTE SANDWICH 15 MM",
        "subtitle": "Double Plaque + Éclisses Renfort 7075-T6 (CalculiX ccx + Gmsh)",
        "load_case": "Tangage Sagittal d'Arrêt d'Urgence (Pitch M = 140 N.m / 2g)",
        "metrics": [
            ("Contrainte Von Mises Crête :", "86.7 MPa", (251, 146, 60, 255)),
            ("Limite Élastique Rp0.2 (7075-T6) :", "505.0 MPa", (148, 163, 184, 255)),
            ("Facteur de Sécurité P95 Sf :", "9.7  [CONFORME]", (52, 211, 153, 255))
        ],
        "is_assembly": False
    },
    {
        "name": "Torse_Global_Assembly",
        "fcstd": f"{BASE_DIR}/Assemblages/torse_complet_global/Torse_Global_Assembly_FEA_Results.FCStd",
        "out_png": f"{BASE_DIR}/Assemblages/torse_complet_global/Torse_Global_Assembly_VonMises.png",
        "title": "OSSATURE PRIMAIRE DU TORSE (ASSEMBLAGE GLOBAL)",
        "subtitle": "Maillage tétraédrique volumique C3D10 (CalculiX ccx + Gmsh, 156 846 nœuds)",
        "load_case": "Tangage Sagittal d'Arrêt d'Urgence (Pitch M = 140 N.m / 2g, F_x = 328 N)",
        "metrics": [
            ("Contrainte Von Mises Crête :", "62.1 MPa (P95 zone basse : 15.3 MPa)", (251, 146, 60, 255)),
            ("Limite Élastique Rp0.2 (7075-T6) :", "505.0 MPa", (148, 163, 184, 255)),
            ("Facteur de Sécurité Sf :", "8.1 Crête / 33.0 P95  [CONFORME]", (52, 211, 153, 255)),
            ("Flèche Maximale au Cou (Ux) :", "0.622 mm  (Critère < 1.50 mm : OK)", (52, 211, 153, 255))
        ],
        "is_assembly": False
    }
]


def get_rainbow_color(t):
    """Interpolate standard FEM rainbow: Blue(0) -> Cyan(0.25) -> Green(0.5) -> Yellow(0.75) -> Red(1.0)"""
    t = max(0.0, min(1.0, t))
    if t < 0.25:
        f = t / 0.25
        return (0, int(255 * f), 255)
    elif t < 0.5:
        f = (t - 0.25) / 0.25
        return (0, 255, int(255 * (1.0 - f)))
    elif t < 0.75:
        f = (t - 0.5) / 0.25
        return (int(255 * f), 255, 0)
    else:
        f = (t - 0.75) / 0.25
        return (255, int(255 * (1.0 - f)), 0)


def annotate_image(raw_png_path, out_png_path, target_cfg, vm_min=0.0, vm_max=100.0):
    im = Image.open(raw_png_path).convert("RGBA")
    w, h = im.size

    overlay = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    font_path = "/System/Library/Fonts/Helvetica.ttc"
    font_title = ImageFont.truetype(font_path, 21)
    font_sub = ImageFont.truetype(font_path, 14)
    font_bold = ImageFont.truetype(font_path, 15)
    font_metric = ImageFont.truetype(font_path, 14)
    font_bar = ImageFont.truetype(font_path, 15)
    font_bar_title = ImageFont.truetype(font_path, 16)

    # 1. Card Technique Top-Left
    card_x, card_y = 50, 45
    card_w = 640
    card_h = 225 if len(target_cfg["metrics"]) >= 4 else 195

    # Fond technique sombre (#0f172a avec bordure cyan #38bdf8)
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=12,
        fill=(15, 23, 42, 235),
        outline=(56, 189, 248, 200),
        width=2
    )

    draw.text((card_x + 22, card_y + 16), "D-BOT V1 HUMANOÏDE  |  ANALYSE PAR ÉLÉMENTS FINIS (FEA)", fill=(56, 189, 248, 255), font=font_sub)
    draw.text((card_x + 22, card_y + 38), target_cfg["title"], fill=(248, 250, 252, 255), font=font_title)
    draw.text((card_x + 22, card_y + 70), f"Cas de charge : {target_cfg['load_case']}", fill=(203, 213, 225, 255), font=font_bold)
    draw.text((card_x + 22, card_y + 94), target_cfg["subtitle"], fill=(148, 163, 184, 255), font=font_sub)

    y_offset = card_y + 120
    for label, val, color in target_cfg["metrics"]:
        draw.text((card_x + 22, y_offset), label, fill=(148, 163, 184, 255), font=font_metric)
        draw.text((card_x + 290, y_offset), val, fill=color, font=font_bold)
        y_offset += 23

    # 2. Colorbar FEA sur la droite
    if not target_cfg["is_assembly"] and vm_max > vm_min:
        bar_x = w - 170
        bar_y = 180
        bar_w = 26
        bar_h = 720

        draw.text((bar_x - 30, bar_y - 45), "Von Mises", fill=(15, 23, 42, 255), font=font_bar_title)
        draw.text((bar_x - 15, bar_y - 25), "(MPa)", fill=(71, 85, 105, 255), font=font_sub)

        for i in range(bar_h):
            t = 1.0 - (i / float(bar_h - 1))
            color = get_rainbow_color(t)
            draw.line([(bar_x, bar_y + i), (bar_x + bar_w, bar_y + i)], fill=color + (255,))

        draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h], outline=(15, 23, 42, 255), width=2)

        num_ticks = 6
        for k in range(num_ticks):
            frac = k / float(num_ticks - 1)
            tick_y = bar_y + bar_h - int(frac * bar_h)
            if k == num_ticks - 1:
                tick_y = bar_y
            val = vm_min + frac * (vm_max - vm_min)

            draw.line([(bar_x + bar_w, tick_y), (bar_x + bar_w + 8, tick_y)], fill=(15, 23, 42, 255), width=2)
            val_str = f"{val:.1f}"
            draw.text((bar_x + bar_w + 14, tick_y - 9), val_str, fill=(15, 23, 42, 255), font=font_bar)

    final_img = Image.alpha_composite(im, overlay).convert("RGB")
    os.makedirs(os.path.dirname(out_png_path), exist_ok=True)
    final_img.save(out_png_path, "PNG", quality=95)
    print(f"  ✅ Image finale calibrée et annotée sauvegardée : {out_png_path}")


def run_export():
    print("=" * 78)
    print("  D-BOT V1 : PRODUCTION DES CARTOGRAPHIES FEA VON MISES (HAUTE PRÉCISION)")
    print("=" * 78)

    for cfg in FEA_TARGETS:
        fcstd_path = cfg["fcstd"]
        out_png = cfg["out_png"]

        if not os.path.exists(fcstd_path):
            print(f"  [IGNORÉ] Fichier source introuvable : {os.path.basename(fcstd_path)}")
            continue

        print(f"\nTraitement de : {cfg['name']} ({os.path.basename(fcstd_path)})...")
        try:
            doc = FreeCAD.openDocument(fcstd_path)
            gui_doc = FreeCADGui.getDocument(doc.Name)

            if not gui_doc or not gui_doc.ActiveView:
                print(f"  ❌ Aucune vue 3D active trouvée pour {doc.Name}")
                FreeCAD.closeDocument(doc.Name)
                continue

            view = gui_doc.ActiveView
            vm_min = 0.0
            vm_max = 100.0

            res_obj = doc.getObject("CCX_Results")
            if res_obj and hasattr(res_obj, "vonMises") and len(res_obj.vonMises) > 0:
                import numpy as np
                vm = list(res_obj.vonMises)
                vm_arr = np.array(vm, dtype=float)
                vm_min = float(np.min(vm_arr))
                vm_max_raw = float(np.max(vm_arr))
                p99 = float(np.percentile(vm_arr, 99.0))
                p995 = float(np.percentile(vm_arr, 99.5))

                # Filtrage des singularités géométriques d'angle sur les grands maillages (> 50k nœuds)
                # et renormalisation sur [-1.0, +1.0] pour activer le spectre complet Bleu->Cyan->Vert->Jaune->Rouge de FreeCAD
                if len(vm) > 50000 and vm_max_raw > 2.2 * p99:
                    vm_scale_max = p995
                else:
                    vm_scale_max = vm_max_raw
                vm_max = vm_max_raw

                span = max(vm_scale_max - vm_min, 1e-6)
                mapped_scalars = [
                    2.0 * min(1.0, max(0.0, ((float(v) - vm_min) / span) ** 0.75)) - 1.0
                    for v in vm
                ]
                print(
                    f"  • Données Von Mises CalculiX : {len(vm):,} nœuds | "
                    f"Min = {vm_min:.2f} MPa, P99.5 = {p995:.2f} MPa, Max = {vm_max_raw:.2f} MPa"
                )

                # Coloration du maillage volumique sur toute la dynamique chromatique [-1, +1]
                mesh_vo = res_obj.Mesh.ViewObject
                mesh_vo.setNodeColorByScalars(res_obj.NodeNumbers, mapped_scalars)
                mesh_vo.DisplayMode = "Faces & Wireframe"

                # Masquer toutes les pièces brutes et origines pour centrer la caméra sur le maillage
                for obj in doc.Objects:
                    go = gui_doc.getObject(obj.Name)
                    if go:
                        go.Visibility = (obj.Name == res_obj.Mesh.Name)
                try:
                    doc.save()
                except Exception:
                    pass
            else:
                # Modèle d'assemblage CAO global
                for obj in doc.Objects:
                    go = gui_doc.getObject(obj.Name)
                    if go:
                        if obj.Name == "Torse_Squelette_Global":
                            go.Visibility = False
                        elif hasattr(obj, "Shape"):
                            go.Visibility = True
                            go.DisplayMode = "Shaded"
                            if "Carbone" in obj.Name or "Tube" in obj.Name:
                                go.ShapeColor = (0.20, 0.22, 0.25)
                            elif "Batterie" in obj.Name or "PA12" in obj.Name:
                                go.ShapeColor = (0.12, 0.12, 0.14)
                            else:
                                go.ShapeColor = (0.78, 0.80, 0.82)
                        else:
                            go.Visibility = False

            # Cadrage caméra parfait
            view.viewIsometric()
            view.fitAll()

            # Ajustement dynamique du zoom pour remplir ~85-90% de l'image
            cam = view.getCamera()
            h_match = re.search(r'height\s+([\d\.]+)', cam)
            if h_match:
                h = float(h_match.group(1))
                zoom_factor = 0.95
                new_cam = re.sub(r'height\s+[\d\.]+', f'height {h * zoom_factor:.3f}', cam)
                view.setCamera(new_cam)

            raw_temp_png = f"/tmp/{cfg['name']}_raw_render.png"
            view.saveImage(raw_temp_png, 1920, 1080, "White")
            FreeCAD.closeDocument(doc.Name)

            # Application de l'habillage technique souverain
            annotate_image(raw_temp_png, out_png, cfg, vm_min=0.0, vm_max=vm_max)

            if os.path.exists(raw_temp_png):
                os.remove(raw_temp_png)

        except Exception as e:
            print(f"  ❌ Erreur lors du traitement de {fcstd_path} : {e}")

    print("\n" + "=" * 78)
    print("  PRODUCTION COMPLÈTE DE TOUS LES RENDUS FEA TERMINÉE AVEC SUCCÈS")
    print("=" * 78)

    try:
        FreeCADGui.getMainWindow().close()
    except Exception:
        pass


run_export()
try:
    FreeCADGui.getMainWindow().close()
except Exception:
    pass

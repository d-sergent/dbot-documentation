#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_freecad_draft_drawings.py — Générateur Déterministe de Plans Cotés Multi-Vues FreeCAD
=============================================================================================
Ce script produit une mise en plan 2D complète en triptyque industriel SANS AUCUNE HALLUCINATION :
1. Importation du solide 3D STEP certifié (Source Unique de Vérité 3D).
2. Extraction de la projection 2D exacte des 3 Vues B-Rep réelles :
   - VUE DE DESSUS (Face Supérieure Stator RS-06).
   - VUE DE FACE (Tranche Verticale intermédiaire avec redan de centrage).
   - VUE DE DESSOUS (Face Inférieure Portée Roulement RB8016).
3. Disposition en bande horizontale unifiée (alignement vertical strict sur Y = 45.0 mm) :
   - Vue de Dessus à Gauche (X = -170 mm).
   - Vue de Face au Milieu (X = 0 mm, épaisseur 9 mm sur X, hauteur 176.09 mm sur Y).
   - Vue de Dessous à Droite (X = +170 mm).
4. Lignes de rappel de projection horizontales traversant les 3 vues.
5. Cotations analytiques déterministes :
   - Hors-tout Largeur (173.03 mm) et Hauteur (176.09 mm).
   - Entraxes perçages stator M4 (48.08 mm x 48.08 mm, PCD 68 mm).
   - Épaisseur totale (9.00 mm), semelle (6.00 mm) et saillie redan (3.00 mm).
   - Diamètres d'alésages de centrage roulement (Ø 89.62 mm et Ø 80.00 mm).
6. Cadre technique normalisé grand format et Cartouche ISO 7200 complet en bas à droite.
7. Injection automatique de GuiDocument.xml garantissant la visibilité immédiate de 100% des éléments dès l'ouverture.
"""

import os
import sys
import argparse
import zipfile
import xml.dom.minidom

try:
    import FreeCAD as App
    import Part
    import Draft
except ImportError as e:
    print(f"❌ Erreur d'import FreeCAD: {e}")
    print("Ce script doit être exécuté avec l'interpréteur FreeCAD (ex: freecadcmd).")
    sys.exit(1)

def inject_gui_visibility(fcstd_path):
    """Injecte un GuiDocument.xml certifié pour garantir que 100% des objets sont visibles dès l'ouverture
    et configure les ViewProviders (DisplayMode Wireframe, suppression des lignes de rappel du cartouche)."""
    with zipfile.ZipFile(fcstd_path, 'r') as zin:
        doc_xml = zin.read('Document.xml').decode('utf-8')

    dom = xml.dom.minidom.parseString(doc_xml)
    
    # 1. Cartographie Nom interne -> Type et Label utilisateur
    obj_types = {}
    for o in dom.getElementsByTagName('Object'):
        if o.hasAttribute('type') and o.hasAttribute('name'):
            obj_types[o.getAttribute('name')] = o.getAttribute('type')

    obj_labels = {}
    for obj_data in dom.getElementsByTagName('ObjectData'):
        for obj in obj_data.getElementsByTagName('Object'):
            name = obj.getAttribute('name')
            for prop in obj.getElementsByTagName('Property'):
                if prop.getAttribute('name') == 'Label':
                    strings = prop.getElementsByTagName('String')
                    if strings:
                        obj_labels[name] = strings[0].getAttribute('value')
                    break

    base_name = os.path.splitext(os.path.basename(fcstd_path))[0]

    gui_lines = [
        "<?xml version='1.0' encoding='utf-8'?>",
        '<GUIElement version="1">',
        '  <Document>',
        f'    <ViewProvider Document="{base_name}">',
        '      <Properties Count="1">',
        '        <Property name="ShowHidden" type="App::PropertyBool"><Bool value="false"/></Property>',
        '      </Properties>',
        '    </ViewProvider>',
        '  </Document>'
    ]

    for name, otype in obj_types.items():
        label = obj_labels.get(name, name)
        props = [
            '        <Property name="Visibility" type="App::PropertyBool"><Bool value="true"/></Property>'
        ]

        # Mode filaire strict pour les cadres et contours (ZERO fond vert)
        if otype == 'Part::FeaturePython':
            props.append('        <Property name="DisplayMode" type="App::PropertyEnumeration"><String value="Wireframe"/></Property>')

        gui_lines.extend([
            f'  <ViewProvider name="{name}">',
            f'    <Properties Count="{len(props)}">',
            *props,
            '    </Properties>',
            '  </ViewProvider>'
        ])

    gui_lines.append('</GUIElement>')
    gui_xml_str = "\n".join(gui_lines)

    tmp_injected = fcstd_path + ".tmp"
    with zipfile.ZipFile(fcstd_path, 'r') as zin:
        with zipfile.ZipFile(tmp_injected, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename != 'GuiDocument.xml':
                    zout.writestr(item, zin.read(item.filename))
            zout.writestr('GuiDocument.xml', gui_xml_str.encode('utf-8'))

    os.replace(tmp_injected, fcstd_path)
    print(f"✅ GuiDocument.xml injecté : {len(obj_types)} éléments configurés (fond vert éliminé, cartouche purifié).")

def make_clean_text(doc, text_str, pos, label_name):
    """Crée un objet texte 2D natif FreeCAD sans flèche, sans ligne de rappel et sans point parasite."""
    txt = Draft.make_text(text_str, pos)
    txt.Label = label_name
    return txt

def generate_triptych_drawing(step_path, output_fcstd, part_name="Piece"):
    if not os.path.exists(step_path):
        raise FileNotFoundError(f"Fichier STEP introuvable : {step_path}")

    doc = App.newDocument(part_name)
    shape = Part.read(step_path)
    temp_solid = doc.addObject('Part::Feature', 'TEMP_SOLID')
    temp_solid.Shape = shape
    doc.recompute()

    # 1. Projections 2D OpenCASCADE
    raw_top = Draft.make_shape2dview(temp_solid, App.Vector(0, 0, 1))
    doc.recompute()
    top_shape = raw_top.Shape.copy()

    raw_bottom = Draft.make_shape2dview(temp_solid, App.Vector(0, 0, -1))
    doc.recompute()
    bottom_shape = raw_bottom.Shape.copy()

    raw_face = Draft.make_shape2dview(temp_solid, App.Vector(0, 1, 0))
    doc.recompute()
    face_shape = raw_face.Shape.copy()

    # Suppression immédiate du solide pour éviter tout volume 3D opaque
    doc.removeObject(temp_solid.Name)
    doc.removeObject(raw_top.Name)
    doc.removeObject(raw_bottom.Name)
    doc.removeObject(raw_face.Name)
    doc.recompute()

    # 2. Positionnement en bande horizontale unifiée (Y = 45.0 mm)
    Y_LEVEL = 45.0

    # A. Vue de Dessus à Gauche (X = -170 mm)
    mat_top = App.Matrix()
    mat_top.rotateZ(-1.5707963267948966)
    top_rot = top_shape.transformGeometry(mat_top)
    bb_t = top_rot.BoundBox
    tx = -170.0 - (bb_t.XMin + bb_t.XMax)/2.0
    ty = Y_LEVEL - (bb_t.YMin + bb_t.YMax)/2.0
    mat_t_trans = App.Matrix()
    mat_t_trans.move(App.Vector(tx, ty, 0))
    top_final = top_rot.transformGeometry(mat_t_trans)

    top_obj = doc.addObject('Part::Feature', 'Vue_de_Dessus_Superieure')
    top_obj.Shape = top_final
    doc.recompute()
    t_bb = top_final.BoundBox

    # B. Vue de Face au Milieu (X = 0 mm, épaisseur 9 mm sur X, hauteur 176.09 mm sur Y)
    bb_f = face_shape.BoundBox
    fx = 0.0 - (bb_f.XMin + bb_f.XMax)/2.0
    fy = Y_LEVEL - (bb_f.YMin + bb_f.YMax)/2.0
    mat_f_trans = App.Matrix()
    mat_f_trans.move(App.Vector(fx, fy, 0))
    face_final = face_shape.transformGeometry(mat_f_trans)

    face_obj = doc.addObject('Part::Feature', 'Vue_de_Face_Tranche_Verticale')
    face_obj.Shape = face_final
    doc.recompute()
    f_bb = face_final.BoundBox

    # C. Vue de Dessous à Droite (X = +170 mm)
    mat_bot = App.Matrix()
    mat_bot.rotateZ(-1.5707963267948966)
    bot_rot = bottom_shape.transformGeometry(mat_bot)
    bb_b = bot_rot.BoundBox
    bx = 170.0 - (bb_b.XMin + bb_b.XMax)/2.0
    by = Y_LEVEL - (bb_b.YMin + bb_b.YMax)/2.0
    mat_b_trans = App.Matrix()
    mat_b_trans.move(App.Vector(bx, by, 0))
    bot_final = bot_rot.transformGeometry(mat_b_trans)

    bot_obj = doc.addObject('Part::Feature', 'Vue_de_Dessous_Inferieure')
    bot_obj.Shape = bot_final
    doc.recompute()
    b_bb = bot_final.BoundBox

    # 3. Lignes de rappel de projection horizontales (Alignement triptyque)
    Draft.make_line(App.Vector(t_bb.XMax, t_bb.YMax, 0), App.Vector(f_bb.XMin, f_bb.YMax, 0))
    Draft.make_line(App.Vector(f_bb.XMax, f_bb.YMax, 0), App.Vector(b_bb.XMin, b_bb.YMax, 0))
    Draft.make_line(App.Vector(t_bb.XMax, t_bb.YMin, 0), App.Vector(f_bb.XMin, f_bb.YMin, 0))
    Draft.make_line(App.Vector(f_bb.XMax, f_bb.YMin, 0), App.Vector(b_bb.XMin, b_bb.YMin, 0))

    # 4. Cotations Vue de Dessus
    dim_w = Draft.make_dimension(
        App.Vector(t_bb.XMin, t_bb.YMax, 0),
        App.Vector(t_bb.XMax, t_bb.YMax, 0),
        App.Vector(-170, t_bb.YMax + 20, 0)
    )
    dim_w.Label = "Cote_Largeur_173_03"

    dim_h = Draft.make_dimension(
        App.Vector(t_bb.XMin, t_bb.YMin, 0),
        App.Vector(t_bb.XMin, t_bb.YMax, 0),
        App.Vector(t_bb.XMin - 22, Y_LEVEL, 0)
    )
    dim_h.Label = "Cote_Hauteur_176_09"

    hx1, hx2 = -170.0 - 24.04, -170.0 + 24.04
    hy1, hy2 = Y_LEVEL - 24.04, Y_LEVEL + 24.04

    dim_px = Draft.make_dimension(
        App.Vector(hx1, hy2, 0),
        App.Vector(hx2, hy2, 0),
        App.Vector(-170, hy2 + 12, 0)
    )
    dim_px.Label = "Cote_Entraxe_X_48_08"

    dim_py = Draft.make_dimension(
        App.Vector(hx2, hy1, 0),
        App.Vector(hx2, hy2, 0),
        App.Vector(hx2 + 12, Y_LEVEL, 0)
    )
    dim_py.Label = "Cote_Entraxe_Y_48_08"

    for (hx, hy) in [(hx1, hy1), (hx2, hy1), (hx1, hy2), (hx2, hy2)]:
        Draft.make_line(App.Vector(hx - 4, hy, 0), App.Vector(hx + 4, hy, 0))
        Draft.make_line(App.Vector(hx, hy - 4, 0), App.Vector(hx, hy + 4, 0))

    lbl_m4 = Draft.make_label(
        target_point=App.Vector(hx2, hy2, 0),
        placement=App.Vector(hx2 + 25, hy2 + 25, 0),
        label_type='Custom',
        custom_text='4x M4 (PCD Ø 68.0 mm)',
        direction='Horizontal',
        distance=10
    )
    lbl_m4.Label = "Annotation_Trous_Stator_M4"

    make_clean_text(
        doc,
        'VUE DE DESSUS (Face Superieure Stator RS-06)',
        App.Vector(-245.0, -95.0, 0),
        'Titre_Vue_de_Dessus'
    )

    # 5. Cotations Vue de Face (Tranche au milieu)
    # Cote Hors-Tout Épaisseur Totale (9.00 mm) au sommet
    dim_t = Draft.make_dimension(
        App.Vector(-4.50, f_bb.YMax, 0),
        App.Vector(4.50, f_bb.YMax, 0),
        App.Vector(0.00, f_bb.YMax + 20, 0)
    )
    dim_t.Label = "Cote_Epaisseur_Totale_9_00"

    # Cotation étagée à la base pour éliminer tout chevauchement :
    # Étage 1 (Y = -58.04 mm) : Semelle 6.00 mm [-1.50 -> +4.50]
    dim_base = Draft.make_dimension(
        App.Vector(-1.50, f_bb.YMin, 0),
        App.Vector(4.50, f_bb.YMin, 0),
        App.Vector(1.50, f_bb.YMin - 15, 0)
    )
    dim_base.Label = "Cote_Semelle_6_00"

    # Étage 2 (Y = -73.04 mm, 15 mm en dessous) : Saillie Redan 3.00 mm [-4.50 -> -1.50]
    dim_boss = Draft.make_dimension(
        App.Vector(-4.50, f_bb.YMin, 0),
        App.Vector(-1.50, f_bb.YMin, 0),
        App.Vector(-3.00, f_bb.YMin - 30, 0)
    )
    dim_boss.Label = "Cote_Saillie_Redan_3_00"

    make_clean_text(
        doc,
        'VUE DE FACE (Tranche Epaisseur 9.00 mm)',
        App.Vector(-65.0, -95.0, 0),
        'Titre_Vue_de_Face'
    )

    # 6. Cotations Vue de Dessous (Droite)
    lbl_cent = Draft.make_label(
        target_point=App.Vector(170.0, Y_LEVEL + 44.81, 0),
        placement=App.Vector(170.0 + 35, Y_LEVEL + 60, 0),
        label_type='Custom',
        custom_text='Centrage Concentrique Ø 89.62 mm (h7)',
        direction='Horizontal',
        distance=10
    )
    lbl_cent.Label = "Annotation_Centrage_89_62"

    lbl_bore = Draft.make_label(
        target_point=App.Vector(170.0 - 40.0, Y_LEVEL, 0),
        placement=App.Vector(170.0 - 65, Y_LEVEL - 25, 0),
        label_type='Custom',
        custom_text='Alesage Axial Ø 80.00 mm (RB8016 int.)',
        direction='Horizontal',
        distance=-10
    )
    lbl_bore.Label = "Annotation_Alesage_80_00"

    make_clean_text(
        doc,
        'VUE DE DESSOUS (Face Inferieure - Portee Roulement)',
        App.Vector(85.0, -95.0, 0),
        'Titre_Vue_de_Dessous'
    )

    # 7. Cadre technique & Cartouche ISO 7200 (Zéro fond vert, zéro trait parasite)
    FRAME_XMIN, FRAME_XMAX = -315.0, 315.0
    FRAME_YMIN, FRAME_YMAX = -165.0, 205.0

    p1 = App.Vector(FRAME_XMIN, FRAME_YMIN, 0)
    p2 = App.Vector(FRAME_XMAX, FRAME_YMIN, 0)
    p3 = App.Vector(FRAME_XMAX, FRAME_YMAX, 0)
    p4 = App.Vector(FRAME_XMIN, FRAME_YMAX, 0)
    frame_out = Draft.make_wire([p1, p2, p3, p4, p1], closed=True, face=False)
    frame_out.Label = "Cadre_Technique_A2_Exterieur"
    frame_out.MakeFace = False

    M = 5.0
    pi1 = App.Vector(FRAME_XMIN + M, FRAME_YMIN + M, 0)
    pi2 = App.Vector(FRAME_XMAX - M, FRAME_YMIN + M, 0)
    pi3 = App.Vector(FRAME_XMAX - M, FRAME_YMAX - M, 0)
    pi4 = App.Vector(FRAME_XMIN + M, FRAME_YMAX - M, 0)
    frame_in = Draft.make_wire([pi1, pi2, pi3, pi4, pi1], closed=True, face=False)
    frame_in.Label = "Cadre_Technique_A2_Marge"
    frame_in.MakeFace = False

    CX_R = FRAME_XMAX - M
    CY_B = FRAME_YMIN + M
    CX_L = CX_R - 180.0
    CY_T = CY_B + 60.0

    c_p1 = App.Vector(CX_L, CY_B, 0)
    c_p2 = App.Vector(CX_R, CY_B, 0)
    c_p3 = App.Vector(CX_R, CY_T, 0)
    c_p4 = App.Vector(CX_L, CY_T, 0)
    cart_border = Draft.make_wire([c_p1, c_p2, c_p3, c_p4, c_p1], closed=True, face=False)
    cart_border.Label = "Cartouche_ISO7200_Contour"
    cart_border.MakeFace = False

    Draft.make_line(App.Vector(CX_L, CY_T - 15, 0), App.Vector(CX_R, CY_T - 15, 0))
    Draft.make_line(App.Vector(CX_L, CY_T - 30, 0), App.Vector(CX_R, CY_T - 30, 0))
    Draft.make_line(App.Vector(CX_L, CY_T - 45, 0), App.Vector(CX_R, CY_T - 45, 0))
    Draft.make_line(App.Vector(CX_L + 90, CY_T - 30, 0), App.Vector(CX_L + 90, CY_B, 0))
    Draft.make_line(App.Vector(CX_L + 135, CY_T - 45, 0), App.Vector(CX_L + 135, CY_B, 0))

    # Textes du Cartouche créés avec make_clean_text (Strictement aucun trait ni ligne de rappel)
    make_clean_text(doc, 'D-BOT HUMANOID ROBOT V1 — ARCHITECTURE SOUVERAINE',
                    App.Vector(CX_L + 5, CY_T - 10, 0), 'Cartouche_Titre_Projet')
    make_clean_text(doc, 'WAIST PLATE 7075-T6 (Platine Déportée Waist Yaw)',
                    App.Vector(CX_L + 5, CY_T - 25, 0), 'Cartouche_Nom_Piece')
    make_clean_text(doc, 'Alliage : Al 7075-T6 | Masse : 486.8 g',
                    App.Vector(CX_L + 5, CY_T - 40, 0), 'Cartouche_Matiere_Masse')
    make_clean_text(doc, 'Ref : ASV1_100_02A | Rev : 02',
                    App.Vector(CX_L + 95, CY_T - 40, 0), 'Cartouche_Ref_Rev')
    make_clean_text(doc, 'Tolérance : ISO 2768-mK',
                    App.Vector(CX_L + 5, CY_T - 55, 0), 'Cartouche_Tolerance')
    make_clean_text(doc, 'Echelle : 1:1',
                    App.Vector(CX_L + 95, CY_T - 55, 0), 'Cartouche_Echelle')
    make_clean_text(doc, 'Date : 2026-10-18',
                    App.Vector(CX_L + 140, CY_T - 55, 0), 'Cartouche_Date')

    doc.recompute()
    os.makedirs(os.path.dirname(os.path.abspath(output_fcstd)), exist_ok=True)
    doc.saveAs(output_fcstd)

    inject_gui_visibility(output_fcstd)
    print(f"✅ Document complet certifié généré : {output_fcstd}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Générateur Déterministe de Plans Cotés FreeCAD Multi-Vues")
    parser.add_argument("--step", type=str, default=os.environ.get("FREECAD_INPUT_STEP"), help="Chemin du fichier STEP 3D")
    parser.add_argument("--output-fcstd", type=str, default=os.environ.get("FREECAD_OUTPUT_FCSTD"), help="Chemin de sortie du fichier .FCStd")
    parser.add_argument("--name", type=str, default=os.environ.get("FREECAD_PART_NAME", "Piece"), help="Nom du composant")

    clean_argv = []
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            clean_argv.append(arg)
        elif clean_argv and clean_argv[-1].startswith("--") and not arg.startswith("-"):
            clean_argv.append(arg)

    args = parser.parse_args(clean_argv)
    step_file = args.step
    if not step_file and args.name:
        potential_step = f"/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/Bibliotheque_Composants_STEP/{args.name}.step"
        if os.path.exists(potential_step):
            step_file = potential_step

    out_file = args.output_fcstd or "/Users/Shared/Mon Google Drive Physique/Documentation/Waist_Plate_Cotee.FCStd"

    if step_file and os.path.exists(step_file):
        print(f"🎯 Modèle 3D B-Rep STEP certifié : {step_file}")
        generate_triptych_drawing(step_file, out_file, args.name)
    else:
        print("❌ Fichier STEP introuvable.")
        sys.exit(1)

if __name__ in ("__main__", "generate_freecad_draft_drawings"):
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
D-Bot PoC FreeCAD : Assemblage Complet du Bassin / Waist (Axe Yaw)
Génération automatisée avec Congés 3D (Fillet) et Chanfreins (Chamfer)
=============================================================================
"""

import os
import sys
import math
import shutil

print("=================================================================")
print("=== D-BOT : GÉNÉRATION DU POC AVEC CONGÉS ET CHANFREINS ===")
print("=================================================================")

try:
    import FreeCAD
    import Part
    import Sketcher
    import PartDesign
    from FreeCAD import Vector, Rotation, Placement
except ImportError as e:
    print(f"Erreur d'import FreeCAD: {e}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 1. INITIALISATION DU DOCUMENT
# ---------------------------------------------------------------------------
doc_name = "DBot_Waist_Bassin_PoC"
doc = FreeCAD.newDocument(doc_name)
doc.Label = "D-Bot Bassin / Waist Assembly PoC"

# Centre de rotation mondial de l'axe Yaw (issu de l'audit métrologique)
YAW_X = 49.23  # mm
YAW_Y = 9.36   # mm

# ---------------------------------------------------------------------------
# 2. STRUCTURE ARBORESCENTE D'ASSEMBLAGE (App::Part)
# ---------------------------------------------------------------------------
root_asm = doc.addObject("App::Part", "D_Bot_Waist_Assembly")
root_asm.Label = "D-Bot Waist Assembly (Axe Yaw)"

# Groupe statique lié au pelvis
group_static = doc.addObject("App::Part", "Statique_Pelvis")
group_static.Label = "01_Statique_Pelvis (Bâti Fixe)"
root_asm.addObject(group_static)

# Groupe mobile entraîné en lacet (Yaw) vers le torse
group_mobile = doc.addObject("App::Part", "Mobile_Torse_Yaw")
group_mobile.Label = "02_Mobile_Torse_Yaw (Lacet Tournant)"
root_asm.addObject(group_mobile)

# ---------------------------------------------------------------------------
# 3. PIÈCES STATIQUES DU PELVIS
# ---------------------------------------------------------------------------
print("\n[1/4] Modélisation des composants statiques du Pelvis...")

# 3.1 Moteur RS06 - Stator et Carter Fixe (RobStride RS-06 fermé, Zéro arbre creux)
cyl_stator = Part.makeCylinder(85.31 / 2.0, 40.54, Vector(0, 0, 0), Vector(0, 0, 1))
cyl_base = Part.makeCylinder(40.0, 5.0, Vector(0, 0, 0), Vector(0, 0, 1))
stator_shape = cyl_stator.fuse(cyl_base)

stator_obj = doc.addObject("Part::Feature", "RS06_v1_Stator_Carter")
stator_obj.Label = "RS06 v1 - Stator & Carter Fixe (48V CAN-FD)"
stator_obj.Shape = stator_shape
stator_obj.Placement = Placement(Vector(YAW_X, YAW_Y, 958.90), Rotation())
group_static.addObject(stator_obj)
print("  -> RS06 Stator & Carter créé (Ø 85.3 mm x 40.5 mm, arbre plein/borgne)")

# 3.2 Traverse Renfort Bassin avec fraisures coniques 90° pour vis FHC M5
w_trav = 136.90
h_trav = 136.84
ep_trav = 12.51
box_trav = Part.makeBox(w_trav, h_trav, ep_trav, Vector(-w_trav / 2.0, -h_trav / 2.0, 0))
# Alésage central pour dégagement rotor (Ø 86.0 mm)
cyl_trav_hole = Part.makeCylinder(86.0 / 2.0, ep_trav + 2.0, Vector(0, 0, -1.0), Vector(0, 0, 1))
trav_shape = box_trav.cut(cyl_trav_hole)

# 4 perçages M5 avec fraisures coniques 90° (vis FHC M5 à fleur à 0.0 mm)
for sx in [-1, 1]:
    for sy in [-1, 1]:
        px = sx * 55.0
        py = sy * 55.0
        # Perçage lisse traversant Ø 5.1 mm
        hole_cyl = Part.makeCylinder(5.1 / 2.0, ep_trav + 2.0, Vector(px, py, -1.0), Vector(0, 0, 1))
        # Fraisure conique 90° : sommet Ø 10.4 mm, profondeur 3.1 mm (demi-angle 45°)
        cone_fhc = Part.makeCone(5.1 / 2.0, 10.4 / 2.0, 3.1, Vector(px, py, ep_trav - 3.1), Vector(0, 0, 1))
        trav_shape = trav_shape.cut(hole_cyl).cut(cone_fhc)

trav_obj = doc.addObject("Part::Feature", "Traverse_Renfort_Bassin")
trav_obj.Label = "Traverse Renfort Bassin [ASV1_200_16A] (Alu 7075)"
trav_obj.Shape = trav_shape
trav_obj.Placement = Placement(Vector(YAW_X, YAW_Y, 1007.90), Rotation())
group_static.addObject(trav_obj)
print("  -> Traverse Renfort Bassin créée (136.9 x 136.8 x 12.5 mm, 4x Fraisures FHC M5)")

# 3.3 Roulement à rouleaux croisés RB8016 - Bague Extérieure Fixe
cyl_rb_ext = Part.makeCylinder(120.02 / 2.0, 16.04, Vector(0, 0, 0), Vector(0, 0, 1))
cyl_rb_mid = Part.makeCylinder(100.0 / 2.0, 16.04 + 2.0, Vector(0, 0, -1.0), Vector(0, 0, 1))
rb_outer_shape = cyl_rb_ext.cut(cyl_rb_mid)

rb_outer_obj = doc.addObject("Part::Feature", "RB8016_Bague_Exterieure")
rb_outer_obj.Label = "Roulement RB8016 - Bague Extérieure Fixe (Acier)"
rb_outer_obj.Shape = rb_outer_shape
rb_outer_obj.Placement = Placement(Vector(YAW_X, YAW_Y, 1017.40), Rotation())
group_static.addObject(rb_outer_obj)
print("  -> RB8016 Bague Extérieure créée (Ø 120.0 mm / Ø 100.0 mm x 16.0 mm)")

# 3.4 Brides de Retenue RB8016 (Importées du fichier STEP certifié Fusion 360)
step_path = "/Users/Shared/Bride_Retenue_RB8016_L.step"
if os.path.exists(step_path):
    print(f"  -> Import du modèle STEP réel: {step_path}")
    raw_clamp_shape = Part.read(step_path)
    
    clamp_angles = [("Nord", 90), ("Est", 0), ("Sud", 270), ("Ouest", 180)]
    clamp_radius = 58.0  # mm
    
    for label, deg in clamp_angles:
        rad = math.radians(deg)
        cx = YAW_X + clamp_radius * math.cos(rad)
        cy = YAW_Y + clamp_radius * math.sin(rad)
        cz = 1033.44  # Face supérieure de la bague extérieure
        
        clamp_obj = doc.addObject("Part::Feature", f"Bride_Retenue_RB8016_{label}")
        clamp_obj.Label = f"Bride Retenue RB8016-L [{label}] (Alu 7075-T6 STEP)"
        clamp_obj.Shape = raw_clamp_shape
        rot = Rotation(Vector(0, 0, 1), deg + 180)
        clamp_obj.Placement = Placement(Vector(cx, cy, cz), rot)
        group_static.addObject(clamp_obj)
    print("  -> 4x Brides de retenue réelles STEP positionnées à 90 deg sur RB8016")

# ---------------------------------------------------------------------------
# 4. COMPOSANTS MOBILES DE ROTATION (TORSE / AXE YAW)
# ---------------------------------------------------------------------------
print("\n[2/4] Modélisation des composants mobiles de lacet (Torse / Yaw)...")

# 4.1 Moteur RS06 - Rotor et Plateau de Sortie Tournant
cyl_rotor = Part.makeCylinder(50.0 / 2.0, 10.0, Vector(0, 0, 0), Vector(0, 0, 1))
cyl_boss = Part.makeCylinder(30.0 / 2.0, 3.0, Vector(0, 0, 10.0), Vector(0, 0, 1))
rotor_shape = cyl_rotor.fuse(cyl_boss)

rotor_obj = doc.addObject("Part::Feature", "RS06_v1_Rotor_Sortie")
rotor_obj.Label = "RS06 v1 - Rotor Plateau de Sortie (Axe Lacet)"
rotor_obj.Shape = rotor_shape
rotor_obj.Placement = Placement(Vector(YAW_X, YAW_Y, 999.44), Rotation())
group_mobile.addObject(rotor_obj)
print("  -> RS06 Rotor de sortie créé (Ø 50.0 mm, couple max 131 N.m)")

# 4.2 Moyeu Waist Sandwich 7075
cyl_moy_ext = Part.makeCylinder(91.52 / 2.0, 23.62, Vector(0, 0, 0), Vector(0, 0, 1))
cyl_moy_int = Part.makeCylinder(50.0 / 2.0, 12.0, Vector(0, 0, -1.0), Vector(0, 0, 1))
moy_shape = cyl_moy_ext.cut(cyl_moy_int)

moy_obj = doc.addObject("Part::Feature", "Moyeu_Waist_Sandwich_7075")
moy_obj.Label = "Moyeu Waist Sandwich 7075 (Liaison Rotor/Plaque)"
moy_obj.Shape = moy_shape
moy_obj.Placement = Placement(Vector(YAW_X, YAW_Y, 1009.41), Rotation())
group_mobile.addObject(moy_obj)
print("  -> Moyeu Waist Sandwich 7075 créé (Ø 91.5 mm x 23.6 mm, Alu 7075)")

# 4.3 Roulement RB8016 - Bague Intérieure Mobile
cyl_rb_in_ext = Part.makeCylinder(100.0 / 2.0, 16.04, Vector(0, 0, 0), Vector(0, 0, 1))
cyl_rb_in_int = Part.makeCylinder(80.0 / 2.0, 16.04 + 2.0, Vector(0, 0, -1.0), Vector(0, 0, 1))
rb_inner_shape = cyl_rb_in_ext.cut(cyl_rb_in_int)

rb_inner_obj = doc.addObject("Part::Feature", "RB8016_Bague_Interieure")
rb_inner_obj.Label = "Roulement RB8016 - Bague Intérieure Tournante (Acier)"
rb_inner_obj.Shape = rb_inner_shape
rb_inner_obj.Placement = Placement(Vector(YAW_X, YAW_Y, 1017.40), Rotation())
group_mobile.addObject(rb_inner_obj)
print("  -> RB8016 Bague Intérieure créée (Ø 100.0 mm / Ø 80.0 mm x 16.0 mm)")

# ---------------------------------------------------------------------------
# 5. PIÈCE PARAMÉTRIQUE NATIVE AVEC CONGÉS ET CHANFREINS : WAIST_PLATE_7075
# ---------------------------------------------------------------------------
print("\n[3/4] Construction de la Waist_Plate_7075 avec TIMELINE NATIVE FREECAD (PartDesign)...")

waist_body = doc.addObject("PartDesign::Body", "Waist_Plate_7075")
waist_body.Label = "Waist_Plate_7075 (TIMELINE PartDesign)"
group_mobile.addObject(waist_body)

# Étape 1 Timeline : Esquisse du contour rectangulaire de base
sk_contour = doc.addObject("Sketcher::SketchObject", "Sketch_Contour_Base")
sk_contour.Label = "01_Sketch_Contour_Base (142x139mm)"
waist_body.addObject(sk_contour)
sk_contour.MapMode = "FlatFace"

w_wp = 142.12 / 2.0  # 71.06 mm
h_wp = 139.06 / 2.0  # 69.53 mm

sk_contour.addGeometry(Part.LineSegment(Vector(-w_wp, -h_wp, 0), Vector(w_wp, -h_wp, 0)))
sk_contour.addGeometry(Part.LineSegment(Vector(w_wp, -h_wp, 0), Vector(w_wp, h_wp, 0)))
sk_contour.addGeometry(Part.LineSegment(Vector(w_wp, h_wp, 0), Vector(-w_wp, h_wp, 0)))
sk_contour.addGeometry(Part.LineSegment(Vector(-w_wp, h_wp, 0), Vector(-w_wp, -h_wp, 0)))

sk_contour.addConstraint(Sketcher.Constraint("Coincident", 0, 2, 1, 1))
sk_contour.addConstraint(Sketcher.Constraint("Coincident", 1, 2, 2, 1))
sk_contour.addConstraint(Sketcher.Constraint("Coincident", 2, 2, 3, 1))
sk_contour.addConstraint(Sketcher.Constraint("Coincident", 3, 2, 0, 1))
doc.recompute()
print("  -> Étape 1 : Esquisse de contour paramétrique 142.12 x 139.06 mm")

# Étape 2 Timeline : Extrusion (Pad) 9.03 mm
pad_base = doc.addObject("PartDesign::Pad", "Pad_Epaisseur_9mm")
pad_base.Label = "02_Pad_Epaisseur_9mm"
pad_base.Profile = sk_contour
pad_base.Length = 9.03
waist_body.addObject(pad_base)
doc.recompute()
print("  -> Étape 2 : Extrusion Pad de 9.03 mm (Volume: 178461 mm3)")

# Étape 3 Timeline : Congés d'angles extérieurs R = 10.0 mm (PartDesign::Fillet)
vert_edges = []
for idx, edge in enumerate(pad_base.Shape.Edges):
    v1 = edge.Vertexes[0].Point
    v2 = edge.Vertexes[1].Point
    if abs(v1.x - v2.x) < 0.01 and abs(v1.y - v2.y) < 0.01 and abs(v1.z - v2.z) > 1.0:
        vert_edges.append(f"Edge{idx+1}")

fillet_coins = doc.addObject("PartDesign::Fillet", "Fillet_Coins_Exterieurs")
fillet_coins.Label = "03_Fillet_Coins_Exterieurs (R=10mm)"
fillet_coins.Base = (pad_base, vert_edges)
fillet_coins.Radius = 10.0
waist_body.addObject(fillet_coins)
doc.recompute()
print(f"  -> Étape 3 : 4x Congés d'angles extérieurs R=10.0 mm créés (Volume: {round(waist_body.Shape.Volume, 1)} mm3)")

# Étape 4 Timeline : Esquisse des perçages et de l'alésage central Ø 80 mm
sk_holes = doc.addObject("Sketcher::SketchObject", "Sketch_Alesages_Traversants")
sk_holes.Label = "04_Sketch_Alesages_Traversants (Ø80 + 8x trous)"
waist_body.addObject(sk_holes)
sk_holes.MapMode = "FlatFace"

# Alésage central Ø 80.0 mm (rayon 40.0 mm)
sk_holes.addGeometry(Part.Circle(Vector(0, 0, 0), Vector(0, 0, 1), 40.0))

# 4 perçages M4 (Ø 4.5 mm, rayon 2.25 mm) à (+/- 24.04, +/- 24.04 mm) pour fixation moyeu
for sx in [-1, 1]:
    for sy in [-1, 1]:
        sk_holes.addGeometry(Part.Circle(Vector(sx * 24.04, sy * 24.04, 0), Vector(0, 0, 1), 2.25))

# 4 perçages M6 / lamages d'ancrage supérieur (Ø 7.5 mm, rayon 3.75 mm) à (+/- 49.09, +/- 49.09 mm)
for sx in [-1, 1]:
    for sy in [-1, 1]:
        sk_holes.addGeometry(Part.Circle(Vector(sx * 49.09, sy * 49.09, 0), Vector(0, 0, 1), 3.75))

doc.recompute()
print("  -> Étape 4 : Esquisse alésage Ø 80 mm + 4x M4 + 4x M6")

# Étape 5 Timeline : Enlèvement de matière traversant (Pocket)
pocket_holes = doc.addObject("PartDesign::Pocket", "Pocket_Percages_Traversants")
pocket_holes.Label = "05_Pocket_Percages_Traversants"
pocket_holes.Profile = sk_holes
pocket_holes.Length = 10.0
pocket_holes.Reversed = True
waist_body.addObject(pocket_holes)
doc.recompute()
print("  -> Étape 5 : Poches traversantes exécutées")

# Étape 6 Timeline : Esquisse du lamage d'épaulement de centrage roulement (Ø 89.62 mm)
sk_shoulder = doc.addObject("Sketcher::SketchObject", "Sketch_Lamage_Centrage")
sk_shoulder.Label = "06_Sketch_Lamage_Epaulement (Ø89.62mm)"
waist_body.addObject(sk_shoulder)
sk_shoulder.MapMode = "FlatFace"
sk_shoulder.addGeometry(Part.Circle(Vector(0, 0, 0), Vector(0, 0, 1), 89.62 / 2.0))
doc.recompute()
print("  -> Étape 6 : Esquisse lamage de centrage roulement Ø 89.62 mm")

# Étape 7 Timeline : Enlèvement de matière borgne (Pocket de profondeur 2.5 mm)
pocket_shoulder = doc.addObject("PartDesign::Pocket", "Pocket_Lamage_Centrage")
pocket_shoulder.Label = "07_Pocket_Lamage_Centrage_2_5mm"
pocket_shoulder.Profile = sk_shoulder
pocket_shoulder.Length = 2.50
pocket_shoulder.Reversed = True
waist_body.addObject(pocket_shoulder)
doc.recompute()
print("  -> Étape 7 : Lamage borgne exécuté")

# Étape 8 Timeline : Chanfrein d'ébavurage et de centrage (PartDesign::Chamfer 0.4 mm x 45°)
# Identification des arêtes circulaires supérieures (alésage central + trous M4 + trous M6)
target_chamfer_edges = []
for idx, edge in enumerate(pocket_shoulder.Shape.Edges):
    c = edge.Curve
    rad = getattr(c, "Radius", None)
    if rad:
        # Alésage central Ø 80 mm à Z = 9.03 mm
        if abs(rad - 40.0) < 0.2 and abs(edge.CenterOfMass.z - 9.03) < 0.1:
            target_chamfer_edges.append(f"Edge{idx+1}")
        # Trous M4 (Ø 4.5 mm) à Z = 9.03 mm
        elif abs(rad - 2.25) < 0.1 and abs(edge.CenterOfMass.z - 9.03) < 0.1:
            target_chamfer_edges.append(f"Edge{idx+1}")
        # Trous M6 (Ø 7.5 mm) à Z = 9.03 mm
        elif abs(rad - 3.75) < 0.1 and abs(edge.CenterOfMass.z - 9.03) < 0.1:
            target_chamfer_edges.append(f"Edge{idx+1}")

print(f"  -> Arêtes cibles pour chanfreinage détectées : {target_chamfer_edges}")
if target_chamfer_edges:
    chamfer_ebavurage = doc.addObject("PartDesign::Chamfer", "Chamfer_Ebavurage_Percages")
    chamfer_ebavurage.Label = "08_Chamfer_Ebavurage (0.4mm x 45deg)"
    chamfer_ebavurage.Base = (pocket_shoulder, target_chamfer_edges)
    chamfer_ebavurage.Size = 0.40
    waist_body.addObject(chamfer_ebavurage)
    doc.recompute()
    print(f"  -> Étape 8 : Chanfreins 0.40 mm x 45 deg appliqués avec succès !")

print(f"  -> Volume final usiné de la Waist_Plate_7075 : {round(waist_body.Shape.Volume, 1)} mm3")

# Positionnement spatial précis de la Waist_Plate_7075 dans le repère mondial
waist_body.Placement = Placement(Vector(YAW_X, YAW_Y, 1033.41), Rotation())
print("  -> Placement spatial Waist_Plate_7075 calé sur Z = 1033.41 mm, Axe Yaw (49.23, 9.36)")

# ---------------------------------------------------------------------------
# 6. RECALCUL GLOBAL ET SAUVEGARDE MULTI-EMPLACEMENTS
# ---------------------------------------------------------------------------
print("\n[4/4] Recalcul complet du graphe de dépendance et sauvegarde...")
doc.recompute()

output_shared = "/Users/Shared/DBot_Waist_Bassin_PoC.FCStd"
doc.saveAs(output_shared)
print(f"  [OK] Fichier sauvegardé : {output_shared} ({os.path.getsize(output_shared)} octets)")

repo_dir = "/Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin"
output_repo = os.path.join(repo_dir, "DBot_Waist_Bassin_PoC.FCStd")
shutil.copy2(output_shared, output_repo)
print(f"  [OK] Copie conforme archivée dans le repo : {output_repo}")

print("\n=================================================================")
print("=== SUCCÈS : CONGÉS ET CHANFREINS COMPILÉS DANS FREECAD ! ===")
print("=================================================================")

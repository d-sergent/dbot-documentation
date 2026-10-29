#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
simulate_corniere_torsion.py — Simulation RDM Éléments Finis Souveraine (FreeCAD 1.1 + CalculiX)

Ce script réalise l'analyse par éléments finis (FEA) de la Cornière Haute Nervurée 7075-T6
du robot D-Bot V1 à partir des exports STEP de 'Bibliotheque_Composants_STEP'.

Capacités :
  - Import direct du STEP B-Rep
  - Identification topologique automatique des faces d'encastrement et d'application des charges (robuste au renommage)
  - Assignation des propriétés élasto-plastiques certifiées Aluminium 7075-T651 (E = 71,7 GPa, nu = 0,33, Re = 505 MPa)
  - Génération d'un maillage volumique tétraédrique quadratique (C3D10 à 10 nœuds) via Gmsh
  - Résolution statique linéaire / non-linéaire via CalculiX (ccx)
  - Post-traitement analytique : Flèche résiduelle (mm), Tenseur de contraintes & Von Mises (MPa), Facteur de sécurité Sf
  - Sauvegarde du document complet natif FreeCAD .FCStd pour inspection visuelle 3D dans le GUI FreeCAD

Exécution recommandée :
  /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd simulate_corniere_torsion.py [--case torsion|traction|flexion] [--force 210]
"""

import os
import sys
import math
import shlex
import shutil
import tempfile
import argparse
import subprocess

# Imports FreeCAD
try:
    import FreeCAD
    import Part
    import ObjectsFem
    from femmesh.gmshtools import GmshTools
    from femtools import ccxtools
    import feminout.importCcxFrdResults as importCcxFrdResults
    import feminout.importCcxDatResults as importCcxDatResults
except ImportError as e:
    print(f"❌ Erreur critique d'import FreeCAD : {e}")
    print("Ce script doit être exécuté avec l'interpréteur FreeCAD (ex: freecadcmd).")
    sys.exit(1)

# Paramètres Matériau Aluminium 7075-T651 (Certifié D-Bot)
ALU_7075_T6 = {
    "Name": "Aluminium-7075-T651",
    "YoungsModulus": "71700 MPa",
    "PoissonRatio": "0.33",
    "Density": "2810 kg/m^3",
    "YieldStrength": 505.0,  # Re (MPa)
    "UltimateStrength": 572.0  # Rm (MPa)
}

# Chemins par défaut (Standard Pack Technique Autonome par Composant)
DEFAULT_STEP_PATH = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/Bibliotheque_Composants_STEP/Corniere_haute.step"
DEFAULT_OUTPUT_DIR = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots/Pieces_Isolees/Corniere_haute"
DEFAULT_OUTPUT_FCSTD = os.path.join(DEFAULT_OUTPUT_DIR, "Corniere_haute_FEA_Results.FCStd")
DEFAULT_CCX_BIN = "/Applications/FreeCAD.app/Contents/Resources/bin/ccx"


def find_topological_features(shape):
    """
    Identifie de manière géométrique et déterministe les faces d'appui et de fixation
    sur le solide B-Rep de la cornière, indépendamment des index 'FaceX' variables.
    """
    bbox = shape.BoundBox
    z_min = bbox.ZMin
    z_max = bbox.ZMax
    
    bottom_face_name = None
    bottom_hole_name = None
    top_slot_cylinders = []
    top_slot_planes = []
    top_mating_face_name = None
    
    for i, face in enumerate(shape.Faces):
        face_name = f"Face{i+1}"
        com = face.CenterOfMass
        surf_type = face.Surface.__class__.__name__
        
        # 1. Semelle inférieure (Plan Z_min avec normale pointant vers -Z)
        if surf_type == "Plane" and abs(com.z - z_min) < 0.5:
            norm = face.normalAt(0, 0)
            if norm.z < -0.8 and face.Area > 200.0:
                bottom_face_name = face_name
                
        # 2. Perçage cylindrique inférieur M4 (rayon ~ 2,15 mm proche de Z_min)
        if surf_type == "Cylinder" and com.z < (z_min + 15.0):
            rad = getattr(face.Surface, "Radius", 0.0)
            if abs(rad - 2.15) < 0.2:
                bottom_hole_name = face_name
                
        # 3. Lumière oblongue supérieure (Z proche de Z_max, Y proche de -78 mm)
        if com.z > (z_max - 15.0):
            if surf_type == "Cylinder":
                rad = getattr(face.Surface, "Radius", 0.0)
                axis = getattr(face.Surface, "Axis", FreeCAD.Vector(0.0, 0.0, 0.0))
                # Le trou oblong M4 est traversant selon l'axe Y (abs(axis.y) > 0.9)
                # Cela élimine rigoureusement le congé horizontal Face1 (axe X)
                if abs(rad - 2.10) < 0.1 and abs(axis.y) > 0.9:
                    top_slot_cylinders.append(face_name)
            elif surf_type == "Plane" and face.Area < 20.0 and abs(com.y - (-77.88)) < 0.5:
                # Flancs latéraux plans verticaux de l'oblong (Face21, Face23)
                top_slot_planes.append(face_name)
                
            # Face d'appui plane supérieure (contact avec rondelle Nord-Lock et tête de vis M4)
            if surf_type == "Plane" and face.Area > 200.0 and abs(com.y - (-79.88)) < 0.5:
                top_mating_face_name = face_name

    return {
        "bottom_face": bottom_face_name,
        "bottom_hole": bottom_hole_name,
        "top_slot_cylinders": top_slot_cylinders,
        "top_slot_planes": top_slot_planes,
        "top_mating_face": top_mating_face_name
    }


def run_fea_simulation(step_path, load_case="torsion", force_n=210.0, cl_max=2.5, cl_min=0.8, output_fcstd=None):
    """
    Exécute le pipeline complet FEA CalculiX dans FreeCAD.
    """
    print("\n" + "=" * 75)
    print(" 🛠️  PIPELINE SOUVERAIN FREECAD 1.1 / CALCULIX — ANALYSE RDM D-BOT")
    print("=" * 75)
    print(f"  Fichier STEP source  : {step_path}")
    print(f"  Cas de charge choisi : {load_case.upper()}")
    print(f"  Effort appliqué      : {force_n:.1f} N")
    print(f"  Discrétisation Gmsh  : ClMax = {cl_max:.1f} mm, ClMin = {cl_min:.1f} mm (Tétraèdres quadratiques C3D10)")
    
    if not os.path.exists(step_path):
        print(f"❌ Erreur : Le fichier STEP '{step_path}' est introuvable.")
        return False

    # 1. Création du Document FreeCAD
    doc = FreeCAD.newDocument("Corniere_Haute_FEA")
    shape = Part.read(step_path)
    part_obj = doc.addObject("Part::Feature", "Corniere_Haute_7075")
    part_obj.Shape = shape
    doc.recompute()
    
    volume_mm3 = shape.Volume
    masse_g = (volume_mm3 * 2.810e-3)
    print(f"  Volume B-Rep net     : {volume_mm3:.2f} mm³ ({volume_mm3/1000.0:.2f} cm³)")
    print(f"  Masse 7075-T6 estimée: {masse_g:.2f} g")

    # 2. Identification Topologique des Faces
    features = find_topological_features(shape)
    print(f"  Semelle d'assise (base)   : {features['bottom_face']}")
    print(f"  Trou vis inférieure M4    : {features['bottom_hole']}")
    print(f"  Oblong haut M4 (cylindres): {features['top_slot_cylinders']}")
    print(f"  Oblong haut M4 (flancs)   : {features['top_slot_planes']}")
    print(f"  Portée d'appui haute      : {features['top_mating_face']}")

    if not features["bottom_face"]:
        print("❌ Erreur : Impossible d'identifier la semelle d'appui inférieure.")
        return False

    # 3. Création du Conteneur d'Analyse et du Solveur
    analysis = ObjectsFem.makeAnalysis(doc, "Analysis")
    solver = ObjectsFem.makeSolverCalculiXCcxTools(doc, "CalculiX")
    analysis.addObject(solver)

    # 4. Matériau 7075-T651
    mat_obj = ObjectsFem.makeMaterialSolid(doc, "Alu7075T6")
    mat_dict = {
        "Name": ALU_7075_T6["Name"],
        "YoungsModulus": ALU_7075_T6["YoungsModulus"],
        "PoissonRatio": ALU_7075_T6["PoissonRatio"],
        "Density": ALU_7075_T6["Density"]
    }
    for k, v in mat_dict.items():
        cur = dict(mat_obj.Material)
        cur[k] = v
        mat_obj.Material = cur
    analysis.addObject(mat_obj)

    # 5. Conditions aux Limites : Encastrement de la Base
    con_fixed = ObjectsFem.makeConstraintFixed(doc, "FixedBase")
    fixed_refs = [(part_obj, features["bottom_face"])]
    if features["bottom_hole"]:
        fixed_refs.append((part_obj, features["bottom_hole"]))
    con_fixed.References = fixed_refs
    analysis.addObject(con_fixed)

    # 6. Conditions aux Limites : Chargement selon le Cas
    con_force = ObjectsFem.makeConstraintForce(doc, "AppliedLoad")
    con_force.Force = f"{force_n:.1f} N"
    
    if load_case == "torsion":
        # Effort de lacet transversal (cisaillement selon X):
        # La vis prend appui sur le flanc intérieur vertical de l'oblong (Face23)
        target_face = features["top_slot_planes"][1] if len(features["top_slot_planes"]) > 1 else features["top_slot_planes"][0]
        con_force.References = [(part_obj, target_face)]
        con_force.DirectionVector = FreeCAD.Vector(1.0, 0.0, 0.0)
        con_force.Reversed = False
        print(f"  --> Charge appliquée sur le flanc intérieur de l'oblong : {target_face} (direction +X)")
    elif load_case == "traction":
        # Effort axial le long du montant (traction dynamique Z):
        # La vis prend appui sur le demi-cylindre supérieur de l'oblong (Face22)
        target_face = features["top_slot_cylinders"][0] if features["top_slot_cylinders"] else features["top_mating_face"]
        con_force.References = [(part_obj, target_face)]
        con_force.DirectionVector = FreeCAD.Vector(0.0, 0.0, 1.0)
        con_force.Reversed = False
        print(f"  --> Charge appliquée sur la voûte cylindrique de l'oblong : {target_face} (direction +Z)")
    elif load_case == "flexion":
        # Force normale au plan de la patte supérieure (flexion frontale Y sur la face d'appui de rondelle Face2)
        target_face = features["top_mating_face"]
        con_force.References = [(part_obj, target_face)]
        con_force.DirectionVector = FreeCAD.Vector(0.0, 1.0, 0.0)
        con_force.Reversed = False
        print(f"  --> Charge appliquée sur la portée d'assise de serrage : {target_face} (direction +Y)")
    else:
        target_face = features["top_slot_planes"][0]
        con_force.References = [(part_obj, target_face)]
        con_force.DirectionVector = FreeCAD.Vector(1.0, 0.0, 0.0)
        con_force.Reversed = False
        
    analysis.addObject(con_force)

    # 7. Maillage Volumique Gmsh (C3D10 Quadratique)
    print("\n⚙️  Génération du maillage tétraédrique volumique (Gmsh)...")
    mesh_obj = ObjectsFem.makeMeshGmsh(doc, "FEMMeshGmsh")
    mesh_obj.Shape = part_obj
    mesh_obj.CharacteristicLengthMax = cl_max
    mesh_obj.CharacteristicLengthMin = cl_min
    mesh_obj.ElementDimension = "3D"
    mesh_obj.ElementOrder = "2nd"
    analysis.addObject(mesh_obj)
    doc.recompute()

    gmsh_mesh = GmshTools(mesh_obj)
    gmsh_mesh.create_mesh()
    node_count = mesh_obj.FemMesh.NodeCount
    elem_count = mesh_obj.FemMesh.VolumeCount
    print(f"  ✅ Maillage réussi : {node_count:,} nœuds, {elem_count:,} éléments C3D10.")

    # 8. Préparation & Exécution du Solveur CalculiX
    work_dir = tempfile.mkdtemp(prefix="dbot_fea_")
    print(f"\n🚀 Résolution CalculiX en cours (dossier temporaire: {work_dir})...")
    
    fea = ccxtools.FemToolsCcx(analysis=analysis, solver=solver, test_mode=True)
    fea.setup_working_dir(work_dir)
    fea.update_objects()
    fea.write_inp_file()

    inp_name = "FEMMeshGmsh"
    ccx_bin = DEFAULT_CCX_BIN if os.path.exists(DEFAULT_CCX_BIN) else (shutil.which("ccx") or "ccx")

    res = subprocess.run([ccx_bin, "-i", inp_name], cwd=work_dir, capture_output=True, text=True, shell=False)
    if res.returncode != 0:
        print(f"❌ Erreur lors de l'exécution CalculiX :\n{res.stderr}")
        return False
    print("  ✅ CalculiX a résolu le système avec succès !")

    # 9. Importation des Résultats
    frd_file = os.path.join(work_dir, inp_name + ".frd")
    dat_file = os.path.join(work_dir, inp_name + ".dat")

    if os.path.exists(frd_file):
        importCcxFrdResults.importFrd(frd_file, analysis, "CCX_", solver.AnalysisType)
    if os.path.exists(dat_file):
        importCcxDatResults.import_dat(dat_file, analysis)
        
    doc.recompute()

    # 10. Traitement Statistique des Résultats
    res_obj = doc.getObject("CCX_Results")
    if not res_obj:
        print("❌ Erreur : Objet CCX_Results absent après résolution.")
        return False

    disp_lengths = res_obj.DisplacementLengths
    disp_max = max(disp_lengths)
    
    sxx = res_obj.NodeStressXX
    syy = res_obj.NodeStressYY
    szz = res_obj.NodeStressZZ
    sxy = res_obj.NodeStressXY
    sxz = res_obj.NodeStressXZ
    syz = res_obj.NodeStressYZ

    vm_stresses = []
    for i in range(len(sxx)):
        s_diff_zz_xx = szz[i] - sxx[i]
        vm = math.sqrt(
            0.5 * (
                (sxx[i] - syy[i]) ** 2 +
                (syy[i] - szz[i]) ** 2 +
                (s_diff_zz_xx) ** 2 +
                6.0 * (sxy[i] ** 2 + syz[i] ** 2 + sxz[i] ** 2)
            )
        )
        vm_stresses.append(vm)

    vm_max = max(vm_stresses)
    vm_sorted = sorted(vm_stresses)
    idx_p95 = int(len(vm_sorted) * 0.95)
    vm_p95 = vm_sorted[idx_p95]
    
    re_7075 = ALU_7075_T6["YieldStrength"]
    sf_peak = re_7075 / vm_max if vm_max > 0 else 999.0
    sf_p95 = re_7075 / vm_p95 if vm_p95 > 0 else 999.0

    print("\n" + "=" * 75)
    print("   📊 RÉSULTATS D'ANALYSE RDM D-BOT (FREECAD / CALCULIX)")
    print("=" * 75)
    print(f"  Cas de chargement             : {load_case.upper()} (F = {force_n:.1f} N)")
    print(f"  Déplacement maximal (Flèche)  : {disp_max:.4f} mm")
    print(f"  Contrainte de Von Mises crête : {vm_max:.2f} MPa")
    print(f"  Contrainte Von Mises (P95)    : {vm_p95:.2f} MPa (filtre des singularités de maillage)")
    print(f"  Limite élastique Re (7075-T6) : {re_7075:.1f} MPa")
    print(f"  Facteur de sécurité crête Sf  : {sf_peak:.2f}")
    print(f"  Facteur de sécurité P95 Sf    : {sf_p95:.2f}")
    print("-" * 75)
    
    # Évaluation des critères de conception D-Bot
    valid_fleche = (disp_max < 0.05)
    valid_sf = (sf_p95 >= 10.0)
    
    if valid_fleche and valid_sf:
        print("  🎯 STATUT CONCEPTION : EXCELLENT ! Conforme aux spécifications D-Bot. ✅")
    else:
        print(f"  ⚠️  STATUT CONCEPTION : Surveillance requise (Flèche={disp_max:.4f} mm, Sf_P95={sf_p95:.2f})")
    print("=" * 75)

    # 11. Sauvegarde du Projet Complet FreeCAD
    if output_fcstd is None:
        output_fcstd = DEFAULT_OUTPUT_FCSTD
        
    os.makedirs(os.path.dirname(output_fcstd), exist_ok=True)
    doc.saveAs(output_fcstd)
    print(f"\n💾 Document FreeCAD 3D complet sauvegardé :")
    print(f"   --> {output_fcstd}")
    print("   (Vous pouvez l'ouvrir directement dans FreeCAD pour visualiser la cartographie couleur 3D des contraintes !)")

    # Nettoyage dossier temporaire
    shutil.rmtree(work_dir, ignore_errors=True)
    return True


def main():
    parser = argparse.ArgumentParser(description="Simulation RDM Souveraine FreeCAD / CalculiX pour le projet D-Bot")
    parser.add_argument("--step", default=DEFAULT_STEP_PATH, help="Chemin du fichier STEP à simuler")
    parser.add_argument("--case", choices=["torsion", "traction", "flexion"], default="torsion", help="Cas de charge")
    parser.add_argument("--force", type=float, default=210.0, help="Effort appliqué en Newtons (défaut : 210 N)")
    parser.add_argument("--clmax", type=float, default=2.5, help="Taille max des éléments Gmsh en mm (défaut : 2.5 mm)")
    parser.add_argument("--clmin", type=float, default=0.8, help="Taille min des éléments Gmsh en mm (défaut : 0.8 mm)")
    parser.add_argument("--out", default=DEFAULT_OUTPUT_FCSTD, help="Fichier FreeCAD .FCStd de sortie")

    raw_args = []
    if "--pass" in sys.argv:
        pass_idx = sys.argv.index("--pass")
        if pass_idx + 1 < len(sys.argv):
            pass_str = sys.argv[pass_idx + 1]
            raw_args = shlex.split(pass_str)
    else:
        # Arguments directs après le nom du script
        for i, a in enumerate(sys.argv[1:], start=1):
            if not a.endswith(".py") and not a.startswith("-"):
                continue
            if a.endswith(".py"):
                raw_args = sys.argv[i+1:]
                break

    args = parser.parse_args(raw_args)
    success = run_fea_simulation(
        step_path=args.step,
        load_case=args.case,
        force_n=args.force,
        cl_max=args.clmax,
        cl_min=args.clmin,
        output_fcstd=args.out
    )
    
    # Sortie propre sans segfault de destructeur statique OpenCASCADE
    os._exit(0 if success else 1)


if __name__ in ("__main__", "simulate_corniere_torsion"):
    main()

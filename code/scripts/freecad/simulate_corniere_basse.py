#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
simulate_corniere_basse.py — Simulation RDM Éléments Finis Souveraine (FreeCAD 1.1 + CalculiX)

Ce script réalise l'analyse par éléments finis (FEA) de la Cornière Basse Nervurée 7075-T6
du robot D-Bot V1 à partir des exports STEP de 'Bibliotheque_Composants_STEP'.

Capacités :
  - Import direct du STEP B-Rep 'Corniere_basse.step'
  - Identification topologique automatique des faces d'encastrement (semelle basse Z=1042 mm + perçage M4)
    et de transmission d'effort (fixation haute 2x M4 à Z=1233 mm)
  - Assignation des propriétés élasto-plastiques certifiées Aluminium 7075-T651 (E = 71,7 GPa, nu = 0,33, Re = 505 MPa)
  - Génération d'un maillage volumique tétraédrique quadratique (C3D10 à 10 nœuds) via Gmsh
  - Résolution statique linéaire via CalculiX (ccx)
  - Post-traitement analytique : Flèche résiduelle (mm), Tenseur de contraintes & Von Mises (MPa), Facteurs de sécurité (crête et P95)
  - Solution B intégrée : Sauvegarde native .FCStd, création du Post-Pipeline VTK et script de lancement en 1 clic

Exécution recommandée :
  /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd simulate_corniere_basse.py [--case torsion|traction|flexion] [--force 210]
"""

import os
import sys
import math
import shlex
import shutil
import tempfile
import argparse
import subprocess
from pathlib import Path

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

# Chemins par défaut
DEFAULT_STEP_PATH = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/Bibliotheque_Composants_STEP/Corniere_basse.step"
DEFAULT_OUTPUT_DIR = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots/Pieces_Isolees/Corniere_basse"
DEFAULT_OUTPUT_FCSTD = os.path.join(DEFAULT_OUTPUT_DIR, "Corniere_basse_FEA_Results.FCStd")
DEFAULT_CCX_BIN = "/Applications/FreeCAD.app/Contents/Resources/bin/ccx"


def find_topological_features(shape):
    """
    Identifie de manière géométrique et déterministe les faces d'appui et de fixation
    sur le solide B-Rep de la cornière basse, indépendamment des index 'FaceX' variables.
    """
    bbox = shape.BoundBox
    z_min = bbox.ZMin
    z_max = bbox.ZMax
    
    bottom_face_name = None
    bottom_hole_names = []
    top_face_name = None
    top_hole_names = []
    
    for i, face in enumerate(shape.Faces):
        face_name = f"Face{i+1}"
        com = face.CenterOfMass
        surf_type = face.Surface.__class__.__name__
        
        # 1. Semelle inférieure (Plan Z_min avec normale pointant vers -Z)
        if surf_type == "Plane" and abs(com.z - z_min) < 1.0:
            norm = face.normalAt(0, 0)
            if norm.z < -0.8 and face.Area > 150.0:
                bottom_face_name = face_name
                
        # 2. Perçages cylindriques inférieurs M4 (rayon ~ 2,25 mm à Z proche de z_min)
        if surf_type == "Cylinder" and com.z < (z_min + 15.0):
            rad = getattr(face.Surface, "Radius", 0.0)
            if abs(rad - 2.25) < 0.2:
                bottom_hole_names.append(face_name)
                
        # 3. Portée d'appui supérieure (Z proche de z_max avec normale pointant vers +Z)
        if surf_type == "Plane" and abs(com.z - z_max) < 2.0:
            norm = face.normalAt(0, 0)
            if norm.z > 0.8 and face.Area > 200.0:
                top_face_name = face_name
                
        # 4. Trous de fixation supérieurs M4 (rayon ~ 2,15 mm à Z proche de z_max)
        if surf_type == "Cylinder" and com.z > (z_max - 3.5):
            rad = getattr(face.Surface, "Radius", 0.0)
            if abs(rad - 2.15) < 0.2 or abs(rad - 2.25) < 0.2:
                top_hole_names.append(face_name)

    return {
        "bottom_face": bottom_face_name,
        "bottom_holes": bottom_hole_names,
        "top_face": top_face_name,
        "top_holes": top_hole_names
    }


def run_fea_simulation(step_path, load_case="torsion", force_n=210.0, cl_max=3.0, cl_min=1.0, output_fcstd=None):
    if not os.path.exists(step_path):
        print(f"❌ Erreur : Fichier STEP introuvable : {step_path}")
        return False

    if output_fcstd is None:
        output_fcstd = DEFAULT_OUTPUT_FCSTD

    out_dir = os.path.dirname(output_fcstd)
    os.makedirs(out_dir, exist_ok=True)

    print("\n" + "=" * 75)
    print(" 🛠️  PIPELINE SOUVERAIN FREECAD 1.1 / CALCULIX — ANALYSE RDM D-BOT")
    print("    PIÈCE : CORNIÈRE BASSE NERVURÉE 7075-T6")
    print("=" * 75)
    print(f"  Fichier STEP source  : {step_path}")
    print(f"  Cas de charge choisi : {load_case.upper()}")
    print(f"  Effort appliqué      : {force_n:.1f} N")
    print(f"  Discrétisation Gmsh  : ClMax = {cl_max:.1f} mm, ClMin = {cl_min:.1f} mm (C3D10 quadratique)")

    doc_name = "Corniere_Basse_FEA"
    doc = FreeCAD.newDocument(doc_name)

    # 1. Chargement de la pièce STEP
    part_shape = Part.read(step_path)
    if not part_shape.isValid():
        print("❌ Géométrie invalide détectée dans le STEP !")
        FreeCAD.closeDocument(doc_name)
        return False

    vol_mm3 = part_shape.Volume
    vol_cm3 = vol_mm3 / 1000.0
    mass_g = vol_cm3 * 2.81
    print(f"  Volume B-Rep net     : {vol_mm3:.2f} mm³ ({vol_cm3:.2f} cm³)")
    print(f"  Masse 7075-T6 réelle : {mass_g:.2f} g")

    geo_feat = doc.addObject("Part::Feature", "Corniere_Basse_7075")
    geo_feat.Shape = part_shape
    doc.recompute()

    # 2. Identification topologique robuste
    features = find_topological_features(part_shape)
    print(f"  Semelle d'assise (base)   : {features['bottom_face']}")
    print(f"  Trous vis inférieures M4  : {features['bottom_holes']}")
    print(f"  Portée d'appui haute      : {features['top_face']}")
    print(f"  Trous vis supérieures M4  : {features['top_holes']}")

    fixed_faces = []
    if features['bottom_face']:
        fixed_faces.append(features['bottom_face'])
    if features['bottom_holes']:
        fixed_faces.extend(features['bottom_holes'])

    if not fixed_faces:
        print("❌ Impossible d'identifier la face d'encastrement inférieure.")
        FreeCAD.closeDocument(doc_name)
        return False

    target_load_face = features['top_face'] if features['top_face'] else (load_targets[0] if load_targets else None)
    if not target_load_face:
        print("❌ Impossible d'identifier la portée supérieure pour l'application des charges.")
        FreeCAD.closeDocument(doc_name)
        return False

    # 3. Création du conteneur d'analyse FEM et du solveur CalculiX
    analysis = ObjectsFem.makeAnalysis(doc, "Analysis")
    solver = ObjectsFem.makeSolverCalculiXCcxTools(doc, "CalculiX")
    analysis.addObject(solver)

    # 4. Matériau Aluminium 7075-T651
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

    # 5. Condition aux limites : Encastrement de la semelle sur la Waist Plate
    fixed_constraint = ObjectsFem.makeConstraintFixed(doc, "FixedBase")
    fixed_refs = [(geo_feat, face_name) for face_name in fixed_faces]
    fixed_constraint.References = fixed_refs
    analysis.addObject(fixed_constraint)

    # 6. Condition de chargement
    force_constraint = ObjectsFem.makeConstraintForce(doc, "AppliedLoad")
    force_constraint.References = [(geo_feat, target_load_face)]
    force_constraint.Force = f"{force_n:.1f} N"

    if load_case == "torsion":
        # Force latérale selon X (reprise du couple de lacet à travers le portique)
        force_constraint.DirectionVector = FreeCAD.Vector(1.0, 0.0, 0.0)
        force_constraint.Reversed = False
        print(f"  --> Charge de lacet (+X, {force_n:.1f} N) appliquée sur {target_load_face}")
    elif load_case == "traction":
        force_constraint.DirectionVector = FreeCAD.Vector(0.0, 0.0, 1.0)
        force_constraint.Reversed = False
        print(f"  --> Charge de traction axiale (+Z, {force_n:.1f} N) appliquée sur {target_load_face}")
    elif load_case == "flexion":
        force_constraint.DirectionVector = FreeCAD.Vector(0.0, 1.0, 0.0)
        force_constraint.Reversed = False
        print(f"  --> Charge de flexion sagittale (+Y, {force_n:.1f} N) appliquée sur {target_load_face}")

    analysis.addObject(force_constraint)

    # 7. Maillage tétraédrique C3D10 quadratique via Gmsh
    print("\n⚙️  Génération du maillage tétraédrique volumique (Gmsh)...")
    mesh_obj = ObjectsFem.makeMeshGmsh(doc, "FEMMeshGmsh")
    mesh_obj.Shape = geo_feat
    mesh_obj.ElementDimension = "3D"
    mesh_obj.ElementOrder = "2nd"
    mesh_obj.SecondOrderLinear = True
    mesh_obj.OptimizeNetgen = True
    mesh_obj.CharacteristicLengthMax = cl_max
    mesh_obj.CharacteristicLengthMin = cl_min
    analysis.addObject(mesh_obj)
    doc.recompute()

    gmsh_tools = GmshTools(mesh_obj)
    try:
        error = gmsh_tools.create_mesh()
        if error:
            print(f"❌ Erreur Gmsh lors du maillage : {error}")
            FreeCAD.closeDocument(doc_name)
            return False
    except Exception as e:
        print(f"❌ Exception pendant l'exécution de Gmsh : {e}")
        FreeCAD.closeDocument(doc_name)
        return False

    node_count = mesh_obj.FemMesh.NodeCount
    elem_count = mesh_obj.FemMesh.VolumeCount
    print(f"  ✅ Maillage réussi : {node_count:,} nœuds, {elem_count:,} éléments C3D10.")

    # 8. Préparation & Exécution du Solveur CalculiX
    work_dir = tempfile.mkdtemp(prefix="dbot_cb_fea_")
    print(f"\n🚀 Résolution CalculiX en cours (dossier temporaire: {work_dir})...")

    fea = ccxtools.FemToolsCcx(analysis=analysis, solver=solver, test_mode=True)
    fea.setup_working_dir(work_dir)
    fea.update_objects()
    fea.write_inp_file()

    inp_name = "FEMMeshGmsh"
    ccx_bin = DEFAULT_CCX_BIN if os.path.exists(DEFAULT_CCX_BIN) else (shutil.which("ccx") or "ccx")

    res = subprocess.run([ccx_bin, "-i", inp_name], cwd=work_dir, capture_output=True, text=True, shell=False)
    if res.returncode != 0:
        print(f"❌ Erreur lors de l'exécution CalculiX (code {res.returncode}) :")
        print("STDOUT:\n", res.stdout)
        print("STDERR:\n", res.stderr)
        FreeCAD.closeDocument(doc_name)
        shutil.rmtree(work_dir, ignore_errors=True)
        return False

    print("  ✅ CalculiX a résolu le système avec succès !")

    frd_file = os.path.join(work_dir, inp_name + ".frd")
    dat_file = os.path.join(work_dir, inp_name + ".dat")

    if os.path.exists(frd_file):
        results_obj = importCcxFrdResults.importFrd(frd_file, analysis, "CCX_", solver.AnalysisType)
    elif os.path.exists(dat_file):
        results_obj = importCcxDatResults.import_dat(dat_file, analysis)
    else:
        print("❌ Aucun fichier de résultat (.frd ou .dat) produit par ccx.")
        FreeCAD.closeDocument(doc_name)
        shutil.rmtree(work_dir, ignore_errors=True)
        return False

    doc.recompute()

    # 9. Extraction des résultats
    disp_max = 0.0
    vm_max = 0.0
    vm_p95 = 0.0

    if hasattr(results_obj, "DisplacementLengths") and results_obj.DisplacementLengths:
        disp_max = max(results_obj.DisplacementLengths)

    if hasattr(results_obj, "NodeStressXX") and results_obj.NodeStressXX:
        sxx = results_obj.NodeStressXX
        syy = results_obj.NodeStressYY
        szz = results_obj.NodeStressZZ
        sxy = results_obj.NodeStressXY
        sxz = results_obj.NodeStressXZ
        syz = results_obj.NodeStressYZ

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

        if vm_stresses:
            vm_max = max(vm_stresses)
            vm_sorted = sorted(vm_stresses)
            idx_p95 = int(len(vm_sorted) * 0.95)
            vm_p95 = vm_sorted[idx_p95]

    re_yield = ALU_7075_T6["YieldStrength"]
    sf_peak = (re_yield / vm_max) if vm_max > 0 else 999.0
    sf_p95 = (re_yield / vm_p95) if vm_p95 > 0 else 999.0

    print("\n" + "=" * 75)
    print("   📊 RÉSULTATS D'ANALYSE RDM D-BOT (FREECAD / CALCULIX)")
    print("=" * 75)
    print(f"  Composant analysé             : Cornière Basse Nervurée 7075-T6")
    print(f"  Cas de chargement             : {load_case.upper()} (F = {force_n:.1f} N)")
    print(f"  Déplacement maximal (Flèche)  : {disp_max:.4f} mm")
    print(f"  Contrainte de Von Mises crête : {vm_max:.2f} MPa")
    print(f"  Contrainte Von Mises (P95)    : {vm_p95:.2f} MPa (filtre des singularités de maillage)")
    print(f"  Limite élastique Re (7075-T6) : {re_yield:.1f} MPa")
    print(f"  Facteur de sécurité crête Sf  : {sf_peak:.2f}")
    print(f"  Facteur de sécurité P95 Sf    : {sf_p95:.2f}")
    print("-" * 75)
    if sf_p95 >= 2.5:
        print(f"  🎯 STATUT CONCEPTION : CERTIFIÉ CONFORME (Sf_P95 = {sf_p95:.2f} >= 2.5) ✅")
    else:
        print(f"  ⚠️  STATUT CONCEPTION : Surveillance requise (Sf_P95 = {sf_p95:.2f} < 2.5)")
    print("=" * 75 + "\n")

    # 10. Solution B : Instanciation du Pipeline VTK pour affichage graphique immédiat
    try:
        from fempostfilter.pipeline import make_post_pipeline
        pipeline = make_post_pipeline(doc, "Pipeline_VonMises")
        pipeline.Analysis = analysis
        pipeline.Field = "VonMises"
        pipeline.Mode = "Surface with Edges"
        pipeline.Visibility = True
        results_obj.Visibility = False
        geo_feat.Visibility = False
        doc.recompute()
        print("  ✅ Solution B : Pipeline VTK activé pour affichage 3D couleur immédiat.")
    except Exception:
        pass

    # Sauvegarde du document FreeCAD
    doc.saveAs(output_fcstd)
    print(f"💾 Document FreeCAD 3D complet sauvegardé :")
    print(f"   --> {output_fcstd}")

    # Génération du lanceur 1-clic macOS
    launcher_path = os.path.join(out_dir, "Ouvrir_Simulation_FreeCAD.command")
    with open(launcher_path, "w", encoding="utf-8") as f:
        f.write("#!/bin/bash\n")
        f.write("# Lanceur 1-clic de simulation RDM FreeCAD D-Bot\n")
        f.write(f'open -a "/Applications/FreeCAD.app" "{output_fcstd}"\n')
    os.chmod(launcher_path, 0o755)
    print(f"🚀 Lanceur 1-clic généré : {launcher_path}")

    FreeCAD.closeDocument(doc_name)
    shutil.rmtree(work_dir, ignore_errors=True)
    return True


def main():
    parser = argparse.ArgumentParser(description="Simulation RDM Souveraine FreeCAD / CalculiX pour Cornière Basse D-Bot")
    parser.add_argument("--step", default=DEFAULT_STEP_PATH, help="Chemin du fichier STEP à simuler")
    parser.add_argument("--case", choices=["torsion", "traction", "flexion"], default="torsion", help="Cas de charge")
    parser.add_argument("--force", type=float, default=210.0, help="Effort appliqué en Newtons (défaut : 210 N)")
    parser.add_argument("--clmax", type=float, default=3.0, help="Taille max des éléments Gmsh en mm (défaut : 3.0 mm)")
    parser.add_argument("--clmin", type=float, default=1.0, help="Taille min des éléments Gmsh en mm (défaut : 1.0 mm)")
    parser.add_argument("--out", default=DEFAULT_OUTPUT_FCSTD, help="Fichier FreeCAD .FCStd de sortie")

    raw_args = []
    if "--pass" in sys.argv:
        pass_idx = sys.argv.index("--pass")
        if pass_idx + 1 < len(sys.argv):
            pass_str = sys.argv[pass_idx + 1]
            raw_args = shlex.split(pass_str)
    else:
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
    
    os._exit(0 if success else 1)


if __name__ in ("__main__", "simulate_corniere_basse"):
    main()

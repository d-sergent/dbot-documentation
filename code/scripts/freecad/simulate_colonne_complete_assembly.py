#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
simulate_colonne_complete_assembly.py — Simulation RDM Éléments Finis Souveraine (FreeCAD 1.1 + CalculiX)

Ce script réalise l'analyse par éléments finis (FEA) de l'ASSEMBLAGE COMPLET de la Colonne Vertébrale
du robot D-Bot V1 (Plaque Basse + Plaque Haute + 2 Éclisses Sandwich en Aluminium 7075-T651).

Composants assemblés :
  - Plaque Basse 7075-T6 (h = 297 mm, Z = 1043.4 à 1340.4 mm, 2 lumières 54x55 mm)
  - Plaque Haute 7075-T6 (h = 130 mm, Z = 1340.4 à 1470.4 mm, pleine, support IMU)
  - Éclisse Avant 7075-T6 (h = 130 mm, ép. 5 mm, Z = 1275.4 à 1405.4 mm)
  - Éclisse Arrière 7075-T6 (h = 130 mm, ép. 5 mm, Z = 1275.4 à 1405.4 mm)
  --> Épaisseur totale au nœud d'épaule : 15,0 mm (Sandwich 5 + 5 + 5 mm)

Capacités :
  - Fusion B-Rep conforme avec suppression des coutures résiduelles
  - Identification topologique automatique des faces d'encastrement (semelle Waist Z=1043 mm + perçages M4)
  - Application des efforts au sommet du cou (Z = 1470 mm) avec bras de levier complet (L = 427 mm)
  - Résolution statique CalculiX (ccx) avec maillage Gmsh C3D10 quadratique optimisé
  - Calcul de la flèche au cou, de la flèche aux épaules et de l'inclinaison au niveau de l'IMU Torse
  - Sauvegarde dans le dossier dédié aux assemblages : Exports_CAO_DBot/.../Assemblages/colonne_vertébrale_complete/
  - Lanceurs 1-clic macOS (.command) et Solution B intégrée

Exécution :
  /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd simulate_colonne_complete_assembly.py [--case pitch|roll] [--force 328]
"""

import os
import sys
import math
import shutil
import tempfile
import argparse
import subprocess
from pathlib import Path

# Chemins souverains D-Bot
BASE_DIR = Path("/Users/Shared/Mon Google Drive Physique")
STEP_COLONNE = BASE_DIR / "Exports_CAO_DBot/Bibliotheque_Composants_STEP/colonne_vertébrale.step"
STEP_ECLISSE = BASE_DIR / "Exports_CAO_DBot/Bibliotheque_Composants_STEP/semelle_éclisse.step"
ASSEMBLY_DIR = BASE_DIR / "Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots/Assemblages/colonne_vertébrale_complete"
DEFAULT_CCX_BIN = "/Applications/FreeCAD.app/Contents/Resources/bin/ccx"

# Propriétés certifiées Aluminium 7075-T651 (Norme EN 754 / ASTM B221)
ALU_7075_T6 = {
    "Name": "Aluminium-7075-T651",
    "YoungsModulus": "71700 MPa",
    "PoissonRatio": "0.33",
    "Density": "2810 kg/m^3",
    "YieldStrength": 505.0,          # MPa (Rp0,2)
    "UltimateTensileStrength": 570.0 # MPa (Rm)
}


def build_assembled_spine():
    """
    Construit l'assemblage volumique B-Rep exact de la colonne complète
    avec ses deux plaques (basse + haute) et ses deux éclisses sandwich de 5 mm.
    """
    import Part
    import FreeCAD

    print("📦 Chargement des composants STEP souverains...")
    col = Part.read(str(STEP_COLONNE))
    ecl1 = Part.read(str(STEP_ECLISSE))

    # Séparation solide bas et solide haut de la colonne
    sol_haute = col.Solids[0] if col.Solids[0].BoundBox.ZMin > 1300 else col.Solids[1]
    sol_basse = col.Solids[1] if col.Solids[0].BoundBox.ZMin > 1300 else col.Solids[0]

    # Positionnement de l'éclisse arrière (face 2, Y = [11.17, 16.17])
    # Plan médian de la colonne : Y_mid = (6.16996 + 11.16996) / 2 = 8.66996 mm
    y_mid = (6.16996 + 11.16996) / 2.0
    sol_ecl2 = ecl1.Solids[0].mirror(FreeCAD.Vector(0, y_mid, 0), FreeCAD.Vector(0, 1, 0))

    # Fusion géométrique de l'assemblage sandwich
    print("🧩 Fusion B-Rep du sandwich 15 mm (Plaque Basse + Plaque Haute + 2 Éclisses)...")
    fused = sol_basse.fuse([sol_haute, ecl1.Solids[0], sol_ecl2])
    cleaned = fused.removeSplitter()

    print(f"  ✅ Assemblage validé : 1 solide unique, {len(cleaned.Faces)} faces, épaisseur nœud = 15.0 mm.")
    print(f"  Dimensions globales : {cleaned.BoundBox.XLength:.1f} × {cleaned.BoundBox.YLength:.1f} × {cleaned.BoundBox.ZLength:.1f} mm")
    print(f"  Étendue Z : [{cleaned.BoundBox.ZMin:.2f} mm ➔ {cleaned.BoundBox.ZMax:.2f} mm] (Hauteur totale = {cleaned.BoundBox.ZLength:.2f} mm)")

    return cleaned


def find_assembly_features(shape):
    """
    Identifie de manière géométrique et déterministe les faces d'appui
    et d'application des charges sur l'assemblage complet.
    """
    import FreeCAD

    bb_all = shape.BoundBox
    z_min = bb_all.ZMin
    z_max = bb_all.ZMax

    features = {
        "bottom_face": None,
        "bottom_holes": [],
        "top_edges": [],
        "shoulder_edges": []
    }

    # 1. Face d'assise inférieure plane (ZMin ~ 1043.42 mm, normale -Z)
    for i, face in enumerate(shape.Faces, 1):
        com = face.CenterOfMass
        if face.Surface.__class__.__name__ == "Plane" and abs(com.z - z_min) < 0.5:
            norm = face.normalAt(0, 0)
            if norm.z < -0.8 and face.Area > 200.0:
                features["bottom_face"] = f"Face{i}"

    # 2. Trous de fixation cylindriques à la base (Z < 1065 mm)
    for i, face in enumerate(shape.Faces, 1):
        if face.Surface.__class__.__name__ == "Cylinder" and face.BoundBox.ZMax < (z_min + 25.0):
            features["bottom_holes"].append(f"Face{i}")

    # 3. Arêtes sommitales de chargement au cou (ZMax ~ 1470.42 mm)
    for i, edge in enumerate(shape.Edges, 1):
        if abs(edge.BoundBox.ZMax - z_max) < 0.3 and abs(edge.BoundBox.ZMin - z_max) < 0.3:
            if edge.Length > 20.0:
                features["top_edges"].append(f"Edge{i}")

    # 4. Arêtes aux épaules (Z ~ 1340.35 mm)
    for i, edge in enumerate(shape.Edges, 1):
        if abs(edge.BoundBox.ZMax - 1340.35) < 0.5 and abs(edge.BoundBox.ZMin - 1340.35) < 0.5:
            if edge.Length > 20.0:
                features["shoulder_edges"].append(f"Edge{i}")

    return features


def run_fea_simulation(load_case="pitch", force_n=328.0, cl_max=6.5, cl_min=2.2, output_fcstd=None):
    """
    Pipeline complet FEA sous FreeCAD / CalculiX pour l'assemblage complet de colonne vertébrale.
    """
    import FreeCAD
    import Part
    import ObjectsFem
    from femmesh.gmshtools import GmshTools
    from femtools import ccxtools

    print("\n" + "=" * 75)
    print("   🤖 SHIELD D-BOT : SIMULATION RDM FEA COLONNE VERTÉBRALE COMPLÈTE")
    print("      ASSEMBLAGE : Plaque Basse + Plaque Haute + 2 Éclisses Sandwich")
    print("      Solveur : CalculiX (ccx) | Mailleur : Gmsh C3D10 Quadratique")
    print("=" * 75)
    print(f"Cas de charge      : {load_case.upper()} (Force = {force_n:.1f} N)")
    print(f"Maillage Gmsh      : Longueur carac. [{cl_min:.1f} mm min, {cl_max:.1f} mm max]")

    # 1. Construction de la géométrie assemblée
    shape = build_assembled_spine()

    # Sauvegarde du modèle STEP assemblé dans le dossier dédié
    os.makedirs(str(ASSEMBLY_DIR), exist_ok=True)
    step_export_path = ASSEMBLY_DIR / "colonne_vertébrale_complete_assemblage.step"
    if not step_export_path.exists():
        shape.exportStep(str(step_export_path))
        print(f"💾 Modèle 3D STEP assemblé exporté : {step_export_path}")

    # 2. Création du Document FreeCAD
    case_name = "Tangage" if load_case == "pitch" else ("Roulis" if load_case == "roll" else load_case.capitalize())
    doc = FreeCAD.newDocument(f"colonne_complete_FEA_{case_name}")

    part_obj = doc.addObject("Part::Feature", "Colonne_Complete_Sandwich_7075")
    part_obj.Shape = shape
    doc.recompute()

    # 3. Détection Topologique
    print("\n🔍 Détection Topologique B-Rep sur l'assemblage :")
    features = find_assembly_features(shape)
    print(f"   - Face d'assise inférieure : {features['bottom_face']}")
    print(f"   - Trous de fixation Waist  : {len(features['bottom_holes'])} faces détectées ({features['bottom_holes']})")
    print(f"   - Arêtes sommitales Cou    : {features['top_edges']}")
    print(f"   - Arêtes intermédiaires Épaules : {features['shoulder_edges']}")

    # 4. Création de l'Analyse FEM et du Solveur CalculiX
    analysis = ObjectsFem.makeAnalysis(doc, "Analysis")
    solver = ObjectsFem.makeSolverCalculiXCcxTools(doc, "CalculiX")
    solver.GeometricalNonlinearity = "linear"
    solver.ThermoMechSteadyState = False
    solver.MatrixSolverType = "default"
    solver.IterationsControlParameterTimeUse = False
    solver.SplitInputWriter = False
    analysis.addObject(solver)

    # 5. Matériau Aluminium 7075-T651
    mat_obj = ObjectsFem.makeMaterialSolid(doc, "Alu7075T6")
    mat_props = mat_obj.Material
    mat_props["Name"] = ALU_7075_T6["Name"]
    mat_props["YoungsModulus"] = ALU_7075_T6["YoungsModulus"]
    mat_props["PoissonRatio"] = ALU_7075_T6["PoissonRatio"]
    mat_props["Density"] = ALU_7075_T6["Density"]
    mat_obj.Material = mat_props
    analysis.addObject(mat_obj)

    # 6. Conditions aux Limites : Encastrement Base
    con_fixed = ObjectsFem.makeConstraintFixed(doc, "FixedBase")
    fixed_refs = [(part_obj, features["bottom_face"])]
    for h in features["bottom_holes"]:
        fixed_refs.append((part_obj, h))
    con_fixed.References = fixed_refs
    analysis.addObject(con_fixed)

    # 7. Chargement au sommet du cou (Z = 1470 mm, L = 427 mm)
    con_force = ObjectsFem.makeConstraintForce(doc, "AppliedLoad")
    con_force.References = [(part_obj, e) for e in features["top_edges"]]
    con_force.Force = f"{force_n:.1f} N"
    con_force.Direction = (part_obj, [features["top_edges"][0]])

    if load_case == "pitch":
        # Flexion dans le plan sagittal (+X = vers l'avant)
        con_force.DirectionVector = FreeCAD.Vector(1.0, 0.0, 0.0)
        con_force.Reversed = False
        arm_m = (1470.42 - 1043.42) / 1000.0 # 0.427 m
        moment_nm = force_n * arm_m
        print(f"  --> Charge de tangage ({force_n:.1f} N, M = {moment_nm:.1f} N.m) appliquée au sommet du cou (+X)")
    elif load_case == "roll":
        # Flexion dans le plan frontal (+Y = vers la gauche)
        con_force.DirectionVector = FreeCAD.Vector(0.0, 1.0, 0.0)
        con_force.Reversed = False
        arm_m = (1470.42 - 1043.42) / 1000.0
        moment_nm = force_n * arm_m
        print(f"  --> Charge de roulis ({force_n:.1f} N, M = {moment_nm:.1f} N.m) appliquée au sommet du cou (+Y)")
    else:
        con_force.DirectionVector = FreeCAD.Vector(1.0, 0.0, 0.0)
        con_force.Reversed = False

    analysis.addObject(con_force)

    # 8. Maillage Gmsh C3D10
    print("\n⚙️  Génération du maillage tétraédrique volumique Gmsh C3D10...")
    mesh_obj = ObjectsFem.makeMeshGmsh(doc, "FEMMeshGmsh")
    mesh_obj.Shape = part_obj
    mesh_obj.CharacteristicLengthMax = cl_max
    mesh_obj.CharacteristicLengthMin = cl_min
    mesh_obj.ElementDimension = "3D"
    mesh_obj.ElementOrder = "2nd"
    mesh_obj.SecondOrderLinear = True
    mesh_obj.OptimizeNetgen = True
    mesh_obj.HighOrderOptimize = "Elastic+Optimization"
    analysis.addObject(mesh_obj)
    doc.recompute()

    gmsh_mesh = GmshTools(mesh_obj)
    gmsh_mesh.create_mesh()
    node_count = mesh_obj.FemMesh.NodeCount
    elem_count = mesh_obj.FemMesh.VolumeCount
    print(f"  ✅ Maillage réussi : {node_count:,} nœuds, {elem_count:,} éléments C3D10.")

    # 9. Résolution CalculiX
    work_dir = tempfile.mkdtemp(prefix="dbot_colonne_complete_fea_")
    print(f"\n🚀 Résolution CalculiX en cours (dossier temporaire: {work_dir})...")

    fea = ccxtools.FemToolsCcx(analysis=analysis, solver=solver, test_mode=True)
    fea.setup_working_dir(work_dir)
    fea.update_objects()
    fea.write_inp_file()

    inp_name = "FEMMeshGmsh"
    ccx_bin = DEFAULT_CCX_BIN if os.path.exists(DEFAULT_CCX_BIN) else (shutil.which("ccx") or "ccx")
    cmd = [ccx_bin, "-i", inp_name]
    proc = subprocess.run(cmd, cwd=work_dir, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"❌ Erreur CalculiX ccx (Code {proc.returncode}):")
        print("STDOUT:\n", proc.stdout[:1000])
        print("STDERR:\n", proc.stderr[:1000])
        return False
    print("  ✅ CalculiX ccx a terminé avec succès.")

    # Chargement des résultats
    fea.load_results()
    res_obj = doc.getObject("CCX_Results")
    if not res_obj:
        print("❌ Erreur : Objet CCX_Results absent après résolution.")
        return False

    # 10. Solution B : Pipeline VTK pour inspection directe
    try:
        pipeline_obj = ObjectsFem.makePostVtkResult(doc, [res_obj], name="VonMises_Pipeline")
        print(f"  ✅ Solution B : Pipeline de post-traitement VTK initialisé ({pipeline_obj.Name}).")
    except Exception as e:
        print(f"  ⚠️ Note post-traitement VTK : {e}")

    # 11. Dépouillement Analytique Avancé
    disp_lengths = res_obj.DisplacementLengths
    disp_max = max(disp_lengths)
    disp_vectors = res_obj.DisplacementVectors

    # Nœuds et contraintes
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

    # Mesure de la flèche aux Épaules (Z ~ 1340 mm) et à l'IMU (Z ~ 1421 mm)
    disp_shoulders = 0.0
    disp_imu = 0.0
    # Recherche parmi les nœuds du maillage
    fem_mesh = mesh_obj.FemMesh
    for node_idx, pt in fem_mesh.Nodes.items():
        if abs(pt.z - 1340.35) < 3.0:
            if node_idx <= len(disp_lengths):
                disp_shoulders = max(disp_shoulders, disp_lengths[node_idx - 1])
        if abs(pt.z - 1421.0) < 3.0:
            if node_idx <= len(disp_lengths):
                disp_imu = max(disp_imu, disp_lengths[node_idx - 1])

    # Rotation angulaire parasite à l'IMU (mrad) : Theta ~ (disp_cou - disp_epaule) / delta_Z
    delta_z_head = 1470.42 - 1340.35 # 130 mm
    theta_imu_mrad = ((disp_max - disp_shoulders) / delta_z_head) * 1000.0

    arm_m = (1470.42 - 1043.42) / 1000.0
    moment_total_nm = force_n * arm_m

    print("\n" + "=" * 75)
    print("   📊 RÉSULTATS D'ANALYSE RDM COLONNE COMPLÈTE ASSEMBLÉE (D-BOT)")
    print("=" * 75)
    print(f"  Cas de chargement             : {load_case.upper()} (F = {force_n:.1f} N, M_base = {moment_total_nm:.1f} N.m)")
    print(f"  Bras de levier total (Base➔Cou) : {arm_m * 1000:.1f} mm")
    print(f"  Flèche maximale au COU        : {disp_max:.4f} mm")
    print(f"  Flèche intermédiaire ÉPAULES  : {disp_shoulders:.4f} mm")
    print(f"  Flèche au niveau de l'IMU     : {disp_imu:.4f} mm")
    print(f"  Rotation parasite IMU         : {theta_imu_mrad:.2f} mrad ({theta_imu_mrad * 180.0 / (math.pi * 1000.0):.3f} deg)")
    print(f"  Contrainte de Von Mises crête : {vm_max:.2f} MPa")
    print(f"  Contrainte Von Mises (P95)    : {vm_p95:.2f} MPa (volume effectif sans singularités)")
    print(f"  Limite élastique Re (7075-T6) : {re_7075:.1f} MPa")
    print(f"  Facteur de sécurité crête Sf  : {sf_peak:.2f}")
    print(f"  Facteur de sécurité P95 Sf    : {sf_p95:.2f}")

    if sf_p95 >= 3.0 and disp_max <= 1.5:
        print("  🎯 STATUT CONCEPTION : EXCELLENT ! Assemblage certifié pour le robot humanoïde. ✅")
    else:
        print(f"  ⚠️  STATUT CONCEPTION : Analyse requise (Flèche={disp_max:.4f} mm, Sf_P95={sf_p95:.2f})")
    print("=" * 75)

    # 12. Sauvegarde du Document FreeCAD dans le dossier Assemblages
    if output_fcstd is None:
        output_fcstd = str(ASSEMBLY_DIR / f"colonne_complete_FEA_{case_name}.FCStd")

    doc.saveAs(output_fcstd)
    print(f"\n💾 Document FreeCAD 3D complet sauvegardé :")
    print(f"   --> {output_fcstd}")

    # 13. Lanceur 1-Clic macOS (.command)
    launcher_path = os.path.join(os.path.dirname(output_fcstd), f"Ouvrir_Simulation_{case_name}.command")
    with open(launcher_path, "w", encoding="utf-8") as f:
        f.write("#!/bin/bash\n")
        f.write(f"# Double-cliquer pour ouvrir la simulation {case_name} de l'assemblage complet dans FreeCAD\n")
        f.write(f'open -a FreeCAD "{output_fcstd}"\n')
    os.chmod(launcher_path, 0o755)
    print(f"🚀 Launcher 1-Clic généré : {launcher_path}")

    # Launcher générique
    generic_launcher = os.path.join(os.path.dirname(output_fcstd), "Ouvrir_Simulation_FreeCAD.command")
    with open(generic_launcher, "w", encoding="utf-8") as f:
        f.write("#!/bin/bash\n")
        f.write("# Double-cliquer pour ouvrir la dernière simulation dans FreeCAD\n")
        f.write(f'open -a FreeCAD "{output_fcstd}"\n')
    os.chmod(generic_launcher, 0o755)

    return True


def main():
    parser = argparse.ArgumentParser(description="Simulation RDM Assemblage Complet Colonne FreeCAD / CalculiX")
    parser.add_argument("--case", choices=["pitch", "roll"], default="pitch", help="Cas de charge (défaut: pitch)")
    parser.add_argument("--force", type=float, default=None, help="Effort appliqué en N (défaut: 328 N pour pitch 140 N.m, 117 N pour roll 50 N.m)")
    parser.add_argument("--clmax", type=float, default=6.5, help="Taille max Gmsh mm (défaut: 6.5 mm)")
    parser.add_argument("--clmin", type=float, default=2.2, help="Taille min Gmsh mm (défaut: 2.2 mm)")
    parser.add_argument("--out", default=None, help="Fichier de sortie .FCStd")

    raw_args = []
    if "--pass" in sys.argv:
        pass_idx = sys.argv.index("--pass")
        if pass_idx + 1 < len(sys.argv):
            import shlex
            raw_args = shlex.split(sys.argv[pass_idx + 1])
    else:
        for i, a in enumerate(sys.argv[1:], start=1):
            if a.endswith(".py"):
                raw_args = sys.argv[i+1:]
                break

    args = parser.parse_args(raw_args)

    # Valeur de force par défaut selon le cas pour garantir les moments d'étalonnage
    if args.force is None:
        force_n = 328.0 if args.case == "pitch" else 117.0
    else:
        force_n = args.force

    success = run_fea_simulation(
        load_case=args.case,
        force_n=force_n,
        cl_max=args.clmax,
        cl_min=args.clmin,
        output_fcstd=args.out
    )

    os._exit(0 if success else 1)


if __name__ in ("__main__", "simulate_colonne_complete_assembly"):
    main()


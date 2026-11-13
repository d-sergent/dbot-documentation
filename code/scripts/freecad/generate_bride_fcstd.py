#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_bride_fcstd.py — Production du Document Officiel FreeCAD FEA (.FCStd)
et des Lanceurs 1-Clic pour la Bride d'Épaule (v87) Alu 7075-T651
"""

import os
import sys
import math
import shutil
import tempfile
import subprocess
from pathlib import Path

# Ajouter les chemins FreeCAD
for p in ["/Applications/FreeCAD.app/Contents/Resources/lib", "/Applications/FreeCAD.app/Contents/Resources/Mod/Fem"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np
import FreeCAD
import Part
import ObjectsFem
from femmesh.gmshtools import GmshTools
from femtools import ccxtools

BASE_DOC = Path("/Users/Shared/Mon Google Drive Physique/Documentation")
STEP_PATH = BASE_DOC / "01_Mecanique_et_Chassis/Torse_et_Bassin/cad/Bride_Epaule.step"
CCX_BIN = "/Applications/FreeCAD.app/Contents/Resources/bin/ccx"

# Destinations d'enregistrement souveraines
EXPORT_DIR = Path("/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/01_Torse_et_Bassin/Visual_Snapshots/Pieces_Isolees/Bride_Epaule")
WORKSPACE_CAD = BASE_DOC / "01_Mecanique_et_Chassis/Torse_et_Bassin/cad"

ALU_7075_T6 = {
    "Name": "Aluminium-7075-T651",
    "YoungsModulus": "71700 MPa",
    "PoissonRatio": "0.33",
    "Density": "2810 kg/m^3",
    "YieldStrength": "505.0 MPa",
    "UltimateTensileStrength": "570.0 MPa"
}

def generate_fea_package():
    print("=" * 75)
    print("GÉNÉRATION DU PACKAGE FEA FREECAD POUR LA BRIDE D'ÉPAULE V87")
    print("=" * 75)

    doc = FreeCAD.newDocument("Bride_Epaule_FEA")
    shape = Part.read(str(STEP_PATH))
    part_obj = doc.addObject("Part::Feature", "Bride_Epaule")
    part_obj.Shape = shape
    doc.recompute()

    print(f"Modèle STEP importé : Volume = {shape.Volume/1000.0:.2f} cm3, Masse 7075 = {shape.Volume*0.00281:.1f} g")

    # Conteneur FEM
    analysis = ObjectsFem.makeAnalysis(doc, "Analysis")
    solver = ObjectsFem.makeSolverCalculiXCcxTools(doc, "CalculiX")
    analysis.addObject(solver)

    # Matériau
    mat_obj = ObjectsFem.makeMaterialSolid(doc, "Alu7075T6")
    mat_obj.Material = ALU_7075_T6
    analysis.addObject(mat_obj)

    # Conditions d'encastrement sur le tube 60x60x2 mm
    fixed_faces = ["Face58", "Face60", "Face72", "Face76", "Face39", "Face43", "Face2", "Face6"]
    con_fixed = ObjectsFem.makeConstraintFixed(doc, "FixedBossage")
    con_fixed.References = [(part_obj, tuple(fixed_faces))]
    analysis.addObject(con_fixed)

    # Maillage Gmsh C3D10
    print("Génération du maillage tétraédrique volumique Gmsh C3D10...")
    mesh_obj = ObjectsFem.makeMeshGmsh(doc, "FEMMeshGmsh")
    mesh_obj.Shape = part_obj
    mesh_obj.CharacteristicLengthMax = 3.5
    mesh_obj.CharacteristicLengthMin = 1.4
    mesh_obj.ElementDimension = "3D"
    mesh_obj.ElementOrder = "2nd"
    mesh_obj.SecondOrderLinear = True
    mesh_obj.OptimizeNetgen = True
    analysis.addObject(mesh_obj)
    doc.recompute()

    GmshTools(mesh_obj).create_mesh()
    femmesh = mesh_obj.FemMesh
    print(f"Maillage généré : {femmesh.NodeCount:,} nœuds, {femmesh.VolumeCount:,} éléments.")

    # Répertoire de travail temporaire CalculiX
    work_dir = tempfile.mkdtemp(prefix="dbot_bride_pkg_", dir="/tmp")
    fea = ccxtools.FemToolsCcx(analysis=analysis, solver=solver, test_mode=True)
    fea.setup_working_dir(work_dir)
    fea.update_objects()
    fea.write_inp_file()

    # Nœuds des 10 perçages M4 du stator
    m4_face_indices = [61, 63, 77, 79, 84, 86, 88, 90, 92, 94]
    m4_nodes = set()
    for f_idx in m4_face_indices:
        for nid in femmesh.getNodesByFace(shape.Faces[f_idx]):
            m4_nodes.add(nid)

    xc_rot = 80.06
    zc_rot = 1340.35
    nodes_coords = {}
    sum_z2 = 0.0
    sum_r2 = 0.0
    for nid in m4_nodes:
        pt = femmesh.getNodeById(nid)
        dx = pt.x - xc_rot
        dz = pt.z - zc_rot
        r = math.sqrt(dx*dx + dz*dz)
        nodes_coords[nid] = (dx, dz, r)
        sum_z2 += dz * dz
        sum_r2 += r * r

    # Cas nominal dimensionnant : Flexion Sagittale Mx = 63.7 N.m + Fz = -128.0 N
    # Port de charge utile de 4.3 kg bras tendu sous 1.5g dynamique
    m_pitch = 63.7 * 1000.0 # N.mm
    k_pitch = m_pitch / sum_z2
    fz_each = -128.0 / len(m4_nodes)

    nodal_forces = {}
    for nid, (dx, dz, r) in nodes_coords.items():
        nodal_forces[nid] = (0.0, k_pitch * dz, fz_each)

    # Injection dans le fichier INP
    inp_path = os.path.join(work_dir, "FEMMeshGmsh.inp")
    with open(inp_path, "r") as f:
        inp_content = f.read()

    cload_lines = ["*CLOAD\n"]
    for nid, (fx, fy, fz) in nodal_forces.items():
        if abs(fx) > 1e-6:
            cload_lines.append(f"{nid},1,{fx:.6f}\n")
        if abs(fy) > 1e-6:
            cload_lines.append(f"{nid},2,{fy:.6f}\n")
        if abs(fz) > 1e-6:
            cload_lines.append(f"{nid},3,{fz:.6f}\n")

    cload_str = "".join(cload_lines)
    inp_content = inp_content.replace("*END STEP", cload_str + "*END STEP")

    with open(inp_path, "w") as f:
        f.write(inp_content)

    print("Résolution CalculiX ccx en cours...")
    proc = subprocess.run([CCX_BIN, "-i", "FEMMeshGmsh"], cwd=work_dir, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"❌ Erreur CalculiX ccx : {proc.stderr}")
        return False
    print("  ✅ Résolution CalculiX terminée avec succès.")

    # Chargement des résultats dans le document
    fea.load_results()
    res_obj = doc.getObject("CCX_Results")
    if not res_obj:
        print("❌ CCX_Results introuvable.")
        return False

    # Calcul et stockage des contraintes Von Mises
    sxx = res_obj.NodeStressXX
    syy = res_obj.NodeStressYY
    szz = res_obj.NodeStressZZ
    sxy = res_obj.NodeStressXY
    sxz = res_obj.NodeStressXZ
    syz = res_obj.NodeStressYZ

    vm_stresses = []
    for i in range(len(sxx)):
        vm = math.sqrt(
            0.5 * (
                (sxx[i] - syy[i]) ** 2 +
                (syy[i] - szz[i]) ** 2 +
                (szz[i] - sxx[i]) ** 2 +
                6.0 * (sxy[i] ** 2 + syz[i] ** 2 + sxz[i] ** 2)
            )
        )
        vm_stresses.append(vm)

    # Affectation du tableau vonMises sur l'objet résultat
    try:
        res_obj.vonMises = vm_stresses
    except Exception:
        pass

    vm_arr = np.array(vm_stresses)
    disp_max = max(res_obj.DisplacementLengths)
    vm_max = float(np.max(vm_arr))
    vm_p95 = float(np.percentile(vm_arr, 95))
    print(f"Résultats RDM : Flèche Max = {disp_max:.4f} mm, VM Peak = {vm_max:.2f} MPa, VM P95 = {vm_p95:.2f} MPa")

    # Activation du pipeline VTK pour affichage 3D couleur direct dans FreeCAD
    try:
        from fempostfilter.pipeline import make_post_pipeline
        pipeline = make_post_pipeline(doc, "Pipeline_VonMises")
        pipeline.Analysis = analysis
        pipeline.Field = "VonMises"
        pipeline.Mode = "Surface with Edges"
        pipeline.Visibility = True
        res_obj.Visibility = False
        part_obj.Visibility = False
        doc.recompute()
        print("  ✅ Pipeline VTK Von Mises instancié avec succès.")
    except Exception as e:
        print(f"  Note pipeline VTK : {e}")

    # Enregistrement des documents .FCStd
    os.makedirs(EXPORT_DIR, exist_ok=True)
    os.makedirs(WORKSPACE_CAD, exist_ok=True)

    fcstd_export = EXPORT_DIR / "Bride_Epaule_FEA_Results.FCStd"
    fcstd_workspace = WORKSPACE_CAD / "Bride_Epaule_FEA_Results.FCStd"

    doc.saveAs(str(fcstd_workspace))
    print(f"💾 Fichier .FCStd sauvegardé dans l'espace de travail : {fcstd_workspace}")

    try:
        shutil.copy2(str(fcstd_workspace), str(fcstd_export))
        print(f"💾 Fichier .FCStd sauvegardé dans Pièces Isolées : {fcstd_export}")
    except Exception as e:
        print(f"⚠️ Erreur copie vers Pieces_Isolees : {e}")

    # Création du lanceur 1-clic macOS .command
    launcher_path = EXPORT_DIR / "Ouvrir_Simulation_FreeCAD.command"
    try:
        with open(launcher_path, "w", encoding="utf-8") as f:
            f.write("#!/bin/bash\n")
            f.write("# Double-cliquer sur ce fichier pour ouvrir la simulation FEA dans FreeCAD\n")
            f.write(f'open -a "/Applications/FreeCAD.app" "{fcstd_export}"\n')
        os.chmod(launcher_path, 0o755)
        print(f"🚀 Lanceur 1-clic macOS créé : {launcher_path}")
    except Exception as e:
        print(f"⚠️ Erreur création launcher : {e}")

    shutil.rmtree(work_dir, ignore_errors=True)
    return True

if __name__ == "__main__":
    success = generate_fea_package()
    os._exit(0 if success else 1)


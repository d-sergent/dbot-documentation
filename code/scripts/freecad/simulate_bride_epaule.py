#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
simulate_bride_epaule.py — Simulation FEA Souveraine Complète de la Bride d'Épaule (v87) Alu 7075-T651
Robot Humanoïde D-Bot V1 — FreeCAD 1.1 + Gmsh C3D10 + CalculiX (ccx)
Mécanique des Solides Déformables & Injection Nodale Exacte des Torseurs d'Efforts
"""

import os
import sys
import math
import shutil
import tempfile
import subprocess
from pathlib import Path

# Ajouter les bibliothèques FreeCAD
for p in ["/Applications/FreeCAD.app/Contents/Resources/lib", "/Applications/FreeCAD.app/Contents/Resources/Mod/Fem"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np
import FreeCAD
import Part
import ObjectsFem
from femmesh.gmshtools import GmshTools
from femtools import ccxtools

# Chemins souverains
BASE_DIR = Path("/Users/Shared/Mon Google Drive Physique")
STEP_PATH = BASE_DIR / "Exports_CAO_DBot/Bibliotheque_Composants_STEP/Bride_Epaule.step"
CCX_BIN = "/Applications/FreeCAD.app/Contents/Resources/bin/ccx"

# Propriétés Aluminium 7075-T651
ALU_7075_T6 = {
    "Name": "Aluminium-7075-T651",
    "YoungsModulus": "71700 MPa",
    "PoissonRatio": "0.33",
    "Density": "2810 kg/m^3",
    "YieldStrength": "505.0 MPa",
    "UltimateTensileStrength": "570.0 MPa"
}

def run_simulation(load_case="torsion", mesh_size=3.5):
    print(f"\n======================================================================")
    print(f" SIMULATION FEA BRIDE D'ÉPAULE V87 — CAS : {load_case.upper()}")
    print(f"======================================================================")
    
    doc = FreeCAD.newDocument(f"FEA_Bride_{load_case}")
    shape = Part.read(str(STEP_PATH))
    part_obj = doc.addObject("Part::Feature", "Bride_Epaule")
    part_obj.Shape = shape
    doc.recompute()

    vol_cm3 = shape.Volume / 1000.0
    mass_g = shape.Volume * 0.00281
    print(f"Géométrie importée : Volume = {vol_cm3:.2f} cm3, Masse 7075-T651 = {mass_g:.1f} g")

    # Conteneur FEM
    analysis = ObjectsFem.makeAnalysis(doc, "Analysis")
    solver = ObjectsFem.makeSolverCalculiXCcxTools(doc, "CalculiX")
    analysis.addObject(solver)

    # Matériau
    mat_obj = ObjectsFem.makeMaterialSolid(doc, "Alu7075T6")
    mat_obj.Material = ALU_7075_T6
    analysis.addObject(mat_obj)

    # Encastrement du bossage carré 55.8x55.8 mm dans le tube 60x60x2 mm + perçage M5 + appui plan axial
    # Faces latérales du bossage: Face58, Face60, Face72, Face76
    # Alésage M5 traversant: Face39, Face43
    # Épaulement d'appui axial sur l'extrémité du tube carbone/alu: Face2, Face6
    fixed_faces = ["Face58", "Face60", "Face72", "Face76", "Face39", "Face43", "Face2", "Face6"]
    con_fixed = ObjectsFem.makeConstraintFixed(doc, "FixedBossage")
    con_fixed.References = [(part_obj, tuple(fixed_faces))]
    analysis.addObject(con_fixed)

    # Maillage Gmsh C3D10
    print(f"Génération du maillage Gmsh C3D10 (cl_max={mesh_size} mm, cl_min={mesh_size*0.4:.1f} mm)...")
    mesh_obj = ObjectsFem.makeMeshGmsh(doc, "FEMMeshGmsh")
    mesh_obj.Shape = part_obj
    mesh_obj.CharacteristicLengthMax = mesh_size
    mesh_obj.CharacteristicLengthMin = mesh_size * 0.4
    mesh_obj.ElementDimension = "3D"
    mesh_obj.ElementOrder = "2nd"
    mesh_obj.SecondOrderLinear = True
    mesh_obj.OptimizeNetgen = True
    analysis.addObject(mesh_obj)
    doc.recompute()

    GmshTools(mesh_obj).create_mesh()
    femmesh = mesh_obj.FemMesh
    node_count = femmesh.NodeCount
    elem_count = femmesh.VolumeCount
    print(f"Maillage généré avec succès : {node_count:,} nœuds, {elem_count:,} éléments C3D10.")

    # Préparation du répertoire de travail CalculiX
    work_dir = tempfile.mkdtemp(prefix=f"dbot_fea_{load_case}_", dir="/tmp")
    fea = ccxtools.FemToolsCcx(analysis=analysis, solver=solver, test_mode=True)
    fea.setup_working_dir(work_dir)
    fea.update_objects()
    fea.write_inp_file()

    # Récupération des nœuds des 10 perçages M4 du stator
    # Indices 0-based des faces cylindriques M4:
    m4_face_indices = [61, 63, 77, 79, 84, 86, 88, 90, 92, 94]
    m4_nodes = set()
    for f_idx in m4_face_indices:
        for nid in femmesh.getNodesByFace(shape.Faces[f_idx]):
            m4_nodes.add(nid)
    
    print(f"Interface boulonnée RS-04 : 10 perçages M4 -> {len(m4_nodes)} nœuds identifiés.")

    # Centre de l'axe moteur RobStride RS-04 (axe Y)
    xc_rot = 80.06
    zc_rot = 1340.35

    # Calcul des coordonnées relatives et des grandeurs quadratiques
    nodes_coords = {}
    sum_r2 = 0.0
    sum_z2 = 0.0
    sum_x2 = 0.0
    n_nodes = len(m4_nodes)

    for nid in m4_nodes:
        pt = femmesh.getNodeById(nid)
        dx = pt.x - xc_rot
        dz = pt.z - zc_rot
        r = math.sqrt(dx*dx + dz*dz)
        nodes_coords[nid] = (dx, dz, r)
        sum_r2 += r * r
        sum_z2 += dz * dz
        sum_x2 += dx * dx

    # Construction du tableau de forces nodales selon le cas de charge
    nodal_forces = {nid: [0.0, 0.0, 0.0] for nid in m4_nodes} # [Fx, Fy, Fz]

    if load_case == "torsion":
        # Couple de calage crête RS-04 : 120.0 N.m (120 000 N.mm) autour de Y
        torque_target = 120.0 * 1000.0 # N.mm
        k_torq = torque_target / sum_r2
        for nid, (dx, dz, r) in nodes_coords.items():
            nodal_forces[nid][0] += -k_torq * dz # Fx
            nodal_forces[nid][2] += k_torq * dx  # Fz
        print(f"Torseur appliqué : Torsion pure My = 120.0 N.m (Couple de calage crête)")

    elif load_case == "pitch_bending":
        # Flexion sagittale : Port de charge 4.3 kg bras tendu sous décélération dynamique 1.5g
        # M_pitch = 63.7 N.m (63 700 N.mm) autour de X + F_vert = -128.0 N selon Z
        m_pitch = 63.7 * 1000.0 # N.mm
        k_pitch = m_pitch / sum_z2
        fz_each = -128.0 / n_nodes
        for nid, (dx, dz, r) in nodes_coords.items():
            # Moment de flexion autour de X : traction en haut (+dz), compression en bas (-dz) selon l'axe Y
            nodal_forces[nid][1] += k_pitch * dz # Fy traction/compression axiale
            nodal_forces[nid][2] += fz_each      # Fz effort tranchant vertical
        print(f"Torseur appliqué : Flexion sagittale Mx = 63.7 N.m + Fz = -128.0 N")

    elif load_case == "roll_shock":
        # Roulis frontal / choc latéral : M_roll = 62.5 N.m (62 500 N.mm) autour de Z + Fx = 250.0 N
        m_roll = 62.5 * 1000.0 # N.mm
        k_roll = m_roll / sum_x2
        fx_each = 250.0 / n_nodes
        for nid, (dx, dz, r) in nodes_coords.items():
            # Moment de roulis autour de Z : traction à droite (+dx), compression à gauche (-dx) selon Y
            nodal_forces[nid][1] += k_roll * dx  # Fy
            nodal_forces[nid][0] += fx_each      # Fx effort tranchant latéral
        print(f"Torseur appliqué : Roulis/Choc frontal Mz = 62.5 N.m + Fx = +250.0 N")

    elif load_case == "traction_axial":
        # Traction axiale pure : Arrachement du bras / suspension du robot par la main (Fy = +600.0 N)
        fy_each = 600.0 / n_nodes
        for nid in m4_nodes:
            nodal_forces[nid][1] += fy_each
        print(f"Torseur appliqué : Traction axiale pure Fy = +600.0 N (Suspension du robot)")

    elif load_case == "combined_extreme":
        # Enveloppe extrême de superposition pire-cas :
        # Torsion 120 N.m + Flexion 63.7 N.m + Roulis 62.5 N.m + Traction 300 N + Cisaillement Fz -128 N + Fx 250 N
        k_torq = (120.0 * 1000.0) / sum_r2
        k_pitch = (63.7 * 1000.0) / sum_z2
        k_roll = (62.5 * 1000.0) / sum_x2
        fy_trac = 300.0 / n_nodes
        fz_each = -128.0 / n_nodes
        fx_each = 250.0 / n_nodes
        for nid, (dx, dz, r) in nodes_coords.items():
            nodal_forces[nid][0] += (-k_torq * dz) + fx_each
            nodal_forces[nid][1] += (k_pitch * dz) + (k_roll * dx) + fy_trac
            nodal_forces[nid][2] += (k_torq * dx) + fz_each
        print(f"Torseur appliqué : SUPERPOSITION ENVELOPPE EXTRÊME (Pire-cas multi-axial)")

    # Injection directe dans le fichier INP CalculiX
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

    # Exécution de CalculiX
    proc = subprocess.run([CCX_BIN, "-i", "FEMMeshGmsh"], cwd=work_dir, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"❌ Erreur CalculiX ccx (Code {proc.returncode}):")
        print("STDERR:\n", proc.stderr[-1000:] if proc.stderr else "None")
        return None
    print(f"  ✅ Résolution CalculiX ccx terminée avec succès.")

    # Chargement et analyse des résultats
    fea.load_results()
    res_obj = doc.getObject("CCX_Results")
    if not res_obj:
        print("❌ Erreur : Résultats absents.")
        return None

    disp_lengths = res_obj.DisplacementLengths
    disp_max = float(max(disp_lengths))

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

    vm_arr = np.array(vm_stresses)
    vm_max = float(np.max(vm_arr))
    vm_p99 = float(np.percentile(vm_arr, 99))
    vm_p95 = float(np.percentile(vm_arr, 95))
    vm_p90 = float(np.percentile(vm_arr, 90))
    vm_p75 = float(np.percentile(vm_arr, 75))
    vm_p50 = float(np.percentile(vm_arr, 50))
    vm_mean = float(np.mean(vm_arr))

    sf_peak = 505.0 / vm_max if vm_max > 0 else 999.0
    sf_p95 = 505.0 / vm_p95 if vm_p95 > 0 else 999.0

    pct_under_10 = float(np.sum(vm_arr < 10.0) / len(vm_arr) * 100.0)
    pct_under_25 = float(np.sum(vm_arr < 25.0) / len(vm_arr) * 100.0)
    pct_25_to_50 = float(np.sum((vm_arr >= 25.0) & (vm_arr < 50.0)) / len(vm_arr) * 100.0)
    pct_50_to_100 = float(np.sum((vm_arr >= 50.0) & (vm_arr < 100.0)) / len(vm_arr) * 100.0)
    pct_over_100 = float(np.sum(vm_arr >= 100.0) / len(vm_arr) * 100.0)

    print(f"\n--- RÉSULTATS FEA : {load_case.upper()} ---")
    print(f"  • Déplacement Maximal (Flèche) : {disp_max:.4f} mm")
    print(f"  • Von Mises Crête (Singularité) : {vm_max:.2f} MPa  (Sf_peak = {sf_peak:.2f})")
    print(f"  • Von Mises Percentile 99      : {vm_p99:.2f} MPa")
    print(f"  • Von Mises Percentile 95      : {vm_p95:.2f} MPa  (Sf_P95  = {sf_p95:.2f})")
    print(f"  • Von Mises Médiane (P50)      : {vm_p50:.2f} MPa")
    print(f"  • Von Mises Moyenne            : {vm_mean:.2f} MPa")
    print(f"  • Répartition volumique :")
    print(f"      - Zones ultra-froides (<10 MPa)  : {pct_under_10:.1f} %")
    print(f"      - Zones froides (<25 MPa)        : {pct_under_25:.1f} %")
    print(f"      - Zones modérées (25 à 50 MPa)   : {pct_25_to_50:.1f} %")
    print(f"      - Zones sollicitées (50-100 MPa) : {pct_50_to_100:.1f} %")
    print(f"      - Zones très chargées (>100 MPa) : {pct_over_100:.1f} %")

    # Nettoyage
    shutil.rmtree(work_dir, ignore_errors=True)

    return {
        "case": load_case,
        "disp_max": disp_max,
        "vm_max": vm_max,
        "vm_p99": vm_p99,
        "vm_p95": vm_p95,
        "vm_p90": vm_p90,
        "vm_p75": vm_p75,
        "vm_p50": vm_p50,
        "vm_mean": vm_mean,
        "sf_peak": sf_peak,
        "sf_p95": sf_p95,
        "pct_under_10": pct_under_10,
        "pct_under_25": pct_under_25,
        "pct_25_to_50": pct_25_to_50,
        "pct_50_to_100": pct_50_to_100,
        "pct_over_100": pct_over_100
    }

if __name__ == "__main__":
    cases = ["torsion", "pitch_bending", "roll_shock", "traction_axial", "combined_extreme"]
    results = {}
    for c in cases:
        res = run_simulation(c, mesh_size=3.5)
        results[c] = res

    print("\n" + "="*85)
    print("BILAN SYNTHÉTIQUE FEA COMPLET — BRIDE D'ÉPAULE V87 (ALU 7075-T651)")
    print("="*85)
    print(f"{'Cas de Charge':<18} | {'Flèche (mm)':<11} | {'VM Peak':<11} | {'VM P95':<11} | {'Sf_P95':<7} | {'% < 25 MPa'}")
    print("-" * 85)
    for c, r in results.items():
        if r:
            print(f"{r['case']:<18} | {r['disp_max']:<11.4f} | {r['vm_max']:<7.1f} MPa | {r['vm_p95']:<7.1f} MPa | {r['sf_p95']:<7.1f} | {r['pct_under_25']:.1f} %")
    print("="*85)
    os._exit(0)

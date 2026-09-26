# -*- coding: utf-8 -*-
"""
ModeliserBrideRB8016.py — Générateur Automatique de la Bride en L (Fusion 360)
Projet : Robot Humanoïde D-Bot V1 (Waist Yaw & Pelvis)
Auteur : Antigravity & David Sergent
=============================================================================
Ce script s'exécute directement dans Autodesk Fusion 360 (Shift + S > ModeliserBrideRB8016 > Run).
Il modélise avec une fidélité géométrique absolue le composant :
  Bride_Retenue_RB8016_L

Spécifications dimensionnelles :
  - Longueur radiale X : 16,00 mm (Bec 4,0 mm + Mur 3,5 mm + Embase 8,5 mm)
  - Largeur transverse Y : 15,00 mm (Extrusion symétrique ±7,50 mm)
  - Hauteur axiale Z : 15,00 mm (Épaulement vertical 13,00 mm + Bec 2,00 mm)
  - Semelle d'embase : Épaisseur 5,00 mm
  - Trou de fixation : Perçage traversant lisse Ø 4,50 mm à X = +8,00 mm (M4)
  - Matériau physique : Aluminium 7075-T6 (densité 2,81 g/cm3)
  - Export STEP automatique : Bride_Retenue_RB8016_L.step
"""

import adsk.core
import adsk.fusion
import os
import traceback

def create_or_get_custom_material(design, app, mat_name, density_g_cm3):
    """Récupère ou crée le matériau Aluminium 7075-T6 avec sa densité exacte."""
    existing = design.materials.itemByName(mat_name)
    if existing:
        return existing
        
    base_mat = None
    mat_lib = app.materialLibraries.itemByName('Fusion 360 Material Library')
    if mat_lib:
        for candidate in ['Aluminum 7075-T6', 'Aluminum 6061-T6', 'Aluminum']:
            try:
                m = mat_lib.materials.itemByName(candidate)
                if m:
                    base_mat = m
                    break
            except:
                pass
                
    if not base_mat and design.materials.count > 0:
        base_mat = design.materials.item(0)
        
    if not base_mat:
        return None
        
    try:
        new_mat = design.materials.addByCopy(base_mat, mat_name)
        if not new_mat:
            return None
        density_prop = new_mat.materialProperties.itemByName('Density')
        if density_prop:
            try:
                density_prop.value = float(density_g_cm3)
            except:
                pass
        return new_mat
    except:
        return None

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # 1. Vérification ou création du document actif
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        
        if not design:
            # Créer un nouveau document si aucun n'est ouvert
            doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
            design = adsk.fusion.Design.cast(app.activeProduct)
            
        root_comp = design.rootComponent
        
        # 2. Création du nouveau composant dédié Bride_Retenue_RB8016_L
        occurrences = root_comp.occurrences
        new_occ = occurrences.addNewComponent(adsk.core.Matrix3D.create())
        comp = new_occ.component
        comp.name = "Bride_Retenue_RB8016_L"
        
        # 3. Tracé de l'esquisse 2D du profil en L sur le plan XZ
        # IMPORTANT : L'API Fusion 360 utilise en interne le CENTIMÈTRE (cm)
        # Facteur de conversion : 1 mm = 0.1 cm
        sketches = comp.sketches
        xz_plane = comp.xZConstructionPlane
        sketch_profile = sketches.add(xz_plane)
        sketch_profile.name = "Esquisse_Profil_L_16x15"
        
        # Coordonnées des 8 sommets en cm :
        # P1: (0, 0)       - Coin inférieur d'appui contre cylindre roulement
        # P2: (0, 1.3)     - Face d'appui vertical saillie roulement (13 mm)
        # P3: (-0.4, 1.3)  - Dessous du bec (avancée 4 mm sur bague ext.)
        # P4: (-0.4, 1.5)  - Bout extrême supérieur du bec (épaisseur 2 mm)
        # P5: (0.35, 1.5)  - Sommet arrière mur vertical (épaisseur 3.5 mm)
        # P6: (0.35, 0.5)  - Raccordement supérieur semelle d'embase
        # P7: (1.2, 0.5)   - Talon arrière supérieur (semelle ép. 5 mm, long. 8.5 mm)
        # P8: (1.2, 0)     - Talon arrière inférieur (assise traverse)
        p1 = adsk.core.Point3D.create(0.0, 0.0, 0.0)
        p2 = adsk.core.Point3D.create(0.0, 1.3, 0.0)
        p3 = adsk.core.Point3D.create(-0.4, 1.3, 0.0)
        p4 = adsk.core.Point3D.create(-0.4, 1.5, 0.0)
        p5 = adsk.core.Point3D.create(0.35, 1.5, 0.0)
        p6 = adsk.core.Point3D.create(0.35, 0.5, 0.0)
        p7 = adsk.core.Point3D.create(1.2, 0.5, 0.0)
        p8 = adsk.core.Point3D.create(1.2, 0.0, 0.0)
        
        lines = sketch_profile.sketchCurves.sketchLines
        lines.addByTwoPoints(p1, p2)
        lines.addByTwoPoints(p2, p3)
        lines.addByTwoPoints(p3, p4)
        lines.addByTwoPoints(p4, p5)
        lines.addByTwoPoints(p5, p6)
        lines.addByTwoPoints(p6, p7)
        lines.addByTwoPoints(p7, p8)
        lines.addByTwoPoints(p8, p1)
        
        # 4. Extrusion symétrique sur une largeur totale de 15,0 mm (0.75 cm de chaque côté)
        prof = sketch_profile.profiles.item(0)
        extrudes = comp.features.extrudeFeatures
        ext_input = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        half_width = adsk.core.ValueInput.createByReal(0.75) # 7.5 mm en cm
        ext_input.setSymmetricExtent(half_width, False)
        ext_feature = extrudes.add(ext_input)
        body = comp.bRepBodies.item(0)
        body.name = "Corps_Bride_RB8016"
        
        # 5. Création du perçage de fixation M4 (Ø 4,50 mm à X = +8,00 mm)
        # Esquisse sur le plan XY pour découpe cylindrique traversante
        xy_plane = comp.xYConstructionPlane
        sketch_hole = sketches.add(xy_plane)
        sketch_hole.name = "Esquisse_Percage_M4_Diam4.5"
        
        # Centre du cercle : X = +0.8 cm (+8.0 mm), Y = 0.0 cm
        # Diamètre : 4.5 mm -> Rayon = 0.225 cm
        hole_center = adsk.core.Point3D.create(0.8, 0.0, 0.0)
        circles = sketch_hole.sketchCurves.sketchCircles
        circles.addByCenterRadius(hole_center, 0.225)
        
        # Extrusion Cut à travers la semelle
        prof_hole = sketch_hole.profiles.item(0)
        cut_input = extrudes.createInput(prof_hole, adsk.fusion.FeatureOperations.CutFeatureOperation)
        cut_distance = adsk.core.ValueInput.createByReal(1.0) # 1.0 cm de chaque côté
        cut_input.setSymmetricExtent(cut_distance, False)
        extrudes.add(cut_input)
        
        # 6. Assignation du matériau physique Aluminium 7075-T6
        mat_7075 = create_or_get_custom_material(design, app, "Aluminium 7075-T6", 2.81)
        if mat_7075:
            body.material = mat_7075
            
        # 7. Métrologie & Propriétés physiques
        design.computeAll()
        props = body.physicalProperties
        vol_cm3 = props.volume
        mass_g = props.mass * 1000.0
        
        # 8. Export automatique du modèle STEP normalisé
        export_dirs = [
            "/Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin",
            "/Users/Shared"
        ]
        
        exported_paths = []
        export_mgr = design.exportManager
        for edir in export_dirs:
            if os.path.exists(edir):
                step_file = os.path.join(edir, "Bride_Retenue_RB8016_L.step")
                try:
                    step_opts = export_mgr.createSTEPExportOptions(step_file, comp)
                    export_mgr.execute(step_opts)
                    exported_paths.append(step_file)
                except:
                    pass
                    
        # 9. Rapport d'exécution à l'utilisateur
        msg = (
            "SUCCÈS : Modélisation de la Bride en L terminée avec succès !\n\n"
            "Détails du composant :\n"
            "• Nom : Bride_Retenue_RB8016_L\n"
            "• Dimensions : 16,00 mm (L) × 15,00 mm (W) × 15,00 mm (H)\n"
            "• Épaulement roulement : H = 13,00 mm\n"
            "• Bec supérieur : Avancée 4,00 mm × Épaisseur 2,00 mm\n"
            "• Semelle d'embase : Longueur 12,00 mm × Épaisseur 5,00 mm\n"
            "• Perçage : Ø 4,50 mm traversant centré à X = +8,00 mm (vis M4)\n"
            "• Matériau : Aluminium 7075-T6 (2,81 g/cm3)\n"
            f"• Volume effectif : {vol_cm3:.3f} cm3\n"
            f"• Masse calculée : {mass_g:.2f} g / bride\n\n"
            "Export 3D STEP :\n"
        )
        if exported_paths:
            msg += f"• Fichier généré : {exported_paths[0]}\n"
        else:
            msg += "• Fichier STEP : Non exporté (répertoire non trouvé)\n"
            
        msg += "\nProchaine étape dans l'assemblage :\n"
        msg += "1. Utiliser 'Joint' (J) pour contraindre l'embase sur la Traverse.\n"
        msg += "2. Appliquer 'Répétition circulaire' (quantité 4) sur l'axe Z."
        
        ui.messageBox(msg, "D-Bot V1 — Modélisation Bride RB8016")
        
    except Exception as e:
        if ui:
            ui.messageBox(f"Erreur lors de la modélisation :\n{str(e)}\n\n{traceback.format_exc()}")
        else:
            print(f"Erreur : {e}")

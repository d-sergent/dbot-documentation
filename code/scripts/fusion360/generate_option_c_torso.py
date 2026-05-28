# -*- coding: utf-8 -*-
"""
Fusion 360 Script: Generate Bionic 3D Torse for D-Bot (Option C - Split-Monocoque)
==================================================================================
Ce script s'exécute directement dans Fusion 360 (Utilitaires -> Scripts et compléments).
Il génère automatiquement la structure 3D bionique ultra-détaillée de l'Option C :
- 1 Composant parent : D-Bot_Torso_Option_C_Bionic
- 1 Composant Pelvis_PA12CF hollow de 300x220x140 mm avec structures triangulaires (truss) et supports RS-04 hanches.
- 1 Composant Thorax_PA12CF hollow de 300x220x140 mm avec structure en X (truss), colliers d'épaules et col du cou.
- 1 Composant Carbon_Tubes de Ø25 mm reliant le bassin au thorax.
- 1 Composant Central_Equip_Mount avec 4 brides de serrage et une platine allégée porte-batterie/Jetson.

Toutes les cotes sont converties en centimètres (cm), l'unité native de l'API de Fusion 360.
Toutes les découpes de parois (truss) sont réalisées par extrusions symétriques depuis les plans centraux,
garantissant un fonctionnement 100% robuste sans dépendre des normales de plans décalés.
"""

import adsk.core, adsk.fusion, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox("❌ Aucun design actif détecté.\nVeuillez ouvrir un nouveau fichier ou un document actif avant de lancer le script.")
            return
            
        rootComp = design.rootComponent
        
        # --- 1. CREATION DU COMPOSANT PARENT ---
        transform = adsk.core.Matrix3D.create()
        occ_option_c = rootComp.occurrences.addNewComponent(transform)
        comp_option_c = occ_option_c.component
        comp_option_c.name = "D-Bot_Torso_Option_C_Bionic"
        
        # --- 2. DÉFINITION DES DIMENSIONS STRUCTURELLES (EN CM) ---
        w = 30.0          # Largeur = 300 mm
        d = 22.0          # Profondeur = 220 mm
        h_pelvis = 14.0   # Hauteur Pelvis = 140 mm
        h_thorax = 14.0   # Hauteur Thorax = 140 mm
        gap = 14.0        # Espace vide = 140 mm (Hauteur totale de 420 mm)
        
        tube_dia = 2.5    # Diamètre tube carbone = 25 mm
        tube_radius = tube_dia / 2.0
        
        # Entraxe des 4 tubes carbone (110 mm en X, 70 mm en Y depuis le centre)
        offsets_x = [-11.0, 11.0]
        offsets_y = [-7.0, 7.0]
        
        # --- 3. COMPOSANT 1 : PELVIS (BASSIN BIONIQUE) ---
        occ_pelvis = comp_option_c.occurrences.addNewComponent(transform)
        comp_pelvis = occ_pelvis.component
        comp_pelvis.name = "Pelvis_PA12CF"
        
        extrudes_pelvis = comp_pelvis.features.extrudeFeatures
        sketches_pelvis = comp_pelvis.sketches
        xyPlane_pelvis = comp_pelvis.xYConstructionPlane
        planes_pelvis = comp_pelvis.constructionPlanes
        
        # A. Bloc Solide Pelvis (Z: 0 à 14)
        sketch_base_pelvis = sketches_pelvis.add(xyPlane_pelvis)
        lines = sketch_base_pelvis.sketchCurves.sketchLines
        lines.addByTwoPoints(adsk.core.Point3D.create(-w/2.0, -d/2.0, 0), adsk.core.Point3D.create(w/2.0, -d/2.0, 0))
        lines.addByTwoPoints(adsk.core.Point3D.create(w/2.0, -d/2.0, 0), adsk.core.Point3D.create(w/2.0, d/2.0, 0))
        lines.addByTwoPoints(adsk.core.Point3D.create(w/2.0, d/2.0, 0), adsk.core.Point3D.create(-w/2.0, d/2.0, 0))
        lines.addByTwoPoints(adsk.core.Point3D.create(-w/2.0, d/2.0, 0), adsk.core.Point3D.create(-w/2.0, -d/2.0, 0))
        
        prof_base_pelvis = sketch_base_pelvis.profiles.item(0)
        extInput_pelvis = extrudes_pelvis.createInput(prof_base_pelvis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        extInput_pelvis.setDistanceExtent(False, adsk.core.ValueInput.createByReal(h_pelvis))
        ext_pelvis = extrudes_pelvis.add(extInput_pelvis)
        
        # B. Évidements Bioniques Frontaux/Dorsaux (Symmetric Cut depuis le plan XZ à Y = 0)
        sketch_truss_pf = sketches_pelvis.add(comp_pelvis.xZConstructionPlane)
        lines_tpf = sketch_truss_pf.sketchCurves.sketchLines
        
        # Triangle gauche (Coordonnées Y de l'esquisse négatives pour correspondre à Z positif en 3D)
        lines_tpf.addByTwoPoints(adsk.core.Point3D.create(-13.5, -1.5, 0), adsk.core.Point3D.create(-13.5, -12.5, 0))
        lines_tpf.addByTwoPoints(adsk.core.Point3D.create(-13.5, -12.5, 0), adsk.core.Point3D.create(-2.0, -7.0, 0))
        lines_tpf.addByTwoPoints(adsk.core.Point3D.create(-2.0, -7.0, 0), adsk.core.Point3D.create(-13.5, -1.5, 0))
        # Triangle droit
        lines_tpf.addByTwoPoints(adsk.core.Point3D.create(13.5, -1.5, 0), adsk.core.Point3D.create(13.5, -12.5, 0))
        lines_tpf.addByTwoPoints(adsk.core.Point3D.create(13.5, -12.5, 0), adsk.core.Point3D.create(2.0, -7.0, 0))
        lines_tpf.addByTwoPoints(adsk.core.Point3D.create(2.0, -7.0, 0), adsk.core.Point3D.create(13.5, -1.5, 0))
        # Triangle supérieur
        lines_tpf.addByTwoPoints(adsk.core.Point3D.create(-11.5, -12.5, 0), adsk.core.Point3D.create(11.5, -12.5, 0))
        lines_tpf.addByTwoPoints(adsk.core.Point3D.create(11.5, -12.5, 0), adsk.core.Point3D.create(0.0, -9.0, 0))
        lines_tpf.addByTwoPoints(adsk.core.Point3D.create(0.0, -9.0, 0), adsk.core.Point3D.create(-11.5, -12.5, 0))
        # Triangle inférieur
        lines_tpf.addByTwoPoints(adsk.core.Point3D.create(-11.5, -1.5, 0), adsk.core.Point3D.create(11.5, -1.5, 0))
        lines_tpf.addByTwoPoints(adsk.core.Point3D.create(11.5, -1.5, 0), adsk.core.Point3D.create(0.0, -5.0, 0))
        lines_tpf.addByTwoPoints(adsk.core.Point3D.create(0.0, -5.0, 0), adsk.core.Point3D.create(-11.5, -1.5, 0))
        
        profs_truss_pf = adsk.core.ObjectCollection.create()
        for i in range(sketch_truss_pf.profiles.count):
            profs_truss_pf.add(sketch_truss_pf.profiles.item(i))
            
        extInput_truss_pf = extrudes_pelvis.createInput(profs_truss_pf, adsk.fusion.FeatureOperations.CutFeatureOperation)
        extInput_truss_pf.setSymmetricExtent(adsk.core.ValueInput.createByReal(12.0), False) # Coupe à 12 cm de chaque côté, traversant Y = ±11 cm
        extrudes_pelvis.add(extInput_truss_pf)
        
        # C. Évidements Bioniques Latéraux Gauche/Droite (Symmetric Cut depuis le plan YZ à X = 0)
        sketch_truss_pl = sketches_pelvis.add(comp_pelvis.yZConstructionPlane)
        lines_tpl = sketch_truss_pl.sketchCurves.sketchLines
        # Triangle haut-gauche (Coordonnées Z directes positives sur le plan YZ)
        lines_tpl.addByTwoPoints(adsk.core.Point3D.create(-9.5, 12.5, 0), adsk.core.Point3D.create(0, 12.5, 0))
        lines_tpl.addByTwoPoints(adsk.core.Point3D.create(0, 12.5, 0), adsk.core.Point3D.create(-9.5, 3.0, 0))
        lines_tpl.addByTwoPoints(adsk.core.Point3D.create(-9.5, 3.0, 0), adsk.core.Point3D.create(-9.5, 12.5, 0))
        # Triangle haut-droit
        lines_tpl.addByTwoPoints(adsk.core.Point3D.create(9.5, 12.5, 0), adsk.core.Point3D.create(0, 12.5, 0))
        lines_tpl.addByTwoPoints(adsk.core.Point3D.create(0, 12.5, 0), adsk.core.Point3D.create(9.5, 3.0, 0))
        lines_tpl.addByTwoPoints(adsk.core.Point3D.create(9.5, 3.0, 0), adsk.core.Point3D.create(9.5, 12.5, 0))
        # Triangle bas central
        lines_tpl.addByTwoPoints(adsk.core.Point3D.create(-8.0, 1.5, 0), adsk.core.Point3D.create(8.0, 1.5, 0))
        lines_tpl.addByTwoPoints(adsk.core.Point3D.create(8.0, 1.5, 0), adsk.core.Point3D.create(0, 10.0, 0))
        lines_tpl.addByTwoPoints(adsk.core.Point3D.create(0, 10.0, 0), adsk.core.Point3D.create(-8.0, 1.5, 0))
        
        profs_truss_pl = adsk.core.ObjectCollection.create()
        for i in range(sketch_truss_pl.profiles.count):
            profs_truss_pl.add(sketch_truss_pl.profiles.item(i))
            
        extInput_truss_pl = extrudes_pelvis.createInput(profs_truss_pl, adsk.fusion.FeatureOperations.CutFeatureOperation)
        extInput_truss_pl.setSymmetricExtent(adsk.core.ValueInput.createByReal(16.0), False) # Coupe à 16 cm de chaque côté, traversant X = ±15 cm
        extrudes_pelvis.add(extInput_truss_pl)

        # D. Poche Interne d'Évidement (Épaisseur paroi = 1.5 cm)
        # Plan décalé à Z = 14
        planeInput_p = planes_pelvis.createInput()
        planeInput_p.setByOffset(xyPlane_pelvis, adsk.core.ValueInput.createByReal(h_pelvis))
        topPlane_pelvis = planes_pelvis.add(planeInput_p)
        
        sketch_pocket_pelvis = sketches_pelvis.add(topPlane_pelvis)
        lines_pocket = sketch_pocket_pelvis.sketchCurves.sketchLines
        pocket_w = w - 3.0 # Paroi de 1.5 cm
        pocket_d = d - 3.0
        lines_pocket.addByTwoPoints(adsk.core.Point3D.create(-pocket_w/2.0, -pocket_d/2.0, 0), adsk.core.Point3D.create(pocket_w/2.0, -pocket_d/2.0, 0))
        lines_pocket.addByTwoPoints(adsk.core.Point3D.create(pocket_w/2.0, -pocket_d/2.0, 0), adsk.core.Point3D.create(pocket_w/2.0, pocket_d/2.0, 0))
        lines_pocket.addByTwoPoints(adsk.core.Point3D.create(pocket_w/2.0, pocket_d/2.0, 0), adsk.core.Point3D.create(-pocket_w/2.0, pocket_d/2.0, 0))
        lines_pocket.addByTwoPoints(adsk.core.Point3D.create(-pocket_w/2.0, pocket_d/2.0, 0), adsk.core.Point3D.create(-pocket_w/2.0, -pocket_d/2.0, 0))
        
        prof_pocket_pelvis = sketch_pocket_pelvis.profiles.item(0)
        extInput_pocket_pelvis = extrudes_pelvis.createInput(prof_pocket_pelvis, adsk.fusion.FeatureOperations.CutFeatureOperation)
        extInput_pocket_pelvis.setDistanceExtent(False, adsk.core.ValueInput.createByReal(-12.5)) # Laisse un fond de 1.5 cm
        extrudes_pelvis.add(extInput_pocket_pelvis)
        
        # E. 4 Trous pour les Tubes Carbone (Z: 0 à 14)
        sketch_holes_pelvis = sketches_pelvis.add(xyPlane_pelvis)
        circles_holes_pelvis = sketch_holes_pelvis.sketchCurves.sketchCircles
        for ox in offsets_x:
            for oy in offsets_y:
                circles_holes_pelvis.addByCenterRadius(adsk.core.Point3D.create(ox, oy, 0), tube_radius)
                
        profs_holes_pelvis = adsk.core.ObjectCollection.create()
        for i in range(sketch_holes_pelvis.profiles.count):
            profs_holes_pelvis.add(sketch_holes_pelvis.profiles.item(i))
            
        extInput_holes_pelvis = extrudes_pelvis.createInput(profs_holes_pelvis, adsk.fusion.FeatureOperations.CutFeatureOperation)
        extInput_holes_pelvis.setDistanceExtent(False, adsk.core.ValueInput.createByReal(h_pelvis))
        extrudes_pelvis.add(extInput_holes_pelvis)
        
        # F. Supports Moteurs RS-04 de Hanches (Brides verticales sous le Pelvis, Z: 0 à -3 cm)
        sketch_hip_mounts = sketches_pelvis.add(xyPlane_pelvis)
        circles_hip = sketch_hip_mounts.sketchCurves.sketchCircles
        lines_hip = sketch_hip_mounts.sketchCurves.sketchLines
        
        # Support Gauche (X: -11, Y: 0)
        circles_hip.addByCenterRadius(adsk.core.Point3D.create(-11.0, 0, 0), 4.5) # Diamètre externe 90 mm
        circles_hip.addByCenterRadius(adsk.core.Point3D.create(-11.0, 0, 0), 3.5) # Diamètre interne 70 mm
        lines_hip.addByTwoPoints(adsk.core.Point3D.create(-15.5, 0, 0), adsk.core.Point3D.create(-15.5, 5.0, 0))
        lines_hip.addByTwoPoints(adsk.core.Point3D.create(-15.5, 5.0, 0), adsk.core.Point3D.create(-6.5, 5.0, 0))
        lines_hip.addByTwoPoints(adsk.core.Point3D.create(-6.5, 5.0, 0), adsk.core.Point3D.create(-6.5, 0, 0))
        
        # Support Droit (X: 11, Y: 0)
        circles_hip.addByCenterRadius(adsk.core.Point3D.create(11.0, 0, 0), 4.5)
        circles_hip.addByCenterRadius(adsk.core.Point3D.create(11.0, 0, 0), 3.5)
        lines_hip.addByTwoPoints(adsk.core.Point3D.create(6.5, 0, 0), adsk.core.Point3D.create(6.5, 5.0, 0))
        lines_hip.addByTwoPoints(adsk.core.Point3D.create(6.5, 5.0, 0), adsk.core.Point3D.create(15.5, 5.0, 0))
        lines_hip.addByTwoPoints(adsk.core.Point3D.create(15.5, 5.0, 0), adsk.core.Point3D.create(15.5, 0, 0))
        
        profs_hip = adsk.core.ObjectCollection.create()
        for i in range(sketch_hip_mounts.profiles.count):
            profs_hip.add(sketch_hip_mounts.profiles.item(i))
            
        extInput_hip = extrudes_pelvis.createInput(profs_hip, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        extInput_hip.setDistanceExtent(False, adsk.core.ValueInput.createByReal(-3.0)) # Extrude vers le bas de 30 mm
        extrudes_pelvis.add(extInput_hip)
        
        # --- 4. COMPOSANT 2 : THORAX (BUSTE BIONIQUE) ---
        occ_thorax = comp_option_c.occurrences.addNewComponent(transform)
        comp_thorax = occ_thorax.component
        comp_thorax.name = "Thorax_PA12CF"
        
        extrudes_thorax = comp_thorax.features.extrudeFeatures
        sketches_thorax = comp_thorax.sketches
        xyPlane_thorax = comp_thorax.xYConstructionPlane
        planes_thorax = comp_thorax.constructionPlanes
        
        # A. Plan de base du Thorax (Z = 28 cm)
        planeInput_tb = planes_thorax.createInput()
        planeInput_tb.setByOffset(xyPlane_thorax, adsk.core.ValueInput.createByReal(h_pelvis + gap))
        basePlane_thorax = planes_thorax.add(planeInput_tb)
        
        # B. Bloc Solide Thorax (Z: 28 à 42)
        sketch_base_thorax = sketches_thorax.add(basePlane_thorax)
        lines_tb = sketch_base_thorax.sketchCurves.sketchLines
        lines_tb.addByTwoPoints(adsk.core.Point3D.create(-w/2.0, -d/2.0, 0), adsk.core.Point3D.create(w/2.0, -d/2.0, 0))
        lines_tb.addByTwoPoints(adsk.core.Point3D.create(w/2.0, -d/2.0, 0), adsk.core.Point3D.create(w/2.0, d/2.0, 0))
        lines_tb.addByTwoPoints(adsk.core.Point3D.create(w/2.0, d/2.0, 0), adsk.core.Point3D.create(-w/2.0, d/2.0, 0))
        lines_tb.addByTwoPoints(adsk.core.Point3D.create(-w/2.0, d/2.0, 0), adsk.core.Point3D.create(-w/2.0, -d/2.0, 0))
        
        prof_base_thorax = sketch_base_thorax.profiles.item(0)
        extInput_thorax = extrudes_thorax.createInput(prof_base_thorax, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        extInput_thorax.setDistanceExtent(False, adsk.core.ValueInput.createByReal(h_thorax))
        ext_thorax = extrudes_thorax.add(extInput_thorax)
        
        # C. Évidements Bioniques Frontaux/Dorsaux (Symmetric Cut depuis le plan XZ à Y = 0, Z: 29.5 à 40.5)
        sketch_truss_tf = sketches_thorax.add(comp_thorax.xZConstructionPlane)
        lines_ttf = sketch_truss_tf.sketchCurves.sketchLines
        # Triangle gauche (Coordonnées Y de l'esquisse négatives pour correspondre à Z positif en 3D)
        lines_ttf.addByTwoPoints(adsk.core.Point3D.create(-13.5, -29.5, 0), adsk.core.Point3D.create(-13.5, -40.5, 0))
        lines_ttf.addByTwoPoints(adsk.core.Point3D.create(-13.5, -40.5, 0), adsk.core.Point3D.create(-2.0, -35.0, 0))
        lines_ttf.addByTwoPoints(adsk.core.Point3D.create(-2.0, -35.0, 0), adsk.core.Point3D.create(-13.5, -29.5, 0))
        # Triangle droit
        lines_ttf.addByTwoPoints(adsk.core.Point3D.create(13.5, -29.5, 0), adsk.core.Point3D.create(13.5, -40.5, 0))
        lines_ttf.addByTwoPoints(adsk.core.Point3D.create(13.5, -40.5, 0), adsk.core.Point3D.create(2.0, -35.0, 0))
        lines_ttf.addByTwoPoints(adsk.core.Point3D.create(2.0, -35.0, 0), adsk.core.Point3D.create(13.5, -29.5, 0))
        # Triangle supérieur
        lines_ttf.addByTwoPoints(adsk.core.Point3D.create(-11.5, -40.5, 0), adsk.core.Point3D.create(11.5, -40.5, 0))
        lines_ttf.addByTwoPoints(adsk.core.Point3D.create(11.5, -40.5, 0), adsk.core.Point3D.create(0.0, -37.0, 0))
        lines_ttf.addByTwoPoints(adsk.core.Point3D.create(0.0, -37.0, 0), adsk.core.Point3D.create(-11.5, -40.5, 0))
        # Triangle inférieur
        lines_ttf.addByTwoPoints(adsk.core.Point3D.create(-11.5, -29.5, 0), adsk.core.Point3D.create(11.5, -29.5, 0))
        lines_ttf.addByTwoPoints(adsk.core.Point3D.create(11.5, -29.5, 0), adsk.core.Point3D.create(0.0, -33.0, 0))
        lines_ttf.addByTwoPoints(adsk.core.Point3D.create(0.0, -33.0, 0), adsk.core.Point3D.create(-11.5, -29.5, 0))
        
        profs_truss_tf = adsk.core.ObjectCollection.create()
        for i in range(sketch_truss_tf.profiles.count):
            profs_truss_tf.add(sketch_truss_tf.profiles.item(i))
            
        extInput_truss_tf = extrudes_thorax.createInput(profs_truss_tf, adsk.fusion.FeatureOperations.CutFeatureOperation)
        extInput_truss_tf.setSymmetricExtent(adsk.core.ValueInput.createByReal(12.0), False)
        extrudes_thorax.add(extInput_truss_tf)
        
        # D. Évidements Bioniques Latéraux Gauche/Droite (Symmetric Cut depuis le plan YZ à X = 0, Z: 29.5 à 40.5)
        sketch_truss_tl = sketches_thorax.add(comp_thorax.yZConstructionPlane)
        lines_ttl = sketch_truss_tl.sketchCurves.sketchLines
        # Triangle haut-gauche (Coordonnées Z directes positives sur le plan YZ)
        lines_ttl.addByTwoPoints(adsk.core.Point3D.create(-9.5, 40.5, 0), adsk.core.Point3D.create(0, 40.5, 0))
        lines_ttl.addByTwoPoints(adsk.core.Point3D.create(0, 40.5, 0), adsk.core.Point3D.create(-9.5, 31.0, 0))
        lines_ttl.addByTwoPoints(adsk.core.Point3D.create(-9.5, 31.0, 0), adsk.core.Point3D.create(-9.5, 40.5, 0))
        # Triangle haut-droit
        lines_ttl.addByTwoPoints(adsk.core.Point3D.create(9.5, 40.5, 0), adsk.core.Point3D.create(0, 40.5, 0))
        lines_ttl.addByTwoPoints(adsk.core.Point3D.create(0, 40.5, 0), adsk.core.Point3D.create(9.5, 31.0, 0))
        lines_ttl.addByTwoPoints(adsk.core.Point3D.create(9.5, 31.0, 0), adsk.core.Point3D.create(9.5, 40.5, 0))
        # Triangle bas central
        lines_ttl.addByTwoPoints(adsk.core.Point3D.create(-8.0, 29.5, 0), adsk.core.Point3D.create(8.0, 29.5, 0))
        lines_ttl.addByTwoPoints(adsk.core.Point3D.create(8.0, 29.5, 0), adsk.core.Point3D.create(0, 38.0, 0))
        lines_ttl.addByTwoPoints(adsk.core.Point3D.create(0, 38.0, 0), adsk.core.Point3D.create(-8.0, 29.5, 0))
        
        profs_truss_tl = adsk.core.ObjectCollection.create()
        for i in range(sketch_truss_tl.profiles.count):
            profs_truss_tl.add(sketch_truss_tl.profiles.item(i))
            
        extInput_truss_tl = extrudes_thorax.createInput(profs_truss_tl, adsk.fusion.FeatureOperations.CutFeatureOperation)
        extInput_truss_tl.setSymmetricExtent(adsk.core.ValueInput.createByReal(16.0), False)
        extrudes_thorax.add(extInput_truss_tl)

        # E. Poche Interne d'Évidement du Thorax (Z: 28 à 41, laisse paroi 1.5 cm)
        sketch_pocket_thorax = sketches_thorax.add(basePlane_thorax)
        lines_pt = sketch_pocket_thorax.sketchCurves.sketchLines
        lines_pt.addByTwoPoints(adsk.core.Point3D.create(-pocket_w/2.0, -pocket_d/2.0, 0), adsk.core.Point3D.create(pocket_w/2.0, -pocket_d/2.0, 0))
        lines_pt.addByTwoPoints(adsk.core.Point3D.create(pocket_w/2.0, -pocket_d/2.0, 0), adsk.core.Point3D.create(pocket_w/2.0, pocket_d/2.0, 0))
        lines_pt.addByTwoPoints(adsk.core.Point3D.create(pocket_w/2.0, pocket_d/2.0, 0), adsk.core.Point3D.create(-pocket_w/2.0, pocket_d/2.0, 0))
        lines_pt.addByTwoPoints(adsk.core.Point3D.create(-pocket_w/2.0, pocket_d/2.0, 0), adsk.core.Point3D.create(-pocket_w/2.0, -pocket_d/2.0, 0))
        
        prof_pocket_thorax = sketch_pocket_thorax.profiles.item(0)
        extInput_pocket_thorax = extrudes_thorax.createInput(prof_pocket_thorax, adsk.fusion.FeatureOperations.CutFeatureOperation)
        extInput_pocket_thorax.setDistanceExtent(False, adsk.core.ValueInput.createByReal(12.5)) # Laisse 1.5 cm au plafond
        extrudes_thorax.add(extInput_pocket_thorax)
        
        # F. 4 Trous pour les Tubes Carbone (Z: 28 à 42)
        sketch_holes_thorax = sketches_thorax.add(basePlane_thorax)
        circles_holes_thorax = sketch_holes_thorax.sketchCurves.sketchCircles
        for ox in offsets_x:
            for oy in offsets_y:
                circles_holes_thorax.addByCenterRadius(adsk.core.Point3D.create(ox, oy, 0), tube_radius)
                
        profs_holes_thorax = adsk.core.ObjectCollection.create()
        for i in range(sketch_holes_thorax.profiles.count):
            profs_holes_thorax.add(sketch_holes_thorax.profiles.item(i))
            
        extInput_holes_thorax = extrudes_thorax.createInput(profs_holes_thorax, adsk.fusion.FeatureOperations.CutFeatureOperation)
        extInput_holes_thorax.setDistanceExtent(False, adsk.core.ValueInput.createByReal(h_thorax))
        extrudes_thorax.add(extInput_holes_thorax)
        
        # G. Supports Épaules Gauche/Droite (RS-04 Épaules, Ø90 ext, Ø70 int, dépasse de 3 cm, Z: 35)
        # Plan latéral gauche X = -15 cm
        planeInput_ls = planes_thorax.createInput()
        planeInput_ls.setByOffset(comp_thorax.yZConstructionPlane, adsk.core.ValueInput.createByReal(-w/2.0))
        leftPlane_thorax = planes_thorax.add(planeInput_ls)
        
        sketch_left_shoulder = sketches_thorax.add(leftPlane_thorax)
        circles_ls = sketch_left_shoulder.sketchCurves.sketchCircles
        circles_ls.addByCenterRadius(adsk.core.Point3D.create(0, 35.0, 0), 4.5)
        circles_ls.addByCenterRadius(adsk.core.Point3D.create(0, 35.0, 0), 3.5)
        
        profs_ls = adsk.core.ObjectCollection.create()
        for i in range(sketch_left_shoulder.profiles.count):
            profs_ls.add(sketch_left_shoulder.profiles.item(i))
            
        extInput_ls = extrudes_thorax.createInput(profs_ls, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        extInput_ls.setDistanceExtent(False, adsk.core.ValueInput.createByReal(-3.0)) # Extrude vers l'extérieur (gauche)
        extrudes_thorax.add(extInput_ls)
        
        # Plan latéral droit X = 15 cm
        planeInput_rs = planes_thorax.createInput()
        planeInput_rs.setByOffset(comp_thorax.yZConstructionPlane, adsk.core.ValueInput.createByReal(w/2.0))
        rightPlane_thorax = planes_thorax.add(planeInput_rs)
        
        sketch_right_shoulder = sketches_thorax.add(rightPlane_thorax)
        circles_rs = sketch_right_shoulder.sketchCurves.sketchCircles
        circles_rs.addByCenterRadius(adsk.core.Point3D.create(0, 35.0, 0), 4.5)
        circles_rs.addByCenterRadius(adsk.core.Point3D.create(0, 35.0, 0), 3.5)
        
        profs_rs = adsk.core.ObjectCollection.create()
        for i in range(sketch_right_shoulder.profiles.count):
            profs_rs.add(sketch_right_shoulder.profiles.item(i))
            
        extInput_rs = extrudes_thorax.createInput(profs_rs, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        extInput_rs.setDistanceExtent(False, adsk.core.ValueInput.createByReal(3.0)) # Extrude vers l'extérieur (droite)
        extrudes_thorax.add(extInput_rs)
        
        # H. Passage du Cou / Tête (Collet supérieur, Z: 42 à 44)
        planeInput_tc = planes_thorax.createInput()
        planeInput_tc.setByOffset(xyPlane_thorax, adsk.core.ValueInput.createByReal(h_pelvis + gap + h_thorax))
        topPlane_thorax = planes_thorax.add(planeInput_tc)
        
        sketch_neck = sketches_thorax.add(topPlane_thorax)
        circles_neck = sketch_neck.sketchCurves.sketchCircles
        circles_neck.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 5.0) # Ø100 mm externe
        circles_neck.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 4.0) # Ø80 mm interne
        
        profs_neck = adsk.core.ObjectCollection.create()
        for i in range(sketch_neck.profiles.count):
            profs_neck.add(sketch_neck.profiles.item(i))
            
        extInput_neck = extrudes_thorax.createInput(profs_neck, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        extInput_neck.setDistanceExtent(False, adsk.core.ValueInput.createByReal(2.0)) # Dépasse de 20 mm vers le haut
        extrudes_thorax.add(extInput_neck)
        
        # --- 5. COMPOSANT 3 : CARBON TUBES (LIAISON RECTILIGNE, Z: 0 à 42) ---
        occ_tubes = comp_option_c.occurrences.addNewComponent(transform)
        comp_tubes = occ_tubes.component
        comp_tubes.name = "Carbon_Tubes"
        
        extrudes_tubes = comp_tubes.features.extrudeFeatures
        sketches_tubes = comp_tubes.sketches
        sketch_tubes = sketches_tubes.add(xyPlane_pelvis)
        
        circles_tubes = sketch_tubes.sketchCurves.sketchCircles
        for ox in offsets_x:
            for oy in offsets_y:
                circles_tubes.addByCenterRadius(adsk.core.Point3D.create(ox, oy, 0), tube_radius)
                
        profs_tubes = adsk.core.ObjectCollection.create()
        for i in range(sketch_tubes.profiles.count):
            profs_tubes.add(sketch_tubes.profiles.item(i))
            
        extInput_tubes = extrudes_tubes.createInput(profs_tubes, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        extInput_tubes.setDistanceExtent(False, adsk.core.ValueInput.createByReal(h_pelvis + gap + h_thorax)) # 42 cm de haut
        extrudes_tubes.add(extInput_tubes)
        
        # --- 6. COMPOSANT 4 : CENTRAL EQUIP MOUNT (PLATINE & COLLIERS, Z: 18 à 24) ---
        occ_equip = comp_option_c.occurrences.addNewComponent(transform)
        comp_equip = occ_equip.component
        comp_equip.name = "Central_Equip_Mount"
        
        extrudes_equip = comp_equip.features.extrudeFeatures
        sketches_equip = comp_equip.sketches
        planes_equip = comp_equip.constructionPlanes
        
        # A. Colliers de serrage (Z: 18 à 24, Ø35 ext, Ø25 int)
        planeInput_ec = planes_equip.createInput()
        planeInput_ec.setByOffset(comp_equip.xYConstructionPlane, adsk.core.ValueInput.createByReal(18.0))
        clampPlane = planes_equip.add(planeInput_ec)
        
        sketch_clamps = sketches_equip.add(clampPlane)
        circles_clamps = sketch_clamps.sketchCurves.sketchCircles
        for ox in offsets_x:
            for oy in offsets_y:
                circles_clamps.addByCenterRadius(adsk.core.Point3D.create(ox, oy, 0), 1.75) # Ø35 mm
                circles_clamps.addByCenterRadius(adsk.core.Point3D.create(ox, oy, 0), 1.25) # Ø25 mm
                
        profs_clamps = adsk.core.ObjectCollection.create()
        for i in range(sketch_clamps.profiles.count):
            profs_clamps.add(sketch_clamps.profiles.item(i))
            
        extInput_clamps = extrudes_equip.createInput(profs_clamps, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        extInput_clamps.setDistanceExtent(False, adsk.core.ValueInput.createByReal(6.0)) # Hauteur collier = 60 mm
        extrudes_equip.add(extInput_clamps)
        
        # B. Platine de support batterie/Jetson (Z: 20.75 à 21.25, épaisseur 5 mm)
        planeInput_ep = planes_equip.createInput()
        planeInput_ep.setByOffset(comp_equip.xYConstructionPlane, adsk.core.ValueInput.createByReal(20.75))
        platePlane = planes_equip.add(planeInput_ep)
        
        sketch_plate = sketches_equip.add(platePlane)
        lines_plate = sketch_plate.sketchCurves.sketchLines
        circles_plate = sketch_plate.sketchCurves.sketchCircles
        
        # Rectangle externe
        lines_plate.addByTwoPoints(adsk.core.Point3D.create(-12.0, -8.0, 0), adsk.core.Point3D.create(12.0, -8.0, 0))
        lines_plate.addByTwoPoints(adsk.core.Point3D.create(12.0, -8.0, 0), adsk.core.Point3D.create(12.0, 8.0, 0))
        lines_plate.addByTwoPoints(adsk.core.Point3D.create(12.0, 8.0, 0), adsk.core.Point3D.create(-12.0, 8.0, 0))
        lines_plate.addByTwoPoints(adsk.core.Point3D.create(-12.0, 8.0, 0), adsk.core.Point3D.create(-12.0, -8.0, 0))
        
        # Trous d'intégration avec les colliers
        for ox in offsets_x:
            for oy in offsets_y:
                circles_plate.addByCenterRadius(adsk.core.Point3D.create(ox, oy, 0), 1.75) # Épouse la forme des brides
                
        # Évidement allégé central rectangulaire
        lines_plate.addByTwoPoints(adsk.core.Point3D.create(-9.0, -5.0, 0), adsk.core.Point3D.create(9.0, -5.0, 0))
        lines_plate.addByTwoPoints(adsk.core.Point3D.create(9.0, -5.0, 0), adsk.core.Point3D.create(9.0, 5.0, 0))
        lines_plate.addByTwoPoints(adsk.core.Point3D.create(9.0, 5.0, 0), adsk.core.Point3D.create(-9.0, 5.0, 0))
        lines_plate.addByTwoPoints(adsk.core.Point3D.create(-9.0, 5.0, 0), adsk.core.Point3D.create(-9.0, -5.0, 0))
        
        profs_plate = adsk.core.ObjectCollection.create()
        for i in range(sketch_plate.profiles.count):
            profs_plate.add(sketch_plate.profiles.item(i))
            
        extInput_plate = extrudes_equip.createInput(profs_plate, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        extInput_plate.setDistanceExtent(False, adsk.core.ValueInput.createByReal(0.5)) # Platine de 5 mm d'épaisseur
        extrudes_equip.add(extInput_plate)
        
        # --- 7. FINALISATION & REFRESH ---
        app.activeViewport.refresh()
        
        success_message = (
            "🎉 Châssis Torse Bionique Option C généré avec un succès absolu !\n\n"
            "Modélisations structurelles réalisées :\n"
            "1. 'Pelvis_PA12CF' : Boîtier bassin évidé avec truss bioniques frontaux et supports RS-04 intégrés.\n"
            "2. 'Thorax_PA12CF' : Boîtier thoracique avec truss en X, collets d'épaules et col du cou.\n"
            "3. 'Carbon_Tubes' : 4x tubes de liaison Ø25 mm.\n"
            "4. 'Central_Equip_Mount' : Platine allégée centrale porte-batterie/Jetson et ses 4 brides de serrage.\n\n"
            "Cette base CAO propre, paramétrique et allégée est prête pour vos finitions !"
        )
        ui.messageBox(success_message, "Succès - D-Bot Bionic Torso CAD")
        
    except Exception as e:
        if ui:
            ui.messageBox(f"❌ Erreur lors de la génération :\n{traceback.format_exc()}", "Erreur - Bionic CAD Generator")

if __name__ == '__main__':
    run(None)

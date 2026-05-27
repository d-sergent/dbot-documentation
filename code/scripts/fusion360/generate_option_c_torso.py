# -*- coding: utf-8 -*-
"""
Fusion 360 Script: Generate Parametric 3D Skeleton for D-Bot Torso (Option C - Split-Monocoque)
=============================================================================================
Ce script s'exécute directement dans Fusion 360 (Utilitaires -> Scripts et compléments).
Il génère automatiquement la structure 3D exacte de l'Option C :
- 1 Composant parent : D-Bot_Torso_Option_C
- 1 Composant Pelvis_PA12CF (Bassin) de 300 x 220 x 140 mm avec ses 4 perçages
- 1 Composant Thorax_PA12CF (Thorax) de 300 x 220 x 140 mm à Z = 280 mm avec ses 4 perçages
- 1 Composant Carbon_Tubes de Ø25 mm reliant les deux blocs sur toute la hauteur (420 mm)

Les unités internes de Fusion 360 étant en centimètres (cm), toutes les cotes sont converties :
300 mm -> 30 cm | 220 mm -> 22 cm | 140 mm -> 14 cm | Ø25 mm -> 2.5 cm
"""

import adsk.core, adsk.fusion, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # Récupérer le document actif
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox("❌ Aucun design actif détecté.\nVeuillez ouvrir un nouveau fichier ou un document actif avant de lancer le script.")
            return
            
        rootComp = design.rootComponent
        
        # --- 1. CREATION DU COMPOSANT PARENT OPTION C ---
        transform = adsk.core.Matrix3D.create()
        occ_option_c = rootComp.occurrences.addNewComponent(transform)
        comp_option_c = occ_option_c.component
        comp_option_c.name = "D-Bot_Torso_Option_C"
        
        # --- 2. CREATION DES SOUS-COMPOSANTS ---
        occ_pelvis = comp_option_c.occurrences.addNewComponent(transform)
        comp_pelvis = occ_pelvis.component
        comp_pelvis.name = "Pelvis_PA12CF"
        
        occ_thorax = comp_option_c.occurrences.addNewComponent(transform)
        comp_thorax = occ_thorax.component
        comp_thorax.name = "Thorax_PA12CF"
        
        occ_tubes = comp_option_c.occurrences.addNewComponent(transform)
        comp_tubes = occ_tubes.component
        comp_tubes.name = "Carbon_Tubes"
        
        # --- 3. DÉFINITION DES DIMENSIONS (EN CM) ---
        w = 30.0          # Largeur = 300 mm
        d = 22.0          # Profondeur = 220 mm
        h_pelvis = 14.0   # Hauteur Pelvis = 140 mm
        h_thorax = 14.0   # Hauteur Thorax = 140 mm
        gap = 14.0        # Espace intermédiaire = 140 mm (Hauteur totale = 42 cm / 420 mm)
        
        tube_dia = 2.5    # Diamètre tube carbone = 25 mm
        tube_radius = tube_dia / 2.0
        
        # Entraxe des tubes (110 mm en X, 70 mm en Y depuis le centre)
        offsets_x = [-11.0, 11.0]
        offsets_y = [-7.0, 7.0]
        
        # --- 4. CONSTRUCTION DU PELVIS (BASSIN) ---
        sketches_pelvis = comp_pelvis.sketches
        xyPlane_pelvis = comp_pelvis.xYConstructionPlane
        
        # Sketch rectangle de base
        sketch_rect_pelvis = sketches_pelvis.add(xyPlane_pelvis)
        lines_pelvis = sketch_rect_pelvis.sketchCurves.sketchLines
        p1 = adsk.core.Point3D.create(-w/2.0, -d/2.0, 0)
        p2 = adsk.core.Point3D.create(w/2.0, -d/2.0, 0)
        p3 = adsk.core.Point3D.create(w/2.0, d/2.0, 0)
        p4 = adsk.core.Point3D.create(-w/2.0, d/2.0, 0)
        
        lines_pelvis.addByTwoPoints(p1, p2)
        lines_pelvis.addByTwoPoints(p2, p3)
        lines_pelvis.addByTwoPoints(p3, p4)
        lines_pelvis.addByTwoPoints(p4, p1)
        
        # Extrusion du bloc solide
        prof_pelvis = sketch_rect_pelvis.profiles.item(0)
        extrudes_pelvis = comp_pelvis.features.extrudeFeatures
        extInput_pelvis = extrudes_pelvis.createInput(prof_pelvis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distance_pelvis = adsk.core.ValueInput.createByReal(h_pelvis)
        extInput_pelvis.setDistanceExtent(False, distance_pelvis)
        ext_pelvis = extrudes_pelvis.add(extInput_pelvis)
        
        # Perçages des 4 trous
        sketch_holes_pelvis = sketches_pelvis.add(xyPlane_pelvis)
        circles_pelvis = sketch_holes_pelvis.sketchCurves.sketchCircles
        for ox in offsets_x:
            for oy in offsets_y:
                center = adsk.core.Point3D.create(ox, oy, 0)
                circles_pelvis.addByCenterRadius(center, tube_radius)
                
        # Collection des profils des cercles pour l'extrusion de coupe
        profs_holes_pelvis = adsk.core.ObjectCollection.create()
        for i in range(sketch_holes_pelvis.profiles.count):
            profs_holes_pelvis.add(sketch_holes_pelvis.profiles.item(i))
            
        extInput_holes_pelvis = extrudes_pelvis.createInput(profs_holes_pelvis, adsk.fusion.FeatureOperations.CutFeatureOperation)
        extInput_holes_pelvis.setDistanceExtent(False, distance_pelvis)
        extrudes_pelvis.add(extInput_holes_pelvis)
        
        # --- 5. CONSTRUCTION DU THORAX ---
        # Création d'un plan décalé à Z = 28 cm (h_pelvis + gap)
        planes_thorax = comp_thorax.constructionPlanes
        planeInput = planes_thorax.createInput()
        offsetValue = adsk.core.ValueInput.createByReal(h_pelvis + gap)
        planeInput.setByOffset(comp_thorax.xYConstructionPlane, offsetValue)
        thoraxPlane = planes_thorax.add(planeInput)
        
        sketches_thorax = comp_thorax.sketches
        
        # Sketch rectangle de base
        sketch_rect_thorax = sketches_thorax.add(thoraxPlane)
        lines_thorax = sketch_rect_thorax.sketchCurves.sketchLines
        p1_t = adsk.core.Point3D.create(-w/2.0, -d/2.0, 0)
        p2_t = adsk.core.Point3D.create(w/2.0, -d/2.0, 0)
        p3_t = adsk.core.Point3D.create(w/2.0, d/2.0, 0)
        p4_t = adsk.core.Point3D.create(-w/2.0, d/2.0, 0)
        
        lines_thorax.addByTwoPoints(p1_t, p2_t)
        lines_thorax.addByTwoPoints(p2_t, p3_t)
        lines_thorax.addByTwoPoints(p3_t, p4_t)
        lines_thorax.addByTwoPoints(p4_t, p1_t)
        
        # Extrusion du bloc solide
        prof_thorax = sketch_rect_thorax.profiles.item(0)
        extrudes_thorax = comp_thorax.features.extrudeFeatures
        extInput_thorax = extrudes_thorax.createInput(prof_thorax, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distance_thorax = adsk.core.ValueInput.createByReal(h_thorax)
        extInput_thorax.setDistanceExtent(False, distance_thorax)
        ext_thorax = extrudes_thorax.add(extInput_thorax)
        
        # Perçages des 4 trous
        sketch_holes_thorax = sketches_thorax.add(thoraxPlane)
        circles_thorax = sketch_holes_thorax.sketchCurves.sketchCircles
        for ox in offsets_x:
            for oy in offsets_y:
                center = adsk.core.Point3D.create(ox, oy, 0)
                circles_thorax.addByCenterRadius(center, tube_radius)
                
        # Collection des profils des cercles pour l'extrusion de coupe
        profs_holes_thorax = adsk.core.ObjectCollection.create()
        for i in range(sketch_holes_thorax.profiles.count):
            profs_holes_thorax.add(sketch_holes_thorax.profiles.item(i))
            
        extInput_holes_thorax = extrudes_thorax.createInput(profs_holes_thorax, adsk.fusion.FeatureOperations.CutFeatureOperation)
        extInput_holes_thorax.setDistanceExtent(False, distance_thorax)
        extrudes_thorax.add(extInput_holes_thorax)
        
        # --- 6. CONSTRUCTION DES TUBES DE CARBONE ---
        sketches_tubes = comp_tubes.sketches
        xyPlane_tubes = comp_tubes.xYConstructionPlane
        sketch_tubes = sketches_tubes.add(xyPlane_tubes)
        
        # Dessiner les 4 cercles de tubes
        circles_tubes = sketch_tubes.sketchCurves.sketchCircles
        for ox in offsets_x:
            for oy in offsets_y:
                center = adsk.core.Point3D.create(ox, oy, 0)
                circles_tubes.addByCenterRadius(center, tube_radius)
                
        # Extruder les 4 tubes sur toute la hauteur
        profs_tubes = adsk.core.ObjectCollection.create()
        for i in range(sketch_tubes.profiles.count):
            profs_tubes.add(sketch_tubes.profiles.item(i))
            
        extrudes_tubes = comp_tubes.features.extrudeFeatures
        extInput_tubes = extrudes_tubes.createInput(profs_tubes, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distance_tubes = adsk.core.ValueInput.createByReal(h_pelvis + gap + h_thorax) # 42.0 cm (420 mm)
        extInput_tubes.setDistanceExtent(False, distance_tubes)
        extrudes_tubes.add(extInput_tubes)
        
        # --- 7. REFRESH & SUCCÈS ---
        app.activeViewport.refresh()
        
        # Message explicatif
        success_message = (
            "🎉 Modèle Squelette 3D Option C généré avec succès !\n\n"
            "Composants créés :\n"
            "1. 'Pelvis_PA12CF' : Bloc bas (Z: 0 à 140 mm)\n"
            "2. 'Thorax_PA12CF' : Bloc haut (Z: 280 à 420 mm)\n"
            "3. 'Carbon_Tubes' : 4x tubes carbone Ø25 mm (Z: 0 à 420 mm)\n\n"
            "Vous pouvez maintenant éditer ces composants natifs pour modéliser vos fixations et supports moteurs !"
        )
        ui.messageBox(success_message, "Succès - D-Bot Torse CAD Generator")
        
    except Exception as e:
        if ui:
            ui.messageBox(f"❌ Erreur lors de la génération :\n{traceback.format_exc()}", "Erreur - CAD Generator")

if __name__ == '__main__':
    run(None)

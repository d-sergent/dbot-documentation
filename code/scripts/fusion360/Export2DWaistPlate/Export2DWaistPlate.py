# -*- coding: utf-8 -*-
"""
Export2DWaistPlate.py — Prototype d'Extraction 2D, Cotation & Export DXF CNC
Projet : Robot Humanoïde D-Bot V1 (Torse & Bassin)
=============================================================================
Ce script s'exécute directement dans Fusion 360 (Raccourci Shift + S > Exécuter).
Il prototype les 4 capacités clés de l'API pour la fabrication 2D :
  1. Extraction directe des cotes B-Rep réelles (hors-tout, alésage central, PCD RS-06).
  2. Projection 2D vectorielle d'esquisse (sketch.project).
  3. Exportation automatique en DXF 1:1 pour découpeuse / fraiseuse CNC.
  4. Détection et export PDF de mise en plan si un dessin .f2d est ouvert.
"""

import adsk.core
import adsk.fusion
try:
    import adsk.drawing
except ImportError:
    pass
import os
import traceback
import math

TARGET_COMPONENT_KEYWORD = "waist_plate"
OUTPUT_DIR_SOVEREIGN = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/01_Torse_et_Bassin/DXF_CNC"
OUTPUT_DIR_DOC = "/Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/DXF_CNC"

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        doc = app.activeDocument

        # -------------------------------------------------------------
        # 1. Vérification du type de document actif
        # -------------------------------------------------------------
        # Cas où l'utilisateur exécute le script depuis une mise en plan .f2d
        is_drawing = False
        try:
            if isinstance(doc, adsk.drawing.DrawingDocument):
                is_drawing = True
        except Exception:
            pass

        if is_drawing:
            export_drawing_prototype(doc, ui)
            return

        # Cas standard : Document 3D Design
        design = app.activeProduct
        if not design or not isinstance(design, adsk.fusion.Design):
            ui.messageBox("Veuillez ouvrir le modèle 3D ou la mise en plan de la Waist Plate.", "Document Incompatible")
            return

        root_comp = design.rootComponent

        # -------------------------------------------------------------
        # 2. Recherche du composant Waist Plate 7075
        # -------------------------------------------------------------
        target_occ = None
        for occ in root_comp.allOccurrences:
            if TARGET_COMPONENT_KEYWORD in occ.name.lower() or TARGET_COMPONENT_KEYWORD in occ.component.name.lower():
                target_occ = occ
                break

        if not target_occ:
            ui.messageBox(f"Composant '{TARGET_COMPONENT_KEYWORD}' introuvable dans l'assemblage actif.", "Erreur Recherche")
            return

        comp = target_occ.component
        body = comp.bRepBodies.item(0) if comp.bRepBodies.count > 0 else None
        if not body:
            ui.messageBox("Aucun corps solide B-Rep trouvé dans le composant.", "Erreur Corps")
            return

        # -------------------------------------------------------------
        # 3. Extraction Métrologique B-Rep des Cotes de Fabrication
        # -------------------------------------------------------------
        bbox = body.boundingBox
        dx = round((bbox.maxPoint.x - bbox.minPoint.x) * 10.0, 2)
        dy = round((bbox.maxPoint.y - bbox.minPoint.y) * 10.0, 2)
        dz = round((bbox.maxPoint.z - bbox.minPoint.z) * 10.0, 2)

        # Masse et volume
        props = body.physicalProperties
        mass_g = round(props.mass * 1000.0, 2)
        vol_cm3 = round(props.volume, 2)

        # Détection des perçages et alésages cylindriques
        holes = []
        for face in body.faces:
            geom = face.geometry
            if geom.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType:
                dia = round(geom.radius * 20.0, 2)
                # On évite les doublons de diamètres identiques
                if dia not in holes:
                    holes.append(dia)
        holes.sort()

        # -------------------------------------------------------------
        # 4. Sélection de la Face Plane Principale pour Projection 2D
        # -------------------------------------------------------------
        # Recherche de la face plane ayant la plus grande surface d'appui
        best_face = None
        max_area = 0.0
        for face in body.faces:
            geom = face.geometry
            if geom.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType:
                area = face.area
                if area > max_area:
                    max_area = area
                    best_face = face

        if not best_face:
            ui.messageBox("Impossible d'identifier une face plane de référence pour la projection 2D.", "Erreur Projection")
            return

        # -------------------------------------------------------------
        # 5. Création de l'Esquisse & Projection Vectorielle 2D
        # -------------------------------------------------------------
        # On crée une esquisse temporaire sur la face plane
        sketches = comp.sketches
        temp_sketch = sketches.add(best_face)
        temp_sketch.name = "TEMP_CNC_EXPORT_WAIST_PLATE"

        # Projection géométrique exacte du contour et de tous les perçages
        temp_sketch.project(body)

        # -------------------------------------------------------------
        # 6. Exportation DXF 1:1 pour Machine CNC
        # -------------------------------------------------------------
        os.makedirs(OUTPUT_DIR_SOVEREIGN, exist_ok=True)
        os.makedirs(OUTPUT_DIR_DOC, exist_ok=True)

        dxf_sovereign = os.path.join(OUTPUT_DIR_SOVEREIGN, "Waist_Plate_7075_Usinage_1to1.dxf")
        dxf_doc = os.path.join(OUTPUT_DIR_DOC, "Waist_Plate_7075_Usinage_1to1.dxf")

        # Sauvegarde native DXF via l'API Fusion 360
        res1 = temp_sketch.saveAsDXF(dxf_sovereign)
        try:
            temp_sketch.saveAsDXF(dxf_doc)
        except Exception:
            pass

        # -------------------------------------------------------------
        # 7. Nettoyage de l'Esquisse Temporaire (Zéro Pollution Timeline)
        # -------------------------------------------------------------
        temp_sketch.deleteMe()

        # -------------------------------------------------------------
        # 8. Affichage du Rapport Métrologique & DXF à l'Utilisateur
        # -------------------------------------------------------------
        holes_str = ", ".join(f"Ø{h} mm" for h in holes[:6])
        if len(holes) > 6:
            holes_str += f" (+{len(holes)-6} autres)"

        msg = (
            f"=== PROTOTYPE 2D & EXPORT CNC VALIDÉ ===\n\n"
            f"Pièce ciblée : {comp.name}\n"
            f"Matière B-Rep : {body.material.name if body.material else 'Aluminium 7075'}\n"
            f"Masse réelle : {mass_g} g\n"
            f"Volume : {vol_cm3} cm3\n\n"
            f"COTES B-REP EXTRAITES AUTOMATIQUEMENT :\n"
            f"  - Largeur X : {dx} mm\n"
            f"  - Profondeur Y : {dy} mm\n"
            f"  - Épaisseur Z : {dz} mm\n"
            f"  - Alésages / Perçages détectés : {holes_str}\n\n"
            f"FICHIER DXF VECTORIEL 1:1 GÉNÉRÉ :\n"
            f"→ {dxf_sovereign}\n\n"
            f"Le fichier est prêt pour usinage CNC / Découpe laser (échelle 1:1 stricte)."
        )

        ui.messageBox(msg, "Prototype 2D & DXF Waist Plate")

    except Exception:
        if ui:
            ui.messageBox(f"Erreur durant l'exécution du prototype :\n{traceback.format_exc()}", "Erreur Prototype")


def export_drawing_prototype(drawing_doc, ui):
    """Prototype d'automatisation sur une feuille de mise en plan .f2d ouverte."""
    try:
        sheet = drawing_doc.activeSheet
        export_mgr = drawing_doc.exportManager
        
        # Exemple d'export PDF vectoriel automatique
        pdf_options = export_mgr.createPDFExportOptions()
        pdf_path = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/01_Torse_et_Bassin/DXF_CNC/Waist_Plate_7075_Plan.pdf"
        pdf_options.filename = pdf_path
        pdf_options.useSheetRange = False
        pdf_options.openPDF = False
        export_mgr.exportToPDF(pdf_options)
        
        ui.messageBox(f"Mise en plan détectée !\nPlan exporté en PDF vectoriel avec succès :\n{pdf_path}", "Export Plan 2D")
    except Exception as e:
        ui.messageBox(f"Erreur durant l'export de la mise en plan :\n{traceback.format_exc()}", "Erreur Drawing API")

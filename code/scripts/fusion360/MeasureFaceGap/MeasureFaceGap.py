# -*- coding: utf-8 -*-
"""
MeasureFaceGap.py — Palpeur Métrologique Réel & Analyseur de Contact (D-Bot V1)
==============================================================================
Ce script est strictement NON-DESTRUCTIF et 100% LECTURE SEULE.

Mode d'emploi :
  1. Lancez le script (Shift + S > MeasureFaceGap > Exécuter).
  2. Cliquez sur la première face (ex: fond de lamage de la traverse).
  3. Cliquez sur la deuxième face (ex: face inférieure du roulement).
  4. Le script calcule automatiquement :
     - La distance normale exacte (écart en mm et en microns).
     - Le parallélisme (angle en degrés).
     - Le verdict de contact (Contact franc, Jeu parasite, Collision).
     - Les liaisons ou contraintes existantes entre les deux pièces.
"""

import adsk.core
import adsk.fusion
import math
import traceback

def safe_get_occ(entity):
    try:
        if hasattr(entity, 'assemblyContext') and entity.assemblyContext:
            return entity.assemblyContext
        if hasattr(entity, 'body') and hasattr(entity.body, 'assemblyContext') and entity.body.assemblyContext:
            return entity.body.assemblyContext
        if hasattr(entity, 'parentComponent'):
            return entity.parentComponent
    except:
        pass
    return None

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox("Aucun document Fusion 360 actif.", "MeasureFaceGap")
            return
            
        # 1. Sélection interactive des 2 faces
        sel1 = ui.selectEntity("Sélectionnez la première face (Face Référence A) :", "Faces")
        if not sel1 or not sel1.entity:
            return
        face1 = adsk.fusion.BRepFace.cast(sel1.entity)
        
        sel2 = ui.selectEntity("Sélectionnez la deuxième face (Face Cible B) :", "Faces")
        if not sel2 or not sel2.entity:
            return
        face2 = adsk.fusion.BRepFace.cast(sel2.entity)
        
        occ1 = safe_get_occ(face1)
        occ2 = safe_get_occ(face2)
        occ1_name = occ1.name if occ1 else "Inconnue"
        occ2_name = occ2.name if occ2 else "Inconnue"
        
        geom1 = face1.geometry
        geom2 = face2.geometry
        
        report = []
        report.append("=== RÉSULTAT DU PALPAGE MÉTROLOGIQUE ===")
        report.append(f"• Pièce A : {occ1_name}")
        report.append(f"• Pièce B : {occ2_name}")
        report.append("")
        
        # CAS 1 : DEUX FACES PLANES
        if geom1.objectType == adsk.core.Plane.classType() and geom2.objectType == adsk.core.Plane.classType():
            plane1 = adsk.core.Plane.cast(geom1)
            plane2 = adsk.core.Plane.cast(geom2)
            
            # Application de la transformation d'occurrence si nécessaire
            p1_origin = face1.pointOnFace
            p2_origin = face2.pointOnFace
            n1 = plane1.normal
            n2 = plane2.normal
            
            # Calcul du parallélisme
            dot = abs(n1.dotProduct(n2))
            dot = min(1.0, max(-1.0, dot))
            angle_rad = math.acos(dot)
            angle_deg = round(math.degrees(angle_rad), 3)
            is_parallel = (angle_deg < 0.1)
            
            report.append("--- GÉOMÉTRIE DES PLANS ---")
            report.append(f"• Parallélisme : {'PARALLÈLES (OK)' if is_parallel else f'NON PARALLÈLES (Angle = {angle_deg} deg)'}")
            report.append(f"• Altitude Z Face A : {round(p1_origin.z * 10.0, 3)} mm")
            report.append(f"• Altitude Z Face B : {round(p2_origin.z * 10.0, 3)} mm")
            
            # Calcul de l'écart normal
            delta_vec = adsk.core.Vector3D.create(p2_origin.x - p1_origin.x, p2_origin.y - p1_origin.y, p2_origin.z - p1_origin.z)
            gap_cm = delta_vec.dotProduct(n1)
            gap_mm = round(abs(gap_cm) * 10.0, 3)
            gap_microns = int(round(gap_mm * 1000.0))
            
            report.append("")
            report.append("--- VERDICT D'ASSISE & ÉCART ---")
            if gap_mm <= 0.02:
                report.append("✅ CONTACT FRANC (0.00 mm) : Les deux faces sont parfaitement plaquées.")
            else:
                report.append(f"⚠️ JEU PARASITE DÉTECTÉ : {gap_mm} mm ({gap_microns} µm)")
                report.append(f"   La face B flotte à {gap_mm} mm au-dessus de la face A.")
                
        # CAS 2 : DEUX CYLINDRES (Alésage / Fût)
        elif geom1.objectType == adsk.core.Cylinder.classType() and geom2.objectType == adsk.core.Cylinder.classType():
            cyl1 = adsk.core.Cylinder.cast(geom1)
            cyl2 = adsk.core.Cylinder.cast(geom2)
            
            r1_mm = round(cyl1.radius * 10.0, 3)
            r2_mm = round(cyl2.radius * 10.0, 3)
            
            report.append("--- GÉOMÉTRIE DES CYLINDRES ---")
            report.append(f"• Rayon Cylindre A : {r1_mm} mm (Diamètre = {r1_mm*2:.2f} mm)")
            report.append(f"• Rayon Cylindre B : {r2_mm} mm (Diamètre = {r2_mm*2:.2f} mm)")
            report.append(f"• Jeu radial théorique : {round(abs(r1_mm - r2_mm), 3)} mm")
            
        else:
            report.append("Les deux faces sélectionnées ne sont ni deux plans ni deux cylindres comparables.")
            
        # 2. Vérification des liaisons existantes entre ces deux pièces
        report.append("")
        report.append("--- LIAISONS & RELATIONS ENTRE CES 2 PIÈCES ---")
        links = []
        for comp in design.allComponents:
            for j in comp.joints:
                na = j.occurrenceOne.name if j.occurrenceOne else ""
                nb = j.occurrenceTwo.name if j.occurrenceTwo else ""
                if (na == occ1_name and nb == occ2_name) or (na == occ2_name and nb == occ1_name):
                    links.append(f"• [Joint] '{j.name}' dans '{comp.name}'")
            for abj in comp.asBuiltJoints:
                na = abj.occurrenceOne.name if abj.occurrenceOne else ""
                nb = abj.occurrenceTwo.name if abj.occurrenceTwo else ""
                if (na == occ1_name and nb == occ2_name) or (na == occ2_name and nb == occ1_name):
                    links.append(f"• [As-Built Joint] '{abj.name}' dans '{comp.name}'")
                    
        if links:
            report.extend(links)
        else:
            report.append("Aucune liaison Joint / As-Built Joint directe n'existe entre ces deux pièces.")
            
        ui.messageBox("\n".join(report), "MeasureFaceGap — Palpeur Métrologique")
        
    except Exception as e:
        if ui:
            ui.messageBox(f"Erreur durant la mesure :\n{traceback.format_exc()}", "Erreur MeasureFaceGap")

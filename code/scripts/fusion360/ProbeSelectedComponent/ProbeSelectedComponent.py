# -*- coding: utf-8 -*-
"""
ProbeSelectedComponent.py — Diagnostic Cinématique Immédiat par Sélection (D-Bot V1)
====================================================================================
Ce script est strictement NON-DESTRUCTIF et 100% LECTURE SEULE.

Mode d'emploi :
  1. Sélectionnez une pièce dans l'écran 3D ou dans l'arbre du navigateur (ou lancez le script qui vous invitera à sélectionner).
  2. Le script analyse instantanément :
     - Si la pièce est fixée au sol (isGrounded).
     - Tous les Groupes Rigides (RigidGroups) dans lesquels elle est verrouillée.
     - Toutes les Liaisons (Joints & AsBuiltJoints) qui lui sont rattachées.
     - Ses coordonnées géométriques (Bounding Box, altitude Z).
"""

import adsk.core
import adsk.fusion
import os
import traceback

def safe_get_occ_name(entity):
    if entity is None:
        return "Origine/Sol"
    try:
        if hasattr(entity, 'name'):
            return entity.name
        if hasattr(entity, 'assemblyContext') and entity.assemblyContext:
            return entity.assemblyContext.name
        return str(entity)
    except:
        return "<Inconnu>"

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox("Aucun document Fusion 360 actif.", "ProbeSelectedComponent")
            return
            
        root_comp = design.rootComponent
        
        # 1. Récupération de la sélection active
        selected_occ = None
        if ui.activeSelections.count > 0:
            sel = ui.activeSelections.item(0).entity
            if hasattr(sel, 'objectType') and 'Occurrence' in sel.objectType:
                selected_occ = adsk.fusion.Occurrence.cast(sel)
            elif hasattr(sel, 'assemblyContext') and sel.assemblyContext:
                selected_occ = sel.assemblyContext
            elif hasattr(sel, 'body') and hasattr(sel.body, 'assemblyContext') and sel.body.assemblyContext:
                selected_occ = sel.body.assemblyContext
                
        # Si rien n'est sélectionné, inviter l'utilisateur à cliquer sur un composant
        if not selected_occ:
            try:
                sel_prompt = ui.selectEntity("Sélectionnez le composant à inspecter :", "Occurrences")
                if sel_prompt and sel_prompt.entity:
                    selected_occ = adsk.fusion.Occurrence.cast(sel_prompt.entity)
            except:
                pass
                
        if not selected_occ:
            ui.messageBox("Aucun composant sélectionné. Veuillez sélectionner une pièce et relancer.", "ProbeSelectedComponent")
            return
            
        occ_name = selected_occ.name
        comp_name = selected_occ.component.name
        is_grounded = selected_occ.isGrounded
        
        # Bounding box
        bbox = selected_occ.boundingBox
        z_min = round(bbox.minPoint.z * 10.0, 3)
        z_max = round(bbox.maxPoint.z * 10.0, 3)
        x_min = round(bbox.minPoint.x * 10.0, 3)
        x_max = round(bbox.maxPoint.x * 10.0, 3)
        y_min = round(bbox.minPoint.y * 10.0, 3)
        y_max = round(bbox.maxPoint.y * 10.0, 3)
        height_z = round(z_max - z_min, 3)
        
        report = []
        report.append(f"=== RAPPORT D'INSPECTION : {occ_name} ===")
        report.append(f"• Composant parent : {comp_name}")
        report.append(f"• Fixé au sol (isGrounded) : {'OUI (Verrouillé absolu)' if is_grounded else 'NON (Libre)'}")
        report.append(f"• BBox Z : [{z_min}, {z_max}] mm (Hauteur = {height_z} mm)")
        report.append(f"• BBox X : [{x_min}, {x_max}] mm | Y : [{y_min}, {y_max}] mm")
        report.append("")
        
        # 2. Recherche dans tous les Groupes Rigides
        report.append("--- GROUPES RIGIDES CONTENANT CE COMPOSANT ---")
        rg_found = []
        for comp in design.allComponents:
            for rg in comp.rigidGroups:
                occ_names = [o.name for o in rg.occurrences]
                if occ_name in occ_names:
                    suppr = " [DÉSACTIVÉ]" if getattr(rg, 'isSuppressed', False) else " [ACTIF]"
                    other_members = [o for o in occ_names if o != occ_name]
                    rg_found.append(
                        f"  🔹 '{rg.name}'{suppr} dans '{comp.name}'\n"
                        f"     Verrouillé avec {len(other_members)} autres pièces : {', '.join(other_members[:5])}" +
                        (f" ... (+{len(other_members)-5} autres)" if len(other_members) > 5 else "")
                    )
        if rg_found:
            report.extend(rg_found)
        else:
            report.append("  Aucun groupe rigide ne contient cette pièce.")
        report.append("")
        
        # 3. Recherche dans toutes les Liaisons (Joints & AsBuiltJoints)
        report.append("--- LIAISONS (JOINTS) TOUCHANT CE COMPOSANT ---")
        joints_found = []
        for comp in design.allComponents:
            for j in comp.joints:
                n1 = safe_get_occ_name(j.occurrenceOne)
                n2 = safe_get_occ_name(j.occurrenceTwo)
                if occ_name in [n1, n2]:
                    other = n2 if n1 == occ_name else n1
                    suppr = " [DÉSACTIVÉ]" if getattr(j, 'isSuppressed', False) else " [ACTIF]"
                    joints_found.append(f"  🔹 [Joint] '{j.name}'{suppr} dans '{comp.name}' ➔ Relié à : '{other}'")
                    
            for abj in comp.asBuiltJoints:
                n1 = safe_get_occ_name(abj.occurrenceOne)
                n2 = safe_get_occ_name(abj.occurrenceTwo)
                if occ_name in [n1, n2]:
                    other = n2 if n1 == occ_name else n1
                    suppr = " [DÉSACTIVÉ]" if getattr(abj, 'isSuppressed', False) else " [ACTIF]"
                    joints_found.append(f"  🔹 [As-Built Joint] '{abj.name}'{suppr} dans '{comp.name}' ➔ Relié à : '{other}'")
                    
        if joints_found:
            report.extend(joints_found)
        else:
            report.append("  Aucune liaison Joint / As-Built Joint rattachée à cette pièce.")
        report.append("")
        
        final_text = "\n".join(report)
        ui.messageBox(final_text, f"Diagnostic — {occ_name}")
        
    except Exception as e:
        if ui:
            ui.messageBox(f"Erreur durant le diagnostic :\n{traceback.format_exc()}", "Erreur ProbeSelectedComponent")

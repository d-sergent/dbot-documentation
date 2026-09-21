# -*- coding: utf-8 -*-
"""
ModifyTorse.py — Script de Modifications Unitaires pour Fusion 360 (D-Bot V1)
=============================================================================
Ce script s'exécute dans Fusion 360 (Shift + S > ModifyTorse > Exécuter).
Il lit le fichier 'actions_to_apply.json' et applique les modifications demandées :
  - Renommage ciblé de composants
  - Assignation et création intelligente de matériaux physiques :
      * Aluminium 7075-T6 (2,81 g/cm3)
      * PA12-CF Plein 100% (1,18 g/cm3)
      * PA12-CF Infill 30% Gyroïde (0,56 g/cm3 - densité apparente)
      * PA12-CF Infill 50% Gyroïde (0,72 g/cm3 - densité apparente)
  - Modification de paramètres utilisateur
"""

import adsk.core
import adsk.fusion
import json
import os
import traceback

def create_or_get_custom_material(design, app, mat_name, density_g_cm3):
    """Crée ou récupère un matériau sur-mesure dans Fusion 360 avec sa densité exacte."""
    # 1. Vérifier si le matériau existe déjà dans le document
    existing = design.materials.itemByName(mat_name)
    if existing:
        return existing
        
    # 2. Trouver un matériau de base à copier
    base_mat = None
    
    # Chercher d'abord dans la bibliothèque Fusion 360
    mat_lib = app.materialLibraries.itemByName('Fusion 360 Material Library')
    if mat_lib:
        for candidate in ['ABS Plastic', 'Nylon 6/6', 'Plastic', 'Polycarbonate']:
            try:
                m = mat_lib.materials.itemByName(candidate)
                if m:
                    base_mat = m
                    break
            except:
                pass
                
    # Si non trouvé, chercher dans toutes les bibliothèques disponibles
    if not base_mat:
        for lib in app.materialLibraries:
            try:
                for m in lib.materials:
                    m_l = m.name.lower()
                    if "nylon" in m_l or "plastic" in m_l or "abs" in m_l or "polyamide" in m_l:
                        base_mat = m
                        break
                if base_mat:
                    break
            except:
                pass
            
    # Fallback sur un matériau existant dans le design
    if not base_mat and design.materials.count > 0:
        base_mat = design.materials.item(0)
        
    if not base_mat:
        return None
        
    try:
        # Utiliser impérativement addByCopy (méthode officielle de l'API Fusion 360)
        new_mat = design.materials.addByCopy(base_mat, mat_name)
        if not new_mat:
            return None
            
        # Ajuster la propriété physique de densité (en g/cm3)
        density_prop = new_mat.materialProperties.itemByName('Density')
        if density_prop:
            try:
                density_prop.value = float(density_g_cm3)
            except:
                pass
        else:
            for prop in new_mat.materialProperties:
                if "density" in prop.name.lower():
                    try:
                        prop.value = float(density_g_cm3)
                        break
                    except:
                        pass
        return new_mat
    except:
        return None

def find_best_material(design, app, req_mat_name):
    """Recherche ou crée le matériau demandé."""
    req_l = req_mat_name.lower()
    
    # 1. Cas spécifiques PA12-CF avec Infill
    if "pa12-cf" in req_l or "pa12" in req_l or "nylon 12-cf" in req_l:
        if "30%" in req_l or "30" in req_l:
            return create_or_get_custom_material(design, app, "PA12-CF (Infill 30% Gyroïde)", 0.56)
        elif "50%" in req_l or "50" in req_l:
            return create_or_get_custom_material(design, app, "PA12-CF (Infill 50% Gyroïde)", 0.72)
        else:
            return create_or_get_custom_material(design, app, "PA12-CF (Plein 100%)", 1.18)
            
    # 2. Cas Aluminium 6060 / 6061
    if "6060" in req_l or "6061" in req_l:
        for m in design.materials:
            if "6060" in m.name.lower() or "6061" in m.name.lower():
                return m
        for lib in app.materialLibraries:
            try:
                for m in lib.materials:
                    if "6060" in m.name.lower() or "6061" in m.name.lower():
                        return design.materials.addByCopy(m, m.name)
            except:
                pass
        return create_or_get_custom_material(design, app, "Aluminium 6060-T6", 2.70)

    # 3. Cas Aluminium 7075
    if "7075" in req_l or "alumin" in req_l:
        for m in design.materials:
            if "7075" in m.name.lower():
                return m
        for lib in app.materialLibraries:
            try:
                for m in lib.materials:
                    if "7075" in m.name.lower():
                        return design.materials.addByCopy(m, m.name)
            except:
                pass
        for m in design.materials:
            if "6061" in m.name.lower() or "alumin" in m.name.lower():
                return m
        return create_or_get_custom_material(design, app, "Aluminium 7075-T6", 2.81)

    # 4. Cas Acier Inoxydable (Stainless Steel)
    if "inox" in req_l or "stainless" in req_l:
        for m in design.materials:
            if "inox" in m.name.lower() or "stainless" in m.name.lower():
                return m
        for lib in app.materialLibraries:
            try:
                for candidate in ['Stainless Steel', 'Acier inoxydable', 'Steel, Stainless']:
                    m = lib.materials.itemByName(candidate)
                    if m:
                        return design.materials.addByCopy(m, m.name)
            except:
                pass
        return create_or_get_custom_material(design, app, "Acier inoxydable A2", 7.93)

    # 5. Cas Acier Carbone / Haute résistance (Steel)
    if "acier" in req_l or "steel" in req_l:
        for m in design.materials:
            if "acier" in m.name.lower() or "steel" in m.name.lower():
                return m
        for lib in app.materialLibraries:
            try:
                for candidate in ['Steel', 'Acier', 'Steel, Mild']:
                    m = lib.materials.itemByName(candidate)
                    if m:
                        return design.materials.addByCopy(m, m.name)
            except:
                pass

    # 6. Recherche par nom direct dans le design ou les bibliothèques
    mat = design.materials.itemByName(req_mat_name)
    if mat:
        return mat
        
    for lib in app.materialLibraries:
        try:
            m = lib.materials.itemByName(req_mat_name)
            if m:
                return design.materials.addByCopy(m, m.name)
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
            ui.messageBox("Aucun modèle actif dans Fusion 360.")
            return
            
        root_comp = design.rootComponent
        
        # Localiser le fichier actions_to_apply.json
        script_dir = os.path.dirname(os.path.realpath(__file__))
        actions_file = os.path.join(script_dir, "actions_to_apply.json")
        repo_actions_file = "/Users/Shared/Mon Google Drive Physique/Documentation/Code/scripts/fusion360/ModifyTorse/actions_to_apply.json"
        
        target_json = actions_file if os.path.exists(actions_file) else repo_actions_file
        
        if not os.path.exists(target_json):
            ui.messageBox(f"Fichier d'actions introuvable :\n{target_json}")
            return
            
        with open(target_json, "r", encoding="utf-8") as f:
            config = json.load(f)
            
        actions = config.get("actions", [])
        if not actions:
            ui.messageBox("Aucune action spécifiée dans le fichier JSON.")
            return
            
        changes_log = []
        
        for action in actions:
            action_type = action.get("type")
            
            # --- 1. Renommage de composant ---
            if action_type == "rename_component":
                target_name = action.get("target_name")
                new_name = action.get("new_name")
                renamed_count = 0
                
                for occ in root_comp.allOccurrences:
                    comp = occ.component
                    if comp.name == target_name:
                        comp.name = new_name
                        import re
                        pn_match = re.search(r'\[([A-Za-z0-9_\-]+)\]', new_name)
                        if pn_match:
                            try:
                                comp.partNumber = pn_match.group(1)
                            except:
                                pass
                        renamed_count += 1
                        changes_log.append(f"Renommé composant : '{target_name}' -> '{new_name}'")
                        
                if renamed_count == 0:
                    changes_log.append(f"Note : '{target_name}' n'a pas été trouvé (déjà renommé en '{new_name}' ?)")
                    
            # --- 2. Assignation de matériau physique ---
            elif action_type == "set_material":
                target_comps = action.get("target_components", [])
                mat_name = action.get("material_name", "Aluminium 7075-T6")
                
                material_obj = find_best_material(design, app, mat_name)
                
                if not material_obj:
                    changes_log.append(f"Avertissement : Matériau '{mat_name}' impossible à charger ou créer.")
                    continue
                    
                applied_count = 0
                for occ in root_comp.allOccurrences:
                    comp = occ.component
                    if comp.name in target_comps:
                        try:
                            comp.material = material_obj
                            for b in comp.bRepBodies:
                                try:
                                    b.material = material_obj
                                except:
                                    pass
                            applied_count += 1
                            changes_log.append(f"Matériau '{material_obj.name}' appliqué sur '{comp.name}'")
                        except Exception as e_mat:
                            changes_log.append(f"Erreur matériau sur '{comp.name}' : {str(e_mat)}")
                            
                if applied_count == 0:
                    changes_log.append(f"Note : Aucun composant correspondant à {target_comps} trouvé pour {mat_name}.")

            # --- 3. Modification de paramètre utilisateur ---
            elif action_type == "set_user_parameter":
                param_name = action.get("parameter_name")
                new_expression = action.get("expression")
                
                param = design.userParameters.itemByName(param_name)
                if param:
                    old_exp = param.expression
                    param.expression = str(new_expression)
                    changes_log.append(f"Paramètre '{param_name}' modifié : {old_exp} -> {new_expression}")
                else:
                    changes_log.append(f"Avertissement : Paramètre '{param_name}' introuvable.")

        summary_msg = "=== MODIFICATIONS APPLIQUÉES DANS FUSION 360 ===\n\n" + "\n".join(changes_log)
        ui.messageBox(summary_msg, "ModifyTorse D-Bot")

    except Exception as e:
        if ui:
            ui.messageBox(f"Erreur durant l'exécution de ModifyTorse :\n{traceback.format_exc()}", "Erreur ModifyTorse")


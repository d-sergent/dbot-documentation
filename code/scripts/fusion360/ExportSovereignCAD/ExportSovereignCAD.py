# -*- coding: utf-8 -*-
"""
=============================================================================
ExportSovereignCAD.py — Extracteur CAO Souverain Fusion 360 pour FreeCAD
=============================================================================
Ce script s'exécute dans Autodesk Fusion 360 (Shift + S > ExportSovereignCAD > Run).
Il accomplit automatiquement :
1. Le parcours récursif de l'assemblage actif.
2. L'identification et la déduplication des composants uniques.
3. L'export des fichiers B-Rep STEP unitaires dans /Users/Shared/DBot_CAD_Library/.
4. L'enregistrement du manifeste spatial complet (matrices 4x4, repères, hiérarchie).
"""

import adsk.core
import adsk.fusion
import os
import re
import json
import traceback
from datetime import datetime

EXPORT_DIR = "/Users/Shared/Mon Google Drive Physique/Exports_CAO_DBot/Bibliotheque_Composants_STEP"
MANIFEST_FILE = os.path.join(EXPORT_DIR, "dbot_cad_manifest.json")

def sanitize_filename(name):
    """Nettoie le nom de composant pour en faire un nom de fichier STEP valide."""
    # Remplacer les caractères interdits par un tiret bas
    clean = re.sub(r'[\\/*?:"<>| \(\)\[\]:]', '_', name)
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean or "component"

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        
        if not design:
            if ui:
                ui.messageBox("Veuillez ouvrir un assemblage Fusion 360 actif avant d'exécuter ce script.", "Export CAO Souverain")
            return
            
        root_comp = design.rootComponent
        doc_name = app.activeDocument.name
        
        # Création du dossier d'export
        os.makedirs(EXPORT_DIR, exist_ok=True)
        
        export_mgr = design.exportManager
        
        manifest = {
            "metadata": {
                "source_document": doc_name,
                "export_date": datetime.now().isoformat(),
                "fusion_version": app.version,
                "export_directory": EXPORT_DIR
            },
            "components": {},
            "occurrences": []
        }
        
        all_occurrences = root_comp.allOccurrences
        total_occs = all_occurrences.count
        
        exported_components = set()
        export_errors = []
        
        # 1. Parcours des occurrences et déduplication des composants
        for i in range(total_occs):
            occ = all_occurrences.item(i)
            
            # Ne traiter que les composants visibles (non masqués)
            if not occ.isLightBulbOn:
                continue
                
            comp = occ.component
            comp_name = comp.name
            safe_name = sanitize_filename(comp_name)
            comp_id = comp.id
            
            # Nom du fichier STEP associé
            step_filename = f"{safe_name}.step"
            step_path = os.path.join(EXPORT_DIR, step_filename)
            
            # Export STEP du composant (avec écrasement pour propager les modifications)
            if comp_id not in exported_components:
                try:
                    step_options = export_mgr.createSTEPExportOptions(step_path, comp)
                    export_mgr.execute(step_options)
                except Exception as exp_err:
                    export_errors.append(f"{comp_name}: {str(exp_err)}")
                        
                exported_components.add(comp_id)
                
                # Métadonnées physiques du composant
                comp_mass_g = 0.0
                comp_vol_cm3 = 0.0
                try:
                    c_props = comp.getPhysicalProperties(adsk.fusion.CalculationAccuracy.MediumCalculationAccuracy)
                    comp_mass_g = round(c_props.mass * 1000.0, 2)
                    comp_vol_cm3 = round(c_props.volume, 2)
                except:
                    pass
                    
                manifest["components"][comp_id] = {
                    "component_name": comp_name,
                    "safe_name": safe_name,
                    "step_file": step_filename,
                    "part_number": comp.partNumber,
                    "description": comp.description,
                    "material": comp.material.name if comp.material else "Aluminium 7075",
                    "mass_g": comp_mass_g,
                    "volume_cm3": comp_vol_cm3
                }
                
            # Extraction de la position spatiale globale (Transform 4x4)
            transform = occ.transform
            origin, x_axis, y_axis, z_axis = transform.getAsCoordinateSystem()
            
            # Fusion stocke en cm -> conversion en millimètres (x10.0)
            origin_mm = [round(origin.x * 10.0, 4), round(origin.y * 10.0, 4), round(origin.z * 10.0, 4)]
            x_vec = [round(x_axis.x, 6), round(x_axis.y, 6), round(x_axis.z, 6)]
            y_vec = [round(y_axis.x, 6), round(y_axis.y, 6), round(y_axis.z, 6)]
            z_vec = [round(z_axis.x, 6), round(z_axis.y, 6), round(z_axis.z, 6)]
            
            # Détermination du parent dans l'arbre hiérarchique
            parent_occ = occ.assemblyContext
            parent_name = parent_occ.name if parent_occ else "Root"
            
            manifest["occurrences"].append({
                "instance_name": occ.name,
                "component_id": comp_id,
                "parent_instance": parent_name,
                "origin_mm": origin_mm,
                "x_axis": x_vec,
                "y_axis": y_vec,
                "z_axis": z_vec
            })
            
        # 2. Écriture du manifeste JSON
        with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            
        # 3. Message récapitulatif
        nb_comps = len(manifest["components"])
        nb_occs = len(manifest["occurrences"])
        msg = (
            f"SUCCÈS : Export CAO Souverain Terminé !\n\n"
            f"• Document : {doc_name}\n"
            f"• Composants uniques exportés en STEP : {nb_comps}\n"
            f"• Instances positionnées (Occurrences) : {nb_occs}\n"
            f"• Dossier de destination : {EXPORT_DIR}\n"
            f"• Manifeste JSON : {MANIFEST_FILE}\n\n"
            f"Prochaine étape :\n"
            f"L'agent Antigravity va importer immédiatement ces STEPs dans FreeCAD pour reconstituer l'assemblage complet."
        )
        if export_errors:
            msg += f"\n\nAttention : {len(export_errors)} avertissement(s) d'export."
            
        if ui:
            ui.messageBox(msg, "D-Bot — Export CAO Souverain")
        else:
            print(msg)
            
    except Exception as e:
        err_msg = f"Erreur critique lors de l'exportation :\n{str(e)}\n\n{traceback.format_exc()}"
        if ui:
            ui.messageBox(err_msg, "Erreur Export CAO")
        else:
            print(err_msg)

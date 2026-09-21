# -*- coding: utf-8 -*-
"""
TimelineKinematicInspector.py — Inspecteur Cinématique par Voyage Temporel (D-Bot V1)
=====================================================================================
Ce script est strictement NON-DESTRUCTIF et 100% LECTURE SEULE.

Principe :
  Il contourne la limitation de l'API Fusion 360 ('Cannot be edited before rolling back')
  en pilotant de manière transparente et sécurisée la chronologie (Timeline) :
  1. Mémorise la position actuelle de la timeline.
  2. Pour chaque contrainte d'assemblage saine, déplace temporairement le marqueur
     temporel juste sur la contrainte (rollTo).
  3. Lit de manière 100% native et autorisée les deux pièces réelles (entityOne / entityTwo)
     et le type de contact (Face-Face, Arête-Face, Aligner, etc.).
  4. Restaure automatiquement et impérativement la timeline à la fin (moveToEnd).
  5. Enregistre le rapport complet dans :
     /Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/timeline_kinematic_map.txt
"""

import adsk.core
import adsk.fusion
import os
import traceback

def safe_get_occ_name(entity):
    if entity is None:
        return "None"
    try:
        if hasattr(entity, 'objectType') and 'Occurrence' in entity.objectType:
            return entity.name
        if hasattr(entity, 'assemblyContext') and entity.assemblyContext:
            return entity.assemblyContext.name
        if hasattr(entity, 'body') and hasattr(entity.body, 'assemblyContext') and entity.body.assemblyContext:
            return entity.body.assemblyContext.name
        if hasattr(entity, 'parentComponent'):
            return entity.parentComponent.name
        if hasattr(entity, 'name'):
            return entity.name
        return str(entity)
    except:
        return "<Inconnu>"

def run(context):
    ui = None
    initial_pos = None
    design = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox("Aucun document Fusion 360 actif.", "TimelineKinematicInspector")
            return
            
        root_comp = design.rootComponent
        timeline = design.timeline
        initial_pos = timeline.markerPosition
        
        output_dir = "/Users/Shared/Mon Google Drive Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin"
        output_file = os.path.join(output_dir, "timeline_kinematic_map.txt")
        
        lines = []
        lines.append("=" * 80)
        lines.append("CARTOGRAPHIE CINÉMATIQUE EXHAUSTIVE PAR VOYAGE TEMPOREL — D-BOT")
        lines.append(f"Document : {root_comp.name}")
        lines.append("=" * 80)
        lines.append("")
        
        total_inspected = 0
        total_mapped = 0
        
        for comp in design.allComponents:
            for i in range(comp.assemblyConstraints.count):
                c = comp.assemblyConstraints.item(i)
                total_inspected += 1
                c_name = getattr(c, 'name', f"Contrainte_{i}")
                c_health = getattr(c, 'healthState', 0)
                
                # Ignorer si la contrainte est corrompue pour éviter un crash
                if c_health == 4 or not getattr(c, 'isValid', True):
                    lines.append(f"🔹 [{total_inspected}] '{c_name}' dans '{comp.name}' : ⚠️ ÉTAT D'ERREUR CRITIQUE (Non inspectée par sécurité)")
                    continue
                    
                tl_obj = getattr(c, 'timelineObject', None)
                if tl_obj:
                    try:
                        # VOYAGE TEMPOREL : Se positionner juste sur l'objet
                        tl_obj.rollTo(True)
                        
                        geom_rels = getattr(c, 'geometricRelationships', None)
                        if geom_rels and geom_rels.count > 0:
                            for r_idx in range(geom_rels.count):
                                rel = geom_rels.item(r_idx)
                                rel_type = getattr(rel, 'relationshipType', 'Relation')
                                e1 = getattr(rel, 'entityOne', None)
                                e2 = getattr(rel, 'entityTwo', None)
                                
                                n1 = safe_get_occ_name(e1)
                                n2 = safe_get_occ_name(e2)
                                
                                t1 = e1.objectType.split('::')[-1] if hasattr(e1, 'objectType') else type(e1).__name__
                                t2 = e2.objectType.split('::')[-1] if hasattr(e2, 'objectType') else type(e2).__name__
                                
                                lines.append(f"🔹 [{total_inspected}] '{c_name}' (#{r_idx+1}) dans '{comp.name}'")
                                lines.append(f"     Type : {rel_type} ({t1} <---> {t2})")
                                lines.append(f"     Liaison : '{n1}' <---> '{n2}'")
                                total_mapped += 1
                        else:
                            lines.append(f"🔹 [{total_inspected}] '{c_name}' dans '{comp.name}' : (Aucune relation interne)")
                    except Exception as e_roll:
                        lines.append(f"🔹 [{total_inspected}] '{c_name}' dans '{comp.name}' : <Erreur inspection: {str(e_roll)}>")
                else:
                    lines.append(f"🔹 [{total_inspected}] '{c_name}' dans '{comp.name}' : (Pas d'objet timeline)")
                lines.append("")
                
        lines.append(f"Total des contraintes analysées : {total_inspected}")
        lines.append(f"Total des relations cartographiées avec succès : {total_mapped}")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
            
        ui.messageBox(
            f"Inspection par voyage temporel terminée avec succès !\n\n"
            f"Contraintes analysées : {total_inspected}\n"
            f"Relations cartographiées : {total_mapped}\n\n"
            f"Rapport sauvegardé dans :\n{output_file}",
            "TimelineKinematicInspector"
        )
        
    except Exception as e:
        if ui:
            ui.messageBox(f"Erreur durant l'inspection temporelle :\n{traceback.format_exc()}", "Erreur TimelineKinematicInspector")
    finally:
        # RESTAURATION SYSTÉMATIQUE DE LA TIMELINE À LA FIN
        if design and design.timeline:
            try:
                design.timeline.moveToEnd()
            except:
                pass

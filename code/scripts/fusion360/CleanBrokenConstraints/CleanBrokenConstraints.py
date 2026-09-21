# -*- coding: utf-8 -*-
"""
CleanBrokenConstraints.py — Docteur d'Assainissement du Solveur d'Assemblage (D-Bot V1)
=====================================================================================
Ce script est un outil de maintenance et d'intégrité pour Fusion 360.

Rôle :
  1. Détecte toutes les Contraintes d'Assemblage, Liaisons ou Groupes Rigides qui sont
     en état d'anomalie ou d'erreur (healthState != 0 ou isValid == False).
  2. Liste les éléments corrompus avec leur code d'erreur exact.
  3. Propose de manière interactive et sécurisée à l'utilisateur de les supprimer
     pour éliminer tout risque de crash ou de blocage du solveur.
"""

import adsk.core
import adsk.fusion
import traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox("Aucun document Fusion 360 actif.", "CleanBrokenConstraints")
            return
            
        broken_items = []
        
        for comp in design.allComponents:
            # 1. Contraintes d'assemblage
            for i in range(comp.assemblyConstraints.count):
                c = comp.assemblyConstraints.item(i)
                health = getattr(c, 'healthState', 0)
                is_valid = getattr(c, 'isValid', True)
                if health != 0 or not is_valid:
                    h_desc = "ERREUR CRITIQUE (Code 4)" if health == 4 else f"Avertissement / Anomalie (Code {health})"
                    broken_items.append({
                        "type": "Contrainte d'assemblage",
                        "name": getattr(c, 'name', f"Contrainte_{i}"),
                        "comp": comp.name,
                        "health": h_desc,
                        "obj": c
                    })
                    
            # 2. Liaisons Joint
            for j in comp.joints:
                health = getattr(j, 'healthState', 0)
                is_valid = getattr(j, 'isValid', True)
                if health != 0 or not is_valid:
                    broken_items.append({
                        "type": "Joint",
                        "name": j.name,
                        "comp": comp.name,
                        "health": f"Code {health}",
                        "obj": j
                    })
                    
            # 3. Liaisons AsBuiltJoint
            for abj in comp.asBuiltJoints:
                health = getattr(abj, 'healthState', 0)
                is_valid = getattr(abj, 'isValid', True)
                if health != 0 or not is_valid:
                    broken_items.append({
                        "type": "AsBuiltJoint",
                        "name": abj.name,
                        "comp": comp.name,
                        "health": f"Code {health}",
                        "obj": abj
                    })
                    
        # Bilan
        if not broken_items:
            ui.messageBox(
                "✅ MODÈLE 100% SAIN !\n\n"
                "Aucune contrainte corrompue, cassée ou en erreur n'a été détectée dans l'ensemble du document.",
                "Modèle Intègre — CleanBrokenConstraints"
            )
            return
            
        # Présentation des éléments en erreur
        lines = []
        lines.append(f"⚠️ {len(broken_items)} ÉLÉMENTS EN ANOMALIE DÉTECTÉS :\n")
        for item in broken_items:
            lines.append(f"• [{item['type']}] '{item['name']}' dans '{item['comp']}' — Statut : {item['health']}")
            
        lines.append("\nCes éléments corrompus peuvent bloquer le solveur ou provoquer des plantages inattendus.")
        lines.append("Souhaitez-vous les SUPPRIMER DÉFINITIVEMENT pour assainir le modèle ?")
        
        # Boîte de confirmation Oui / Non
        confirm = ui.messageBox(
            "\n".join(lines),
            "Docteur d'Assainissement — Confirmation",
            adsk.core.MessageBoxButtonTypes.YesNoButtonType,
            adsk.core.MessageBoxIconTypes.WarningIconType
        )
        
        if confirm == adsk.core.DialogResults.DialogYes:
            deleted_count = 0
            for item in broken_items:
                try:
                    obj = item["obj"]
                    if hasattr(obj, 'deleteMe'):
                        obj.deleteMe()
                        deleted_count += 1
                except Exception as e_del:
                    pass
                    
            ui.messageBox(
                f"✅ ASSAINISSEMENT RÉUSSI !\n\n"
                f"{deleted_count} élément(s) corrompu(s) ont été supprimés avec succès.\n"
                f"Le solveur d'assemblage de Fusion 360 est désormais assaini et stable.",
                "Assainissement Terminé"
            )
        else:
            ui.messageBox("Opération annulée. Aucun élément n'a été modifié.", "Annulation")
            
    except Exception as e:
        if ui:
            ui.messageBox(f"Erreur durant l'assainissement :\n{traceback.format_exc()}", "Erreur CleanBrokenConstraints")

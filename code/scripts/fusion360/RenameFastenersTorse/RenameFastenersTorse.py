# -*- coding: utf-8 -*-
"""
RenameFastenersTorse.py — Standardisation Automatisée des Noms de Visserie dans Fusion 360
========================================================================================
Ce script s'exécute directement dans Fusion 360 (Shift + S > RenameFastenersTorse > Exécuter).
Il parcourt l'ensemble des composants et occurrences du Torse et Bassin D-Bot,
identifie les chaînes brutes d'importation McMaster-Carr et les renomme selon
la nomenclature officielle du projet :
  - Vis CHC M4x20 [92290A168]
  - Vis CHC M4x16 [92290A154]
  - Vis FHC M3x8 [92125A128]
  - Rondelle Plate DIN 125A M4 [93475A230]
  - Ecrou Nylstop M4 [93625A150]
  - Goupille cylindrique ISO 8734 Ø3x14 [91585A374]
Il renseigne également le 'Part Number' et la 'Description' officielle de chaque pièce.
"""

import adsk.core
import adsk.fusion
import traceback
import re

FASTENER_RULES = [
    {
        "pattern": r"92290A168",
        "new_name": "Vis CHC M4x20 [92290A168]",
        "part_number": "92290A168",
        "description": "Vis CHC M4 × 20 mm Inox 316 (ISO 4762 / DIN 912)"
    },
    {
        "pattern": r"92290A154",
        "new_name": "Vis CHC M4x16 [92290A154]",
        "part_number": "92290A154",
        "description": "Vis CHC M4 × 16 mm Inox 316 (ISO 4762 / DIN 912)"
    },
    {
        "pattern": r"92125A128",
        "new_name": "Vis FHC M3x8 [92125A128]",
        "part_number": "92125A128",
        "description": "Vis FHC M3 × 8 mm Inox 18-8 (ISO 10642 / DIN 7991)"
    },
    {
        "pattern": r"93475A230",
        "new_name": "Rondelle Plate DIN 125A M4 [93475A230]",
        "part_number": "93475A230",
        "description": "Rondelle Plate DIN 125A M4 Inox 18-8 (ISO 7089 / DIN 125A)"
    },
    {
        "pattern": r"93625A150",
        "new_name": "Ecrou Nylstop M4 [93625A150]",
        "part_number": "93625A150",
        "description": "Écrou Frein Nylstop M4 Inox 18-8 (ISO 7040 / DIN 985)"
    },
    {
        "pattern": r"91585A374",
        "new_name": "Goupille cylindrique ISO 8734 Ø3x14 [91585A374]",
        "part_number": "91585A374",
        "description": "Goupille cylindrique rectifiée Ø 3 × 14 mm Inox 18-8 (ISO 8734 / ISO 2338)"
    },
    {
        "pattern": r"91595A114",
        "new_name": "Goupille cylindrique ISO 8734 Ø3x14 [91595A114]",
        "part_number": "91595A114",
        "description": "Goupille cylindrique rectifiée Ø 3 × 14 mm Acier allié trempé (ISO 8734 / DIN 6325)"
    }
]

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

        renamed_components = 0
        renamed_occurrences = 0
        log_lines = []

        # 1. Parcourir tous les composants uniques du document
        for comp in design.allComponents:
            old_name = comp.name
            for rule in FASTENER_RULES:
                if re.search(rule["pattern"], old_name, re.IGNORECASE):
                    # Si le nom n'est pas déjà exactement le nom standardisé
                    if comp.name != rule["new_name"]:
                        comp.name = rule["new_name"]
                        try:
                            comp.partNumber = rule["part_number"]
                        except:
                            pass
                        try:
                            comp.description = rule["description"]
                        except:
                            pass
                        renamed_components += 1
                        log_lines.append(f"• '{old_name}'\n   ➔ '{rule['new_name']}'")
                    break

        # 2. Nettoyer les occurrences dont le nom d'instance aurait été personnalisé
        root_comp = design.rootComponent
        for occ in root_comp.allOccurrences:
            old_occ_name = occ.name
            for rule in FASTENER_RULES:
                if re.search(rule["pattern"], old_occ_name, re.IGNORECASE):
                    base_prefix = rule["new_name"].split(" [")[0]
                    if not old_occ_name.startswith(base_prefix):
                        try:
                            # Réinitialiser pour reprendre le nom du composant
                            match = re.search(r':(\d+)$', old_occ_name)
                            idx = match.group(1) if match else "1"
                            occ.name = f"{rule['new_name']}:{idx}"
                            renamed_occurrences += 1
                        except:
                            pass
                    break

        # Message de synthèse à l'utilisateur
        msg = "=== STANDARDISATION DE LA VISSERIE TERMINÉE ===\n\n"
        msg += f"Composants uniques renommés : {renamed_components}\n"
        if renamed_occurrences > 0:
            msg += f"Occurrences d'assemblage actualisées : {renamed_occurrences}\n"
        msg += "\n"
        
        if log_lines:
            msg += "Modifications appliquées :\n\n" + "\n\n".join(log_lines)
        else:
            msg += "Toutes les références de visserie sont déjà 100% conformes à la nomenclature D-Bot !"

        ui.messageBox(msg, "RenameFastenersTorse — D-Bot")

    except Exception as e:
        if ui:
            ui.messageBox(f"Erreur durant l'exécution de RenameFastenersTorse :\n{traceback.format_exc()}", "Erreur RenameFastenersTorse")

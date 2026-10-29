# -*- coding: utf-8 -*-
"""
CreateSelectionSetsTorse.py — Organisation Sans Risque par Jeux de Sélection (D-Bot V1)
========================================================================================
Ce script s'exécute directement dans Autodesk Fusion 360 (Shift + S > CreateSelectionSetsTorse > Exécuter).

Rôle et Avantages Majeurs :
1. ZÉRO RISQUE CINÉMATIQUE / SOLVEUR :
   - Ne déplace AUCUN composant dans l'arborescence physique.
   - Ne touche à AUCUNE liaison (Joints), contrainte d'assemblage ou groupe rigide.
   - Ne modifie AUCUNE opération de la chronologie (Timeline).
   - Ne rompt AUCUNE symétrie miroir ni projection d'esquisse.

2. ORGANISATION ET PRODUCTIVITÉ IMMÉDIATE :
   - Classe automatiquement les 419 pièces du Torse et Bassin en 5 familles logiques dans le dossier natif 'Jeux de sélection'.
   - Permet en 1 clic de sélectionner tout un sous-ensemble, de le masquer/afficher (touche V) ou de l'isoler.
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
            ui.messageBox("Aucun document de conception Fusion 360 actif.", "CreateSelectionSetsTorse")
            return
            
        root_comp = design.rootComponent
        selection_sets = design.selectionSets
        
        # ---------------------------------------------------------------------------
        # 1. DÉFINITION DES RÈGLES DE CLASSIFICATION PAR GROUPE
        # ---------------------------------------------------------------------------
        FASTENER_KEYS = [
            'vis', '91292', '92290', '92855', '90348', '90128', '91290', '92125', 
            '91585', 'luosi', 'rondelle', '93475', '91812', 'ecrou', '93625', '90631'
        ]
        
        COVER_KEYS = [
            'carenage', 'plastron', 'panier', 'capot', 'platine_connectique', 'trappe_inferieure'
        ]
        
        STRUCTURE_KEYS = [
            'waist_plate', 'plaque_de_cou', 'colonne', 'semelle', 'insert', 'corniere', 
            'bride epaule', 'tube transverse', 'equerre', 'moyeu_waist', 'bride_retenue', 
            'cou - tube'
        ]
        
        PELVIS_KEYS = [
            'bassin_pelvis', 'chassis_structurel_bassin', 'traverse_renfort_bassin', 
            'support_hanche', 'liaison_hanche'
        ]

        def match_fastener(name_lower):
            return any(k in name_lower for k in FASTENER_KEYS)
            
        def match_cover(name_lower):
            return any(k in name_lower for k in COVER_KEYS)
            
        def match_structure(name_lower):
            return any(k in name_lower for k in STRUCTURE_KEYS)
            
        def match_pelvis(name_lower):
            return any(k in name_lower for k in PELVIS_KEYS)

        # Ordre strict de priorité
        group_definitions = [
            ("01_Quincaillerie_Torse", match_fastener, "Vis, écrous, rondelles et quincaillerie McMaster (1 clic pour tout masquer/afficher)"),
            ("02_Coques_Habillage_PA12CF", match_cover, "Plastron, carénages, panier batterie et trappes d'habillage"),
            ("03_Squelette_Structure_Alu", match_structure, "Colonne vertébrale, plaques cou/waist, brides, tubes, cornières"),
            ("04_Bassin_et_Hanches", match_pelvis, "Châssis structurel bassin, supports hanche, traverses et pelvis"),
            ("05_Actionneurs_Mecanismes", lambda n: True, "Moteurs RS04, RS06, EL05, roulement RB8016 et mécanismes internes")
        ]
        
        # ---------------------------------------------------------------------------
        # 2. PARCOURS ET CLASSIFICATION DE TOUTES LES OCCURRENCES
        # ---------------------------------------------------------------------------
        all_occurrences = []
        for occ in root_comp.allOccurrences:
            all_occurrences.append(occ)
            
        classified_groups = {g[0]: [] for g in group_definitions}
        
        for occ in all_occurrences:
            name_lower = occ.name.lower()
            for grp_name, matcher, _ in group_definitions:
                if matcher(name_lower):
                    classified_groups[grp_name].append(occ)
                    break
                    
        # ---------------------------------------------------------------------------
        # 3. CRÉATION SÉCURISÉE DES JEUX DE SÉLECTION DANS FUSION 360
        # ---------------------------------------------------------------------------
        created_count = 0
        summary_lines = []
        
        for grp_name, _, desc in group_definitions:
            occs = classified_groups[grp_name]
            if not occs:
                continue
                
            # Suppression d'un jeu existant du même nom pour mise à jour propre
            existing = selection_sets.itemByName(grp_name)
            if existing:
                try:
                    existing.deleteMe()
                except:
                    pass
                    
            # Tentative d'ajout via liste native ou ObjectCollection
            success = False
            try:
                selection_sets.add(occs, grp_name)
                success = True
            except:
                try:
                    coll = adsk.core.ObjectCollection.create()
                    for o in occs:
                        coll.add(o)
                    selection_sets.add(coll, grp_name)
                    success = True
                except:
                    try:
                        selection_sets.add(grp_name, occs)
                        success = True
                    except:
                        pass
                        
            if success:
                created_count += 1
                summary_lines.append(f"• {grp_name} : {len(occs)} pièces\n  ({desc})")
            else:
                summary_lines.append(f"• {grp_name} : Échec de création via l'API.")

        # ---------------------------------------------------------------------------
        # 4. MESSAGE RÉCAPITULATIF À L'UTILISATEUR
        # ---------------------------------------------------------------------------
        msg = "=== ORGANISATION PAR JEUX DE SÉLECTION TERMINÉE ===\n\n"
        msg += f"Total d'occurrences classées : {len(all_occurrences)} pièces.\n"
        msg += f"Jeux de sélection créés / actualisés : {created_count} / {len(group_definitions)}\n\n"
        msg += "\n\n".join(summary_lines)
        msg += "\n\n"
        msg += "💡 Utilisation au quotidien :\n"
        msg += "1. Regardez dans le dossier 'Jeux de sélection' en haut de votre Navigateur.\n"
        msg += "2. Cliquez sur 'Sélectionner' à droite du nom du jeu.\n"
        msg += "3. Appuyez sur la touche 'V' de votre clavier pour masquer ou réafficher tout le groupe en 1 clic !"
        
        ui.messageBox(msg, "Jeux de Sélection D-Bot")

    except Exception as e:
        if ui:
            ui.messageBox(f"Erreur lors de la création des jeux de sélection :\n{traceback.format_exc()}", "Erreur")

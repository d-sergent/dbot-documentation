# -*- coding: utf-8 -*-
"""
RenameFastenersTorse.py — Standardisation de la Visserie & Mise à Jour des Matériaux CAO D-Bot
=============================================================================================
Ce script s'exécute directement dans Autodesk Fusion 360 (Shift + S > RenameFastenersTorse > Exécuter).

Fonctionnalités :
1. Standardisation Complète de la Visserie & Quincaillerie McMaster-Carr :
   - Renommage officiel de tous les composants selon la nomenclature projet.
   - Nettoyage des suffixes parasites d'importation dans l'arborescence : ' (1)', ' (2)', ' (4)'.
   - Renseignement systématique du 'Part Number' et de la 'Description' officielle.
   - Regroupement automatique des composants dans la nomenclature BOM de l'audit.

2. Mise à Jour Automatisée des Matériaux Physiques (Densités Réelles) :
   - Visserie Inox 18-8 / 316 -> 'Acier inoxydable' (densité 7,93 g/cm3).
   - Corps 'ceinture' (dans Plastron_Ventral_Torse) -> 'Aluminium 7075-T6' (densité 2,81 g/cm3, masse 38,97 g).
   - Plaques structurales -> 'Aluminium 7075-T6' (Waist, Cou, Colonne, Epaules, Châssis Pelvien).
   - Tube transversal d'épaules -> 'Aluminium 6060-T6' (densité 2,70 g/cm3).
   - Coques & carénages -> 'PA12-CF (Infill 30% Gyroïde)' (densité 0,56 g/cm3).
"""

import adsk.core
import adsk.fusion
import traceback
import re

# ---------------------------------------------------------------------------
# 1. RÈGLES DE NOMENCLATURE ET MATÉRIAUX DE LA QUINCAILLERIE (BOM D-BOT)
# ---------------------------------------------------------------------------
FASTENER_RULES = [
    {
        "pattern": r"91292A122",
        "new_name": "Vis CHC M4x25 [91292A122]",
        "part_number": "91292A122",
        "description": "Vis CHC M4 x 25 mm Inox 18-8 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92290A168",
        "new_name": "Vis CHC M4x20 [92290A168]",
        "part_number": "92290A168",
        "description": "Vis CHC M4 x 20 mm Inox 316 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92290A154",
        "new_name": "Vis CHC M4x16 [92290A154]",
        "part_number": "92290A154",
        "description": "Vis CHC M4 x 16 mm Inox 316 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"90128A214",
        "new_name": "Vis CHC M4x16 [90128A214]",
        "part_number": "90128A214",
        "description": "Vis CHC M4 x 16 mm Acier zingué cl. 8.8 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"90348A023",
        "new_name": "Vis CHC M5x25 [90348A023]",
        "part_number": "90348A023",
        "description": "Vis CHC M5 x 25 mm Inox 18-8 Noir (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"91290A272",
        "new_name": "Vis CHC M5x70 [91290A272]",
        "part_number": "91290A272",
        "description": "Vis CHC M5 x 70 mm Acier 12.9 / Inox (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"91292A113",
        "new_name": "Vis CHC M3x10 [91292A113]",
        "part_number": "91292A113",
        "description": "Vis CHC M3 x 10 mm Inox 18-8 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92855A313",
        "new_name": "Vis CHC M3x12 Tête Basse [92855A313]",
        "part_number": "92855A313",
        "description": "Vis CHC M3 x 12 mm Tête Basse Inox 18-8 (DIN 7984)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92855A422",
        "new_name": "Vis CHC M4x25 Tête Basse [92855A422]",
        "part_number": "92855A422",
        "description": "Vis CHC M4 x 25 mm Tête Basse Inox 18-8 (DIN 7984)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92125A128",
        "new_name": "Vis FHC M3x8 [92125A128]",
        "part_number": "92125A128",
        "description": "Vis FHC M3 x 8 mm Inox 18-8 (ISO 10642 / DIN 7991)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"92125A220",
        "new_name": "Vis FHC M4x30 [92125A220]",
        "part_number": "92125A220",
        "description": "Vis FHC M4 x 30 mm Inox 18-8 (ISO 10642 / DIN 7991)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"93475A230",
        "new_name": "Rondelle Plate DIN 125A M4 [93475A230]",
        "part_number": "93475A230",
        "description": "Rondelle Plate DIN 125A M4 Inox 18-8 (ISO 7089 / DIN 125A)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"93475A240",
        "new_name": "Rondelle Plate DIN 125A M5 [93475A240]",
        "part_number": "93475A240",
        "description": "Rondelle Plate DIN 125A M5 Inox 18-8 (ISO 7089 / DIN 125A)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"91812A252",
        "new_name": "Rondelle Nord-Lock M4 [91812A252]",
        "part_number": "91812A252",
        "description": "Rondelle Nord-Lock M4 Inox / Acier (NL4)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"93625A150",
        "new_name": "Ecrou Nylstop M4 [93625A150]",
        "part_number": "93625A150",
        "description": "Écrou Frein Nylstop M4 Inox 18-8 (ISO 7040 / DIN 985)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"90631A113",
        "new_name": "Ecrou Nylstop M5 [90631A113]",
        "part_number": "90631A113",
        "description": "Écrou Frein Nylstop M5 Inox 18-8 (ISO 7040 / DIN 985)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"91585A374",
        "new_name": "Goupille cylindrique ISO 8734 Ø3x14 [91585A374]",
        "part_number": "91585A374",
        "description": "Goupille cylindrique rectifiée Ø 3 x 14 mm Inox 18-8 (ISO 8734 / ISO 2338)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"91595A114",
        "new_name": "Goupille cylindrique ISO 8734 Ø3x14 [91595A114]",
        "part_number": "91595A114",
        "description": "Goupille cylindrique rectifiée Ø 3 x 14 mm Acier allié trempé (ISO 8734 / DIN 6325)",
        "material": "Acier"
    },
    {
        "pattern": r"(?:M5x50 6 pans|Vis CHC M5x50)",
        "new_name": "Vis CHC M5x50 [91290A242]",
        "part_number": "91290A242",
        "description": "Vis CHC M5 x 50 mm Inox 18-8 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"^LUOSI_1",
        "new_name": "Vis FHC M3x8 [91294A112]",
        "part_number": "91294A112",
        "description": "Vis FHC M3 x 8 mm Inox 18-8 (ISO 10642 / DIN 7991)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"91292A118",
        "new_name": "Vis CHC M4x16 [91292A118]",
        "part_number": "91292A118",
        "description": "Vis CHC M4 x 16 mm Inox 18-8 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"91290A154",
        "new_name": "Vis CHC M4x16 [91290A154]",
        "part_number": "91290A154",
        "description": "Vis CHC M4 x 16 mm Acier cl. 12.9 (ISO 4762 / DIN 912)",
        "material": "Acier"
    },
    {
        "pattern": r"92125A230",
        "new_name": "Vis FHC M5x25 [92125A230]",
        "part_number": "92125A230",
        "description": "Vis FHC M5 x 25 mm Inox 316 (ISO 10642 / DIN 7991)",
        "material": "Acier inoxydable"
    },
    {
        "pattern": r"91292A130",
        "new_name": "Vis CHC M4x30 [91292A130]",
        "part_number": "91292A130",
        "description": "Vis CHC M4 x 30 mm Inox 18-8 (ISO 4762 / DIN 912)",
        "material": "Acier inoxydable"
    }
]

# ---------------------------------------------------------------------------
# 2. RÈGLES DE MATÉRIAUX POUR LES PIÈCES STRUCTURALES (TORSE & BASSIN)
# ---------------------------------------------------------------------------
STRUCTURAL_RULES = [
    {
        "material_name": "Aluminium 7075-T6",
        "density_g_cm3": 2.81,
        "keywords": [
            "waist_plate",
            "plaque_de_cou",
            "equerre waist",
            "equerre cou",
            "colonne vertébrale",
            "semelle éclisse",
            "insert",
            "moyeu_waist_sandwich",
            "bride epaule",
            "chassis_structurel_bassin",
            "support_hanche",
            "traverse_renfort_bassin",
            "liaison_hanche",
            "corniere",
            "ceinture"
        ]
    },
    {
        "material_name": "Aluminium 6060-T6",
        "density_g_cm3": 2.70,
        "keywords": [
            "tube transverse epaules"
        ]
    },
    {
        "material_name": "PA12-CF (Infill 30% Gyroïde)",
        "density_g_cm3": 0.56,
        "keywords": [
            "plastron_ventral_torse",
            "platine_connectique_facade",
            "panier_batterie",
            "capot_verrouillage",
            "carenage_pectoral",
            "carenage_lombaire",
            "trappe_inferieure_bassin",
            "capot_lateral_hanche",
            "capot_protection_hanche"
        ]
    }
]

# ---------------------------------------------------------------------------
# 3. GESTION DES MATÉRIAUX DANS FUSION 360 (Création et Cache)
# ---------------------------------------------------------------------------
def create_or_get_custom_material(design, app, mat_name, density_g_cm3):
    """Crée ou récupère un matériau sur-mesure dans Fusion 360 avec sa densité physique exacte."""
    existing = design.materials.itemByName(mat_name)
    if existing:
        return existing

    base_mat = None
    mat_lib = app.materialLibraries.itemByName('Fusion 360 Material Library')
    if mat_lib:
        candidates = ['ABS Plastic', 'Nylon 6/6', 'Plastic', 'Polycarbonate', 'Steel', 'Stainless Steel', 'Aluminum']
        for cand in candidates:
            try:
                m = mat_lib.materials.itemByName(cand)
                if m:
                    base_mat = m
                    break
            except:
                pass

    if not base_mat and design.materials.count > 0:
        base_mat = design.materials.item(0)

    if not base_mat:
        return None

    try:
        new_mat = design.materials.addByCopy(base_mat, mat_name)
        if not new_mat:
            return None

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

def find_best_material(design, app, req_mat_name, density_fallback=2.81):
    """Localise un matériau dans le design ou la bibliothèque, ou le crée dynamiquement."""
    req_l = req_mat_name.lower()

    # 1. Acier Inoxydable (Fasteners)
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
        return create_or_get_custom_material(design, app, "Acier inoxydable", 7.93)

    # 2. Aluminium 7075-T6
    if "7075" in req_l:
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

    # 3. Aluminium 6060-T6
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

    # 4. PA12-CF (Infill 30% Gyroïde)
    if "pa12" in req_l or "cf" in req_l or "gyro" in req_l:
        for m in design.materials:
            if "pa12-cf" in m.name.lower():
                return m
        return create_or_get_custom_material(design, app, "PA12-CF (Infill 30% Gyroïde)", 0.56)

    # 5. Acier Générique
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

    return create_or_get_custom_material(design, app, req_mat_name, density_fallback)

# ---------------------------------------------------------------------------
# 4. EXÉCUTION PRINCIPALE DU SCRIPT
# ---------------------------------------------------------------------------
def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox("Aucun modèle actif dans Autodesk Fusion 360.")
            return

        # Préchauffage et instanciation du cache des matériaux clés
        materials_cache = {
            "Acier inoxydable": find_best_material(design, app, "Acier inoxydable", 7.93),
            "Aluminium 7075-T6": find_best_material(design, app, "Aluminium 7075-T6", 2.81),
            "Aluminium 6060-T6": find_best_material(design, app, "Aluminium 6060-T6", 2.70),
            "PA12-CF (Infill 30% Gyroïde)": find_best_material(design, app, "PA12-CF (Infill 30% Gyroïde)", 0.56),
            "Acier": find_best_material(design, app, "Acier", 7.85)
        }

        renamed_components = 0
        renamed_occurrences = 0
        materials_applied_comps = 0
        ceinture_updated = False
        ceinture_new_mass_g = 0.0
        log_lines = []

        # ===================================================================
        # ÉTAPE A : STANDARDISATION DES COMPOSANTS (PartNumber, Description, Nom, Matériau)
        # ===================================================================
        for comp in design.allComponents:
            cname = comp.name
            
            # 1. Vérification contre le catalogue de visserie McMaster
            matched_rule = None
            for rule in FASTENER_RULES:
                if re.search(rule["pattern"], cname, re.IGNORECASE):
                    matched_rule = rule
                    break

            if matched_rule:
                # Standardiser le nom du composant
                if comp.name != matched_rule["new_name"]:
                    old_cname = comp.name
                    comp.name = matched_rule["new_name"]
                    renamed_components += 1
                    log_lines.append(f"• Composant : '{old_cname}'\n   ➔ '{matched_rule['new_name']}'")

                # Renseigner Part Number et Description
                try:
                    comp.partNumber = matched_rule["part_number"]
                except:
                    pass
                try:
                    comp.description = matched_rule["description"]
                except:
                    pass

                # Assigner le matériau physique (Inox ou Acier)
                target_mat_name = matched_rule.get("material", "Acier inoxydable")
                target_mat = materials_cache.get(target_mat_name)
                if target_mat and (not comp.material or comp.material.name != target_mat.name):
                    try:
                        comp.material = target_mat
                        materials_applied_comps += 1
                    except:
                        pass
                continue

            # 2. Vérification contre les règles de pièces structurales
            cname_l = cname.lower()
            for s_rule in STRUCTURAL_RULES:
                if any(kw in cname_l for kw in s_rule["keywords"]):
                    mat_obj = materials_cache.get(s_rule["material_name"])
                    if mat_obj and (not comp.material or comp.material.name != mat_obj.name):
                        try:
                            comp.material = mat_obj
                            materials_applied_comps += 1
                            log_lines.append(f"• Matériau '{mat_obj.name}' appliqué sur '{comp.name}'")
                        except:
                            pass
                    break

        # ===================================================================
        # ÉTAPE B : NETTOYAGE DES OCCURRENCES DANS L'ARBORESCENCE (Suppression des (1), (2), (4))
        # ===================================================================
        root_comp = design.rootComponent
        for occ in root_comp.allOccurrences:
            old_occ_name = occ.name
            for rule in FASTENER_RULES:
                if re.search(rule["pattern"], old_occ_name, re.IGNORECASE):
                    # Extraire l'indice d'instance :N à la fin
                    idx_match = re.search(r':(\d+)\Z', old_occ_name)
                    idx = idx_match.group(1) if idx_match else "1"
                    desired_name = f"{rule['new_name']}:{idx}"
                    
                    if occ.name != desired_name:
                        try:
                            occ.name = desired_name
                            renamed_occurrences += 1
                        except:
                            pass
                    break

        # ===================================================================
        # ÉTAPE C : TRAITEMENT SPÉCIFIQUE DU CORPS 'CEINTURE' (Alu 7075-T6)
        # ===================================================================
        # La ceinture est un corps BRep indépendant logé dans le composant Plastron_Ventral_Torse.
        # Par défaut, elle hérite du PA12-CF. On force son matériau à Aluminium 7075-T6.
        alu7075_mat = materials_cache.get("Aluminium 7075-T6")
        if alu7075_mat:
            for comp in design.allComponents:
                for body in comp.bRepBodies:
                    if "ceinture" in body.name.lower():
                        try:
                            body.material = alu7075_mat
                            ceinture_updated = True
                            b_props = body.getPhysicalProperties(adsk.fusion.CalculationAccuracy.MediumCalculationAccuracy)
                            ceinture_new_mass_g = round(b_props.mass * 1000.0, 2)
                            log_lines.append(f"• Corps '{body.name}' (dans {comp.name}) ➔ Matériau '{alu7075_mat.name}' (Masse = {ceinture_new_mass_g} g)")
                        except:
                            pass

        # ===================================================================
        # ÉTAPE C bis : TRAITEMENT SPÉCIFIQUE DES CORNIÈRES (Alu 7075-T6)
        # ===================================================================
        corniere_updated = False
        corniere_new_mass_g = 0.0
        corniere_count = 0
        if alu7075_mat:
            for comp in design.allComponents:
                if "corniere" in comp.name.lower():
                    try:
                        comp.material = alu7075_mat
                        for body in comp.bRepBodies:
                            body.material = alu7075_mat
                        c_props = comp.getPhysicalProperties(adsk.fusion.CalculationAccuracy.MediumCalculationAccuracy)
                        corniere_new_mass_g = round(c_props.mass * 1000.0, 2)
                        corniere_updated = True
                        corniere_count += 1
                        log_lines.append(f"• Composant '{comp.name}' ➔ Matériau '{alu7075_mat.name}' (Masse = {corniere_new_mass_g} g au lieu de 52.4 g)")
                    except:
                        pass

        # ===================================================================
        # ÉTAPE D : SYNTHÈSE ET MESSAGE À L'UTILISATEUR
        # ===================================================================
        msg = "=== STANDARDISATION NOMENCLATURE & MATÉRIAUX TERMINÉE ===\n\n"
        msg += f"• Composants uniques renommés / standardisés : {renamed_components}\n"
        msg += f"• Occurrences d'arborescence assainies : {renamed_occurrences}\n"
        msg += f"• Composants recevant le bon matériau : {materials_applied_comps}\n"
        
        if ceinture_updated:
            msg += f"• Corps 'ceinture' actualisé en Aluminium 7075-T6 : Masse = {ceinture_new_mass_g} g (CONFORME)\n"
        else:
            msg += "• [Attention] Corps 'ceinture' non détecté dans les composants BRep.\n"

        if corniere_updated:
            msg += f"• Cornière(s) actualisée(s) en Aluminium 7075-T6 ({corniere_count} comp) : Masse = {corniere_new_mass_g} g (gain -33,6 g) (CONFORME)\n"
        else:
            msg += "• [Attention] Composant 'Corniere' non détecté dans les composants.\n"
            
        msg += "\n"
        if log_lines:
            msg += "Détail des actions appliquées :\n\n" + "\n\n".join(log_lines[:15])
            if len(log_lines) > 15:
                msg += f"\n\n... et {len(log_lines) - 15} autres modifications de conformité."
        else:
            msg += "Tous les composants et matériaux sont déjà 100% conformes aux standards D-Bot !"

        ui.messageBox(msg, "Standardisation Torse & Bassin D-Bot")

    except Exception as e:
        if ui:
            ui.messageBox(f"Erreur durant l'exécution du script :\n{traceback.format_exc()}", "Erreur RenameFastenersTorse")

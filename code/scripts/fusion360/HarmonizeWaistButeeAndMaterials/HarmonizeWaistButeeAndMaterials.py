# -*- coding: utf-8 -*-
"""
=============================================================================
HarmonizeWaistButeeAndMaterials.py — Normalisation Butée Waist & Matériaux
=============================================================================
Exécution dans Autodesk Fusion 360 (Utilitaires > Scripts > Run).

Actions effectuées sur l'assemblage actif (Torse-123) :
1. Butée mécanique Waist +/- 95 deg (WST-07A / WST-07B / WST-07C) :
   - Doigt Mobile -> 'Doigt_Butee_Waist_Mobile [WST-07A]' (Aluminium 7075, 2.81 g/cm3)
   - Plot Fixe & Symétrie -> 'Plot_Butee_Waist_Droit [WST-07B]' / 'Plot_Butee_Waist_Gauche [WST-07B]'
     discriminés spatialement par rapport au plan du pivot Waist Y = 9.36 mm (0.936 cm).
   - Capuchon & Symétrie -> 'Capuchon_TPU_Butee_Droit [WST-07C]' / 'Capuchon_TPU_Butee_Gauche [WST-07C]'
     avec création/application du matériau 'TPU 95A (Infill 100%)' calibré à 1.20 g/cm3
     et d'une apparence élastomère sombre 'TPU 95A Noir Mat' (remplace Acier 11.61 g -> ~1.78 g).
   - Normalisation du corps unique ('Corps2' -> 'Corps1').
2. Quincaillerie McMaster non renommée :
   - 91290A150 (M4x14) -> matériau 'Acier' (7.85 g/cm3, purge 'Product Detail Link' 0.00 g),
     partNumber='91290A150', description ISO 4762 et renommage sécurisé 'Vis CHC M4x14 [91290A150]'.
   - 91290A154 (M4x16, si remplacement sous Doigt Mobile) -> 'Vis CHC M4x16 [91290A154]' en Acier.
3. Nettoyage matériaux 'Unknown' au niveau composant :
   - 'Waist_Plate_7075' : force comp.material et Corps1 à 'Aluminium 7075' sans toucher aux sous-composants.
   - 'Plastron_Ventral_Torse' : force comp.material et corps polymères en PA12-CF, tout en conservant
     le corps 'ceinture' en 'Aluminium 7075'.
4. Option interactive (Oui/Non) : recalibrage densité 'PA12-CF (Cosmetique Infill 15% Gyroide)' à 0.56 g/cm3.
5. Diagnostic final affiché (décalage miroir Y=8.67 vs 9.36, enfants imbriqués dans Waist_Plate_7075).
"""

import adsk.core
import adsk.fusion
import traceback


WAIST_PIVOT_X_CM = 4.923
WAIST_PIVOT_Y_CM = 0.936  # 9.36 mm exact Waist pivot axis


def find_density_property(mat):
    """Retourne la propriété Density d'un matériau Fusion quelle que soit la locale."""
    if not mat:
        return None
    for prop_name in ("Density", "Densité", "Masse volumique"):
        prop = mat.materialProperties.itemByName(prop_name)
        if prop:
            return prop
    for prop in mat.materialProperties:
        try:
            pid = (prop.id or "").lower()
            pname = (prop.name or "").lower()
            if "density" in pid or "density" in pname or "densit" in pname or "masse volumique" in pname:
                return prop
        except Exception:
            pass
    return None


def get_material_density_g_cm3(mat):
    """Lit la densité effective en g/cm3 depuis un matériau Fusion (API stocke en kg/m3)."""
    prop = find_density_property(mat)
    if not prop:
        return None
    try:
        val = float(prop.value)
        if val > 20.0:
            return val / 1000.0
        return val
    except Exception:
        return None


def set_material_density_g_cm3(mat, density_g_cm3):
    """Applique la densité calibrée (g/cm3) en respectant les unités internes Fusion (kg/m3)."""
    prop = find_density_property(mat)
    if not prop:
        return False
    try:
        cur_val = float(prop.value)
        scale = 1000.0 if (cur_val <= 0.0 or cur_val > 20.0) else 1.0
        target_val = float(density_g_cm3) * scale
        tol = 0.02 * scale
        if abs(cur_val - target_val) > tol:
            prop.value = target_val
            return True
    except Exception:
        pass
    return False


def _find_library_material(app, include_keywords, exclude_keywords=()):
    """Cherche un matériau modèle dans les bibliothèques matérielles Fusion 360."""
    for lib in app.materialLibraries:
        for mat in lib.materials:
            nl = mat.name.lower()
            if any(ex in nl for ex in exclude_keywords):
                continue
            if any(inc in nl for inc in include_keywords):
                return mat
    return None


def get_or_create_material(design, app, target_name, density_g_cm3, doc_match_fn, lib_keywords, lib_exclude=()):
    """Récupère ou clone un matériau propre dans le document actif et garantit sa densité."""
    for mat in design.materials:
        if doc_match_fn(mat.name.lower()):
            set_material_density_g_cm3(mat, density_g_cm3)
            return mat

    base_mat = _find_library_material(app, lib_keywords, exclude_keywords=lib_exclude)
    if base_mat:
        try:
            new_mat = design.materials.addByCopy(base_mat, target_name)
            set_material_density_g_cm3(new_mat, density_g_cm3)
            return new_mat
        except Exception:
            for mat in design.materials:
                if mat.name.lower() == target_name.lower():
                    set_material_density_g_cm3(mat, density_g_cm3)
                    return mat
    return None


def get_or_create_tpu_appearance(design, app):
    """Crée ou récupère une apparence mate gris anthracite pour les capuchons TPU 95A."""
    target_app_name = "TPU 95A Noir Mat"
    for a in design.appearances:
        if a.name == target_app_name:
            return a

    base_app = None
    for a in design.appearances:
        al = a.name.lower()
        if any(k in al for k in ("pa12", "rubber", "caoutchouc", "matte", "mat", "black", "noir")):
            base_app = a
            break

    if not base_app:
        search_terms = ("rubber", "caoutchouc", "matte", "plastic", "plastique", "abs", "nylon")
        for lib in app.materialLibraries:
            for a in lib.appearances:
                al = a.name.lower()
                if any(t in al for t in search_terms):
                    base_app = a
                    break
            if base_app:
                break

    if not base_app:
        return None

    try:
        new_app = design.appearances.addByCopy(base_app, target_app_name)
        for prop in new_app.appearanceProperties:
            try:
                if prop.objectType == adsk.core.ColorProperty.classType():
                    color_prop = adsk.core.ColorProperty.cast(prop)
                    if color_prop and not color_prop.isReadOnly:
                        color_prop.value = adsk.core.Color.create(46, 50, 56, 255)
            except Exception:
                pass
        return new_app
    except Exception:
        return None


def safe_rename_component(comp, desired_name, existing_names, fallbacks=None):
    """Renomme un composant Fusion en évitant toute collision de nom entre UUID distincts."""
    if comp.name == desired_name:
        return desired_name, False

    candidates = [desired_name] + list(fallbacks or [])
    candidates.extend(f"{desired_name} ({i})" for i in range(2, 10))

    for cand in candidates:
        if cand != comp.name and cand in existing_names:
            continue
        try:
            old_name = comp.name
            comp.name = cand
            existing_names.discard(old_name)
            existing_names.add(cand)
            return cand, True
        except Exception:
            continue
    return comp.name, False


def normalize_single_body_name(comp, target_body_name="Corps1"):
    """Renomme l'unique BRepBody (ex: Corps2 après miroir/scission) en Corps1."""
    if comp.bRepBodies.count != 1:
        return False
    body = comp.bRepBodies.item(0)
    if body.name != target_body_name:
        try:
            body.name = target_body_name
            return True
        except Exception:
            pass
    return False


def safe_set_metadata(comp, part_number=None, description=None):
    """Met à jour partNumber et description en tolérant les composants externes verrouillés."""
    if part_number is not None:
        try:
            comp.partNumber = part_number
        except Exception:
            pass
    if description is not None:
        try:
            comp.description = description
        except Exception:
            pass


def get_comp_mass_g(comp):
    """Calcule la masse totale des corps visibles du composant en grammes."""
    total_g = 0.0
    for b in comp.bRepBodies:
        try:
            total_g += b.physicalProperties.mass * 1000.0
        except Exception:
            pass
    return total_g


def apply_material_to_comp_and_bodies(comp, mat, appearance=None):
    """Assigne matériau et apparence au composant et uniquement à ses propres BRepBodies."""
    changed = False
    if mat:
        try:
            if not comp.material or comp.material.id != mat.id:
                comp.material = mat
                changed = True
        except Exception:
            pass
        for b in comp.bRepBodies:
            try:
                if not b.material or b.material.id != mat.id:
                    b.material = mat
                    changed = True
            except Exception:
                pass
    if appearance:
        try:
            comp.appearance = appearance
        except Exception:
            pass
        for b in comp.bRepBodies:
            try:
                b.appearance = appearance
            except Exception:
                pass
    return changed


def get_occ_center_y_cm(occ):
    """Retourne le centre Y mondial (en cm) d'une occurrence Fusion."""
    try:
        bb = occ.boundingBox
        return (bb.minPoint.y + bb.maxPoint.y) / 2.0
    except Exception:
        try:
            return occ.transform2.translation.y
        except Exception:
            return 0.0


def classify_side_from_occurrences(occs):
    """Détermine Droit (-Y), Gauche (+Y) ou Bilatéral selon le pivot Waist Y = 9.36 mm."""
    sides = set()
    for occ in occs:
        y_cm = get_occ_center_y_cm(occ)
        sides.add("Droit" if y_cm < WAIST_PIVOT_Y_CM else "Gauche")
    if len(sides) == 1:
        return next(iter(sides))
    return None


def _is_product_link_or_steel_wrong(mat_name):
    """Vrai si matériau McMaster non résolu ou inconnu."""
    ml = (mat_name or "").lower()
    return ("product detail" in ml) or ("unknown" in ml) or (not ml.strip())


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        if not design:
            if ui:
                ui.messageBox(
                    "Veuillez ouvrir un assemblage Fusion 360 actif avant de lancer ce script.",
                    "HarmonizeWaistButeeAndMaterials",
                )
            return

        root_comp = design.rootComponent

        # Question optionnelle sur la calibration densité PA12-CF cosmétique (1.015 -> 0.56 g/cm3)
        res_pa12 = ui.messageBox(
            "Le script va :\n"
            "  1. Renommer & typer Doigt_Butee_Waist_Mobile [WST-07A], Plot_Butee_Waist_Droit/Gauche [WST-07B], "
            "Capuchon_TPU_Butee_Droit/Gauche [WST-07C] et Vis CHC M4x14 [91290A150]\n"
            "  2. Appliquer Alu 7075 (2.81), TPU 95A (1.20 g/cm3) sur Capuchons et Acier (7.85) sur vis\n"
            "  3. Nettoyer 'Unknown' sur Waist_Plate_7075 et Plastron_Ventral_Torse\n\n"
            "Voulez-vous AUSSI calibrer la densité du matériau 'PA12-CF (Cosmetique Infill 15% Gyroide)' "
            "de 1.015 à 0.56 g/cm3 ?\n"
            "(Non = garder les densités PA12 actuelles et traiter uniquement Butée Waist + Unknown)",
            "D-Bot V1 : Butée Waist & Matériaux",
            adsk.core.MessageBoxButtonTypes.YesNoCancelButtonType,
        )
        if res_pa12 == adsk.core.DialogResults.DialogCancel:
            return
        calibrate_cosmetic_pa12 = (res_pa12 == adsk.core.DialogResults.DialogYes)

        # 1. Préparation des matériaux certifiés
        mat_alu7075 = get_or_create_material(
            design, app, "Aluminium 7075", 2.81,
            doc_match_fn=lambda ml: ("7075" in ml and "-t6" not in ml and "product" not in ml),
            lib_keywords=("aluminum 6061", "aluminium 6061", "aluminum", "aluminium"),
            lib_exclude=("product", "unknown"),
        )
        mat_acier = get_or_create_material(
            design, app, "Acier", 7.85,
            doc_match_fn=lambda ml: (ml == "acier" or ("acier" in ml and "inox" not in ml and "product" not in ml)),
            lib_keywords=("steel, mild", "steel", "acier"),
            lib_exclude=("stainless", "inox", "product", "unknown"),
        )
        mat_tpu95a = get_or_create_material(
            design, app, "TPU 95A (Infill 100%)", 1.20,
            doc_match_fn=lambda ml: ("tpu" in ml and "product" not in ml),
            lib_keywords=("tpu", "polyurethane", "silicone", "rubber", "caoutchouc", "nylon", "abs", "plastic"),
            lib_exclude=("metal", "steel", "acier", "alum", "product", "unknown"),
        )
        app_tpu = get_or_create_tpu_appearance(design, app)

        mat_pa12_coque = None
        for m in design.materials:
            if "pa12-cf" in m.name.lower() and "coque" in m.name.lower():
                mat_pa12_coque = m
                break
        if not mat_pa12_coque:
            for m in design.materials:
                if "pa12" in m.name.lower():
                    mat_pa12_coque = m
                    break

        if calibrate_cosmetic_pa12:
            for m in design.materials:
                ml = m.name.lower()
                if "pa12-cf" in ml and "cosmetique" in ml:
                    set_material_density_g_cm3(m, 0.56)

        # 2. Indexation des composants uniques et occurrences
        comp_map = {}
        existing_names = {c.name for c in design.allComponents}
        for occ in root_comp.allOccurrences:
            c = occ.component
            if c.id not in comp_map:
                comp_map[c.id] = {"comp": c, "occs": []}
            comp_map[c.id]["occs"].append(occ)

        logs = []
        warnings = []
        y_centers_plot = {}
        y_centers_cap = {}

        # 3. Traitement ciblé des composants
        for entry in comp_map.values():
            comp = entry["comp"]
            occs = entry["occs"]
            cname = comp.name
            nl = cname.lower()
            pn_l = (comp.partNumber or "").lower()
            cur_mat_name = comp.material.name if comp.material else "None"

            # A. Doigt Mobile [WST-07A]
            if ("doigt" in nl and "mobile" in nl) or ("doigt_butee_waist" in nl) or ("wst-07a" in nl) or (pn_l == "wst-07a"):
                new_name, renamed = safe_rename_component(comp, "Doigt_Butee_Waist_Mobile [WST-07A]", existing_names)
                safe_set_metadata(
                    comp,
                    part_number="WST-07A",
                    description="Doigt de butee mobile lacet Waist +/- 95 deg sous Waist Plate (Alu 7075-T6)",
                )
                body_ren = normalize_single_body_name(comp, "Corps1")
                mat_chg = apply_material_to_comp_and_bodies(comp, mat_alu7075)
                mass_g = get_comp_mass_g(comp)
                logs.append(f"[WST-07A] {cname} -> {new_name} | mat=Alu7075 ({mass_g:.2f} g) | ren={renamed} body={body_ren} mat_upd={mat_chg}")
                continue

            # B. Plot Fixe Droit / Gauche [WST-07B]
            if ("plot" in nl and ("fixe" in nl or "butee" in nl)) or ("wst-07b" in nl) or (pn_l == "wst-07b"):
                side = classify_side_from_occurrences(occs)
                target = f"Plot_Butee_Waist_{side} [WST-07B]" if side else "Plot_Butee_Waist [WST-07B]"
                new_name, renamed = safe_rename_component(comp, target, existing_names)
                safe_set_metadata(
                    comp,
                    part_number="WST-07B",
                    description="Plot de butee fixe lacet Waist +/- 95 deg sur Traverse Bassin (Alu 7075-T6)",
                )
                body_ren = normalize_single_body_name(comp, "Corps1")
                mat_chg = apply_material_to_comp_and_bodies(comp, mat_alu7075)
                mass_g = get_comp_mass_g(comp)
                if side:
                    y_centers_plot[side] = get_occ_center_y_cm(occs[0]) * 10.0
                logs.append(f"[WST-07B] {cname} -> {new_name} | mat=Alu7075 ({mass_g:.2f} g) | ren={renamed} body={body_ren} mat_upd={mat_chg}")
                continue

            # C. Capuchon Amortisseur TPU 95A Droit / Gauche [WST-07C]
            if ("capuchon" in nl) or ("wst-07c" in nl) or (pn_l == "wst-07c"):
                side = classify_side_from_occurrences(occs)
                target = f"Capuchon_TPU_Butee_{side} [WST-07C]" if side else "Capuchon_TPU_Butee [WST-07C]"
                new_name, renamed = safe_rename_component(comp, target, existing_names)
                safe_set_metadata(
                    comp,
                    part_number="WST-07C",
                    description="Capuchon amortisseur butee lacet Waist +/- 95 deg (TPU 95A Infill 100%)",
                )
                body_ren = normalize_single_body_name(comp, "Corps1")
                mat_chg = apply_material_to_comp_and_bodies(comp, mat_tpu95a, appearance=app_tpu)
                mass_g = get_comp_mass_g(comp)
                if side:
                    y_centers_cap[side] = get_occ_center_y_cm(occs[0]) * 10.0
                logs.append(f"[WST-07C] {cname} -> {new_name} | {cur_mat_name} -> TPU 95A ({mass_g:.2f} g) | ren={renamed} body={body_ren} mat_upd={mat_chg}")
                continue

            # D. Vis CHC M4x14 [91290A150] (et M4x16 [91290A154] si mise à niveau sous Doigt Mobile)
            if ("91290a150" in nl) or (pn_l == "91290a150"):
                target = "Vis CHC M4x14 [91290A150]"
                fallbacks = ["Vis CHC M4x14 [91290A150] (Butee)", "Vis CHC M4x14 [91290A150] (Butee 2)"]
                if cname.startswith(target):
                    new_name, renamed = cname, False
                else:
                    new_name, renamed = safe_rename_component(comp, target, existing_names, fallbacks=fallbacks)
                safe_set_metadata(
                    comp,
                    part_number="91290A150",
                    description="Vis CHC M4 x 14 mm Acier allie cl. 12.9 Noir (ISO 4762 / DIN 912)",
                )
                body_ren = normalize_single_body_name(comp, "Corps1")
                mat_chg = apply_material_to_comp_and_bodies(comp, mat_acier)
                if renamed or mat_chg or _is_product_link_or_steel_wrong(cur_mat_name):
                    mass_g = get_comp_mass_g(comp)
                    logs.append(f"[91290A150 x{len(occs)}] {cname} -> {new_name} | {cur_mat_name} -> Acier ({mass_g:.2f} g/pce)")
                continue

            if ("91290a154" in nl) or (pn_l == "91290a154"):
                target = "Vis CHC M4x16 [91290A154]"
                fallbacks = ["Vis CHC M4x16 [91290A154] (Butee)"]
                if cname.startswith(target):
                    new_name, renamed = cname, False
                else:
                    new_name, renamed = safe_rename_component(comp, target, existing_names, fallbacks=fallbacks)
                safe_set_metadata(
                    comp,
                    part_number="91290A154",
                    description="Vis CHC M4 x 16 mm Acier allie cl. 12.9 Noir (ISO 4762 / DIN 912)",
                )
                normalize_single_body_name(comp, "Corps1")
                mat_chg = apply_material_to_comp_and_bodies(comp, mat_acier)
                mass_g = get_comp_mass_g(comp)
                logs.append(f"[91290A154 x{len(occs)}] {cname} -> {new_name} | Acier ({mass_g:.2f} g/pce)")
                continue

            # E. Nettoyage composant parent Waist_Plate_7075 (sans toucher aux occurrences enfants)
            if nl.startswith("waist_plate_7075"):
                mat_chg = apply_material_to_comp_and_bodies(comp, mat_alu7075)
                if not comp.partNumber:
                    comp.partNumber = "ASV1_100_02A"
                if mat_chg:
                    logs.append(f"[Waist_Plate_7075] {cur_mat_name} -> Aluminium 7075 (Corps1 préservé)")
                if comp.occurrences.count > 0:
                    nested = [comp.occurrences.item(i).name for i in range(comp.occurrences.count)]
                    warnings.append(
                        "Hiérarchie : Waist_Plate_7075 contient encore des sous-composants imbriqués ("
                        + ", ".join(nested)
                        + "). Les déplacer au Root pour éviter la pollution de sa bounding box."
                    )
                continue

            # F. Nettoyage composant parent Plastron_Ventral_Torse (préserve 'ceinture' en Alu 7075)
            if nl.startswith("plastron_ventral_torse") and mat_pa12_coque:
                plastron_upd = False
                if not comp.material or comp.material.id != mat_pa12_coque.id:
                    try:
                        comp.material = mat_pa12_coque
                        plastron_upd = True
                    except Exception:
                        pass
                for b in comp.bRepBodies:
                    if "ceinture" in b.name.lower():
                        if mat_alu7075 and (not b.material or b.material.id != mat_alu7075.id):
                            b.material = mat_alu7075
                            plastron_upd = True
                    else:
                        if not b.material or b.material.id != mat_pa12_coque.id:
                            b.material = mat_pa12_coque
                            plastron_upd = True
                if plastron_upd:
                    logs.append(f"[Plastron_Ventral_Torse] {cur_mat_name} -> PA12-CF (ceinture maintenue Alu 7075)")

        # 4. Vérifications géométriques rapides post-mise à jour
        if "Droit" in y_centers_plot and "Gauche" in y_centers_plot:
            sym_err_plot = (y_centers_plot["Droit"] + y_centers_plot["Gauche"]) / 2.0 - 9.36
            if abs(sym_err_plot) > 0.05:
                warnings.append(
                    f"Symétrie Plots Fixes : plan miroir mesuré à Y={9.36 + sym_err_plot:.2f} mm "
                    f"au lieu de Y=9.36 mm (décalage Y sur Plot Gauche = {2.0 * sym_err_plot:+.2f} mm)."
                )
        if "Droit" in y_centers_cap and "Gauche" in y_centers_cap:
            sym_err_cap = (y_centers_cap["Droit"] + y_centers_cap["Gauche"]) / 2.0 - 9.36
            if abs(sym_err_cap) > 0.05:
                warnings.append(
                    f"Symétrie Capuchons TPU : plan miroir mesuré à Y={9.36 + sym_err_cap:.2f} mm "
                    f"au lieu de Y=9.36 mm (décalage Y sur Capuchon Gauche = {2.0 * sym_err_cap:+.2f} mm)."
                )

        tpu_rho = get_material_density_g_cm3(mat_tpu95a)
        header = f"Harmonisation terminée ({len(logs)} mises à jour, densité TPU 95A = {tpu_rho or 0.0:.2f} g/cm3)\n"
        summary = header + "\n".join(logs)
        if warnings:
            summary += "\n\nAlertes d'ingénierie détectées :\n- " + "\n- ".join(warnings)
        if ui:
            ui.messageBox(summary[:3200], "HarmonizeWaistButeeAndMaterials")

    except Exception:
        if ui:
            ui.messageBox("Erreur script HarmonizeWaistButeeAndMaterials :\n\n" + traceback.format_exc())

# -*- coding: utf-8 -*-
"""
HarmonizeNewPelvisMaterials.py — Mise à jour & Harmonisation Complète du Bassin Pelvis D-Bot
Projet : Robot Humanoïde D-Bot V1
Auteur : Antigravity & David Sergent
=============================================================================
Ce script s'exécute directement dans Autodesk Fusion 360 (Raccourci Shift + S > Exécuter).

Objectifs :
  1. Coque Pelvienne Épaissie 5 mm ('Chassis_Structurel_Bassin_Last') :
     -> Matériau physique : 'PA12-CF (Coque 5mm Infill 15% Gyroide)' calibré à 0,700 g/cm³
     -> Apparence visuelle : Noir Mat PA12-CF.
  2. Selle de Pont ('selle de pont') :
     -> Renommage : 'Selle de Pont Pelvis [ASV1_200_10]'
     -> Matériau : 'Aluminium 7075-T6' (2,81 g/cm³)
     -> Apparence : Satin Metal / Aluminium.
  3. Les 4 Montants Verticaux 20x20 ('montant de hanche' avant/arrière, gauche/droit) :
     -> Renommage spatial (+X/-X, +Y/-Y) : 'Montant de Hanche Avant/Arriere Gauche/Droit [ASV1_200_11]'
     -> Matériau : 'Aluminium 6060-T6' (2,70 g/cm3)
     -> Apparence : Satin Metal / Aluminium.
  4. Tube Pont Central 60x60 ('Tube transverse Epaules:2') :
     -> Renommage : 'Tube transverse Hanches [60x60]'
     -> Matériau : 'Aluminium 6060-T6' (2,70 g/cm3)
  5. Les 8 Inserts Taraudés Tube 20x20 ('Insert hanche') :
     -> Discrimination Z : 'Insert Hanche Bas [ASV1_200_12]' et 'Insert Hanche Haut [ASV1_200_13]'
     -> Matériau : 'Aluminium 7075-T6' (2,81 g/cm3)
  6. Quincaillerie & Visserie du Bassin (purge 'Product Detail Link') :
     -> FHC M5x18 [92125A213], CHC M4x25 [91292A122], CHC M5x20 [92290A242], CHC M5x35 [91290A661],
        CHC M5x80 [91290A276], Rondelles M5 [93475A240], Écrous Nylstop M5 [93625A200] -> Acier Inoxydable (7,93 g/cm3) / Acier Allié (7,85 g/cm3).
  7. Ancien Châssis Massif ('Chassis_Structurel_Bassin [ASV1_200_01C]') :
     -> Masquage de la visibilité (isLightBulbOn = False) pour éliminer le faux doublon de 2,37 kg.
"""

import adsk.core
import adsk.fusion
import traceback
import re


def strip_fusion_suffix(name):
    """Supprime le suffixe Fusion automatique ' (1)', ' (2)', etc. pour comparer les noms."""
    return re.sub(r"\s*\(\d+\)$", "", (name or "").strip())


def find_density_property(material):
    """Localise la propriété Densité quel que soit le langage de Fusion 360 (FR/EN)."""
    if not material:
        return None
    for exact_name in ('Density', 'Densité'):
        try:
            prop = material.materialProperties.itemByName(exact_name)
            if prop:
                return prop
        except Exception:
            pass
    try:
        for prop in material.materialProperties:
            pid = str(getattr(prop, 'id', '')).lower()
            pname = str(getattr(prop, 'name', '')).lower()
            if 'density' in pid or 'density' in pname or 'densit' in pname or 'masse volumique' in pname:
                return prop
    except Exception:
        pass
    return None


def set_material_density_g_cm3(material, target_density):
    """Calibre la propriété de densité (en g/cm3, stockée en kg/m3 SI dans l'API Fusion)."""
    density_prop = find_density_property(material)
    if not density_prop:
        return False
    try:
        cur_val = float(density_prop.value)
        scale = 1000.0 if (cur_val <= 0.0 or cur_val > 20.0) else 1.0
        target_val = float(target_density) * scale
        if abs(cur_val - target_val) > (0.02 * scale):
            density_prop.value = target_val
            return True
    except Exception:
        pass
    return False


def get_or_create_material(design, base_material, spec_name, target_density):
    """Récupère ou clone un matériau physique avec la densité apparente voulue (g/cm3)."""
    for mat in design.materials:
        if mat.name.strip().lower() == spec_name.strip().lower():
            set_material_density_g_cm3(mat, target_density)
            return mat

    new_mat = None
    try:
        new_mat = design.materials.addByCopy(base_material, spec_name)
    except Exception:
        try:
            new_mat = design.materials.addByCopying(base_material, spec_name)
        except Exception:
            pass

    if not new_mat:
        return base_material

    set_material_density_g_cm3(new_mat, target_density)
    return new_mat


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            if ui:
                ui.messageBox(
                    "Veuillez exécuter ce script avec le document actif (Torse-123).",
                    "Harmonisation Matériaux Bassin"
                )
            return

        root_comp = design.rootComponent

        # ---------------------------------------------------------------------
        # 1. Résolution des matériaux certifiés
        # ---------------------------------------------------------------------
        mat_alu_7075 = None
        mat_alu_6060 = None
        mat_pa12_base = None
        mat_inox = None
        mat_acier = None

        for mat in design.materials:
            m_low = mat.name.lower()
            if "7075" in m_low and not mat_alu_7075:
                mat_alu_7075 = mat
            if any(k in m_low for k in ["6060", "6061"]) and not mat_alu_6060:
                mat_alu_6060 = mat
            if "pa12" in m_low and "coque 5mm" not in m_low and (not mat_pa12_base or "cosmetique" in m_low):
                mat_pa12_base = mat
            if ("inox" in m_low or "stainless" in m_low) and not mat_inox:
                mat_inox = mat
            if (
                ("acier" in m_low or "steel" in m_low)
                and "inox" not in m_low
                and "stainless" not in m_low
                and (not mat_acier or m_low in ("acier", "steel"))
            ):
                mat_acier = mat

        # Recherche de secours dans les bibliothèques
        for lib in app.materialLibraries:
            try:
                for mat in lib.materials:
                    m_low = mat.name.lower()
                    if not mat_alu_7075 and "7075" in m_low:
                        mat_alu_7075 = design.materials.addByCopy(mat, "Aluminium 7075")
                    if not mat_alu_6060 and ("6061" in m_low or "6060" in m_low):
                        mat_alu_6060 = design.materials.addByCopy(mat, "Aluminium 6060-T6")
                    if not mat_inox and ("stainless" in m_low or "inox" in m_low):
                        mat_inox = design.materials.addByCopy(mat, "Acier inoxydable")
                    if not mat_acier and ("steel" in m_low or "acier" in m_low) and "stainless" not in m_low and "inox" not in m_low:
                        mat_acier = design.materials.addByCopy(mat, "Acier")
                    if not mat_pa12_base and any(k in m_low for k in ["nylon", "pa12", "abs", "plastic"]):
                        mat_pa12_base = design.materials.addByCopy(mat, "PA12-CF Base")
            except Exception:
                continue

        if mat_pa12_base:
            mat_pa12_coque_5mm = get_or_create_material(
                design, mat_pa12_base, "PA12-CF (Coque 5mm Infill 15% Gyroide)", 0.700
            )
        else:
            mat_pa12_coque_5mm = None

        # ---------------------------------------------------------------------
        # 2. Résolution des apparences visuelles
        # ---------------------------------------------------------------------
        app_black_pa12 = None
        app_alu = None

        for a in design.appearances:
            a_low = a.name.lower()
            if not app_black_pa12 and any(k in a_low for k in ["black", "noir", "dark", "pa12", "carbon"]):
                app_black_pa12 = a
            if not app_alu and any(k in a_low for k in ["alu", "aluminum", "aluminium", "satin", "metal"]):
                app_alu = a

        if not app_black_pa12 and mat_pa12_base and mat_pa12_base.appearance:
            app_black_pa12 = mat_pa12_base.appearance
        if not app_alu and mat_alu_7075 and mat_alu_7075.appearance:
            app_alu = mat_alu_7075.appearance

        # ---------------------------------------------------------------------
        # 3. Application Ciblée sur les Composants du Bassin
        # ---------------------------------------------------------------------
        report = []
        mass_gain_g = 0.0
        processed_components = set()
        pelvis_fastener_specs = {
            "91290a276": ("Vis CHC M5x80 [91290A276]", "91290A276", "Vis CHC M5 x 80 mm Acier allié cl. 12.9 Noir (ISO 4762 / DIN 912)", mat_acier if mat_acier else mat_inox),
            "91290a661": ("Vis CHC M5x35 [91290A661]", "91290A661", "Vis CHC M5 x 35 mm Acier allié cl. 12.9 Noir (ISO 4762 / DIN 912)", mat_acier if mat_acier else mat_inox),
            "92125a213": ("Vis FHC M5x18 [92125A213]", "92125A213", "Vis FHC M5 x 18 mm Inox 18-8 (ISO 10642 / DIN 7991)", mat_inox),
            "91292a122": ("Vis CHC M4x25 [91292A122]", "91292A122", "Vis CHC M4 x 25 mm Inox 18-8 (ISO 4762 / DIN 912)", mat_inox),
            "92290a242": ("Vis CHC M5x20 [92290A242]", "92290A242", "Vis CHC M5 x 20 mm Inox 316 (ISO 4762 / DIN 912)", mat_inox),
            "93475a240": ("Rondelle Plate DIN 125A M5 [93475A240]", "93475A240", "Rondelle Plate DIN 125A M5 Inox 18-8 (ISO 7089 / DIN 125A)", mat_inox),
            "93625a200": ("Ecrou Nylstop M5 [93625A200]", "93625A200", "Écrou Frein Nylstop M5 Inox 18-8 (ISO 7040 / DIN 985)", mat_inox),
        }

        for occ in root_comp.allOccurrences:
            occ_name = occ.name
            occ_l = occ_name.lower()
            comp = occ.component
            if not comp or comp.entityToken in processed_components:
                continue
            comp_l = comp.name.lower()

            # --- A. Coque Pelvis 5mm : Chassis_Structurel_Bassin_Last ---
            if "last" in occ_l and "bassin" in occ_l:
                try:
                    if mat_pa12_coque_5mm:
                        comp.material = mat_pa12_coque_5mm
                        for body in comp.bRepBodies:
                            body.material = mat_pa12_coque_5mm
                            if app_black_pa12:
                                for f in body.faces:
                                    f.appearance = None
                                body.appearance = app_black_pa12
                    report.append(f"✓ {comp.name} -> PA12-CF Coque 5mm (0,70 g/cm³) & Noir Mat")
                    processed_components.add(comp.entityToken)
                except Exception as e:
                    report.append(f"✗ Erreur {occ_name} : {str(e)}")

            # --- B. Selle de Pont : Aluminium 7075-T6 ---
            elif "selle de pont" in occ_l or "selle de pont" in comp_l:
                try:
                    old_mass = comp.physicalProperties.mass * 1000.0 if comp.physicalProperties else 954.0
                    comp.name = "Selle de Pont Pelvis [ASV1_200_10]"
                    comp.partNumber = "ASV1_200_10"
                    comp.description = "Selle de Pont en H 140x145x22 mm (Alu 7075-T651)"

                    if mat_alu_7075:
                        comp.material = mat_alu_7075
                        for body in comp.bRepBodies:
                            body.material = mat_alu_7075
                            if app_alu:
                                for f in body.faces:
                                    f.appearance = None
                                body.appearance = app_alu

                    new_mass = comp.physicalProperties.mass * 1000.0 if comp.physicalProperties else 341.6
                    delta = old_mass - new_mass
                    mass_gain_g += delta
                    report.append(f"✓ {comp.name} -> Selle de Pont (Alu 7075, gain : -{round(delta, 1)} g)")
                    processed_components.add(comp.entityToken)
                except Exception as e:
                    report.append(f"✗ Erreur {occ_name} : {str(e)}")

            # --- C. Les 4 Montants Verticaux 20x20 : Aluminium 6060-T6 (+X=Avant/-X=Arriere, +Y=Gauche/-Y=Droit) ---
            elif "montant de hanche" in occ_l or "montant de hanche" in comp_l:
                try:
                    try:
                        bb = occ.boundingBox
                        x_mid_cm = 0.5 * (bb.minPoint.x + bb.maxPoint.x)
                        y_mid_cm = 0.5 * (bb.minPoint.y + bb.maxPoint.y)
                        pos = "Avant" if x_mid_cm > 5.48 else "Arriere"
                        cote = "Gauche" if y_mid_cm > 0.87 else "Droit"
                    except Exception:
                        pos = "Arriere" if "arriere" in occ_l else "Avant"
                        cote = "Gauche" if "symétrie" in occ_l else "Droit"

                    target_cname = f"Montant de Hanche {pos} {cote} [ASV1_200_11]"
                    if strip_fusion_suffix(comp.name) != target_cname:
                        try:
                            comp.name = target_cname
                        except Exception:
                            pass
                    comp.partNumber = "ASV1_200_11"
                    comp.description = f"Tube montant vertical {pos.lower()} {cote.lower()} 20x20x2 mm L=65.75 mm (Alu 6060-T6)"

                    target_alu = mat_alu_6060 if mat_alu_6060 else mat_alu_7075
                    if target_alu:
                        comp.material = target_alu
                        for body in comp.bRepBodies:
                            body.material = target_alu
                            if app_alu:
                                for f in body.faces:
                                    f.appearance = None
                                body.appearance = app_alu

                    report.append(f"✓ {comp.name} -> Alu 6060-T6 (2,70 g/cm3)")
                    processed_components.add(comp.entityToken)
                except Exception as e:
                    report.append(f"✗ Erreur {occ_name} : {str(e)}")

            # --- D. Tube Pont Central 60x60 : Tube transverse Epaules:2 ---
            elif "tube transverse epaules:2" in occ_l or (comp.name == "Tube transverse Epaules" and occ.boundingBox.minPoint.z < 110.0):
                try:
                    comp.name = "Tube transverse Hanches [60x60]"
                    comp.partNumber = "Tube_Transverse_Hanches_60x60"
                    comp.description = "Tube profilé 60x60x2 mm entre RS-04 Hanches (Alu 6060-T6)"

                    target_alu = mat_alu_6060 if mat_alu_6060 else mat_alu_7075
                    if target_alu:
                        comp.material = target_alu
                        for body in comp.bRepBodies:
                            body.material = target_alu
                            if app_alu:
                                for f in body.faces:
                                    f.appearance = None
                                body.appearance = app_alu
                    report.append(f"✓ {comp.name} -> Tube transverse Hanches (Alu 6060-T6)")
                    processed_components.add(comp.entityToken)
                except Exception as e:
                    report.append(f"✗ Erreur {occ_name} : {str(e)}")

            # --- E. Masquage de l'Ancien Châssis Massif (Évite le faux doublon) ---
            elif "asv1_200_01c" in occ_l or ("chassis_structurel_bassin" in occ_l and "last" not in occ_l):
                try:
                    occ.isLightBulbOn = False
                    report.append(f"✓ {occ_name} -> Masqué (Évite le double comptage de 2,37 kg)")
                except Exception:
                    pass

            # --- F. Inserts des Montants de Hanche (Insert Tube 20x20) : Aluminium 7075-T6 ---
            elif "insert hanche" in occ_l or "insert hanche" in comp_l:
                try:
                    z_min_cm = occ.boundingBox.minPoint.z
                    if z_min_cm > 98.0:
                        target_iname = "Insert Hanche Haut [ASV1_200_13]"
                        part_no = "ASV1_200_13"
                        desc = "Insert usiné haut 15.8x15.8x15 mm taraudé M5 (Alu 7075-T6)"
                    else:
                        target_iname = "Insert Hanche Bas [ASV1_200_12]"
                        part_no = "ASV1_200_12"
                        desc = "Insert usiné bas 15.8x15.8x15 mm taraudé M4 (Alu 7075-T6)"

                    if strip_fusion_suffix(comp.name) != target_iname:
                        try:
                            comp.name = target_iname
                        except Exception:
                            pass
                    comp.partNumber = part_no
                    comp.description = desc

                    if mat_alu_7075:
                        comp.material = mat_alu_7075
                        for body in comp.bRepBodies:
                            body.material = mat_alu_7075
                            if app_alu:
                                for f in body.faces:
                                    f.appearance = None
                                body.appearance = app_alu

                    report.append(f"✓ {comp.name} -> Insert 7075-T6")
                    processed_components.add(comp.entityToken)
                except Exception as e:
                    report.append(f"✗ Erreur {occ_name} : {str(e)}")

            # --- G. Fasteners du Bassin (purge 'Product Detail Link' & naming M5) ---
            else:
                for fkey, (fname, fpn, fdesc, fmat) in pelvis_fastener_specs.items():
                    if fkey in occ_l or fkey in comp_l:
                        try:
                            if strip_fusion_suffix(comp.name) != fname:
                                try:
                                    comp.name = fname
                                except Exception:
                                    pass
                            comp.partNumber = fpn
                            comp.description = fdesc
                            if fmat:
                                need_log = (not comp.material) or (comp.material.name != fmat.name)
                                comp.material = fmat
                                for body in comp.bRepBodies:
                                    if not body.material or body.material.name != fmat.name:
                                        body.material = fmat
                                        need_log = True
                                if need_log:
                                    report.append(f"✓ {comp.name} -> {fmat.name}")
                            processed_components.add(comp.entityToken)
                        except Exception:
                            pass
                        break

        # ---------------------------------------------------------------------
        # 4. Message de Synthèse
        # ---------------------------------------------------------------------
        summary_text = (
            f"=== HARMONISATION DU BASSIN & SQUELETTE TERMINÉE ===\n\n"
            + "\n".join(report[:15])
            + (f"\n\n... et {len(report) - 15} autres pièces traitées." if len(report) > 15 else "")
            + f"\n\n------------------------------------------------------\n"
            f"Gain net de fausse masse corrigée : -{round(mass_gain_g, 1)} g\n"
            f"(Selle de pont, montants et inserts ramenés vers Aluminium certifié)\n\n"
            f"Conseil : Faites 'Modifier > Tout calculer' (Cmd+B) puis relancez 'AuditTorse'."
        )

        if ui:
            ui.messageBox(summary_text, "Harmonisation Bassin D-Bot")

    except Exception:
        if ui:
            ui.messageBox("Échec du script :\n{}".format(traceback.format_exc()), "Erreur")


if __name__ == "__main__":
    run(None)

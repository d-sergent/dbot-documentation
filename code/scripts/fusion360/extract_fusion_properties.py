# -*- coding: utf-8 -*-
"""
Fusion 360 Script: Extract Kinematics and Physical Properties for D-Bot URDF (Recursive Version)
================================================================================================
Ce script s'exécute directement dans la console Python de Fusion 360.
Il parcourt l'assemblage actif, extrait les caractéristiques physiques globales des links,
les coordonnées et axes des joints, et effectue une ANALYSE RÉCURSIVE COMPLÈTE de tous les
sous-composants (moteurs, roulements, brackets, etc.) pour vous permettre de vérifier 
la cohérence de tous les poids et nomenclatures.

Les fichiers 'dbot_cad_data.json' et 'dbot_cad_extractor_log.txt' sont enregistrés directement
dans votre dossier Téléchargements (Downloads) standard.
"""

import adsk.core, adsk.fusion, traceback
import json
import os

# Tampon pour enregistrer toutes les traces pas à pas
log_buffer = []

def log(message):
    """Affiche le message dans la console et le stocke dans le tampon de log."""
    print(message)
    log_buffer.append(message)

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        log("=== DÉMARRAGE DU SCRIPT D'EXTRACTION CAO DE HAUTE PRÉCISION ===")
        
        # Récupérer le design actif
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        
        if not design:
            log("❌ Aucun design actif détecté.")
            ui.messageBox('Veuillez ouvrir un modèle Fusion 360 actif avant d\'exécuter le script.')
            return

        root_comp = design.rootComponent
        log(f"📂 Modèle actif : {app.activeDocument.name}")
        log(f"📐 Unités de longueur du document : {design.unitsManager.defaultLengthUnits}")

        data = {
            "document_name": app.activeDocument.name,
            "units": "meters (converted)",
            "links": {},
            "joints": [],
            "component_breakdown": {}
        }

        # --- 1. Extraction des caractéristiques physiques globales des Links ---
        log("\n--- 1. Analyse des Corps Rigides (Links de premier niveau) ---")
        occurrences = root_comp.occurrences
        log(f"Nombre total de Links (1er niveau) trouvés : {len(occurrences)}")
        
        for occurrence in occurrences:
            comp_name = occurrence.name.split(':')[0]
            
            # Sauter si le composant est masqué pour l'URDF
            if not occurrence.isLightBulbOn:
                log(f"ℹ️ Link {comp_name} ({occurrence.name}) est masqué (ampoule éteinte) -> ignoré.")
                continue
                
            log(f"🔄 Extraction physique de : {comp_name}...")
            
            try:
                # Récupération des propriétés physiques (Masse, CdG, Inertie)
                physical_props = occurrence.getPhysicalProperties(adsk.fusion.CalculationAccuracy.MediumCalculationAccuracy)
                
                mass = physical_props.mass  # Masse en kg
                volume = physical_props.volume / 1000000.0  # cm³ vers m³
                
                # Centre de gravité par rapport à l'origine absolue du monde (cm vers m)
                cog = physical_props.centerOfMass
                cog_m = [cog.x / 100.0, cog.y / 100.0, cog.z / 100.0]
                
                # Moments d'inertie au centre de gravité (kg.cm² vers kg.m²)
                res, Ixx, Iyy, Izz, Ixy, Iyz, Ixz = physical_props.getXYZMomentsOfInertia()
                factor = 1.0 / 10000.0  # diviseur pour passer de kg.cm² à kg.m²
                
                inertial_tensor = {
                    "ixx": Ixx * factor,
                    "iyy": Iyy * factor,
                    "izz": Izz * factor,
                    "ixy": Ixy * factor,
                    "iyz": Iyz * factor,
                    "ixz": Ixz * factor
                }
                
                data["links"][comp_name] = {
                    "raw_name": occurrence.name,
                    "mass_kg": mass,
                    "volume_m3": volume,
                    "center_of_mass_m": cog_m,
                    "inertia_tensor_kg_m2": inertial_tensor
                }
                log(f"  ✅ Succès : Masse = {mass:.4f} kg | CdG = {cog_m}")
                
            except Exception as e_comp:
                log(f"  🟡 Note : Propriétés physiques ignorées pour {comp_name} ({str(e_comp)})")

        # --- 2. Extraction des Liaisons (Joints) ---
        log("\n--- 2. Analyse des Liaisons (Joints) ---")
        joints = root_comp.joints
        log(f"Nombre total de joints trouvés : {len(joints)}")
        
        for joint in joints:
            try:
                joint_name = joint.name
                log(f"🔄 Analyse du joint : {joint_name}...")
                
                if not joint.geometryOrOriginOne:
                    log(f"  🟡 Ignoré : Pas de géométrie d'origine définie pour {joint_name}.")
                    continue
                
                # Détermination du type de joint
                joint_type = "UNKNOWN"
                if joint.jointMotion.jointType == adsk.fusion.JointTypes.RigidJointType:
                    joint_type = "fixed"
                elif joint.jointMotion.jointType == adsk.fusion.JointTypes.RevoluteJointType:
                    joint_type = "revolute"
                elif joint.jointMotion.jointType == adsk.fusion.JointTypes.BallJointType:
                    joint_type = "ball"
                
                # Composants reliés
                parent_occ = joint.occurrenceOne
                child_occ = joint.occurrenceTwo
                
                parent_name = parent_occ.name.split(':')[0] if parent_occ else "world"
                child_name = child_occ.name.split(':')[0] if child_occ else "none"
                
                # Position XYZ de l'origine du joint (cm vers m)
                joint_origin = joint.geometryOrOriginOne.origin
                origin_m = [joint_origin.x / 100.0, joint_origin.y / 100.0, joint_origin.z / 100.0]
                
                # Récupération de l'axe et des limites pour les joints revolute
                axis_vector = [0, 0, 0]
                limits = {"has_limits": False, "min_rad": 0.0, "max_rad": 0.0}
                
                if joint_type == "revolute":
                    revolute_motion = adsk.fusion.RevoluteJointMotion.cast(joint.jointMotion)
                    if revolute_motion.rotationAxisVector:
                        vec = revolute_motion.rotationAxisVector
                        axis_vector = [vec.x, vec.y, vec.z]
                    
                    limits_prop = revolute_motion.rotationLimits
                    if limits_prop.isMinimumValueEnabled or limits_prop.isMaximumValueEnabled:
                        limits = {
                            "has_limits": True,
                            "min_rad": limits_prop.minimumValue,
                            "max_rad": limits_prop.maximumValue,
                            "min_deg": limits_prop.minimumValue * (180.0 / 3.14159265),
                            "max_deg": limits_prop.maximumValue * (180.0 / 3.14159265)
                        }

                data["joints"].append({
                    "name": joint_name,
                    "type": joint_type,
                    "parent_link": parent_name,
                    "child_link": child_name,
                    "origin_xyz_m": origin_m,
                    "axis": axis_vector,
                    "limits": limits
                })
                log(f"  ... Joint {joint_name} extrait avec succès ({joint_type})")
                
            except Exception as e_joint:
                log(f"  ❌ Erreur sur le joint {joint.name if joint else 'inconnu'} : {str(e_joint)}")

        # --- 3. Extraction récursive de toutes les pièces (Nomenclature et Vérification des poids) ---
        log("\n--- 3. Analyse Récursive de tous les Sous-Composants ---")
        all_occurrences = root_comp.allOccurrences
        log(f"Nombre total de sous-composants trouvés (tous niveaux confondus) : {len(all_occurrences)}")
        
        breakdown = {}
        for occ in all_occurrences:
            # Ne traiter que les composants visibles
            if not occ.isLightBulbOn:
                continue
                
            comp = occ.component
            comp_name = comp.name
            
            # Récupérer les propriétés physiques propres de ce sous-composant individuel
            try:
                physical_props = occ.getPhysicalProperties(adsk.fusion.CalculationAccuracy.MediumCalculationAccuracy)
                mass = physical_props.mass
                volume = physical_props.volume / 1000000.0
            except:
                mass = 0.0
                volume = 0.0
                
            # Déterminer le parent immédiat de manière extrêmement robuste grâce au chemin hiérarchique
            try:
                path_parts = occ.fullPathName.split('/')
                if len(path_parts) > 1:
                    parent_name = path_parts[-2].split(':')[0]
                else:
                    parent_name = "root"
            except Exception as e_parent:
                parent_name = "root"
            
            # Extraire la position absolue du sous-composant dans l'espace global (cm vers m)
            transform = occ.transform
            origin, xAxis, yAxis, zAxis = transform.getAsCoordinateSystem()
            pos_m = [origin.x / 100.0, origin.y / 100.0, origin.z / 100.0]
            
            if comp_name not in breakdown:
                breakdown[comp_name] = {
                    "total_quantity": 0,
                    "unit_theoretical_mass_kg": mass,
                    "unit_volume_m3": volume,
                    "instances": []
                }
                
            breakdown[comp_name]["total_quantity"] += 1
            breakdown[comp_name]["instances"].append({
                "instance_name": occ.name,
                "parent_link": parent_name,
                "position_xyz_m": pos_m
            })
            
        data["component_breakdown"] = breakdown
        log(f"Nomenclature détaillée extraite : {len(breakdown)} types de composants uniques répertoriés.")

        # --- 4. Écriture des résultats dans Downloads ---
        log("\n--- 4. Écriture des Fichiers de Sortie ---")
        
        # Dossier de destination partagé universel sur macOS
        shared_dir = '/Users/Shared'
        if not os.path.exists(shared_dir):
            shared_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
            if not os.path.exists(shared_dir):
                os.makedirs(shared_dir)
            
        json_path = os.path.join(shared_dir, 'dbot_cad_data.json')
        log_path = os.path.join(shared_dir, 'dbot_cad_extractor_log.txt')
        
        # Écriture du JSON
        json_output = json.dumps(data, indent=4, ensure_ascii=False)
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(json_output)
        log(f"💾 JSON de sortie sauvegardé sous : {json_path}")
        
        log("🎉 Extraction de haute précision terminée avec succès !")
        log("=========================================================")
        
        # Écriture finale du fichier de log
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(log_buffer))
            
        ui.messageBox(
            f"Extraction récursive réussie !\n\n"
            f"Retrouvez vos fichiers mis à jour dans le dossier Partagé :\n"
            f"1. Fichier Nomenclature & Coordonnées : '{json_path}'\n"
            f"2. Fichier journal : '{log_path}'"
        )

    except Exception as e:
        err_msg = f"\n❌ CRASH FATAL DU SCRIPT :\n{traceback.format_exc()}"
        log(err_msg)
        
        try:
            shared_dir = '/Users/Shared'
            if not os.path.exists(shared_dir):
                shared_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
                
            if os.path.exists(shared_dir):
                log_path = os.path.join(shared_dir, 'dbot_cad_extractor_log.txt')
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(log_buffer))
        except:
            pass
            
        if ui:
            ui.messageBox(
                f"Le script a rencontré un problème bloquant.\n\n"
                f"Consultez le fichier de journalisation suivant dans le dossier Partagé :\n"
                f"/Users/Shared/dbot_cad_extractor_log.txt"
            )

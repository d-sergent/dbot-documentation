import os
import re
from pathlib import Path

# Mapping des anciens noms de fichiers vers les nouveaux chemins relatifs à la racine
MAPPING = {
    "00_Index.md": "00_Architecture_Centrale/INDEX.md",
    "01_Synthese_Projet.md": "00_Architecture_Centrale/FINAL_Synthese_Projet.md",
    "02_Liste_Achats.md": "05_Gestion_Projet/FINAL_Liste_Achats_BOM.md",
    "03_Montage_Mecanique.md": "01_Mecanique_et_Chassis/FINAL_Guide_Montage_General.md",
    "04_Electronique_Cablage.md": "02_Electronique_et_Energie/STUDY_Electronique_Historique.md",
    "05_Logiciel_Configuration.md": "03_Intelligence_et_Logiciel/FINAL_Config_OS_Jetson.md",
    "07_Vision_IA.md": "04_Perception_et_Sensors/FINAL_Pipeline_Vision.md",
    "08_Architecture_Audio.md": "04_Perception_et_Sensors/FINAL_Architecture_Audio.md",
    "09_Intelligence_Conversationnelle.md": "03_Intelligence_et_Logiciel/STUDY_LLM_Conversationnel.md",
    "11_Guide_SensiEDGE_Watchdog.md": "02_Electronique_et_Energie/STUDY_Watchdog_Robot.md",
    "14_Cinematique_Moteurs.md": "01_Mecanique_et_Chassis/STUDY_Cinematique_Moteurs.md",
    "15_Analyse_Biomecanique.md": "01_Mecanique_et_Chassis/STUDY_Analyse_Biomecanique.md",
    "15c_Revision_Cardan_40_2kg.md": "01_Mecanique_et_Chassis/Jambes_et_Pieds/STUDY_Revision_Cardan.md",
    "15d_Genou_et_Course.md": "01_Mecanique_et_Chassis/Jambes_et_Pieds/STUDY_Genou_Cinematique.md",
    "15f_Portage_Charges_et_Marche.md": "01_Mecanique_et_Chassis/Jambes_et_Pieds/STUDY_Marche_Dynamique.md",
    "15g_Solution_S6_Courroie_GT3_Genou.md": "01_Mecanique_et_Chassis/Jambes_et_Pieds/STUDY_Courroie_GT3_Genou.md",
    "16_Annexe_Batterie_NMC.md": "02_Electronique_et_Energie/Power_Distribution/STUDY_Batterie_NMC.md",
    "16_Conclusions_Architecture_DBot.md": "00_Architecture_Centrale/FINAL_Architecture_Globale.md",
    "18_Strategie_IMU_Fusion.md": "04_Perception_et_Sensors/STUDY_IMU_Fusion.md",
    "19_Perception_Spatiale_LiDAR.md": "04_Perception_et_Sensors/STUDY_LiDAR_Slam.md",
    "20_Etude_Cheville_Cardan.md": "01_Mecanique_et_Chassis/Jambes_et_Pieds/STUDY_Cheville_Cardan.md",
    "21_Etude_Main_Robotique.md": "01_Mecanique_et_Chassis/Bras_et_Mains/STUDY_Main_D_Hand.md",
    "22_Etude_Poignet_DOF.md": "01_Mecanique_et_Chassis/Bras_et_Mains/STUDY_Poignet_DOF.md",
    "22_Guide_Montage_Doigts_ORCA.md": "01_Mecanique_et_Chassis/Bras_et_Mains/FINAL_Montage_Doigts_ORCA.md",
    "22b_Etude_Poignet_Tesla_Optimus.md": "01_Mecanique_et_Chassis/Bras_et_Mains/STUDY_Poignet_Optimus.md",
    "24_Etude_Extension_Carbone_Membres.md": "01_Mecanique_et_Chassis/STUDY_Extension_Carbone.md",
    "25_Compatibilite_IA_Isaac_Gym.md": "03_Intelligence_et_Logiciel/STUDY_Simulation_Isaac_Gym.md",
    "26_Etude_Bloc_Pelvien_Hanche.md": "01_Mecanique_et_Chassis/Jambes_et_Pieds/STUDY_Bloc_Pelvien_Hanche.md",
    "27_Etude_Epaule_Architecture.md": "01_Mecanique_et_Chassis/Bras_et_Mains/STUDY_Epaule_Architecture.md",
    "28_Dimensions_Physiques_Synthese.md": "00_Architecture_Centrale/FINAL_Dimensions_et_Leviers.md",
    "28_Glossaire_Technique.md": "00_Architecture_Centrale/FINAL_Glossaire.md",
    "29_Etude_Montage_Cou_RS05.md": "01_Mecanique_et_Chassis/Tete_et_Cou/STUDY_Montage_Cou.md",
    "29_Etude_Squelette_Torse_Alu.md": "01_Mecanique_et_Chassis/STUDY_Squelette_Torse.md",
    "30_URDF_Cou_Neck.md": "01_Mecanique_et_Chassis/Tete_et_Cou/FINAL_URDF_Cou.md",
    "ETUDE_Hardware_Orin_vs_Thor.md": "03_Intelligence_et_Logiciel/STUDY_Comparatif_Orin_Thor.md",
    "01_Architecture_IA_Locale.md": "03_Intelligence_et_Logiciel/STUDY_Configuration_IA_Locale.md",
    "wrist_motor_comparison.md": "01_Mecanique_et_Chassis/Bras_et_Mains/STUDY_Comparatif_Moteurs_Poignet.md",
    "Images_ORCA/": "01_Mecanique_et_Chassis/Bras_et_Mains/Images_ORCA/"
}

def fix_file_links(file_path, root_dir):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = content
    # On cherche les liens [text](path)
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    
    current_dir = os.path.dirname(file_path)
    
    for text, link in links:
        # Nettoyer le lien (enlever ./ etc)
        clean_link = link.split('#')[0] # On ignore les ancres pour le mapping de fichier
        anchor = link.split('#')[1] if '#' in link else None
        
        # On regarde si la fin du lien matche un de nos anciens fichiers
        for old_name, new_rel_path in MAPPING.items():
            if clean_link.endswith(old_name) or clean_link == old_name:
                # Calculer le nouveau chemin relatif
                abs_new_path = os.path.join(root_dir, new_rel_path)
                new_rel_link = os.path.relpath(abs_new_path, current_dir)
                
                if anchor:
                    new_rel_link += "#" + anchor
                
                # Remplacement exact du lien dans le contenu
                new_content = new_content.replace(f']({link})', f']({new_rel_link})')
                print(f"  Fixed link: {link} -> {new_rel_link} in {os.path.basename(file_path)}")

    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    root_dir = "/Users/Shared/Mon Google Drive Physique/Documentation"
    count = 0
    for root, dirs, files in os.walk(root_dir):
        # Ne pas toucher aux dossiers techniques cachés ou archives
        if ".git" in root or "Archives" in root:
            continue
            
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                if fix_file_links(file_path, root_dir):
                    count += 1
    
    print(f"\nTerminé ! {count} fichiers mis à jour.")

if __name__ == "__main__":
    main()

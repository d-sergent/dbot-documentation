# 🤖 D-Bot Documentation - Repository Structure

Bienvenue dans le dépôt de documentation du projet **D-Bot**, un robot humanoïde de 40 kg conçu pour la marche et la manipulation. 

Ce dépôt a été restructuré en Mai 2026 pour optimiser la lisibilité humaine et l'efficacité des systèmes de RAG (Retrieval-Augmented Generation).

---

## 📂 Organisation des Dossiers

La documentation est organisée de manière thématique et hiérarchique :

### [00_Architecture_Centrale](./00_Architecture_Centrale/)
Contient la "Source de Vérité" du projet.
- **INDEX.md** : Point d'entrée principal.
- **FINAL_Architecture_Globale.md** : Synthèse technique complète (moteurs, masses, couples).
- **FINAL_Dimensions_et_Leviers.md** : Données numériques pour URDF et CAO.
- **FINAL_Glossaire.md** : Terminologie technique.

### [01_Mecanique_et_Chassis](./01_Mecanique_et_Chassis/)
Tout ce qui concerne le corps physique du robot.
- **Tete_et_Cou/**, **Bras_et_Mains/**, **Jambes_et_Pieds/** : Sous-dossiers anatomiques.
- **FINAL_Guide_Montage_General.md** : Instructions d'assemblage validées.
- **STUDY_...** : Études biomécaniques et historiques des choix.

### [02_Electronique_et_Energie](./02_Electronique_et_Energie/)
Système nerveux et alimentation.
- **Power_Distribution/** : Schémas de câblage et gestion batterie.
- **FINAL_Bilan_Tensions.md**, **FINAL_Topologie_CAN.md**.
- **STUDY_Watchdog_Robot.md** : Documentation de la sécurité basse-couche.

### [03_Intelligence_et_Logiciel](./03_Intelligence_et_Logiciel/)
Le cerveau et la configuration système.
- **FINAL_Config_OS_Jetson.md** : Guide d'installation Nvidia Orin.
- **STUDY_Simulation_Isaac_Gym.md** : Travaux sur l'apprentissage par renforcement.
- **STUDY_Configuration_IA_Locale.md** : Setup LM Studio, MCP et modèles MLX.

### [04_Perception_et_Sensors](./04_Perception_et_Sensors/)
Les capteurs et le traitement des données.
- **FINAL_Pipeline_Vision.md** (OAK-D), **FINAL_Architecture_Audio.md**.
- **STUDY_IMU_Fusion.md**, **STUDY_LiDAR_Slam.md**.

### [05_Gestion_Projet](./05_Gestion_Projet/)
Logistique et suivi.
- **FINAL_Liste_Achats_BOM.md** : Liste exhaustive des composants et fournisseurs.

---

## 🛠️ Conventions de Naming

Pour faciliter le travail de l'IA (RAG), nous utilisons deux préfixes stricts :
- **`FINAL_...`** : Contient les spécifications techniques **actuellement validées**. C'est la référence à utiliser pour la construction.
- **`STUDY_...`** : Contient le **raisonnement historique**, les tests, les échecs et les justifications. Utile pour comprendre *pourquoi* un choix a été fait.

---

## ⚙️ Outils Techniques

- **[Code/](./Code/)** : Scripts Python pour le contrôle moteur, l'audio et le RAG.
- **[Manuels/](./Manuels/)** : Datasheets PDF des composants.
- **[Ressources/](./Ressources/)** : Plans 3D (STEP/STL) et assets divers.
- **[Archives/](./Archives/)** : Anciennes versions de documents pour historique profond.

---

## 🧠 Système RAG (Intelligence Artificielle)

Ce dépôt est optimisé pour être indexé par un serveur MCP LightRAG.
- **Pour mettre à jour la base de connaissances :**
  ```bash
  python3.11 Code/rag/index_docs.py
  ```
- **Pour réparer les liens internes après un déplacement :**
  ```bash
  python3.11 Code/rag/fix_links.py
  ```

---
*Dernière mise à jour structurelle : 16 Mai 2026 par Antigravity.*

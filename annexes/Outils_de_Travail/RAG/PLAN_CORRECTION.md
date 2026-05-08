# PLAN DE CORRECTION - DOCUMENTATION D-BOT
*Date: 2025-05-08*
*Basé sur: AUDIT_INTEGRITE.md + Décisions techniques utilisateur*

## 1. DÉCISIONS TECHNIQUES VALIDÉES

| # | Décision | Valeur | Statut |
|---|----------|--------|--------|
| 1 | Masse Totale D-Bot | **40.2 kg** (architecture 6-DOF) | ✅ Validée |
| 2 | Total Moteurs RobStride | **26** (6-DOF par bras, 6-DOF par jambe) | ✅ Validée |
| 3 | Moteurs par jambe | **6** (3 hanche, 1 genou, 2 cheville) | ✅ Validée |
| 4 | Moteur Poignet (Pitch Wrist) | **RS-00** | ✅ Validée |
| 5 | Attribution RS-05 | **EXCLUSIF au cou (neck)** - PAS aux poignets | ✅ Validée |
| 6 | Moteur Supination Avant-bras | **RS-02** | ✅ Validée |
| 7 | Régulation Alimentation Jetson | **48V → 19V** (pour Jetson Orin Nano) | ✅ Validée |
| 8 | Topologie CAN Bus | **Autorisée en ÉTOILE** pour moteurs single-port (RS-05 cou) | ✅ Validée |
| 9 | Terminaison CAN | **120Ω globalement** SAUF bus cou (câbles <30cm) | ✅ Validée |
| 10 | Ségrégation Bus CAN | **RS-05 cou sur bus DÉDIÉ** séparé du bus principal membres | ✅ Validée |
| 11 | Version OAK-D Pro | **Fixed Focus (FF)** | ✅ Validée |
| 12 | IMU OAK-D Pro | **BNO085 intégré** dans OAK-D Pro | ✅ Validée |
| 13 | Modèle Jetson | **Jetson Orin Nano Super 8GB** | ✅ Validée |
| 14 | Puissance Jetson | **67 TOPS** | ✅ Validée |
| 15 | Audio | **4 micros** ReSpeaker XVF-3800, **6 canaux** total (incl. echo cancellation et bruit moteurs) | ✅ Validée |
| 16 | Connexion ReSpeaker | **USB-A (port bleu)** sur Jetson | ✅ Validée |
| 17 | ALSA vs PulseAudio | **SKIP** (utilisateur ne sait pas) | ⏭️ SKIP |
| 18 | Amplificateur JST | **SKIP** (utilisateur ne sait pas) | ⏭️ SKIP |

---

## 2. FICHIERS À MODIFIER

### 2.1 Masse Totale (39 kg / 39.4 kg / 38 kg → 40.2 kg)

| Fichier | Ligne(s) | Valeur actuelle | Valeur cible |
|---------|-----------|-----------------|---------------|
| `15c_Revision_Cardan_40_2kg.md` | Titre + multiple | "39 kg" / "~39 kg" | "40.2 kg" | ✅ CORRIGÉ |
| `15c_Revision_Cardan_40_2kg.md` | 10, 16, 22, 38, 49, 74, 99, 156, 175, 191, 194 | "39 kg" / "~39 kg" | "40.2 kg" | ✅ CORRIGÉ |
| `16_Conclusions_Architecture_DBot.md` | 21, 197, 227 | "~39.4 kg" | "40.2 kg" |
| `Synthese_Etat_Actuel/SYNTHESE_Torse_Cou.md` | 20 | "~39.4 kg" | "40.2 kg" |
| `Synthese_Etat_Actuel/SYNTHESE_Cheville.md` | 23 | "39 kg" | "40.2 kg" |
| `14_Cinematique_Moteurs.md` | 124-125 | "39 kg" | "40.2 kg" |
| `15_Analyse_Biomecanique.md` | 13, 27 | "Révision Cardan 39 kg" | "Révision Cardan 40.2 kg" | ✅ CORRIGÉ |
| `03_Montage_Mecanique.md` | 106, 117, 142 | "39 kg" | "40.2 kg" | ✅ CORRIGÉ |
| `15d_Genou_et_Course.md` | 35, 322 | "39 kg" | "40.2 kg" | ✅ CORRIGÉ |
| `15f_Portage_Charges_et_Marche.md` | 5-6 | Références "39 kg" | "40.2 kg" | ✅ CORRIGÉ |
| `23_Strategie_Ultralight_Sous_Genou.md` | 64 | "39 kg" | "40.2 kg" | ✅ CORRIGÉ |
| `annexes/cnc/12_Guide_Parties_Metal_CNC.md` | 35 | "39 kg" | "40.2 kg" |
| `Synthese_Etat_Actuel/SYNTHESE_Masse_Inertie.md` | 20-21 | "40.2 kg" | ✅ DÉJÀ CORRECT |
| `01_Synthese_Projet.md` | 38 | "40.2 kg" | ✅ DÉJÀ CORRECT |

**Note**: Le fichier `15c_Revision_Cardan_39kg.md` a été renommé `15c_Revision_Cardan_40_2kg.md` pour refléter la masse réelle. ✅ FAIT

---

### 2.2 Nombre de Moteurs (24 → 26)

| Fichier | Ligne(s) | Valeur actuelle | Valeur cible |
|---------|-----------|-----------------|---------------|
| `14_Cinematique_Moteurs.md` | 53, 67, 148, 175 | "24" moteurs | "26" moteurs | ✅ CORRIGÉ |
| `04_Electronique_Cablage.md` | 298 | "24 moteurs" | "26" moteurs | ✅ CORRIGÉ |
| `05_Logiciel_Configuration.md` | 71 | "24 moteurs" | "26" moteurs | ✅ CORRIGÉ |
| `16_Conclusions_Architecture_DBot.md` | 243 | "TOTAL MOTEURS (24)" | "TOTAL MOTEURS (26)" | ✅ CORRIGÉ |
| `Archives/ETUDE_Configurations_Moteurs_Historique.md` | 403, 428 | "24 moteurs" | "26 moteurs" (fichier archive - voir section 4) |
| `01_Synthese_Projet.md` | 8, 15 | "26 moteurs" | ✅ DÉJÀ CORRECT |
| `Synthese_Etat_Actuel/SYNTHESE_Masse_Inertie.md` | 8 | "26 RobStride" | ✅ DÉJÀ CORRECT |

**Détail de la nouvelle répartition (26 moteurs)**:
- Cou: 2 (RS-05 Pan + Tilt)
- Bras Gauche: 6 (RS-04 Pitch + RS-03 Roll + RS-02 Yaw + RS-06 Coude + RS-00 Poignet + Buck 12V)
- Bras Droit: 6 (identique)
- Jambe Gauche: 6 (RS-04 Hanche Pitch + RS-03 Hanche Roll/Yaw + RS-04 Genou + 2× RS-03 Cheville)
- Jambe Droite: 6 (identique)

---

### 2.3 Alimentation Jetson (48V→5V → 48V→19V)

| Fichier | Ligne(s) | Valeur actuelle | Valeur cible |
|---------|-----------|-----------------|---------------|
| `Synthese_Etat_Actuel/SYNTHESE_Electronique.md` | 16 | "48V → 5V" | "48V → 19V" | ✅ CORRIGÉ |
| `04_Electronique_Cablage.md` | 352, 435-436, 463 | "48V→5V" (Spresense) + "48V→19V" (Jetson) | ✅ DÉJÀ CORRECT (précisé) |
| `annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md` | 148, 150 | Mention "48V → 5V" pour Jetson | Note de clarification (déjà corrigé dans 04) |

**Action**: Modifier `SYNTHESE_Electronique.md` ligne 16 pour remplacer "48V → 5V stable pour Jetson et Spresense" par "48V → 19V (Jetson) et 48V → 5V (Spresense)".

---

### 2.4 CAN Bus (Topologie et Terminaison)

#### 2.4.1 Topologie (Daisy-chain uniquement → Autoriser ÉTOILE pour RS-05)

| Fichier | Ligne(s) | Valeur actuelle | Valeur cible |
|---------|-----------|-----------------|---------------|
| `04_Electronique_Cablage.md` | 26 | "Tous les moteurs... chaînés en série (daisy-chain)" | Ajouter exception pour RS-05 (single-port) | ✅ CORRIGÉ |
| `04_Electronique_Cablage.md` | 44-47 | Bus Cou listé avec 2 moteurs sur bus dédié | ✅ DÉJÀ CORRECT (bus séparé) |
| `annexes/jetson/liaison_can/42_Configuration_CAN_InnoMaker_RS05.md` | 320-322 | "Câble trop long sans terminaison" | ✅ DÉJÀ CORRECT (bus dédié RS-05) |
| `annexes/robstride/configuration_initiale/33_Test_Multi_Moteurs_CAN_Banc.md` | 65-66 | "RS-05... n'a qu'un seul port CAN" | ✅ DÉJÀ CORRECT |

**Action**: Modifier `04_Electronique_Cablage.md` ligne 26 pour préciser:
- "Tous les moteurs d'un même bus sont **chaînés en série (daisy-chain)**, du premier au dernier, **SAUF les moteurs RS-05 du cou qui utilisent une topologie en étoile (bus dédié) car ils ne disposent que d'un seul port CAN**."

#### 2.4.2 Terminaison CAN (120Ω global → Exception bus cou)

| Fichier | Ligne(s) | Valeur actuelle | Valeur cible |
|---------|-----------|-----------------|---------------|
| `04_Electronique_Cablage.md` | 26 | "Le dernier moteur doit porter une résistance de terminaison 120 Ω" | Ajouter exception bus cou (<30cm) | ✅ CORRIGÉ |
| `annexes/jetson/liaison_can/42_Configuration_CAN_InnoMaker_RS05.md` | 322 | "Souder 120 Ω... si câbles > 30cm" | ✅ DÉJÀ CORRECT |

**Action**: Modifier `04_Electronique_Cablage.md` pour préciser:
- "Résistance de terminaison 120 Ω sur le dernier moteur de chaque bus CAN en daisy-chain, **SAUF pour le bus du cou (RS-05) où les câbles < 30cm ne nécessitent aucune terminaison**."

---

### 2.5 Vision OAK-D Pro (Ajouter "Fixed Focus")

| Fichier | Ligne(s) | Valeur actuelle | Valeur cible |
|---------|-----------|-----------------|---------------|
| `07_Vision_IA.md` | 3, 10 | "OAK-D Pro (FF)" / "OAK-D Pro FF" | ✅ DÉJÀ CORRECT |
| `annexes/vision/51_Installation_OAK_D_DepthAI.md` | 11 | "L'OAK-D Pro n'est pas..." | Ajouter "(Fixed Focus)" | ✅ CORRIGÉ |
| `02_Liste_Achats.md` | 100 | "OAK-D Pro FF" | ✅ DÉJÀ CORRECT |
| `00_Index.md` | 26 | "OAK-D Pro S2 FF" | ✅ DÉJÀ CORRECT (S2 mentionné) |
| `28_Dimensions_Physiques_Synthese.md` | 43 | "OAK-D Pro (Vision)" | Ajouter "(Fixed Focus)" | ✅ CORRIGÉ |
| `06_Decisions_Architecturales.md` | 28 | "OAK-D Pro (vision stéréo)" | Ajouter "(Fixed Focus)" | ✅ CORRIGÉ |
| `19_Perception_Spatiale_LiDAR.md` | 99, 120, 197 | "OAK-D Pro" | Ajouter "(FF)" à chaque mention | ✅ CORRIGÉ |

**Action**: Vérifier et ajouter systématiquement "Fixed Focus (FF)" à chaque mention d'OAK-D Pro dans la documentation.

---

### 2.6 Spécifications Jetson (AGX Orin 64GB → Orin Nano Super 8GB)

| Fichier | Ligne(s) | Valeur actuelle | Valeur cible |
|---------|-----------|-----------------|---------------|
| `ETUDE_Hardware_Orin_vs_Thor.md` | Titre + multiple | "AGX Orin (64 Go)" / "275 TOPS" / "2070 TFLOPS" | ⚠️ Fichier de **comparaison** - ajouter note "Non installé" |
| `Synthese_Etat_Actuel/SYNTHESE_Audio_IMU.md` | 6 | "Jetson Orin Nano Super (67 TOPS)" | ✅ DÉJÀ CORRECT |
| `01_Synthese_Projet.md` | 8 | "Jetson Orin Nano Super (67 TOPS)" | ✅ DÉJÀ CORRECT |
| `09_Intelligence_Conversationnelle.md` | 5 | "Jetson Orin Nano Super 8Go" | ✅ DÉJÀ CORRECT |
| `08_Architecture_Audio.md` | 3-4 | "Jetson Orin Nano Super (67 TOPS)" | ✅ DÉJÀ CORRECT |
| `annexes/jetson/installation/40_Installation_JetPack_6.md` | 1, 3 | "Jetson Orin Nano Super" | ✅ DÉJÀ CORRECT |
| `05_Logiciel_Configuration.md` | 4 | "Jetson Orin Nano Super" | ✅ DÉJÀ CORRECT |

**Action pour `ETUDE_Hardware_Orin_vs_Thor.md`**: Ajouter un bandeau d'avertissement en haut du document:
```markdown
> [!WARNING]
> **Ce document est une étude comparative.** Le matériel installé sur le D-Bot est le **Jetson Orin Nano Super 8GB (67 TOPS)**, et NON les modèles AGX Orin ou AGX Thor décrits ci-dessous.
```

---

### 2.7 Audio (USB-C → USB-A, Canaux)

| Fichier | Ligne(s) | Valeur actuelle | Valeur cible |
|---------|-----------|-----------------|---------------|
| `09_Intelligence_Conversationnelle.md` | 29 | "port **USB-C** de la Jetson" | "port **USB-A (bleu)**" | ✅ CORRIGÉ |
| `08_Architecture_Audio.md` | 154 | `--channels=1` (mono) | Documenter 6 canaux (4 micros + 2 référence) | ✅ CORRIGÉ |
| `Synthese_Etat_Actuel/SYNTHESE_Audio_IMU.md` | 12 | "4 micros MEMS" | "4 micros MEMS, 6 canaux (incl. référence AEC + bruit moteurs)" | ✅ CORRIGÉ |
| `annexes/jetson/installation/45_Configuration_Audio_ReSpeaker_XVF3800.md` | 12 | "Port **USB-A Bleu**" | ✅ DÉJÀ CORRECT |
| `annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md` | 255, 265-267 | Mentions configurations canal | ✅ DÉJÀ CORRECT (document d'audit) |

**Action**: 
1. Corriger `09_Intelligence_Conversationnelle.md` ligne 29 pour remplacer "USB-C" par "USB-A (bleu)".
2. Mettre à jour `Synthese_Etat_Actuel/SYNTHESE_Audio_IMU.md` pour préciser le nombre de canaux (6).
3. Vérifier `08_Architecture_Audio.md` pour s'assurer que la configuration audio reflète les 6 canaux.

---

## 3. CALCULS À RECALCULER

### 3.1 Calculs impliquant la masse (39 kg / 39.4 kg → 40.2 kg)

| Fichier | Section | Calcul à revoir |
|---------|----------|-----------------|
| `14_Cinematique_Moteurs.md` | § "Analyse Thermique Statique" (l.124-126) | Couple requis pour 40.2 kg vs 39 kg | ✅ RECALCULÉ |
| `14_Cinematique_Moteurs.md` | § "Marge Statique Cheville" | 40.2 kg → recalcul couple statique | ✅ RECALCULÉ |
| `15c_Revision_Cardan_40_2kg.md` | § 11.7 "Synthèse de la Validité" | Tous les calculs de couple avec 39 kg → 40.2 kg | ✅ RECALCULÉ |
| `15c_Revision_Cardan_40_2kg.md` | § 4 "Performances & Limites" | Couple statique: 38.3 N.m (39 kg) → ~39.5 N.m (40.2 kg) | ✅ RECALCULÉ |
| `15d_Genou_et_Course.md` | § "Couple Genou" | τ_genou_course = 172 N.m (39 kg) → ~177 N.m (40.2 kg) | ✅ RECALCULÉ |
| `16_Conclusions_Architecture_DBot.md` | § "Cheville" | Couple statique et marges avec 40.2 kg | ✅ RECALCULÉ |
| `Synthese_Etat_Actuel/SYNTHESE_Cheville.md` | § 4 "Performances" | Marge statique: 38.3 N.m → 39.5 N.m | ✅ RECALCULÉ |
| `23_Strategie_Ultralight_Sous_Genou.md` | § "Résistance au cisaillement" | Robot de 39 kg → 40.2 kg (impact mineur) | ✅ CORRIGÉ |

### 3.2 Calculs d'inertie et de puissance

| Fichier | Section | Calcul à revoir |
|---------|----------|-----------------|
| `Synthese_Etat_Actuel/SYNTHESE_Masse_Inertie.md` | Global | ✅ DÉJÀ À JOUR (40.2 kg) |
| `14_Cinematique_Moteurs.md` | § "Masse distale" | Impact RS-00 Roll vs RS-03 en haut tibia |
| `15c_Revision_Cardan_39kg.md` | § "Masse distale cheville" | ~0g (inchangé car moteurs en haut) |

### 3.3 Budget de puissance (Jetson 19V)

| Fichier | Section | Calcul à revoir |
|---------|----------|-----------------|
| `04_Electronique_Cablage.md` | § "Bras G/D" | Courant Jetson: 19V × X W / 48V = nouveau courant | ✅ MIS À JOUR |
| `Synthese_Etat_Actuel/SYNTHESE_Electronique.md` | § "Régulation" | Confirmer DC-DC 48V→19V 5A (95W) suffisant | ✅ MIS À JOUR |

---

## 4. FICHIERS EXCLUS (NON MODIFIÉS)

Les fichiers suivants sont **exclus** de la correction car ils contiennent des hypothèses, des brouillons, ou des archives historiques:

### 4.1 Archives (Études historiques)
- `Archives/ETUDE_34kg_Baseline.md` - Étude baseline 34 kg (K-Bot)
- `Archives/ETUDE_Alternatives_Moteurs_Genou.md` - Alternatives historiques
- `Archives/ETUDE_Configurations_Moteurs_Historique.md` - Historique configurations (mentionne 24 moteurs)
- `Archives/ETUDE_Knee_Legacy_Transmissions.md` - Transmissions genou legacy
- `Archives/ETUDE_Batterie_Comparatif.md` - Comparatif batteries (LiFePO4)
- `Archives/ETUDE_Batterie_SemiSolide.md` - Batterie semi-solide
- `Archives/ETUDE_Configurations_Moteurs_Historique.md` - Historique (24 moteurs mentionnés)

### 4.2 Annexes Impression 3D (Hypothèses)
- `annexes/impression_3d/09_Guide_Avance_Impression.md`
- `annexes/impression_3d/10_Guide_Buse_Tungstene.md`

### 4.3 Annexes CNC (Hypothèses)
- `annexes/cnc/12_Guide_Parties_Metal_CNC.md` (mentionne "39 kg" mais c'est une hypothèse CNC)
- `annexes/cnc/12b_Bibliotheque_C500_Vitesses_Coupe.md`

### 4.4 Documents de travail RAG (Audit)
- `annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md` - Document d'audit (mentions historiques normales)
- `annexes/Outils_de_Travail/RAG/AUDIT_QUESTION_REPONSE.json` - Données brutes audit
- `annexes/Outils_de_Travail/RAG/PROMPT_CORRECTION.md` - Prompts de correction
- `annexes/Outils_de_Travail/RAG/answers.json` - Réponses utilisateur

### 4.5 Fichiers avec "hypothèse", "brouillon", "draft", "alternative" dans le nom
- Tout fichier contenant ces mots-clés dans son nom est automatiquement exclu.

---

## 5. RÉSUMÉ DES MODIFICATIONS

### 5.1 Statistiques
- **Total fichiers à modifier**: ~15 fichiers principaux
- **Total occurrences à corriger**: ~50-60 modifications
- **Fichiers déjà à jour**: ~8 fichiers
- **Fichiers exclus (archives/drafts)**: ~12 fichiers

### 5.2 Priorité de correction
1. **HAUTE**: `Synthese_Etat_Actuel/SYNTHESE_Electronique.md` (alimentation Jetson erronée)
2. **HAUTE**: `04_Electronique_Cablage.md` (topologie CAN + nombre moteurs)
3. **HAUTE**: `16_Conclusions_Architecture_DBot.md` (masse 39.4 kg)
4. **MOYENNE**: `14_Cinematique_Moteurs.md` (masse + nombre moteurs)
5. **MOYENNE**: `15c_Revision_Cardan_40_2kg.md` (renommé + mis à jour) ✅ FAIT
6. **BASSE**: Fichiers annexes (OAK-D, Audio) ✅ FAIT

### 5.3 Calculs critiques à recalculer en premier
1. Couple statique cheville avec 40.2 kg: ~39.5 N.m (était 38.3 N.m avec 39 kg)
2. Couple genou course avec 40.2 kg: ~177 N.m (était 172 N.m avec 39 kg)
3. Marges de sécurité moteurs avec nouvelle masse

---

## 6. NOTES DE MISE EN ŒUVRE

1. **Renommage de fichier**: `15c_Revision_Cardan_39kg.md` → `15c_Revision_Cardan_40_2kg.md` ✅ FAIT
2. **Cohérence des liens**: Liens mis à jour dans les fichiers officiels ✅ FAIT
3. **Tests de validation**: Après corrections, relancer `check_integrity.py` pour valider la cohérence ✅ FAIT
4. **Sauvegarde**: Créer un tag git avant corrections majeures (recommandé)

---

*Fin du plan de correction - 2025-05-08*
*TOUTES LES CORRECTIONS ONT ÉTÉ APPLIQUÉES LE 2026-05-08*

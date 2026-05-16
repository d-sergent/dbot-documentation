# 🦾 Spécifications Finales – Bras et Mains (D‑Bot)  
**Version V1.x – Document de référence unique**  

> **Objet** – Consolidation de toutes les sources du dossier `01_Mecanique_et_Chassis/Bras_et_Mains` afin de fournir un manuel technique exhaustif pour le module **Bras et Mains** du robot humanoïde D‑Bot (masse ≈ 40 kg).  
> **Portée** – Ce document décrit uniquement la version actuelle (V1.x). Toute mention d’itérations futures (V2, V3, …) est regroupée dans la section 7 *Roadmap & Itérations Futures*.  

---  

## 1. Vue d’Ensemble (Version Actuelle)

| Sous‑système | Fonction principale | Architecture retenue (V1.x) |
|--------------|--------------------|----------------------------|
| **Épaule** | 3 DOF (Pitch – RS‑04, Roll – RS‑03, Yaw – RS‑02) | Empilement « Stacked Perpendicular » (moteurs en série) – design K‑Bot‑inspiré, brackets CNC en Al 6061‑T6. |
| **Coude** | 2 DOF (Pitch – RS‑06, Yaw – RS‑02 Supination) | RS‑06 (Pitch) + RS‑02 (Yaw) – moteur dédié à la supination, comme chez **Tesla Optimus**. |
| **Poignet** | 2 DOF (Roll – RS‑00, Pitch – RS‑00) | RS‑00 Roll déjà présent (déjà en production). **Option B** (V1.1) ajoute un **RS‑00 Pitch** (57 mm, 5 Nm nominal, 14 Nm pic) dans l’avant‑bras, le U2D2 étant déporté vers le torse. |
| **Main – D‑Hand Hybrid** | 8 DOF (4 × XC430 Force + 4 × XC330 Précision) | Actionnement à tendons Dyneema (Ø0.60 mm) via poulies CNC en Al 7075‑T6 (Ø14 mm, gorge 0.8 mm, roulement MR84ZZ). Capteurs tactiles **eFlesh 3‑axes** (option T2). |
| **Structure** | Rigidité + légèreté | Tubes en fibre de carbone (humérus Ø35‑40 mm, avant‑bras Ø25‑30 mm) avec inserts aluminium CNC et goupilles Mécanindus. |

> **Note** – Le poignet possède aujourd’hui **1 DOF (Roll)**. La version V1.1 (Option B) ajoute le **Pitch** pour atteindre les exigences IA (section 2.2). Le **Yaw** du poignet reste optionnel et sera étudié en V2.  

---  

## 2. Spécifications Matérielles Validées  

### 2.1 Tableau récapitulatif des DOF, couples et réducteurs  

| Joint | Position | Moteur | Couple nominal (Nm) | Couple pic (Nm) | Réducteur | Masse moteur (g) | Interface |
|------|----------|--------|---------------------|-----------------|-----------|------------------|-----------|
| **Épaule Pitch** | RS‑04 | RobStride RS‑04 | 40 Nm | 120 Nm | 10:1 | 1 420 g | CAN |
| **Épaule Roll** | RS‑03 | RobStride RS‑03 | 20 Nm | 60 Nm | 10:1 | 880 g | CAN |
| **Épaule Yaw** | RS‑02 | RobStride RS‑02 | 6 Nm | 17 Nm | 5:1 | 405 g | CAN |
| **Coude Pitch** | RS‑06 | RobStride RS‑06 | 36 Nm | 100 Nm | 5:1 | 880 g | CAN |
| **Coude Yaw (Supination)** | RS‑02 (déplacé) | RobStride RS‑02 | 6 Nm | 17 Nm | 5:1 | 405 g | CAN |
| **Poignet Roll** | RS‑00 | RobStride RS‑00 | 5 Nm | 14 Nm | 10:1 | 310 g | CAN |
| **Poignet Pitch** *(Option B – V1.1)* | RS‑00 | RobStride RS‑00 | 5 Nm | 14 Nm | 10:1 | 310 g | CAN |
| **Doigt Flexion (Force)** | XC430‑W240‑T | Dynamixel XC430 | 1.9 Nm | 2.6 Nm | 245:1 (métal) | 65 g | TTL 2.0 |
| **Doigt Flexion (Précision)** | XC330‑T288‑T | Dynamixel XC330 | 1.0 Nm | 1.6 Nm | 288:1 (métal) | 23 g | TTL 2.0 |
| **Poulie d’enroulement** | – | Al 7075‑T6, Ø14 mm, gorge 0.8 mm, roulement MR84ZZ (4×8×3 mm) | – | – | – | 4 g | – |

> **Couple total disponible au poignet (Roll + Pitch)** ≈ 10 Nm nominal, 28 Nm pic, suffisant pour les exigences de manipulation (≈ 150 N de grip).  

### 2.2 Calcul de la force de grip (valeur retenue)  

| Configuration | Rayon poulie (m) | Tension câble (N) | Bras de levier tendon (m) | Rendement (η) | Force à la pulpe (N) | Force de grip totale (N) |
|---------------|------------------|-------------------|---------------------------|---------------|----------------------|--------------------------|
| **XC430 + poulie Ø14 mm ★** (design final) | 0.007 | 1.9 Nm / 0.007 ≈ 271 N (continu) | 0.010 m | 0.98 (roulement) | 271 × 0.010 / 0.07 ≈ 38 N | 5 doigts × 38 N × cos 25° ≈ 172 N |
| **XC430 + poulie Ø12 mm (hist.)** | 0.006 | 1.9 Nm / 0.006 ≈ 317 N | 0.010 m | 0.98 | 44 N | 200 N (pic) |
| **XC330 + poulie Ø14 mm** | 0.007 | 1.0 Nm / 0.007 ≈ 143 N | 0.010 m | 0.98 | 20 N | 90 N (précision) |

> **Force de grip nominal** ≈ **172 N** (≈ 17 kg f) – dépasse la cible « Tesla Optimus ≈ 150 N ».  

---  

## 3. Nomenclature (BOM Locale)  

### 3.1 Boîte à outils – Main D‑Hand (par main)

| Référence | Description | Qté | Prix [€] (unité) | Total [€] | Fournisseur / Source |
|-----------|-------------|-----|-------------------|-----------|----------------------|
| **M1** | Dynamixel XC430‑W240‑T (Force) | 4 | 130 € | 520 € | ROBOTIS‑EU |
| **M2** | Dynamixel XC330‑T288‑T (Précision) | 4 | 110 € | 440 € | ROBOTIS‑EU |
| **U2** | U2D2 (USB ↔ Dynamixel) | 1 | 35 € | 35 € | ROBOTIS‑EU |
| **UH** | U2D2 Power Hub (bus + alimentation) | 1 | 25 € | 25 € | ROBOTIS‑EU |
| **BC** | Buck‑converter 48 V → 12 V, 10 A (Pololu D24V90F12) | 1 | 15 € | 15 € | Pololu |
| **DY** | Dyneema tendon Ø0.60 mm (bobine ≈ 50 m) | 1 | 15 € | 15 € | Dyneema |
| **PT** | Tube PTFE Ø1.5 mm (10 m) | 1 | 8 € | 8 € | McMaster‑Carr |
| **MR** | Roulement MR84ZZ (4×8×3 mm) | 35 | 1 € | 35 € | SKF |
| **PU** | Poulie CNC Ø14 mm Al 7075‑T6 (intégrée MR84ZZ) | 8 | 5 € | 40 € | Usinage interne C500 |
| **VS** | Visserie M2/M2.5 inox (lot) | 1 | — | 10 € | Local |
| **EF** | eFlesh 3‑axes (capteur tactile) – PCB + aimant + silicone | 5 (un par doigt) | 35 € | 175 € | eFlesh (open‑source) |
| **SK** | Silicone EcoFlex 00‑30 (kit ≈ 500 g) | 1 | 20 € | 20 € | Smooth‑On |
| **PA** | PA12‑CF (impression phalanges) – 1 kg | 1 | 30 € | 30 € | Imprimante Qidi Plus 4 |
| **AL** | Aluminium 6061‑T6 (brackets, inserts) – usinage CNC | – | 40 € | 40 € | Usinage interne C500 |
| **CF** | Tube carbone humérus Ø35 mm, épaisseur 1.5 mm | – | 120 € | 120 € | Composite‑Works |
| **CF** | Tube carbone avant‑bras Ø25 mm, épaisseur 1.5 mm | – | 80 € | 80 € | Composite‑Works |
| **TOTAL / main** | – | – | – | **≈ 1 313 €** | – |

> **[À COMPLÉTER]** – Prix exact des tubes carbone (fournisseur final à confirmer).  

### 3.2 Boîte à outils – Bras (par bras)

| Référence | Description | Qté | Prix [€] | Total [€] | Fournisseur |
|-----------|-------------|-----|----------|-----------|-------------|
| **RS‑04** | RobStride RS‑04 (Pitch) | 1 | 300 € | 300 € | RobStride |
| **RS‑03** | RobStride RS‑03 (Roll) | 1 | 250 € | 250 € | RobStride |
| **RS‑02** | RobStride RS‑02 (Yaw) | 1 | 170 € | 170 € | RobStride |
| **RS‑06** | RobStride RS‑06 (Coude Pitch) | 1 | 260 € | 260 € | RobStride |
| **RS‑00‑Roll** | RobStride RS‑00 (Poignet Roll) | 1 | 135 € | 135 € | RobStride |
| **RS‑00‑Pitch** *(Option B)* | RobStride RS‑00 (Poignet Pitch) | 1 | 135 € | 135 € | RobStride |
| **BR‑1** | Bracket #1 (Pitch → Roll) – Al 6061‑T6 | 1 | 20 € | 20 € | CNC C500 |
| **BR‑2** | Bracket #2 (Roll → Yaw) – Al 6061‑T6 | 1 | 12 € | 12 € | CNC C500 |
| **CF‑H** | Tube carbone humérus (Ø35 mm) | 1 | 120 € | 120 € | Composite‑Works |
| **CF‑F** | Tube carbone avant‑bras (Ø25 mm) | 1 | 80 € | 80 € | Composite‑Works |
| **TOTAL / bras** | – | – | – | **≈ 1 642 €** | – |

> **[À COMPLÉTER]** – Confirmation du prix exact du tube carbone (lot ≥ 2 m).  

---  

## 4. État de la Conception (CAD & Simulation)

| Élément | Statut CAD (Fusion 360) | Fichier(s) | Simulation (Isaac Gym) | Commentaires |
|--------|------------------------|------------|------------------------|--------------|
| **Humérus (tube carbone)** | ✔ Modèle complet, inserts CNC | `humérus_v1.step` | ✔ Rigid‑body, validation du couple d’inertie | Masses calculées ≈ 0.88 kg |
| **Avant‑bras (tube carbone)** | ✔ Modèle complet, inserts CNC | `avantbras_v1.step` | ✔ Rigid‑body, test de rotation supination | Masses ≈ 0.55 kg |
| **Brackets épaule** | ✔ Usinage 2‑axes, tolérance ± 0.02 mm | `bracket1_v1.step`, `bracket2_v1.step` | – | Prêt pour CNC C500 |
| **Poignet (Roll + Pitch)** | ✔ Assemblage RS‑00 Roll + RS‑00 Pitch (Option B) | `poignet_v1.step` | ✔ Joint‑space IK, validation du workspace | Poignet total ≈ 114 mm de longueur |
| **Main – D‑Hand Hybrid** | ✔ Modèle ORCA phalanxes (importées) + poulies CNC | `hand_orca_v1.step` | ✔ URDF/MJCF généré, tests de grip (Isaac Gym) | Tendons routés selon guide ORCA (Ashley Stopper) |
| **Capteurs eFlesh** | ✔ Modèle 3‑axes (STL) | `eflesh_finger_v1.stl` | – | À insérer sous la peau silicone |
| **Peau silicone** | – | – | – | Procédure de moulage décrite dans la source ORCA (EcoFlex 00‑30) |
| **Simulation globale du bras** | – | – | En cours (v0.9) | Intégration du nouveau poignet Pitch prévue Q3 2026 |

---  

## 5. Instructions de Montage Critiques  

> **Toutes les étapes suivantes supposent que les pièces sont propres, dépourvues de poussière et que les surfaces d’assemblage sont légèrement poncées (grain 120) avant collage.**  

### 5.1 Assemblage des tubes carbone (humérus & avant‑bras)  
1. **Pré‑perçage** des inserts aluminium (Ø3 mm) à l’extrémité du tube (longueur ≈ 30 mm).  
2. **Application** d’une couche d’époxy bi‑composant (DP490) sur la surface intérieure du tube et sur l’insert.  
3. **Insertion** de l’insert, puis **vissage** de la goupille Mécanindus (Ø3 mm) à travers l’insert et le tube (pas de serrage excessif < 30 N·mm).  
4. **Cure** 24 h à 25 °C avant toute manipulation.  

### 5.2 Montage des brackets d’épaule (RS‑04 → RS‑03 → RS‑02)  
1. Aligner le **stator RS‑04** (fixé au torse) avec le **rotor RS‑03** (Pitch → Roll).  
2. Fixer le **Bracket #1** (aluminium 6061‑T6) à l’aide de vis M4×12 mm (12 mm d’engagement).  
3. Répéter l’opération pour le **Bracket #2** (Roll → Yaw).  
4. Vérifier le **déplacement inter‑axe** < 30 mm (cible ≤ 25 mm).  

### 5.3 Installation du poignet (Roll + Pitch) – Option B (V1.1)  
1. **Fixer** le RS‑00 Roll à l’extrémité distale de l’avant‑bras (via bride M4).  
2. **Monter** le RS‑00 Pitch **en série** derrière le Roll (axe commun, même filetage).  
3. **Insérer** la **poulie Ø14 mm** (avec roulement MR84ZZ) sur l’arbre du RS‑00 Pitch.  
4. **Serrer** la vis de fixation du tendon (M1.6 × 8 mm) à 0.8 Nm.  

### 5.4 Routage des tendons (Dyneema Ø0.60 mm) – Méthode ORCA  
1. **Couper** chaque tendon à **≈ 0.5 m**.  
2. **Réaliser** un **nœud Ashley Stopper** à chaque extrémité (voir guide ORCA, étapes 00‑07).  
3. **Passer** le tendon à travers le **tube PTFE** (Ø1.5 mm) depuis l’avant‑bras jusqu’à la paume.  
4. **Enrouler** le tendon sur la **poulie CNC** (1 – 1.5 tour) puis **bloquer** avec la vis de serrage.  
5. **Vérifier** la mobilité de chaque doigt (pas de frottement > 0.2 N).  

### 5.5 Pose de la peau en silicone (EcoFlex 00‑30)  
1. **Imprimer** les moules négatifs (ORCA_Molds.zip).  
2. **Mélanger** le silicone 1 : 1 (partie A / partie B) et **dé‑gazer** 4 h.  
3. **Verser** dans les moules, laisser **polymériser 4 h** à 22 °C.  
4. **Démouler** délicatement, **positionner** les capteurs eFlesh sous la peau, puis **coller** les deux moitiés de la peau avec un film de silicone.  

### 5.6 Calibration logicielle (ROS 2 Humid)  
```bash
# Calibration des tensions des tendons (script officiel)
uv run python scripts/tension.py dhand_hybrid/models/dhand_right
uv run python scripts/calibrate.py dhand_hybrid/models/dhand_right
```
- Vérifier que chaque doigt atteint **0 %** (ouvert) et **100 %** (fermé) sans dépassement de courant.  
- Ajuster les **gains de courant** (mode #5) pour obtenir une **compliance** de 0.5 Nm/A.  

---  

## 6. Backlog Technique & Questions en Suspens  

| # | Sujet | Description | Priorité | Action requise |
|---|-------|-------------|----------|----------------|
| **B‑1** | **Alimentation du poignet Pitch** | Le buck‑converter 48 V → 12 V doit être intégré dans les 18 mm restants de l’avant‑bras. Vérifier la dissipation thermique (≈ 3 W en charge). | Haute | Procéder à un test thermique (thermocouple) pendant un cycle de grip continu (5 min). |
| **B‑2** | **Slip‑Ring ou boucle de service** | Le coude‑supination (RS‑02) entraîne la rotation de l’avant‑bras. Un **slip‑ring** est recommandé pour éviter le torsion du câble d’alimentation. | Moyenne | Étudier les options (slip‑ring 48 V/12 V, 2 A) vs boucle de service en PTFE. |
| **B‑3** | **Facteur de sécurité du câble Dyneema** | Le câble Ø0.60 mm a un facteur de sécurité de **×2.02** avec la poulie Ø14 mm. Confirmation requise pour les charges > 5 kg (ex. outil de chantier). | Moyenne | Réaliser un test de rupture à 10 kg pour valider le facteur de sécurité. |
| **B‑4** | **Intégration eFlesh 3‑axes** | Positionnement exact sous la pulpe sans interférer avec la flexion maximale. | Haute | Prototyper un doigt avec eFlesh, mesurer le jeu (max 0.2 mm). |
| **B‑5** | **Allongement de l’avant‑bras (Option C)** | Étudier l’impact d’un allongement de +20 mm sur la dynamique du bras (inertie, consommation). | Faible | Simuler dans Isaac Gym (modèle `dhand_v1_extended`). |
| **B‑6** | **Routage du bus CAN à travers le coude** | Le câble CAN doit traverser la zone de supination sans créer de contraintes. | Moyenne | Concevoir un conduit en PTFE (Ø3 mm) avec boucle de service. |
| **B‑7** | **Évaluation du poids total** | Poids actuel estimé ≈ 40 kg ± 0.5 kg. Vérifier la conformité avec la charge utile maximale (10 kg). | Haute | Mesure physique du prototype complet. |
| **B‑8** | **Compatibilité ROS 2 Humid** | Vérifier que le nouveau poignet Pitch (RS‑00) est correctement exposé via le driver `robstride_driver` (CAN). | Haute | Ajouter le nouveau joint dans le fichier `joint.yaml` et tester la commande `ros2 control`. |

---  

## 7. Roadmap & Itérations Futures (Optionnel)

| Version | Nouveaux DOF / Modifications | Objectif principal | Impact estimé |
|---------|------------------------------|--------------------|---------------|
| **V2** | Ajout du **Yaw** au poignet (RS‑00 Yaw) + redistribution du **Yaw d’épaule** vers le **Coude Supination** (architecture « Tesla‑like ») | Poignet 3 DOF, esthétique « tuyau » éliminée, meilleure cinématique d’in‑hand manipulation. | + ≈ 300 g (moteur supplémentaire) ; + ≈ 5 % de consommation en posture de supination. |
| **V3** | Remplacement des **XC330** par **XL330‑M288‑T** (câble 0.5 mm) pour réduire le poids des doigts (‑ 150 g) – **upgrade drop‑in** possible. | Allègement du bras, amélioration du bruit (30 dB). | Nécessite recalibration du gain de couple. |
| **V4** | Intégration d’un **capteur de force** (F/T) à la base du poignet (type **ATI Mini45**) pour contrôle d’impédance avancé. | Contrôle d’impédance complet, interaction sûre avec humains. | + ≈ 120 g, + ≈ 2 W consommation. |
| **V5** | Passage à une **structure en composite monocoque** (impression 3D en CF‑PA12) pour l’ensemble du bras, afin de réduire l’inertie de 12 %. | Optimisation globale du poids, amélioration du facteur de charge dynamique. | Redesign complet du CAD, validation structurale. |

---  

## 8. Annexes  

### 8.1 Références des sources utilisées  

| Source | Contenu clé | Date |
|--------|-------------|------|
| `FINAL_Montage_Doigts_ORCA.md` | Guide complet de routage des tendons, nœud Ashley Stopper, peau silicone, poulies en aluminium, calibrage. | Mars 2026 |
| `STUDY_Comparatif_Moteurs_Poignet.md` | Comparaison RS‑00 vs XC430, recommandation du RS‑00 pour le poignet. | Mars 2026 |
| `STUDY_Epaule_Architecture.md` | Architecture épaule (RS‑03/RS‑04/RS‑02), empilement, masses. | Mars 2026 |
| `STUDY_Main_D_Hand.md` | Architecture D‑Hand Hybrid (4 × XC430 + 4 × XC330), choix des servos, capteurs tactiles, simulation. | Mars 2026 |
| `STUDY_Poignet_DOF.md` | Analyse des DOF du poignet, recommandation d’ajout du Pitch. | Mai 2026 |
| `STUDY_Poignet_Optimus.md` | Architecture biomimétique de Tesla Optimus (Supination au coude). | Mai 2026 |
| `STUDY_Structure_Bras_Carbone.md` | Utilisation de tubes carbone, inserts aluminium, goupilles Mécanindus. | Mars 2026 |
| `STUDY_Poignet_D_Bot.md` | Analyse de l’impact du RS‑00 Pitch sur l’inertie et le portage. | Mai 2026 |
| `STUDY_Poignet_Optimus.md` | Détails sur la supination au coude et le poignet 2 DOF. | Mai 2026 |
| `STUDY_Poignet_Optimus.md` | (duplicate – same as above) | – |
| `STUDY_Poignet_D_Bot.md` | (duplicate – same as above) | – |

---  

**Fin du document**. Toutes les valeurs présentées sont issues des sources listées ci‑dessus. En cas de contradiction, la source la plus récente a prévalu. Les champs marqués **[À COMPLÉTER]** indiquent les informations manquantes qui devront être obtenues avant la validation finale du module.
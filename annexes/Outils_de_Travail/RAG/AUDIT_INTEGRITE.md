# 🛡️ Dossier d'Audit d'Intégrité D-Bot [Scope: cinematique_moteurs]
> **Date de génération** : 2026-10-18 09:15:50
> **Mode d'intelligence** : `antigravity`

## 2. Cinématique (Moteurs par Axe) [Analyse par l'Agent Antigravity]
> **Consigne pour l'Agent Antigravity** : Analyse ce corpus multi-sources extrait de la documentation. Identifie les divergences et contradictions (masses, cotes, références moteurs, bus CAN). Cite les fichiers sources qui se contredisent et génère les questions d'arbitrage au format '**Question :** ...'.

### Données Multi-Fichiers Extraites du RAG (20 sources candidates) :

**[Extrait 1: AUDIT_INTEGRITE.md]**
```text
sources suivants présentent des valeurs divergentes pour le nombre de moteurs RobStride alloués aux jambes :
- 04_Electronique_Cablage.md
- annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md
- 14_Cinematique_Moteurs.md

**Question :** Le décompte de 12 moteurs pour les jambes (6 par jambe) est-il correct, ou faut-il ajuster ce nombre pour refléter l'architecture F-A-R à la hanche et les actionneurs de la cheville (ce qui pourrait porter le total à 14 ou 16 moteurs RobStride pour les jambes) ?

### References

- [1] annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md
- [2] 01_Synthese_Projet.md
- [3] 14_Cinematique_Moteurs.md
- [4] 04_Electronique_Cablage.md
- [5] 15_Analyse_Biomecanique.md

---

## 2. Cinématique (Moteurs par Axe)
### Vérification de la cohérence des modèles de moteurs par articulation

J'ai analysé l'ensemble du Knowledge Graph et des Document Chunks fournis pour valider les modèles de moteurs associés à chaque articulation (Épaule, Coude, Poignet, Hanche, Genou, Cheville), identifier les contradictions et signaler les anciens modèles encore présents.

---

#### Épaule (Shoulder)
Aucun modèle de moteur spécifique n'est explicitement associé à l'épaule dans les documents consultés. Les servomoteurs RS-02, RS-03, RS-04 et RS-06 sont mentionnés comme utilisés dans les membres (limbs) du robot, mais aucune attribution claire à l'épaule n'est faite.

---

#### Coude (Elbow)
Le modèle **RS-06** (version 0.6.0.11) est cohérentment identifié comme le moteur de pitch du coude dans le document `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`. Ce modèle bénéficie de mises à jour en Avril 2026 (planificateur de vitesse adaptatif, remontées d'erreurs CANopen exclusives) et ne présente aucune contradiction documentaire.

---

#### Poignet (Wrist)
Le modèle **RS-00** est listé comme moteur de pitch du poignet dans `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`. Cependant, ce modèle n'est pas inclus dans les mises à jour de moteurs d'Avril 2026, et une référence à l'ancienne révision RS00.27 est faite dans les notes de mise à jour. L'entité Sn du Knowledge Graph mentionne également que les RS-00 sont destinés aux poignets, mais ce modèle semble être une version ancienne par rapport aux gammes RS-03 (v0.3.1.41), RS-04 (v0.4.1.29), RS-05 (v0.5.0.13) et RS-06 (v0.6.0.11) qui bénéficient de mises à jour régulières.

Fichiers sources en contradiction :
- `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`
- Notes de mise à jour des moteurs Avril 2026 (chunk sans nom de fichier, contenu débutant par "sur les bras/cuisses.\n\n### RS03 Actuel (v0.3.1.41)...")
- Knowledge Graph (entité Sn)

**Question :** Le moteur RS-00 (révision 0.0.27) est-il toujours le modèle actuel pour le poignet (Poignet Pitch) malgré l'absence de mises à jour dans les notes de version Avril 2026, ou doit-il être remplacé par un modèle plus récent ?

---

#### Hanche (Hip)
Les modèles **RS-04** (pitch, version 0.4.1.29) et **RS-03** (roll et yaw, version 0.3.1.41) sont cohérents entre tous les documents consultés. L'architecture F-A-R (Pitch→Roll→Yaw) adoptée en Avril 2026 référence explicitement ces modèles, qui bénéficient tous deux de mises à jour fonctionnelles en Avril 2026. Aucune contradiction n'est identifiée.

---

#### Genou (Knee)
Le modèle **RS-04** est associé au vilebrequin de la transmission GT3 du genou dans les chunks de leviers biomécaniques, ce qui est cohérent avec la documentation `15d_Genou_et_Course.md` référencée dans `15_Analyse_Biomecanique.md`. Les modèles RS-02, RS-03 et RS-06 sont listés uniquement comme alternatives de mise à niveau dans `15e_Alternatives_Moteurs_Genou.md`, sans contradiction avec l'usage actuel du RS-04.

---

#### Cheville (Ankle)
Le modèle **RS-03** (2 unités) est associé à l'architecture de cheville cardan dans `15c_Revision_Cardan_39kg.md` (référencé dans `15_Analyse_Biomecanique.md`). Ce modèle bénéficie de mises à jour en Avril 2026, et aucune contradiction n'est identifiée.

---

#### Incohérence supplémentaire : Attribution du RS-05 (Cou vs Poignet)
L'entité Sn du Knowledge Graph mentionne que les RS-05 sont destinés aux poignets et au cou, mais l'entité Rs05 du Knowledge Graph et le document `32_Configuration_ID_Limites_Cou.md` restre
```

**[Extrait 2: unknown_source]**
```text
moteurs RobStride alloués aux jambes :
- 04_Electronique_Cablage.md
- annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md
- 14_Cinematique_Moteurs.md

**Question :** Le décompte de 12 moteurs pour les jambes (6 par jambe) est-il correct, ou faut-il ajuster ce nombre pour refléter l'architecture F-A-R à la hanche et les actionneurs de la cheville (ce qui pourrait porter le total à 14 ou 16 moteurs RobStride pour les jambes) ?

### References

- [1] annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md
- [2] 01_Synthese_Projet.md
- [3] 14_Cinematique_Moteurs.md
- [4] 04_Electronique_Cablage.md
- [5] 15_Analyse_Biomecanique.md

---

## 2. Cinématique (Moteurs par Axe)
### Vérification de la cohérence des modèles de moteurs par articulation

J'ai analysé l'ensemble du Knowledge Graph et des Document Chunks fournis pour valider les modèles de moteurs associés à chaque articulation (Épaule, Coude, Poignet, Hanche, Genou, Cheville), identifier les contradictions et signaler les anciens modèles encore présents.

---

#### Épaule (Shoulder)
Aucun modèle de moteur spécifique n'est explicitement associé à l'épaule dans les documents consultés. Les servomoteurs RS-02, RS-03, RS-04 et RS-06 sont mentionnés comme utilisés dans les membres (limbs) du robot, mais aucune attribution claire à l'épaule n'est faite.

---

#### Coude (Elbow)
Le modèle **RS-06** (version 0.6.0.11) est cohérentment identifié comme le moteur de pitch du coude dans le document `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`. Ce modèle bénéficie de mises à jour en Avril 2026 (planificateur de vitesse adaptatif, remontées d'erreurs CANopen exclusives) et ne présente aucune contradiction documentaire.

---

#### Poignet (Wrist)
Le modèle **RS-00** est listé comme moteur de pitch du poignet dans `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`. Cependant, ce modèle n'est pas inclus dans les mises à jour de moteurs d'Avril 2026, et une référence à l'ancienne révision RS00.27 est faite dans les notes de mise à jour. L'entité Sn du Knowledge Graph mentionne également que les RS-00 sont destinés aux poignets, mais ce modèle semble être une version ancienne par rapport aux gammes RS-03 (v0.3.1.41), RS-04 (v0.4.1.29), RS-05 (v0.5.0.13) et RS-06 (v0.6.0.11) qui bénéficient de mises à jour régulières.

Fichiers sources en contradiction :
- `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`
- Notes de mise à jour des moteurs Avril 2026 (chunk sans nom de fichier, contenu débutant par "sur les bras/cuisses.\n\n### RS03 Actuel (v0.3.1.41)...")
- Knowledge Graph (entité Sn)

**Question :** Le moteur RS-00 (révision 0.0.27) est-il toujours le modèle actuel pour le poignet (Poignet Pitch) malgré l'absence de mises à jour dans les notes de version Avril 2026, ou doit-il être remplacé par un modèle plus récent ?

---

#### Hanche (Hip)
Les modèles **RS-04** (pitch, version 0.4.1.29) et **RS-03** (roll et yaw, version 0.3.1.41) sont cohérents entre tous les documents consultés. L'architecture F-A-R (Pitch→Roll→Yaw) adoptée en Avril 2026 référence explicitement ces modèles, qui bénéficient tous deux de mises à jour fonctionnelles en Avril 2026. Aucune contradiction n'est identifiée.

---

#### Genou (Knee)
Le modèle **RS-04** est associé au vilebrequin de la transmission GT3 du genou dans les chunks de leviers biomécaniques, ce qui est cohérent avec la documentation `15d_Genou_et_Course.md` référencée dans `15_Analyse_Biomecanique.md`. Les modèles RS-02, RS-03 et RS-06 sont listés uniquement comme alternatives de mise à niveau dans `15e_Alternatives_Moteurs_Genou.md`, sans contradiction avec l'usage actuel du RS-04.

---

#### Cheville (Ankle)
Le modèle **RS-03** (2 unités) est associé à l'architecture de cheville cardan dans `15c_Revision_Cardan_39kg.md` (référencé dans `15_Analyse_Biomecanique.md`). Ce modèle bénéficie de mises à jour en Avril 2026, et aucune contradiction n'est identifiée.

---

#### Incohérence supplémentaire : Attribution du RS-05 (Cou vs Poignet)
L'entité Sn du Knowledge Graph mentionne que les RS-05 sont destinés aux poignets et au cou, mais l'entité Rs05 du Knowledge Graph et le document `32_Configuration_ID_Limites_Cou.md` restreignent l'usage du RS-05 au cou (
```

**[Extrait 3: unknown_source]**
```text
moteurs RobStride alloués aux jambes :
- 04_Electronique_Cablage.md
- annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md
- 14_Cinematique_Moteurs.md

**Question :** Le décompte de 12 moteurs pour les jambes (6 par jambe) est-il correct, ou faut-il ajuster ce nombre pour refléter l'architecture F-A-R à la hanche et les actionneurs de la cheville (ce qui pourrait porter le total à 14 ou 16 moteurs RobStride pour les jambes) ?

### References

- [1] annexes/Outils_de_Travail/RAG/AUDIT_INTEGRITE.md
- [2] 01_Synthese_Projet.md
- [3] 14_Cinematique_Moteurs.md
- [4] 04_Electronique_Cablage.md
- [5] 15_Analyse_Biomecanique.md

---

## 2. Cinématique (Moteurs par Axe)
### Vérification de la cohérence des modèles de moteurs par articulation

J'ai analysé l'ensemble du Knowledge Graph et des Document Chunks fournis pour valider les modèles de moteurs associés à chaque articulation (Épaule, Coude, Poignet, Hanche, Genou, Cheville), identifier les contradictions et signaler les anciens modèles encore présents.

---

#### Épaule (Shoulder)
Aucun modèle de moteur spécifique n'est explicitement associé à l'épaule dans les documents consultés. Les servomoteurs RS-02, RS-03, RS-04 et RS-06 sont mentionnés comme utilisés dans les membres (limbs) du robot, mais aucune attribution claire à l'épaule n'est faite.

---

#### Coude (Elbow)
Le modèle **RS-06** (version 0.6.0.11) est cohérentment identifié comme le moteur de pitch du coude dans le document `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`. Ce modèle bénéficie de mises à jour en Avril 2026 (planificateur de vitesse adaptatif, remontées d'erreurs CANopen exclusives) et ne présente aucune contradiction documentaire.

---

#### Poignet (Wrist)
Le modèle **RS-00** est listé comme moteur de pitch du poignet dans `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`. Cependant, ce modèle n'est pas inclus dans les mises à jour de moteurs d'Avril 2026, et une référence à l'ancienne révision RS00.27 est faite dans les notes de mise à jour. L'entité Sn du Knowledge Graph mentionne également que les RS-00 sont destinés aux poignets, mais ce modèle semble être une version ancienne par rapport aux gammes RS-03 (v0.3.1.41), RS-04 (v0.4.1.29), RS-05 (v0.5.0.13) et RS-06 (v0.6.0.11) qui bénéficient de mises à jour régulières.

Fichiers sources en contradiction :
- `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`
- Notes de mise à jour des moteurs Avril 2026 (chunk sans nom de fichier, contenu débutant par "sur les bras/cuisses.\n\n### RS03 Actuel (v0.3.1.41)...")
- Knowledge Graph (entité Sn)

**Question :** Le moteur RS-00 (révision 0.0.27) est-il toujours le modèle actuel pour le poignet (Poignet Pitch) malgré l'absence de mises à jour dans les notes de version Avril 2026, ou doit-il être remplacé par un modèle plus récent ?

---

#### Hanche (Hip)
Les modèles **RS-04** (pitch, version 0.4.1.29) et **RS-03** (roll et yaw, version 0.3.1.41) sont cohérents entre tous les documents consultés. L'architecture F-A-R (Pitch→Roll→Yaw) adoptée en Avril 2026 référence explicitement ces modèles, qui bénéficient tous deux de mises à jour fonctionnelles en Avril 2026. Aucune contradiction n'est identifiée.

---

#### Genou (Knee)
Le modèle **RS-04** est associé au vilebrequin de la transmission GT3 du genou dans les chunks de leviers biomécaniques, ce qui est cohérent avec la documentation `15d_Genou_et_Course.md` référencée dans `15_Analyse_Biomecanique.md`. Les modèles RS-02, RS-03 et RS-06 sont listés uniquement comme alternatives de mise à niveau dans `15e_Alternatives_Moteurs_Genou.md`, sans contradiction avec l'usage actuel du RS-04.

---

#### Cheville (Ankle)
Le modèle **RS-03** (2 unités) est associé à l'architecture de cheville cardan dans `15c_Revision_Cardan_39kg.md` (référencé dans `15_Analyse_Biomecanique.md`). Ce modèle bénéficie de mises à jour en Avril 2026, et aucune contradiction n'est identifiée.

---

#### Incohérence supplémentaire : Attribution du RS-05 (Cou vs Poignet)
L'entité Sn du Knowledge Graph mentionne que les RS-05 sont destinés aux poignets et au cou, mais l'entité Rs05 du Knowledge Graph et le document `32_Configuration_ID_Limites_Cou.md` restreignent l'usage du RS-05 au cou (
```

**[Extrait 4: STUDY_Analyse_Biomecanique.md]**
```text
---
Fichier: 01_Mecanique_et_Chassis/Jambes_et_Pieds/STUDY_Analyse_Biomecanique.md
Projet: D-Bot
---

# 15 — Analyse Biomécanique D-Bot (Hub)

Cette section a été restructurée pour plus de clarté. Le contenu est désormais réparti en **4 documents spécialisés** et un **document de conclusions**.

---


## 📑 Sommaire

- [**Navigation**](#navigation)
- [**Logique de Lecture Recommandée**](#logique-de-lecture-recommandée)

---

## Navigation

| # | Document | Contenu | Lignes |
| :---: | :--- | :--- | :---: |
| **15a** | [Locomotion & Portage (Baseline K-Bot)](./15a_Analyse_Locomotion_Baseline.md) | Paramètres physiques, couples requis marche/course/portage, faiblesses initiales | ~200 |
| **15b** | [Configurations Moteurs & Évolutions](./15b_Configurations_Moteurs.md) | Options A/B/C/D, comparatifs, DOF Roll, stabilité, capteurs FSR, algorithmes | ~900 |
| **15c** | [Révision Cardan 40.2 kg](Jambes_et_Pieds/STUDY_Revision_Cardan.md) | Recalcul complet avec masse 40.2 kg et architecture cheville cardan 2×RS-03 | ~200 |
| **15d** | [Genou — Analyse & Solution GT3](Jambes_et_Pieds/STUDY_Genou_Cinematique.md) | **Document principal genou (fusionné 15d+15g)** — S1 à S5 explorées, S6 (GT3 2.5:1, 300 N.m) retenue, compatibilité F-A-R hanche validée | ~300 |
| **15e** | [Alternatives Moteurs Genou](./15e_Alternatives_Moteurs_Genou.md) | Comparatif RS-02, RS-03, RS-06 pour upgrades | ~150 |
| **15g** | [→ Redirection vers 15d](Jambes_et_Pieds/STUDY_Courroie_GT3_Genou.md) | Contenu fusionné dans 15d (Avril 2026) | — |
| **15h** | [Alternatives Transmission Genou](./15h_Alternatives_Transmission_Genou.md) | Archive des débats Vérins Linéaires vs Chaîne vs Courroie vs Pivots Variables | ~70 |
| **16** | [**Conclusions & Architecture Finale D-Bot**](../00_Architecture_Centrale/FINAL_Architecture_Globale.md) | **Décisions finales par articulation. Lire en premier.** | ~100 |

---

## Logique de Lecture Recommandée

```
Nouveau lecteur :
  → 16_Conclusions  (résumé décisions)
  → 15c (recalcul définitif 40.2 kg)
  → 15d (course et genou)

Analyse historique :
  → 15a (baseline K-Bot)
  → 15b (toutes les options étudiées)

Ingénierie détaillée :
  → 15b §7-10 (configurations finales, capteurs)
  → 15d §12.3.1 (cinématique tirant genou)
```

---

*Document restructuré en Mars 2026 — contenu complet dans les 4 sous-documents ci-dessus.*
```

**[Extrait 5: STUDY_Bloc_Pelvien_Hanche.md]**
```text
---
Fichier: 01_Mecanique_et_Chassis/Jambes_et_Pieds/STUDY_Bloc_Pelvien_Hanche.md
Projet: D-Bot
---

# 26 — Étude : Architecture du Bloc Pelvien (Cardan de Hanche)

Suite à la définition du "Fémur Hybride" (qui se connecte en sandwich au dernier moteur de la jambe), il est indispensable d'étudier ce qui se passe *au-dessus* du fémur : le fameux **"Bloc de Hanche" à 3 degrés de liberté (DOF)**.

L'**Addendum 11 de la page 15b** montrait l'architecture historique du K-Bot. Comment cette architecture se compare-t-elle aux standards actuels de l'industrie (Tesla Optimus, Unitree G1/H1, Agility Digit) et comment devons-nous concevoir celle du D-Bot ?

---


## 📑 Sommaire

- [**1. La Problématique des Moteurs QDD (Quasi-Direct Drive)**](#1-la-problématique-des-moteurs-qdd-quasi-direct-drive)
- [**2. Benchmark de l'Industrie**](#2-benchmark-de-lindustrie)
  - [A. L'approche K-Bot Originale](#a-lapproche-k-bot-originale)
  - [B. L'approche Tesla Optimus : séquentielle A-R-F](#b-lapproche-tesla-optimus-séquentielle-a-r-f)
  - [C. L'approche Unitree H1 / H1-2 : Sphérique (Grappe Concentrée)](#c-lapproche-unitree-h1-h1-2-sphérique-grappe-concentrée)
  - [D. L'approche Gen2 (Figure 02, Unitree G1) : F-A-R](#d-lapproche-gen2-figure-02-unitree-g1-f-a-r)
- [**3. L'Architecture D-Bot : Chaîne F-A-R (Méthode Gen2)**](#3-larchitecture-d-bot-chaîne-f-a-r-méthode-gen2)
  - [Maillon 1 : L'Axe Pitch (Moteur RS-04)](#maillon-1-laxe-pitch-moteur-rs-04)
  - [Maillon 2 : L'Axe Roll (Moteur RS-03)](#maillon-2-laxe-roll-moteur-rs-03)
  - [Maillon 3 : L'Axe Yaw (Moteur RS-03)](#maillon-3-laxe-yaw-moteur-rs-03)
  - [Le Bout de la Chaîne : Le Fémur Hybride](#le-bout-de-la-chaîne-le-fémur-hybride)
- [**4. Analyse des Marges de Couple en F-A-R**](#4-analyse-des-marges-de-couple-en-f-a-r)
- [**5. Étude Option GT3 Hip Pitch — Analyse et Rejet**](#5-étude-option-gt3-hip-pitch-analyse-et-rejet)
  - [Principe étudié](#principe-étudié)
  - [Avantages identifiés](#avantages-identifiés)
  - [Raisons du rejet](#raisons-du-rejet)
- [**6. Conséquences pour l'Ingénierie (Usinage C500)**](#6-conséquences-pour-lingénierie-usinage-c500)

---

## 1. La Problématique des Moteurs QDD (Quasi-Direct Drive)

Dans le corps humain, la hanche est une articulation sphérique parfaite : les 3 axes de rotation (Yaw, Roll, Pitch) se croisent exactement au même point x,y,z (le centre de la tête du fémur).

En robotique basée sur des actionneurs cylindriques massifs (les moteurs QDD type RS-03/RS-04), **deux moteurs physiques ne peuvent pas occuper le même espace au même moment**. 
Il est donc géométriquement impossible d'avoir une vraie liaison sphérique concourante. L'industrie résout ce problème en séparant les axes et en *empilant* les moteurs les uns à la suite des autres via de solides équerres structurelles. C'est ce qu'on appelle la **Chaîne Cinématique (Kinematic Chain)**.

---

## 2. Benchmark de l'Industrie

### A. L'approche K-Bot Originale
Les images du K-Bot montrent une tentative de compacter les 3 moteurs dans un espace très restreint (sorte de grappe entremêlée).
- *Inconvénient majeur* : Cette conception crée souvent des collisions (auto-intersections) lors de mouvements combinés extrêmes et rend l'usinage des pièces de liaison affreusement complexe en CAO 3D.

### B. L'approche Tesla Optimus : séquentielle A-R-F

Tesla a opté pour une chaîne cinématique **A-R-F** (Abduction→Rotation→Flexion), soit Roll→Yaw→Pitch dans notre nomenclature :
1. **Maillon 1 : Roll (Abduction)** — fixé au bassin, stabilité latérale.
2. **Maillon 2 : Yaw (Rotation)** — rotation interne/externe.
3. **Maillon 3 : Pitch (Flexion)** — dans la cuisse, levée et propulsion.

![Référence du Pelvis et Bloc de Hanche Tesla Optimus](../../Assets/img_optimus_pelvis_reference.jpg
```

**[Extrait 6: unknown_source]**
```text
---
Fichier: 01_Mecanique_et_Chassis/Jambes_et_Pieds/STUDY_Analyse_Biomecanique.md
Projet: D-Bot
---

# 15 — Analyse Biomécanique D-Bot (Hub)

Cette section a été restructurée pour plus de clarté. Le contenu est désormais réparti en **4 documents spécialisés** et un **document de conclusions**.

---

## Navigation

| # | Document | Contenu | Lignes |
| :---: | :--- | :--- | :---: |
| **15a** | [Locomotion & Portage (Baseline K-Bot)](./15a_Analyse_Locomotion_Baseline.md) | Paramètres physiques, couples requis marche/course/portage, faiblesses initiales | ~200 |
| **15b** | [Configurations Moteurs & Évolutions](./15b_Configurations_Moteurs.md) | Options A/B/C/D, comparatifs, DOF Roll, stabilité, capteurs FSR, algorithmes | ~900 |
| **15c** | [Révision Cardan 40.2 kg](Jambes_et_Pieds/STUDY_Revision_Cardan.md) | Recalcul complet avec masse 40.2 kg et architecture cheville cardan 2×RS-03 | ~200 |
| **15d** | [Genou — Analyse & Solution GT3](Jambes_et_Pieds/STUDY_Genou_Cinematique.md) | **Document principal genou (fusionné 15d+15g)** — S1 à S5 explorées, S6 (GT3 2.5:1, 300 N.m) retenue, compatibilité F-A-R hanche validée | ~300 |
| **15e** | [Alternatives Moteurs Genou](./15e_Alternatives_Moteurs_Genou.md) | Comparatif RS-02, RS-03, RS-06 pour upgrades | ~150 |
| **15g** | [→ Redirection vers 15d](Jambes_et_Pieds/STUDY_Courroie_GT3_Genou.md) | Contenu fusionné dans 15d (Avril 2026) | — |
| **15h** | [Alternatives Transmission Genou](./15h_Alternatives_Transmission_Genou.md) | Archive des débats Vérins Linéaires vs Chaîne vs Courroie vs Pivots Variables | ~70 |
| **16** | [**Conclusions & Architecture Finale D-Bot**](../00_Architecture_Centrale/FINAL_Architecture_Globale.md) | **Décisions finales par articulation. Lire en premier.** | ~100 |

---

## Logique de Lecture Recommandée

```
Nouveau lecteur :
  → 16_Conclusions  (résumé décisions)
  → 15c (recalcul définitif 40.2 kg)
  → 15d (course et genou)

Analyse historique :
  → 15a (baseline K-Bot)
  → 15b (toutes les options étudiées)

Ingénierie détaillée :
  → 15b §7-10 (configurations finales, capteurs)
  → 15d §12.3.1 (cinématique tirant genou)
```

---

*Document restructuré en Mars 2026 — contenu complet dans les 4 sous-documents ci-dessus.*
```

**[Extrait 7: unknown_source]**
```text
modèle bénéficie de mises à jour en Avril 2026, et aucune contradiction n'est identifiée.

---

#### Incohérence supplémentaire : Attribution du RS-05 (Cou vs Poignet)
L'entité Sn du Knowledge Graph mentionne que les RS-05 sont destinés aux poignets et au cou, mais l'entité Rs05 du Knowledge Graph et le document `32_Configuration_ID_Limites_Cou.md` restreignent l'usage du RS-05 au cou (Neck) et aux applications Pan-Tilt. Le document `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md` confirme par ailleurs que le poignet utilise le RS-00, pas le RS-05.

Fichiers sources en contradiction :
- Knowledge Graph (entité Sn)
- Knowledge Graph (entité Rs05)
- `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`
- `32_Configuration_ID_Limites_Cou.md`

**Question :** Le moteur RS-05 est-il exclusivement réservé au cou (Neck) comme indiqué dans l'entité Rs05 et le document 32_Configuration_ID_Limites_Cou.md, ou doit-il également être utilisé pour les poignets comme mentionné dans l'entité Sn du Knowledge Graph ?

---

#### Anciens modèles encore présents
- **RS-02** : Utilisé comme moteur de supination (rotation de l'avant-bras) dans `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`. Ce modèle partage un bug (Sn bug) avec le RS-01 selon l'entité Sn, n'est pas inclus dans les mises à jour Avril 2026, et est listé uniquement comme alternative de mise à niveau pour le genou.

Fichiers sources en contradiction :
- `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`
- `15_Analyse_Biomecanique.md` (référence `15e_Alternatives_Moteurs_Genou.md`)
- Knowledge Graph (entité Sn)

**Question :** Le moteur RS-02 est-il toujours le modèle actuel pour la supination de l'avant-bras, ou doit-il être remplacé par un modèle plus récent (RS-03, RS-04, RS-06) comme suggéré par son absence des mises à jour Avril 2026 ?

---

### References

---

## 3. Électronique (Bus & Puissance)
Voici le résultat de la vérification de cohérence entre les documents de synthèse, le guide électronique (04_Electronique_Cablage.md) et les guides de test, portant sur la tension d'alimentation et le nombre de moteurs par bus CAN.

Plusieurs points sont cohérents entre les sources : les tests sur banc utilisent une tension de 24V pour les moteurs Robstride, conformément au guide de test (33_Test_Multi_Moteurs_CAN_Banc.md) et aux documents de configuration du cou. La Jetson Orin Nano est spécifiée pour recevoir une alimentation en 19V dans le guide électronique et les fiches techniques matérielles. Le système final D-Bot suit la norme de tension K-Bot de 48V (13S NMC), comme indiqué dans la synthèse et les entités de la base de connaissances. Le bus CAN fonctionne à une vitesse de 1 Mbps, partagé entre la Jetson et les 24 moteurs Robstride répartis sur 5 bus dédiés, ce qui est cohérent entre le guide électronique et les spécifications du projet.

## 1. Alimentation (Tension Batterie)

Une incohérence majeure concerne l'alimentation de la Jetson Orin Nano :
- Fichiers sources contradictoires :
  - 04_Electronique_Cablage.md indique une alimentation de 19V DC pour la Jetson.
  - Synthese_Etat_Actuel/SYNTHESE_Electronique.md indique une régulation DC-DC 48V → 5V pour la Jetson et la Spresense, incompatible avec la plage de tension de 19V requise pour la Jetson Orin Nano.

**Question :** Le document de synthèse indique une régulation 48V → 5V pour la Jetson, tandis que le guide électronique (04_Electronique_Cablage.md) et les spécifications matérielles de la Jetson Orin Nano imposent une alimentation en 19V : souhaitez-vous corriger la synthèse pour indiquer une régulation 48V → 19V pour la Jetson ?

## 2. Bus CAN (Nombre de moteurs par bus)

Première incohérence : règle de topologie du bus CAN
- Fichiers sources contradictoires :
  - 04_Electronique_Cablage.md interdit formellement toute topologie en étoile (Y) et impose une topologie en daisy-chain (série) pour tous les bus CAN.
  - Doc 42 (Guide de configuration du cou) et 33_Test_Multi_Moteurs_CAN_Banc.md imposent une topologie en étoile pour le bus du cou (moteurs RS-05), ces derniers ne disposant que d'un port CAN et ne pouvant être chaînés en série.

**Question :** Le guide électronique (04_Electronique_Cablage.md) interdit formellement toute topologie en étoile pour le bus CAN, mais les documents spécifiques au cou (Doc 42) et le guide de test (33_Test_Multi_Moteurs_CAN_Banc.md) imposent une topologie en étoile pour les moteurs RS-05 : souhaitez-vous modifier le guide électronique pour autoriser une exception de topologie en étoile pour les bus utilisant des moteurs à port
```

**[Extrait 8: unknown_source]**
```text
modèle bénéficie de mises à jour en Avril 2026, et aucune contradiction n'est identifiée.

---

#### Incohérence supplémentaire : Attribution du RS-05 (Cou vs Poignet)
L'entité Sn du Knowledge Graph mentionne que les RS-05 sont destinés aux poignets et au cou, mais l'entité Rs05 du Knowledge Graph et le document `32_Configuration_ID_Limites_Cou.md` restreignent l'usage du RS-05 au cou (Neck) et aux applications Pan-Tilt. Le document `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md` confirme par ailleurs que le poignet utilise le RS-00, pas le RS-05.

Fichiers sources en contradiction :
- Knowledge Graph (entité Sn)
- Knowledge Graph (entité Rs05)
- `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`
- `32_Configuration_ID_Limites_Cou.md`

**Question :** Le moteur RS-05 est-il exclusivement réservé au cou (Neck) comme indiqué dans l'entité Rs05 et le document 32_Configuration_ID_Limites_Cou.md, ou doit-il également être utilisé pour les poignets comme mentionné dans l'entité Sn du Knowledge Graph ?

---

#### Anciens modèles encore présents
- **RS-02** : Utilisé comme moteur de supination (rotation de l'avant-bras) dans `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`. Ce modèle partage un bug (Sn bug) avec le RS-01 selon l'entité Sn, n'est pas inclus dans les mises à jour Avril 2026, et est listé uniquement comme alternative de mise à niveau pour le genou.

Fichiers sources en contradiction :
- `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`
- `15_Analyse_Biomecanique.md` (référence `15e_Alternatives_Moteurs_Genou.md`)
- Knowledge Graph (entité Sn)

**Question :** Le moteur RS-02 est-il toujours le modèle actuel pour la supination de l'avant-bras, ou doit-il être remplacé par un modèle plus récent (RS-03, RS-04, RS-06) comme suggéré par son absence des mises à jour Avril 2026 ?

---

### References

---

## 3. Électronique (Bus & Puissance)
Voici le résultat de la vérification de cohérence entre les documents de synthèse, le guide électronique (04_Electronique_Cablage.md) et les guides de test, portant sur la tension d'alimentation et le nombre de moteurs par bus CAN.

Plusieurs points sont cohérents entre les sources : les tests sur banc utilisent une tension de 24V pour les moteurs Robstride, conformément au guide de test (33_Test_Multi_Moteurs_CAN_Banc.md) et aux documents de configuration du cou. La Jetson Orin Nano est spécifiée pour recevoir une alimentation en 19V dans le guide électronique et les fiches techniques matérielles. Le système final D-Bot suit la norme de tension K-Bot de 48V (13S NMC), comme indiqué dans la synthèse et les entités de la base de connaissances. Le bus CAN fonctionne à une vitesse de 1 Mbps, partagé entre la Jetson et les 24 moteurs Robstride répartis sur 5 bus dédiés, ce qui est cohérent entre le guide électronique et les spécifications du projet.

## 1. Alimentation (Tension Batterie)

Une incohérence majeure concerne l'alimentation de la Jetson Orin Nano :
- Fichiers sources contradictoires :
  - 04_Electronique_Cablage.md indique une alimentation de 19V DC pour la Jetson.
  - Synthese_Etat_Actuel/SYNTHESE_Electronique.md indique une régulation DC-DC 48V → 5V pour la Jetson et la Spresense, incompatible avec la plage de tension de 19V requise pour la Jetson Orin Nano.

**Question :** Le document de synthèse indique une régulation 48V → 5V pour la Jetson, tandis que le guide électronique (04_Electronique_Cablage.md) et les spécifications matérielles de la Jetson Orin Nano imposent une alimentation en 19V : souhaitez-vous corriger la synthèse pour indiquer une régulation 48V → 19V pour la Jetson ?

## 2. Bus CAN (Nombre de moteurs par bus)

Première incohérence : règle de topologie du bus CAN
- Fichiers sources contradictoires :
  - 04_Electronique_Cablage.md interdit formellement toute topologie en étoile (Y) et impose une topologie en daisy-chain (série) pour tous les bus CAN.
  - Doc 42 (Guide de configuration du cou) et 33_Test_Multi_Moteurs_CAN_Banc.md imposent une topologie en étoile pour le bus du cou (moteurs RS-05), ces derniers ne disposant que d'un port CAN et ne pouvant être chaînés en série.

**Question :** Le guide électronique (04_Electronique_Cablage.md) interdit formellement toute topologie en étoile pour le bus CAN, mais les documents spécifiques au cou (Doc 42) et le guide de test (33_Test_Multi_Moteurs_CAN_Banc.md) imposent une topologie en étoile pour les moteurs RS-05 : souhaitez-vous modifier le guide électronique pour autoriser une exception de topologie en étoile pour les bus utilisant des moteurs à port
```

**[Extrait 9: AUDIT_INTEGRITE.md]**
```text
15_Analyse_Biomecanique.md`). Ce modèle bénéficie de mises à jour en Avril 2026, et aucune contradiction n'est identifiée.

---

#### Incohérence supplémentaire : Attribution du RS-05 (Cou vs Poignet)
L'entité Sn du Knowledge Graph mentionne que les RS-05 sont destinés aux poignets et au cou, mais l'entité Rs05 du Knowledge Graph et le document `32_Configuration_ID_Limites_Cou.md` restreignent l'usage du RS-05 au cou (Neck) et aux applications Pan-Tilt. Le document `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md` confirme par ailleurs que le poignet utilise le RS-00, pas le RS-05.

Fichiers sources en contradiction :
- Knowledge Graph (entité Sn)
- Knowledge Graph (entité Rs05)
- `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`
- `32_Configuration_ID_Limites_Cou.md`

**Question :** Le moteur RS-05 est-il exclusivement réservé au cou (Neck) comme indiqué dans l'entité Rs05 et le document 32_Configuration_ID_Limites_Cou.md, ou doit-il également être utilisé pour les poignets comme mentionné dans l'entité Sn du Knowledge Graph ?

---

#### Anciens modèles encore présents
- **RS-02** : Utilisé comme moteur de supination (rotation de l'avant-bras) dans `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`. Ce modèle partage un bug (Sn bug) avec le RS-01 selon l'entité Sn, n'est pas inclus dans les mises à jour Avril 2026, et est listé uniquement comme alternative de mise à niveau pour le genou.

Fichiers sources en contradiction :
- `Synthese_Etat_Actuel/SYNTHESE_Bras_AvantBras.md`
- `15_Analyse_Biomecanique.md` (référence `15e_Alternatives_Moteurs_Genou.md`)
- Knowledge Graph (entité Sn)

**Question :** Le moteur RS-02 est-il toujours le modèle actuel pour la supination de l'avant-bras, ou doit-il être remplacé par un modèle plus récent (RS-03, RS-04, RS-06) comme suggéré par son absence des mises à jour Avril 2026 ?

---

### References

---

## 3. Électronique (Bus & Puissance)
Voici le résultat de la vérification de cohérence entre les documents de synthèse, le guide électronique (04_Electronique_Cablage.md) et les guides de test, portant sur la tension d'alimentation et le nombre de moteurs par bus CAN.

Plusieurs points sont cohérents entre les sources : les tests sur banc utilisent une tension de 24V pour les moteurs Robstride, conformément au guide de test (33_Test_Multi_Moteurs_CAN_Banc.md) et aux documents de configuration du cou. La Jetson Orin Nano est spécifiée pour recevoir une alimentation en 19V dans le guide électronique et les fiches techniques matérielles. Le système final D-Bot suit la norme de tension K-Bot de 48V (13S NMC), comme indiqué dans la synthèse et les entités de la base de connaissances. Le bus CAN fonctionne à une vitesse de 1 Mbps, partagé entre la Jetson et les 24 moteurs Robstride répartis sur 5 bus dédiés, ce qui est cohérent entre le guide électronique et les spécifications du projet.

## 1. Alimentation (Tension Batterie)

Une incohérence majeure concerne l'alimentation de la Jetson Orin Nano :
- Fichiers sources contradictoires :
  - 04_Electronique_Cablage.md indique une alimentation de 19V DC pour la Jetson.
  - Synthese_Etat_Actuel/SYNTHESE_Electronique.md indique une régulation DC-DC 48V → 5V pour la Jetson et la Spresense, incompatible avec la plage de tension de 19V requise pour la Jetson Orin Nano.

**Question :** Le document de synthèse indique une régulation 48V → 5V pour la Jetson, tandis que le guide électronique (04_Electronique_Cablage.md) et les spécifications matérielles de la Jetson Orin Nano imposent une alimentation en 19V : souhaitez-vous corriger la synthèse pour indiquer une régulation 48V → 19V pour la Jetson ?

## 2. Bus CAN (Nombre de moteurs par bus)

Première incohérence : règle de topologie du bus CAN
- Fichiers sources contradictoires :
  - 04_Electronique_Cablage.md interdit formellement toute topologie en étoile (Y) et impose une topologie en daisy-chain (série) pour tous les bus CAN.
  - Doc 42 (Guide de configuration du cou) et 33_Test_Multi_Moteurs_CAN_Banc.md imposent une topologie en étoile pour le bus du cou (moteurs RS-05), ces derniers ne disposant que d'un port CAN et ne pouvant être chaînés en série.

**Question :** Le guide électronique (04_Electronique_Cablage.md) interdit formellement toute topologie en étoile pour le bus CAN, mais les documents spécifiques au cou (Doc 42) et le guide de test (33_Test_Multi_Moteurs_CAN_Banc.md) imposent une topologie en étoile pour les moteurs RS-05 : souhaitez-vous modifier le guide électronique pour autoriser une exception de topologie
```

**[Extrait 10: unknown_source]**
```text
---
Fichier: 01_Mecanique_et_Chassis/Jambes_et_Pieds/STUDY_Bloc_Pelvien_Hanche.md
Projet: D-Bot
---

# 26 — Étude : Architecture du Bloc Pelvien (Cardan de Hanche)

Suite à la définition du "Fémur Hybride" (qui se connecte en sandwich au dernier moteur de la jambe), il est indispensable d'étudier ce qui se passe *au-dessus* du fémur : le fameux **"Bloc de Hanche" à 3 degrés de liberté (DOF)**.

L'**Addendum 11 de la page 15b** montrait l'architecture historique du K-Bot. Comment cette architecture se compare-t-elle aux standards actuels de l'industrie (Tesla Optimus, Unitree G1/H1, Agility Digit) et comment devons-nous concevoir celle du D-Bot ?

---

## 1. La Problématique des Moteurs QDD (Quasi-Direct Drive)

Dans le corps humain, la hanche est une articulation sphérique parfaite : les 3 axes de rotation (Yaw, Roll, Pitch) se croisent exactement au même point x,y,z (le centre de la tête du fémur).

En robotique basée sur des actionneurs cylindriques massifs (les moteurs QDD type RS-03/RS-04), **deux moteurs physiques ne peuvent pas occuper le même espace au même moment**. 
Il est donc géométriquement impossible d'avoir une vraie liaison sphérique concourante. L'industrie résout ce problème en séparant les axes et en *empilant* les moteurs les uns à la suite des autres via de solides équerres structurelles. C'est ce qu'on appelle la **Chaîne Cinématique (Kinematic Chain)**.

---

## 2. Benchmark de l'Industrie

### A. L'approche K-Bot Originale
Les images du K-Bot montrent une tentative de compacter les 3 moteurs dans un espace très restreint (sorte de grappe entremêlée).
- *Inconvénient majeur* : Cette conception crée souvent des collisions (auto-intersections) lors de mouvements combinés extrêmes et rend l'usinage des pièces de liaison affreusement complexe en CAO 3D.

### B. L'approche Tesla Optimus : séquentielle A-R-F

Tesla a opté pour une chaîne cinématique **A-R-F** (Abduction→Rotation→Flexion), soit Roll→Yaw→Pitch dans notre nomenclature :
1. **Maillon 1 : Roll (Abduction)** — fixé au bassin, stabilité latérale.
2. **Maillon 2 : Yaw (Rotation)** — rotation interne/externe.
3. **Maillon 3 : Pitch (Flexion)** — dans la cuisse, levée et propulsion.

**Avantage** : Le gros moteur Pitch (le plus lourd) est le dernier maillon et ne porte que la cuisse.  
**Inconvénient** : Architecture "Gen 1" — le bassin reste très large et les proportions du torse sont moins naturelles.

### C. L'approche Unitree H1 / H1-2 : Sphérique (Grappe Concentrée)

De son côté, Unitree adopte une philosophie radicalement différente pour maximiser la dynamique et la vitesse (le H1 détient le record du monde de vitesse humanoïde).
1. **Concentration des masses** : Les trois moteurs de la hanche (des modèles M107 ultra-compacts et très coupleux développés en interne) sont agglutinés en une **grappe très dense** directement centrée sur le bassin.
2. **Quasi-concourants** : À l'inverse de Tesla, Unitree s'efforce de faire en sorte que les axes de ces 3 moteurs se croisent *presque* au même point géométrique. L'objectif est d'imiter la vraie articulation "sur rotule" du corps humain.
3. **Bras de levier réduit** : Aucun moteur lourd n'est inséré dans le haut de la cuisse. Toute la puissance est dans le bassin, réduisant l'inertie lors des déplacements rapides.

> ⚠️ L'approche sphérique d'Unitree nécessite des moteurs sur-mesure imbriqués, incompatibles avec nos moyens de production en atelier.

### D. L'approche Gen2 (Figure 02, Unitree G1) : F-A-R

Les robots humanoides de deuxième génération (Figure 02, Unitree G1) ont convergé vers l'ordre **F-A-R** (Flexion→Abduction→Rotation), soit Pitch→Roll→Yaw :

1. **Maillon 1 : Pitch (Flexion)** — fixé au haut du bassin/torse, axe principal.
2. **Maillon 2 : Roll (Abduction)** — suspendu sous l'axe Pitch.
3. **Maillon 3 : Yaw (Rotation)** — en bas, vers la cuisse.

**Avantages** :
- Packaging anatomique — le bassin est plus fin, le torse proportionnellement plus long.
- Le pivot principal (Pitch) est haut, ce qui donne des proportions humaines naturelles.
- Standard de l'industrie 2024-2025.

**Inconvénient** :
- Le moteur Pitch porte les masses des moteurs Roll et Yaw lors du swing de jambe, ce qui augmente théoriquement l'inertie distale. En pratique, les marges de couple des RS-04 rendent cet inconvénient négligeable (voir §4).

---

## 3. L'Architecture D-Bot : Chaîne F-A-R (Méthode Gen2)

**Pour le D
```

**[Extrait 11: STUDY_Simulation_Isaac_Gym.md]**
```text
couloir tout en regardant et attrapant un objet sur une table à sa droite, l'IA cherchera l'axe *Waist Yaw*. Sans axe Z au torse, le robot devrait marcher en "pas chassés" (crabe) ce qui est énergétiquement inefficace, ou tourner entièrement son corps sans cesse.

> **Verdict D-Bot** : La version actuelle (V1) fait l'impasse sur le Waist Yaw pour des raisons de rigidité structurelle et de simplicité. Mais, comme expliqué plus bas dans la **Section 4 (La Tête et le Cou)**, cette absence est **magistralement compensée par les 2 moteurs du cou (Pan/Tilt)**. En utilisant la Vision Active (Active Vision), le robot peut tourner la tête pour cibler un objet asymétrique, et utiliser les 5 DOFs de ses bras pour l'atteindre, sans avoir besoin de faire pivoter son bassin. L'ajout d'un Waist Yaw reste une piste d'optimisation (V2) pour des postures extrêmes, mais l'IA s'adaptera sans problème à son absence sur la V1 grâce à la tête articulée.

---

## 2. Le Haut du Corps : Épaules et Coudes

Pour le haut du corps, les algorithmes de RL (surtout ceux formés sur des données de *Motion Capture* humaine) sont beaucoup plus rigides sur le standard attendu.

### 2.1 Les Épaules (3 DOFs) : Le Standard Absolu

Le bras humain est un système à 7 DOF au total (3 épaule, 1 coude, 3 poignet). L'IA s'attend à une vraie conception sphérique (3 axes concourants) ou quasi-sphérique à l'épaule.

| Axe (Convention) | Action | Statut IA | D-Bot V1 |
| :--- | :--- | :---: | :---: |
| **Shoulder Pitch (Y)** | Lever le bras devant soi | 🟢 **Obligatoire** | ✅ RS-03 |
| **Shoulder Roll (X)** | Écarter le bras sur le côté | 🟢 **Obligatoire** | ✅ RS-03 |
| **Shoulder Yaw (Z)** | Effectuer une rotation interne du bras | 🟢 **Fortement Recommandé** | ✅ RS-02 |

> **Bonne nouvelle pour le D-Bot** : L'architecture actuelle du bras (Pitch/Roll puissants + Yaw plus léger) correspond **exactement** à la topologie standard URDF utilisée dans Isaac Gym pour l'entraînement à la manipulation (par exemple, le bras du robot PANDA ou ALOHA). L'IA n'aura besoin d'aucun "hack".

### 2.2 Le Coude (1 ou 2 DOFs)

| Axe | Action | Statut IA | D-Bot V1 |
| :--- | :--- | :---: | :---: |
| **Elbow Pitch (Y)** | Plier le coude | 🟢 **Obligatoire** | ✅ RS-02 |
| **Elbow Yaw (Z)** | Supination/Pronation de l'avant bras | 🟡 Optionnel | ❌ |

Beaucoup de robots simplifiés transfèrent le Yaw de l'avant-bras directement au niveau du poignet. C'est ce que nous faisons.

---

## 3. L'Extrémité : Le Poignet et la Main (End-Effectors)

Dans les environnements comme Isaac Gym, la main est généralement traitée comme un objet terminal appelé **End-Effector**.

### 3.1 Le Poignet (1 à 3 DOFs)

Le minimum viable pour qu'une IA puisse orienter un outil dans l'espace (couplé aux 4 DOFs Épaule+Coude) est l'ajout du "Poignet Roll" (Torsion).

| Axe | Action | Statut IA | D-Bot V1 |
| :--- | :--- | :---: | :---: |
| **Wrist Roll (Z)** | Tourner la poignée de porte | 🟢 **Obligatoire** | ✅ RS-00 |
| **Wrist Pitch (Y)** | Casser le poignet bas/haut | 🟡 Recommandé | ❌ |
| **Wrist Yaw (X)** | Saluer de la main | 🔴 Optionnel | ❌ |

Le D-Bot possède un bras à **5 DOFs** (3 épaule + 1 coude + 1 poignet torsif). C'est le strict minimum canonique pour faire de la manipulation d'objets en RL. Cela couvre 90% de l'espace de travail frontal. 

### 3.2 La Main (L'approche IA)

C'est ici que l'approche matérielle dicte l'approche logicielle. Isaac Gym gère la main de deux manières distinctes :

1. **Approche "Pince Parallel" (Gripper - 1 DOF)** : L'IA envoie simplement un signal (Ouvrir / Fermer / Force). 90% des challenges RL grand public (ramasser une pomme) utilisent ça.
2. **Approche "Dexterous Hand" (Main Anthropomorphe - >4 DOFs)** : C'est le domaine phare actuel (Shadow Hand, D-Hand). L'IA doit contrôler individuellement les doigts. Isaac Gym excelle dans ce domaine de la *Dexterous Manipulation*.

> **Verdict D-Bot** : L'utilisation de notre **D-Hand Premium (8 moteurs XC
```

**[Extrait 12: STUDY_Bloc_Pelvien_Hanche.md]**
```text
→Yaw→Pitch dans notre nomenclature :
1. **Maillon 1 : Roll (Abduction)** — fixé au bassin, stabilité latérale.
2. **Maillon 2 : Yaw (Rotation)** — rotation interne/externe.
3. **Maillon 3 : Pitch (Flexion)** — dans la cuisse, levée et propulsion.

![Référence du Pelvis et Bloc de Hanche Tesla Optimus](../../Assets/img_optimus_pelvis_reference.jpg)

*Figure 2.1 : Référence d'architecture du bloc pelvien et de hanche de Tesla Optimus.*

---

**Avantage** : Le gros moteur Pitch (le plus lourd) est le dernier maillon et ne porte que la cuisse.  
**Inconvénient** : Architecture "Gen 1" — le bassin reste très large et les proportions du torse sont moins naturelles.

### C. L'approche Unitree H1 / H1-2 : Sphérique (Grappe Concentrée)

De son côté, Unitree adopte une philosophie radicalement différente pour maximiser la dynamique et la vitesse (le H1 détient le record du monde de vitesse humanoïde).
1. **Concentration des masses** : Les trois moteurs de la hanche (des modèles M107 ultra-compacts et très coupleux développés en interne) sont agglutinés en une **grappe très dense** directement centrée sur le bassin.
2. **Quasi-concourants** : À l'inverse de Tesla, Unitree s'efforce de faire en sorte que les axes de ces 3 moteurs se croisent *presque* au même point géométrique. L'objectif est d'imiter la vraie articulation "sur rotule" du corps humain.
3. **Bras de levier réduit** : Aucun moteur lourd n'est inséré dans le haut de la cuisse. Toute la puissance est dans le bassin, réduisant l'inertie lors des déplacements rapides.

> ⚠️ L'approche sphérique d'Unitree nécessite des moteurs sur-mesure imbriqués, incompatibles avec nos moyens de production en atelier.

### D. L'approche Gen2 (Figure 02, Unitree G1) : F-A-R

Les robots humanoides de deuxième génération (Figure 02, Unitree G1) ont convergé vers l'ordre **F-A-R** (Flexion→Abduction→Rotation), soit Pitch→Roll→Yaw :

1. **Maillon 1 : Pitch (Flexion)** — fixé au haut du bassin/torse, axe principal.
2. **Maillon 2 : Roll (Abduction)** — suspendu sous l'axe Pitch.
3. **Maillon 3 : Yaw (Rotation)** — en bas, vers la cuisse.

**Avantages** :
- Packaging anatomique — le bassin est plus fin, le torse proportionnellement plus long.
- Le pivot principal (Pitch) est haut, ce qui donne des proportions humaines naturelles.
- Standard de l'industrie 2024-2025.

**Inconvénient** :
- Le moteur Pitch porte les masses des moteurs Roll et Yaw lors du swing de jambe, ce qui augmente théoriquement l'inertie distale. En pratique, les marges de couple des RS-04 rendent cet inconvénient négligeable (voir §4).

---

## 3. L'Architecture D-Bot : Chaîne F-A-R (Méthode Gen2)

**Pour le D-Bot, nous adoptons officiellement l'ordre F-A-R**, en ligne avec les standards de la robotique humanoïde 2024-2025. C'est la seule approche qui soit à la fois réaliste avec des moteurs QDD standards "off-the-shelf" (RobStride) et qui offre des proportions anatomiques satisfaisantes.

Concrètement, la liaison entre le Bassin et le Fémur (Cuisse) du robot se décompose ainsi :

![Schéma Éclaté du Cardan de Hanche](./assets/img_hip_kinematic_chain.png)

### Maillon 1 : L'Axe Pitch (Moteur RS-04)
* **Emplacement** : Fixé au sommet du bassin ou en partie basse du torse (axe Y — horizontal, regarde sur les côtés du robot).
* **Rôle** : C'est le boss de la motricité. Il encaisse la charge principale pour lever la cuisse, s'accroupir, ou propulser le robot en avant.
* **Connexion sortante** : Son rotor porte la première équerre (un L-Bracket usiné en alu massif) qui descend vers le moteur Roll.
* **Motorisation** : RS-04 (120 N.m pic) — le plus fort, justement placé en premier pour encaisser tous les efforts.

### Maillon 2 : L'Axe Roll (Moteur RS-03)
* **Emplacement** : Fixé horizontalement (axe X) à l'extrémité du L-Bracket venant du moteur Pitch. Il regarde devant ou derrière le robot.
* **Rôle** : Permettre au robot de faire le grand écart ou d'écarter la jambe sur le côté.
* **Connexion sortante** : Son rotor porte la deuxième équerre (un U-Bracket ou L-Bracket) vers le Yaw.

### Maillon 3 : L'Axe Yaw (Moteur RS-03)
* **Emplacement** : Fixé verticalement (axe Z) à l'extrémité de l'équerre du moteur Roll, en haut de la cuisse.
* **Rôle** : Rotation interne/externe (tourner la pointe du pied vers l'intérieur ou l'extérieur).
* **Connexion sortante
```

---

# Fiche Technique Comparative : Robot K-Bot (Standard K-Scale Labs)

> [!IMPORTANT]
> **STATUT DE CE DOCUMENT : DOCUMENTATION DE RÉFÉRENCE CONCURRENTIELLE / COMPARATIVE EXTERNE**
> Ce fichier décrit l'architecture du robot **K-Bot d'origine (K-Scale Labs, 20 DOF)**.
> 
> **CONSIGNE CRITIQUE POUR LES SYSTEMES D'IA / RAG** : 
> *   Ce robot est un **système tiers externe** servant de benchmark historique et comparatif.
> *   **NE PAS** incorporer, fusionner, ou mélanger les moteurs, couples, masses ou configurations de ce robot K-Bot avec les spécifications actives du **D-Bot (26 DOF)**. 
> *   Le D-Bot a sa propre cinématique distincte (double RS-03 à la cheville, coude RS-06, etc.) décrite dans ses propres fichiers d'études.

---

## 1. Caractéristiques Générales du K-Bot Standard

Le K-Bot standard est un humanoïde de recherche open-source de taille réelle conçu par K-Scale Labs. Sa structure mécanique est conçue principalement pour la marche lente et la manipulation basique en laboratoire.

*   **Nombre de moteurs** : 20 moteurs RobStride (QDD).
*   **Nombre de Degrés de Liberté (DOF)** : 20 DOF.
*   **Masse totale du robot** : ~34.0 kg.
*   **Type de structure** : Brackets en aluminium plié et pièces imprimées en impression 3D FDM.

---

## 2. Cinématique Détaillée du K-Bot (20 DOF)

La configuration d'origine du K-Bot répartit ses 20 actionneurs sur 4 membres et le bassin, sans tête articulée (cou rigide).

### 🦾 Membres Supérieurs (10 moteurs au total - 5 par bras)
*   **Épaule Pitch** (Flexion/Extension) : 1× RobStride **RS-03** (60 N.m peak / 20 N.m nom.)
*   **Épaule Roll** (Abduction/Adduction) : 1× RobStride **RS-03** (60 N.m peak / 20 N.m nom.)
*   **Épaule Yaw** (Rotation interne/externe) : 1× RobStride **RS-02** (17 N.m peak / 6 N.m nom.)
*   **Coude Pitch** (Flexion/Extension) : 1× RobStride **RS-02** (17 N.m peak / 6 N.m nom.)
*   **Poignet Roll** (Rotation main) : 1× RobStride **RS-00** (14 N.m peak / 5 N.m nom.)
*   *Main d'origine* : Main passive en plastique imprimé, sans servomoteur Dynamixel.

### 🦵 Membres Inférieurs (10 moteurs au total - 5 par jambe)
*   **Hanche Pitch** (Flexion/Extension) : 1× RobStride **RS-04** (120 N.m peak / 40 N.m nom.)
*   **Hanche Roll** (Abduction/Adduction) : 1× RobStride **RS-03** (60 N.m peak / 20 N.m nom.)
*   **Hanche Yaw** (Rotation) : 1× RobStride **RS-03** (60 N.m peak / 20 N.m nom.)
*   **Genou Pitch** (Flexion/Extension) : 1× RobStride **RS-04** (120 N.m peak / 40 N.m nom. - montage direct-drive)
*   **Cheville Pitch** (Propulsion) : 1× RobStride **RS-02** (17 N.m peak / 6 N.m nom. - couplé à un tirant mécanique simple type pushrod multipliant par ~2 le couple effectif pour atteindre ~34 N.m).
*   *Axe de Roll de Cheville* : ❌ Absent (aucun degré de liberté latéral, pied rigide latéralement).

---

## 3. Inventaire des Moteurs K-Bot Standard (20 DOF)

Voici le décompte exact des actionneurs RobStride équipant un K-Bot d'origine :

| Modèle Moteur | Quantité | Couple Pic | Couple Nom. | Poids Unit. | Usage sur le K-Bot |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **RS-04** | **4** | 120 N.m | 40 N.m | 1420g | Hanches Pitch (2) + Genoux (2) |
| **RS-03** | **8** | 60 N.m | 20 N.m | 880g | Épaules Pitch/Roll (4) + Hanches Roll/Yaw (4) |
| **RS-02** | **6** | 17 N.m | 6 N.m | 405g | Épaules Yaw (2) + Coudes (2) + Chevilles Pitch (2) |
| **RS-00** | **2** | 14 N.m | 5 N.m | 310g | Poignets Roll (2) |
| **TOTAL** | **20** | — | — | **~17.2 kg** | **Masse totale des moteurs seuls** |

---

## 4. Limitations Majeures identifiées sur le K-Bot

Cette architecture d'origine, bien que simple, présente plusieurs limites techniques critiques qui ont rendu la refonte D-Bot obligatoire :

1.  **L'absence de Roll à la cheville** : Empêche le robot d'adapter son pied aux irrégularités du sol ou de corriger les déséquilibres latéraux en phase de double appui, limitant la marche aux sols parfaitement plats.
2.  **Faiblesse du genou en course** : Le RS-04 en prise directe au genou plafonne à 120 N.m de couple de pic. La dynamique de course pour un robot de ce gabarit requiert plus de 170 N.m, exposant le moteur à la surcharge et au glissement.
3.  **Faiblesse du couple de coude** : Le RS-02 (17 N.m) limite le portage de charges bras replié à moins de 800g par bras.
4.  **Tête fixe** : Pas de vision active orientable, obligeant le robot à tourner tout son buste pour balayer son environnement avec ses caméras.

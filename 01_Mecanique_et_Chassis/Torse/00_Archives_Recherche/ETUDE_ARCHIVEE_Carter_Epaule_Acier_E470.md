# 📦 [ARCHIVE] Étude Technique Historique : Carter Monobloc d'Épaule en Acier E470

> [!WARNING]
> **DOCUMENT D'ARCHIVE HISTORIQUE (Août 2026)**
> Cette étude et les spécifications associées du carter cylindrique monobloc en **Acier E470** sont **archivées et remplacées par la Cage H-Bracket en Aluminium 7075-T6** (2 plaques 5.0 mm évidées à Ø95 mm + bride monobloc 48.20 mm + tirants M5 axiaux à 23.4°).
> 
> **Raisons du remplacement par la Cage H-Bracket Alu 7075-T6 :**
> 1. **Gain de masse massif** : Allégement de près de 500 g sur le haut du torse.
> 2. **Usinabilité simplifiée sur CNC C500** : Découpe 2D directe dans des tôles et disques d'aluminium sans usinage lourd d'ébauche creuse en acier allié.
> 3. **Dissipation thermique supérieure** : Moteur RS-04 à l'air libre (cage ouverte) avec convection directe au lieu d'un carter clos.
> 4. **Rigidité Roll augmentée (×15.5)** : Bras de levier des tirants M5 à R = 72 mm offrant une flèche au cou < 0.1 mm.
> 5. **Démontage 100% mécanique sans collage** : Suppression du collage irréversible à la résine JB Weld dans le collet PA12-CF.
>
> 📄 **Document actif de référence** : [GUIDE_Fabrication_Torse_D-Bot_Hybride.md](../GUIDE_Fabrication_Torse_D-Bot_Hybride.md)

---

## 1. Concept Initial : Carter Monobloc Acier E470 Ouvert à l'Avant

L'approche visait à insérer le moteur RobStride RS-04 par l'avant (façade extérieure) dans un carter en acier mécano-usiné :

![Coupe axiale du carter monobloc acier E470 d'épaule](.../media/manchon_acier_e470_coupe_axiale.svg)

*Coupe axiale du concept de Support RS-04 en acier E470 CNC avec sa flasque arrière de 4,0 mm (évidement central Ø 97,0 mm) et sa paroi cylindrique 360° de 1,9 mm (Ø ext 124,0 mm).*

---

## 2. Plan de Définition CAO 2D (`Support RS-04` — David SERGENT 03/08/2026)

![Plan de Définition 2D — Support RS-04 en Acier E470 par David SERGENT](.../media/plan_2d_support_rs04_acier_e470.png)

*Plan de Définition 2D du Support RS-04 en Acier E470 (par David SERGENT — 03/08/2026) : Ø ext 124,0 mm, alésage Ø 120,2 mm H7, paroi 1,9 mm, fond 4,0 mm évidé à Ø 97,0 mm, 10× perçages lisses Ø 4,3 mm sur PCD Ø 106,0 mm.*

---

## 3. Spécifications du Plan CAO `Support RS-04`

* **Matériau** : **Acier E470** (ébauche creuse Blockenstock d131 / d88)
* **Diamètre extérieur final (D_ext)** : **Ø 124,0 mm**
* **Diamètre intérieur alésage (D_int)** : **Ø 120,2 mm H7** (120,2 + 2 × 1,9 = 124,0 mm)
* **Épaisseur de paroi cylindrique** : **1,9 mm**
* **Hauteur axiale totale (H)** : **39,0 mm** (Profondeur utile de poche = 35,0 mm)
* **Épaisseur du fond (flasque d'embase)** : **4,0 mm**
* **Évidement central arrière** : **Ø 97,0 mm** (dégagement connectique)
* **PCD Perçages Stator Arrière** : **10× perçages lisses Ø 4,3 mm (ISO 273 Moyen)** sur PCD Ø 106,0 mm
* **Masse unitaire** : ~344 g

---

## 4. Étude Comparative Historique : Alu 6061-T6 vs Acier E470

| Critère de Dimensionnement | Option A : Aluminium 6061-T6 | Option B : Acier E470 | Remarque |
|:---|:---:|:---:|:---|
| **Module d'Young (E - Rigidité)** | 69 GPa | **210 GPa** | Acier 3,04× plus rigide |
| **Limite d'Élasticité (Re)** | 275 MPa | **470 MPa** | +71% de résistance à la plastification |
| **Épaisseur de Paroi Cylindrique** | 3,0 mm | **1,9 mm** | Ø ext final = 124,0 mm |
| **Diamètre Alésage Intérieur** | 120,0 mm H7 | **120,2 mm H7** | Ajustement encastrement RS-04 |
| **Hauteur Axiale Totale** | 52,2 mm | **39,0 mm** (Poche 35 mm) | Logement ajusté |
| **Épaisseur du Fond (Flasque)** | 6,0 mm | **4,0 mm** (Évidement Ø 97 mm) | +53% plus rigide en flexion hors-plan |
| **Rigidité Flexion Paroi Cylindrique** | 1,0 (Référence) | **1,93 (+93%)** | Quasi doublement de rigidité |
| **Masse Totale du Support** | ~220 g (alu plein) | **~344 g** (avec évidement Ø97) | +124 g par épaule |
| **Perçages Stator Arrière** | 10× Ø 4,5 mm | **10× Ø 4,3 mm sur PCD Ø 106 mm** | Ancrage direct stator RS-04 |
| **Usinabilité C500** | Évidement depuis bloc plein | **Ébauche creuse d131/d88** | Usinage rapide dans ébauche creuse |

---

## 5. Directives d'Usinage C500 pour Acier E470

1. **Approvisionnement Blockenstock** : [Ébauche creuse d131 / d88 au cm - Acier E470](https://www.blockenstock.fr/d131-d88-au-cm-acier-e470-c2x42431541) (tronçons bruts de 40 mm).
2. **Outil** : Fraise carbure monobloc Ø 4 mm ou Ø 6 mm revêtue **AlTiN / TiAlN** (spécial acier).
3. **Vitesse de broche** : **5 000 à 6 000 tr/min** sous lubrification active (huile de coupe / WD-40).
4. **Avance & Passes** : Avance de **300 mm/min**, passes en Z de **0,5 mm** en fraisage hélicoïdal.
5. **Ordre d'usinage** :
   - Surfaçage face avant de 40,0 mm à 39,0 mm net.
   - Alésage intérieur de Ø 88,0 mm à Ø 120,2 mm H7 sur 35,0 mm.
   - Évidement central arrière à Ø 97,0 mm et perçage des 10 trous lisses Ø 4,3 mm sur PCD Ø 106 mm.
   - Contournage extérieur final à Ø 124,0 mm.

---

## 6. Séquence d'Assemblage Historique (Collage JB Weld)

```
Étape 1 : Insérer et coller le Carter Monobloc Acier E470 dans le collet PA12-CF de la coque (résine époxy JB Weld)
          → Laisser polymériser 24h

Étape 2 : Connecter et goupiller le tube carbone Ø30 mm dans le socket de la bride d'épaule

Étape 3 : Insérer le moteur RS-04 par l'AVANT (extérieur de l'épaule) dans l'alésage Ø120.2 mm H7

Étape 4 : Serrer les 10 vis CHC M4 × 10 mm depuis l'intérieur du torse à travers les perçages lisses Ø4.3 mm
```

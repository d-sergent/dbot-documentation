# 23 — Stratégie Ultralight : Matériaux sous le Genou

> **Règle d'or en robotique bipède :** un gramme gagné au bout du pied (inertie distale) vaut dix grammes gagnés à la hanche. L'inertie de balancement de la jambe a un impact exponentiel sur le couple requis aux hanches et genoux lors de la course.

Pour garantir les performances du D-Bot, la zone située **sous le genou** doit suivre une stratégie stricte : **bannir le métal massif** (sauf exception mécanique critique) au profit de solutions hybrides combinant impression 3D (Qidi Plus 4), usinage CNC (C500) et composants aérospatiaux standards.

Voici la stratégie d'ingénierie optimisée composant par composant.

---

## 1. Le Tibia (Corps de la Jambe)

* **❌ À proscrire** : Un tibia usiné en bloc d'aluminium (trop lourd, inertie catastrophique).
* **✅ Option 1 (Full 3D Print)** : Impression sur la Qidi en **PA12-CF** (Nylon chargé carbone). Le nylon offre l'absorption des chocs (évite la rupture nette) et la fibre de carbone apporte la rigidité. *Paramètres : Remplissage gyroid 30%, 5-6 périmètres extérieurs.*
* **🏆 Option 2 (Hybride Pro — Recommandée)** : Utiliser un **tube en fibre de carbone tressé** du commerce (ex: Ø40mm, ép. 2mm). Le rapport poids/rigidité est imbattable.
  * **Intégration** : Imprimer des "bouchons" structurels en PA12-CF sur la Qidi, et les coller à l'époxy structurale (Loctite EA) aux deux extrémités de ce tube. Ces bouchons feront la liaison avec l'axe du genou (haut) et le cardan (bas).

---

## 2. Le Bloc Moteurs Cheville (Sous le genou)

* **Contexte** : Les 2 moteurs RS-03 (120 N.m combinés) génèrent un couple énorme et chauffent. Ils sont logés en haut du tibia, juste sous l'axe du genou.
* **✅ Matériau** : **Aluminium 6061-T6 (usiné CNC C500)**.
* **Justification** : C'est la seule exception métallique. Le métal est ici obligatoire pour encaisser les stress de torsion massifs, et surtout pour servir de **dissipateur thermique (heatsink)** aux moteurs. Puisque cette masse est située très haut (près de la base d'oscillation), son impact sur l'inertie de la foulée reste limité.

---

## 3. Les Bielles de Cheville (Pitch/Roll)

* **✅ Matériau** : **Tubes Fibre de Carbone 3K pultrudé** (Ø ext 10mm / Ø int 8mm).
* **Justification** :
  1. **Flambement** : Sous des pointes à plus de 1 500 N, l'aluminium plierait. Avec le module de Young du carbone (120-150 GPa), le risque de flambement est nul.
  2. **Poids** : ~20 g/mètre (carbone) contre ~40 g/mètre (aluminium).
  3. **Fatigue** : Résistance cyclique virtuellement infinie, contrairement à l'alu qui micro-fissure avec les millions de pas.
* **Embouts** : Utilisation de petites rotules en **polymère hautes performances** (ex: Igus EBRM-05), plus légères que l'acier, enchassées dans les tubes avec de la résine époxy.

---

## 4. Le Cardan de Cheville (Joint Universel)

* **Contexte** : Articulation centrale de la cheville DIN 808.
* **✅ Matériau** : **Aluminium (Duralumin)** si disponible, ou Acier évidé.
* **Justification** : Un cardan standard en acier de 12mm pèse entre 150g et 200g. En trouvant la référence en alliage léger (chez Michaud Chailly ou HPC), le poids chute à ~60-80g. Ce gain de 100g, situé très bas sur la jambe, est capital. Si seule la version C45 acier est retenue (pour la robustesse extrême), un usinage au tour pour évider l'axe central est fortement recommandé.

---

## 5. Le Pied (Structure et Semelle)

Le pied est la pièce la plus éloignée de la hanche. Son inertie est maximale. De plus, un bloc d'aluminium ici transmettrait l'onde de choc (ringing) directement dans les encodeurs des RS-03 via les bielles.

**Architecture idéale (Hybride) :**

1. **Le Cou-de-Pied (Interface Cardan-Pied)** : Pièce courte imprimée en **PA12-CF** (Qidi). Solide tout en amortissant les très hautes fréquences de résonance.
2. **La Plaque Plantaire (Ossature)** : Découpée à la CNC C500 dans une feuille **plate de Fibre de Carbone (3mm)**. Outre sa légèreté extrême (~30-40g), le carbone plat agit comme un ressort à lame (Leaf Spring) et restitue de l'énergie à la poussée de l'orteil.
3. **Les Pads d'Appui (Talon/Avant-pied)** : Imprimés sur la Qidi en **TPU (Shore 95A ou 85A)** puis collés ou vissés sous le carbone. Le TPU offre l'adhérence (grip) et l'absorption primaire de l'impact (damper).

---

## Bilan Massique Souhaité (Sous l'axe genou)

*(Estimations pour la partie mobile, hors bloc moteurs/genou (qui reste "en haut"))*

| Composant | Stratégie Matériau | Poids Estimé (par jambe) |
| :--- | :--- | :---: |
| Tibia | Tube Carbone Ø40mm + Embouts PA12-CF | ~150g |
| Bielles | 2× Tubes Carbone Ø10/8mm + Rotules Igus | ~30g |
| Cardan | DIN 808 Alu (Duralumin) ou Acier light | ~80g - 120g |
| Pied | Plaque Carbone plat 3mm + Cou PA12 + Pads TPU | ~200g |
| **Total** | **Masse mobile distale à balancer** | **~400 à 460 g** |

Un sous-genou à **moins de 500 grammes** est exceptionnel à l'échelle d'un humanoïde de près de 40 kg. C'est ce qui permettra d'atteindre les vitesses de course cibles (~5 à 10 km/h) sans exiger le passage aux monstrueux moteurs RS-06.

# 23 — Stratégie Ultralight : Matériaux sous le Genou

> **Règle d'or en robotique bipède :** un gramme gagné au bout du pied (inertie distale) vaut dix grammes gagnés à la hanche. L'inertie de balancement de la jambe a un impact exponentiel sur le couple requis aux hanches et genoux lors de la course.

Pour garantir les performances du D-Bot, la zone située **sous le genou** doit suivre une stratégie stricte : **bannir le métal massif** (sauf exception mécanique critique) au profit de solutions hybrides combinant impression 3D (Qidi Plus 4), usinage CNC (C500) et composants aérospatiaux standards.

Voici la stratégie d'ingénierie optimisée composant par composant.

---

## 1. Le Tibia (Corps de la Jambe)

* **❌ À proscrire** : Un tibia usiné en bloc d'aluminium (trop lourd, inertie catastrophique).
* **✅ Option 1 (Full 3D Print)** : Impression sur la Qidi en **PA12-CF** (Nylon chargé carbone). Le nylon offre l'absorption des chocs (évite la rupture nette) et la fibre de carbone apporte la rigidité. *Paramètres : Remplissage gyroid 30%, 5-6 périmètres extérieurs.*
* **🏆 Option 2 (Hybride Pro — Recommandée)** : Utiliser un **tube en fibre de carbone tressé** du commerce (ex: Ø40mm ext / Ø36mm int, épaisseur 2mm). Le rapport poids/rigidité est imbattable.
  
  **Où acheter le tube carbone Ø40mm ?**
  - **Spécifications requises** : Finition sergé (Twill) 3K, procédé **"Roll-wrapped"** (fibres croisées préimprégnées) impératif ! Ne jamais acheter du pultrudé (fibres axiales uniquement) pour un tibia, il fendrait sous l'effort.
  - **Fournisseurs** : Boutiques spécialisées ULM/Drones/RC comme *CarbonTube.net*, *EasyComposites*, ou sur *AliExpress* (boutiques certifiées matériaux composites comme *RJX Hobby*).
  - *Note : Une longueur de 500 mm suffit largement pour y découper les 2 tibias (longueur estimée ~220 mm).*

  **A. Montage complet HAUT (Connexion au Genou RS-04 — Bracket en L + Goupille)**
  ![Montage_Haut](./img_tibia_montage_haut.png)

  Le moteur RS-04 du genou a son **axe de sortie dans le même axe que le corps du moteur** (configuration inline). Le tibia ne peut donc pas se fixer directement dans l'axe du moteur : il faut un **bracket en forme de L** pour faire le renvoi à 90°.

  1. **Le Bracket en L (Aluminium CNC — C500)** :
     - Une pièce en **Aluminium 6061-T6** usinée à la CNC C500.
     - La **branche horizontale** du L se fixe sur l'axe de sortie du RS-04 (par clavetage, vis de pression ou moyeu fendu selon le modèle).
     - La **branche verticale** du L descend et vient envelopper le sommet du tube carbone. Elle comporte un alésage semi-circulaire ou une pince qui épouse la forme du tube Ø40mm.

  2. **Le Bouchon Interne Haut (Alu ou PA12-CF)** :
     - Identique au principe du montage bas : un bouchon massif (Ø36mm) est inséré et collé (Époxy Structurale) à l'intérieur du tube carbone, sur 30 mm de profondeur.
     - **Rôle** : renforcer le tube carbone contre l'écrasement lors du goupillage, et augmenter la surface de transmission des efforts.

  3. **Goupille Mécanindus Traversante (Sécurité Anti-arrachement)** :
     - Même principe que le montage bas : une **goupille élastique Ø3mm** traverse de part en part : *Bracket Alu → Paroi Carbone → Bouchon → Paroi Carbone → Bracket Alu*.
     - **Pourquoi ne pas se contenter de l'époxy ?** L'époxy structurale est extrêmement résistante en cisaillement et en compression, mais elle peut céder en traction pure (arrachement) sous des chocs répétés de course. La goupille garantit que le tube ne pourra **jamais** se séparer du bracket, même en cas de défaillance du joint collé.
     - La colle époxy reste utile en complément : elle assure le zéro-jeu et distribue les contraintes sur toute la surface de contact (~34 cm²).

  4. **Transmission des efforts** : *RS-04 → Axe de sortie → Bracket Alu en L → Goupille + Époxy → Bouchon → Tube Carbone*.

  **B. Montage complet BAS (Connexion au Cardan DIN 808 — Goupille Mécanindus)**
  ![Montage_Bas](./img_tibia_montage_bas.png)

  La fixation du tibia dans le cardan utilise la méthode la plus robuste de l'ingénierie mécanique : une **goupille élastique Mécanindus (roll pin) traversante**. Cette solution gère à la fois l'anti-rotation ET l'anti-arrachement en un seul composant. Il n'y a besoin ni de clavette, ni de circlips, ni de bague d'arrêt.

  1. **Achat du Cardan (Avec perçage sur mesure)** :
     - Commander un **Joint de Cardan DIN 808** (ex: [Michaud Chailly A5 473](https://maurin-embedded.partcommunity.com/3d-cad-models/mod%C3%A8le-a5-473-joint-de-cardan-simple-michaud-chailly-direct-transmission?info=michaud_chailly_transmission%2Ftransmission%2Fjoints_cardans%2Fa5_473.prj&cwid=6179)).
     - **Demander au fournisseur un perçage traversant de Ø3mm sur chaque moyeu** (usinage sur plan). Formuler la demande ainsi :
       *"Bonjour, je souhaite commander la référence A5-473 avec une modification : un perçage traversant de Ø3mm sur chaque moyeu pour insertion d'une goupille élastique, centré à X mm du bord."*
     - *(Autres fournisseurs : HPC Europe, Norelem, Prud'homme Transmissions)*.

  2. **Le Bouchon Interne (Obligatoire pour tube creux)** :
     - Insérer et coller (Époxy Structurale) un **bouchon massif en Aluminium ou PA12-CF** (Ø36mm) à l'intérieur du tube carbone, sur 30 mm de profondeur.
     - **Rôle critique** : Lorsque la goupille traversera le tube carbone, le bouchon empêche les fibres de carbone de s'écraser et de se délaminer sous la pression de la goupille. Sans bouchon, le tube éclaterait.

  3. **Assemblage et Perçage (Canon de perçage)** :
     - Emmancher le tube carbone (avec son bouchon collé) dans le moyeu du cardan déjà percé.
     - **Astuce Pro** : Utiliser les trous du cardan (acier trempé) comme **canon de perçage** pour percer le tube carbone et le bouchon avec une simple perceuse. L'acier guide le foret parfaitement au centre. Aucun alignement artisanal n'est nécessaire.

  4. **Insertion de la Goupille Mécanindus** :
     - Enfoncer une **goupille élastique (roll pin) Ø3mm en acier** à l'aide d'un marteau et d'un chasse-goupille. Elle doit forcer légèrement (principe de la goupille élastique).
     - **Résistance au cisaillement** : ~6 300 N (~630 kg) en double cisaillement, soit un **coefficient de sécurité de 5×** pour un robot de 40.2 kg à l'impact en course.
     - **Résultat** : Pour séparer le tibia du cardan, il faudrait littéralement cisailler l'acier de la goupille (plusieurs tonnes de force). C'est la garantie absolue que rien ne bougera, même en cas de chute ou de saut.

  > [!TIP]
  > **Dimensionnement de la goupille selon le diamètre de l'axe :**
  > | Diamètre Axe | Goupille Ø | Résistance cisaillement | Impact matière |
  > |---|---|---|---|
  > | 8 mm | 2,5 mm | ~4 400 N (~440 kg) | Acceptable (5,5 mm restants) |
  > | 8 mm | 3 mm | ~6 300 N (~630 kg) | Limite pour la torsion |
  > | 10 mm | 3 mm | ~6 300 N (~630 kg) | **Idéal** — très robuste |

### 📐 Pourquoi un Tube Carbone et pas un Tube en Aluminium/Acier ?

| Critère | **Tube Carbone 3K** (Ø40/36mm) | **Tube Aluminium 6061** (Ø40mm) | **Tube Acier** (Ø40mm) |
|---|---|---|---|
| **Masse** (L=220mm) | **~80 g** | ~180 g | ~450 g |
| **Rigidité spécifique** (E/ρ) | **⭐⭐⭐⭐⭐** (~75 GPa·cm³/g) | ⭐⭐⭐ (~26 GPa·cm³/g) | ⭐⭐⭐ (~27 GPa·cm³/g) |
| **Résistance fatigue** | **Infinie** (pas de limite d'endurance) | Limitée (fissures après ~10⁷ cycles) | Bonne |
| **Impact inertiel** | **Minimal** — réduction de ~55% par rapport à l'alu | Référence | Catastrophique (~2,5× l'alu) |
| **Assemblage** | Nécessite bouchon interne (collé + goupille) | Goupille directe, simple | Goupille directe, simple |
| **Coût** | ~15-25 € (500mm) | ~5-10 € | ~5-10 € |

**Verdict** : Le carbone est **2× plus léger** que l'aluminium et **5× plus léger** que l'acier, à rigidité égale ou supérieure. Pour un composant oscillant en bout de jambe (inertie distale maximale), cette réduction de masse a un **impact exponentiel** sur le couple requis aux genoux et hanches lors de la course. Le surcoût est négligeable (~15 €). Le bouchon interne (nécessaire pour protéger les fibres lors du goupillage) pèse ~15-20 g seulement.

### 📐 Tube Carbone vs Lame de Carbone pour le Tibia ?

| Critère | **Tube Carbone Ø40mm** | **Lame (plaque) Carbone** |
|---|---|---|
| **Résistance en flexion** | ⭐⭐⭐⭐⭐ Excellente dans **toutes** les directions (profil circulaire = inertie isotrope) | ⭐⭐⭐ Forte en pitch (sagittal) mais **très faible en lacet/roll** |
| **Résistance en torsion** | ⭐⭐⭐⭐⭐ Moment d'inertie polaire élevé | ⭐⭐ Très mauvaise — une plaque fine vrille facilement |
| **Assemblage cardan** | ⭐⭐⭐⭐ Bouchon + goupille traversante → très solide | ⭐⭐ Comment fixer un cardan sur une plaque plate ? Système de pince complexe |
| **Poids** | ~80-100g | ~40-60g (mais à rigidité égale en 3D, il faut 2 plaques en V → poids comparable) |
| **Amortissement passif** | Rigide (pas de flex) | ⭐⭐⭐⭐⭐ Fléchit comme un ressort à lame → absorption des chocs |
| **Complexité** | Simple — un seul composant | Élevée — 2 plaques + pièces de jonction haut/bas |

**Verdict** : Pour un tibia rigide relié à un cardan par goupille, le **tube carbone est le meilleur choix**. La lame serait intéressante uniquement dans une architecture "tibia flexible" (Solution S5 du document 15d), mais dans ce cas elle complète le tube, elle ne le remplace pas.

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

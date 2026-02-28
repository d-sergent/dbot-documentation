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

  **A. Montage complet HAUT (Connexion au Genou RS-04)**
  ![Montage_Haut](./img_tibia_montage_haut.png)
  1. **Le Bouchon Haut (Plug PA12-CF)** : Pièce en "T" imprimée en 3D (Qidi). La jupe du bouchon (Ø36mm) s'insère en force dans le tube carbone sur environ 30 mm de profondeur.
  2. **Collage Époxy Structural** : Dépolir l'intérieur du tube carbone avec du papier de verre (grain 120), nettoyer à l'isopropanol. Enduire la jupe du bouchon de résine époxy bicomposant longue durée (ex: Loctite EA 9466 ou DP490) puis emmancher. L'immense surface de contact (~34 cm²) rend cet joint virtuellement indestructible en traction/compression.
  3. **Interface Moteur (Bracket Alu)** : Une pièce CNC en Aluminium (C500) fait la liaison entre le chapeau du Moteur Genou RS-04 et ce bouchon PA12-CF.
  4. **Assemblage Mécanique** : 4 longues vis M4 ou M5 traversent verticalement la pièce aluminium, traversent l'épaulement du bouchon PA12-CF, et viennent se visser dans des écrous ou inserts taraudés noyés profondément dans le PA12-CF. Ainsi, la force est transmise : *RS-04 → Bracket Alu → Vis M4 → Bouchon PA12-CF → Joint Époxy → Tube Carbone*.

  **B. Montage complet BAS (Connexion au Cardan DIN 808)**
  ![Montage_Bas](./img_tibia_montage_bas.png)
  1. **Le Bouchon Bas (Plug PA12-CF)** : Cylindre imprimé sur le même principe (Ø36mm), inséré et collé à l'époxy sur 30 mm au fond du tube carbone.
  2. **Logement de la Cheville** : La base de ce bouchon PA12-CF est évidée (cylindre interne ou hexagone) au diamètre EXACT de la cage supérieure du joint de cardan (pour un cardan DIN 808 d'axe 12mm, le diamètre extérieur du manchon est souvent de 25 mm).
  3. **Liaison Tibia / Cardan (Perçage et Goupillage)** : Le bouchon PA12-CF joue ici le rôle d'entretoise structurelle. La cage supérieure en acier du cardan est emmanchée dans la cavité du bouchon. **Comment l'ensemble reste-t-il définitivement solidaire ?** Grâce à une unique **goupille élastique (Mécanindus / roll pin) de 4 ou 5 mm en acier**.
     - On perce un trou traversant de part en part, qui traverse diamétralement : la première paroi du tube carbone → le flanc du bouchon PA12-CF → **le manchon central en acier du cardan** → l'autre flanc du bouchon → la seconde paroi du carbone.
     - On frappe la goupille en force dans ce tunnel traversant.
     - **Résultat** : Cette goupille verrouille mécaniquement les 3 pièces (Carbone + PA12 + Cardan Acier) en même temps. Elle empêche totalement la rotation (transmission du couple lacet/yaw) ET bloque l'arrachement vertical du pied en phase de vol, avec zéro jeu.

> [!CAUTION]
> **Méthodologie d'Usinage : Comment percer le cardan en acier massif ?**
> Tenter de percer un cardan industriel (souvent en acier C45 ou plus durci) à la main avec un foret métaux standard (HSS) est voué à l'échec (dérapage, casse du foret, trou de travers).
> 
> **Procédure impérative :**
> 1. **Maintien ferme** : Utiliser un étau de perçage équipé d'un **Vé (V-block)** pour caler parfaitement le cylindre d'acier et empêcher toute rotation.
> 2. **Perceuse à colonne** : Indispensable pour garantir une descente parfaitement verticale à 90°.
> 3. **Type de foret** : Utiliser exclusivement des forets **Acier Cobalt (HSS-Co 5% ou 8%)** ou en **Carbure massif**.
> 4. **Lubrification** : Appliquer abondamment de l'huile de coupe (Cutting fluid) tout au long du perçage.
> 5. **Vitesse et Avance** : Vitesse de rotation très lente (ex: 400-600 RPM) avec une pression de descente forte et constante pour faire de vrais copeaux, sans brûler le foret.
> 6. **Avant-trou** : Commencer par faire une empreinte avec un foret à pointer (Center drill), puis percer un avant-trou (ex: Ø 2.5 mm) avant de passer au diamètre final exigeant la goupille (ex: Ø 4.0 mm).
> 
> ❌ **La CNC C500 n'est PAS adaptée pour ce perçage traversant.** Les fraiseuses de bureau ont des broches (spindles) tournant beaucoup trop vite (10 000+ tr/min) pour percer de l'acier durci, ce qui brûlerait le foret instantanément. De plus, utiliser une micro-fraise (3mm) pour descendre à 25mm de profondeur provoquerait des vibrations fatales (chatter).

### 📝 Alternatives CNC "Sans Perçage" (Idéal avec la C500)

Si vous ne possédez pas de perceuse à colonne robuste, la fraiseuse CNC C500 vous offre **deux excellentes alternatives beaucoup plus élégantes** pour bloquer la rotation du cardan sans avoir à le percer de part en part :

**Alternative A : Usinage externe de Méplats (Surface Milling)**
Sur une CNC C500, faire un surfaçage extérieur est très facile.
1. Fixer le cardan couché dans l'étau rotatif de la C500.
2. Avec une fraise carbure (DLC) de 6mm, usiner 2 ou 4 faces planes (méplats) sur la circonférence extérieure de la cage en acier, pour créer un profil carré ou en "double D". (L'acier s'usine très bien en passe fine à haute vitesse).
3. Modéliser l'empreinte femelle exacte dans le bouchon PA12-CF.
4. Une fois emboîté et collé à l'époxy, l'ensemble ne pourra **plus jamais tourner**. L'arrachement vertical est empêché par la colle et un petit épaulement interne.

**Alternative B : Utilisation de l'alésage interne (Méthode Pro - Sélectionnée)**
Au lieu d'imprimer un bouchon PA12-CF qui "avale" le cardan entier, on exploite l'intérieur du cardan. C'est la fixation d'ingénierie mécanique standardisée.

1. **Achat (Où trouver le cardan rainuré ?)** : 
   - Vous devez rechercher un **Joint de Cardan DIN 808 avec alésage H7 ET rainure de clavette JS9** (Keyway).
   - **Fournisseurs Pros** : *Michaud Chailly* (rechercher "Moyeu à alésage et rainure de clavette", famille F2 ou F4), *HPC Europe* (Transmission Mécanique), *Norelem*, ou *Prud'homme Transmissions*.
   - *Astuce* : Si la version rainurée est introuvable ou trop chère en petite série, l'usinage d'une rainure interne (brochage) dans un cardan alésé standard coûte peu cher chez un petit tourneur/fraiseur local.

2. **Usinage de l'Insert (Aluminium sur la C500)** : 
   - Usiner une pièce d'adaptation en **Aluminium 6061-T6 ou 7075**.
   - Le *haut* de l'insert a une jupe qui rentre dans le tube carbone 40mm (collé à l'époxy structurale).
   - Le *bas* de l'insert est un cylindre mâle (ex: Ø12mm) couplé à une clavette, qui rentre *dans* le cardan.
   - *Rôle de la clavette* : Elle bloque 100% de la rotation (effort de lacet/yaw).

3. **Verrouillage Axial (Comment empêcher le pied de tomber ?)** :
   La clavette stoppe la rotation, mais pas la translation verticale (arrachement). Pour bloquer l'insert fermement dans le cardan, deux solutions mécaniques classiques (selon le modèle de cardan acheté) :
   - **Solution B.1 (Filetage interne + Écrou Nyloc — Incassable)** : L'alésage du cardan traverse géneralement la mâchoire de part en part (jusqu'à la noix centrale). Usinez l'extrémité de votre bout d'arbre en aluminium pour le fileter (ex: M6 ou M8). Une fois l'insert en alu emmanché dans le cardan avec la clavette, venez serrer un écrou Nyloc bascule, par l'intérieur de la mâchoire du cardan. La tension de l'écrou tire l'insert et écrase sa collerette contre le bord du cardan.
   - **Solution B.2 (Vis de pression radiale — Standard industriel)** : La quasi-totalité des cardans rainurés vendus par *Michaud Chailly* ou *HPC* comportent de série un trou taraudé transversal au niveau de la rainure. Une fois l'arbre en alu et la clavette insérés, on vient visser à refus une vis pointeau sans tête (Set screw) enduite de frein fileté fort (Loctite rouge) dans ce trou. La pointeau vient mordre le dos de la clavette ou l'arbre alu : le mouvement vertical est condamné.

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

# 🛠️ Guide de Fabrication Hybride : Torse D-Bot (Architecture Cruciforme + FDM PA12-CF + CNC Alu)

*Ce document remplace le [GUIDE_Fabrication_Torse_Asimov_Hybride.md](./00_Archives_Recherche/GUIDE_Fabrication_Torse_Asimov_Hybride.md) (archivé). Il intègre l'architecture cruciforme interne (plaque sagittale à lumières 2D + traverse carbone), les 2 paniers batterie latéraux avec hot-swap, l'orientation d'impression verticale, et les manchons d'épaule en aluminium.*

> [!NOTE]
> **Évolution architecturale majeure (Mai 2026)** : Le torse passe d'une coque PA12-CF porteuse primaire à une **coque secondaire allégée** habillant un **squelette métallique cruciforme** qui reprend l'intégralité des efforts structurels.

---

## 1. Principe Architectural : Le Squelette Cruciforme Interne

### A. Philosophie de conception

Le torse du D-Bot est basé sur la coque organique de l'Asimov v1 (mise à l'échelle de +18 %), mais son architecture interne est radicalement différente :

| Élément | Ancien design (Asimov pur) | Nouveau design (D-Bot Cruciforme) |
|:---|:---|:---|
| **Structure porteuse** | Coque PA12-CF seule (6 périmètres, 35% infill) | **Squelette alu/carbone/acier cruciforme** |
| **Rôle de la coque** | Primaire (porte tous les efforts) | **Secondaire** (protection, forme, transmission locale) |
| **Colonne vertébrale** | 2 lattes alu latérales (irréalisable) | **1 plaque sagittale à lumières 2D** (dos→ventre, toute la hauteur) |
| **Traverse épaules** | Aucune | **Tube carbone Ø30mm** reliant les 2 brides de liaison d'épaule |
| **Flasques épaules** | Disques plats alu 5mm | **Carter monobloc CNC alu 6082-T6** (Plan 2D *Support RS-04* : Ø~126mm, alésage Ø120.2mm H7, paroi 3.0mm, fond 4mm évidé Ø97mm, insertion par l'extérieur) |
| **Batterie** | 1 panier coulissant central | **2 paniers latéraux** (G + D) avec hot-swap |
| **Orientation impression** | Dos au plateau (horizontal) | **Verticale** (debout sur le plan de coupe) |

### B. Schéma de la Structure Cruciforme

![Schéma d'Architecture de la Structure Cruciforme du Torse](./media/structure_cruciforme.svg)

*Schéma d'architecture 2D de la structure cruciforme du torse D-Bot : Vue de Face (Plan Frontal avec la traverse carbone Ø30mm, la plaque sagittale à lumières 2D 5mm et les moteurs RS-04/RS-06) et Vue de Dessus (Plan Transversal avec l'orientation sagittal dos->ventre et les 2 paniers batteries latéraux).*


### C. Rigidité comparée

| Sollicitation | Ancien (lattes) | Nouveau (cruciforme) | Gain | Note |
|:---|:---:|:---:|:---:|:---|
| **Flexion Pitch** (avant/arrière) | I ≈ 773 000 mm⁴ | I ≈ 600 000 mm⁴ (plaque nette + brides) | **~×0.8** | Masse ÷3 à rigidité comparable |
| **Flexion Roll** (latérale) | Bon | **Faible sans tirants** — **Bon avec 2 tirants M5 à ±60 mm** | ×1 → **×7** | Tirants M5 ±60 mm recommandés (60g) |
| **Torsion Yaw** | Très faible | Bon (boîte de torsion fermée + nervures ±45°) | **×5-8** | — |
| **Compression axiale** | Bon | Excellent | ×2 | — |

---

## 2. Plaques de Colonne Vertébrale — Conception Option B (Lumières 2D Traversantes)

### A. Spécifications Générales

| Paramètre | Valeur |
|:---|:---|
| **Matériau** | Aluminium 6061-T6, tôle de 5,0 mm |
| **Orientation** | Plan sagittal (dos → ventre), verticale sur toute la hauteur du torse |
| **Conception retenue** | **Option B (Lumières 2D Traversantes ⭐)** : Évidements 100% débouchants en 1 seule passe |
| **Dimensions brutes** | ~432 mm (hauteur totale) × **120,0 mm (profondeur max d'usinage C500)** |
| **Découpage** | En **2 parties** (Haute 142,67 mm + Basse 290,0 mm) jointes au Nœud Central d'épaule (h = 290 mm) |
| **Jonction des 2 parties** | **Nœud Demi-Coquilles CNC Alu** + Tube Carbone Ø30 mm + Goupille Verticale Z (60 mm) |
| **Fixation haute & basse** | **Équerres CNC Alu en Sandwich (L-Brackets)** fixées par vis M4 traversantes |
| **Masse totale 2 plaques** | **~355 g** (vs 668 g pleine — **économie de 313 g / -47%**) |
| **Étude de dimensionnement** | 📄 Voir **[ETUDE_Dimensionnement_Colonne_Vertebrale.md](./ETUDE_Dimensionnement_Colonne_Vertebrale.md)** pour le calcul des moments et flèches |

#### Solution de Fixation Haute et Basse (Équerres CNC L-Brackets en Sandwich)

![Solution de fixation par équerres L-Brackets en sandwich](./media/solution_liaison_embase_cou.svg)

*Principe d'assemblage en sandwich : 2 équerres en L en aluminium 6061-T6 (à gauche et à droite) enserrent la tôle de 5 mm avec 3 à 4 vis traversantes M4. Le rebord horizontal des équerres est vissé sur les plaques circulaires de cou (5 mm) et de taille (6 mm).*

---

### B. Justification & Comparatif des Formes d'Évidements

![Comparatif des options d'usinage de la colonne vertébrale](./media/comparatif_plaques_colonne.svg)

> [!IMPORTANT]
> **Décision d'Architecture (Août 2026) : Adoption de l'Option B (Lumières 2D Traversantes)**
> La solution d'évidement 2D traversant est retenue comme le choix optimal pour le torse D-Bot par rapport à l'Isogrid (Option C) :
> 1. **Solidité supérieure** : Propose un facteur de sécurité **$S_f = \times 9,21$** sous choc dynamique de 220 Nm à la base ($\sigma_{\text{max}} = 26,05\text{ MPa}$), très supérieur à l'Isogrid ($S_f = \times 5,70$).
> 2. **Gain de poids massif (-47%)** : Économise 313 g sur la colonne (masse totale = 355 g contre 668 g en plaque pleine).
> 3. **Fiabilité d'Usinage C500** : Découpée en **une seule passe 2D débouchante** en 15 minutes total. Risque de voilement ("bananage" alu) NUL et aucun retournement de pièce requis (pas de Flip Z).

![Plaques de Colonne Vertébrale Évidées 2D](./media/plaques_colonne_2d_evidees.svg)

---

### C. Fabrication CNC sur NestWorks C500

| Étape | Détail |
|:---|:---|
| **1. Bridage** | Fixer la tôle brute 6061-T6 de 5,0 mm à plat sur la table C500 (sur martyre MDF) |
| **2. Outil** | Fraise carbure Ø6 mm DLC (O-Type 1 dent) |
| **3. Paramètres de coupe** | Vitesse 10 000 tr/min, avance 800 mm/min, passes de Z = -1,25 mm (4 passes) |
| **4. Lumières 2D** | Découpe 100% débouchante à Z = -5,2 mm en une passe continue |
| **5. Contour & Perçages** | Découpe du profil sagittal + trous M4 de fixation |
| **Temps estimé** | **~15 minutes au total pour les 2 plaques** (vs 3-4h pour Isogrid) |

---

---

## 3. Traverse Horizontale (Liaison Épaules)

### A. Spécifications

> [!IMPORTANT]
> **Orientation du tube — Point fondamental** : Le tube carbone est un élément **transversal** (axe X, gauche ↔ droite). Il passe **perpendiculairement au plan sagittal** formé par les plaques de colonne vertébrale. Les plaques (Colonne Supérieure et Inférieure) sont dans le plan Y-Z (dos ↔ ventre, vertical). Le tube carbone **ne traverse pas** les plaques : il passe dans le joint entre la Colonne Supérieure et la Colonne Inférieure, au niveau de l'axe des épaules (h = 290 mm). Seules les **brides demi-coquilles** possèdent un demi-alésage Ø30 mm.

| Paramètre | Valeur |
|:---|:---|
| **Matériau** | Tube carbone 3K, époxy, Ø30 mm extérieur, épaisseur 2 mm |
| **Longueur** | ~260 mm (entraxe des carters d'épaule) |
| **Axe** | **Transversal (X)**, perpendiculaire au plan sagittal des plaques |
| **Masse** | ~70 g |
| **Rigidité torsionnelle** | J ≈ 52 000 mm⁴ (×15 par rapport à une plaque de 5 mm de même largeur) |
| **Fixation aux épaules** | Emmanché dans le socket du carter monobloc alu CNC de chaque côté, goupille Ø4 mm + bouchon de renfort |
| **Fixation centrale (nœud)** | **2 demi-coquilles CNC alu** (Bride Sup. + Bride Inf.) serrant le tube sur 45 mm de longueur, boulonnées aux plaques |

### B. Nœud d'Intersection Plaque/Traverse — Système Demi-Coquilles

> [!IMPORTANT]
> **Évolution architecturale (Juillet 2026)** : La "Grande Bride Sagittale Longue" monobloc est remplacée par un système de **deux demi-coquilles distinctes** (Bride Supérieure + Bride Inférieure), inspiré du principe du chapeau de bielle / split clamp block. Ce design est mécaniquement supérieur (distribution d'effort ×6, pas de taraudage dans les brides, assemblage sans outil spécialisé).

![Nœud d'intersection — Système Demi-Coquilles Alu CNC](./media/noeud_demi_coquilles_bride.svg)

*Vue en coupe frontale (plan sagittal Y-Z) et vue de dessus (plan transversal X-Y) du nœud d'intersection. Le tube carbone Ø30 mm est transversal (axe X), il sort perpendiculairement au plan des plaques. La Bride Supérieure s'appuie sur la face inférieure de la Colonne Supérieure via ses ailes en L ; la Bride Inférieure s'appuie sur la face supérieure de la Colonne Inférieure. Les deux brides sont serrées l'une contre l'autre par 2× vis M6 traversantes + écrous Nylstop, créant le pincement du tube carbone sur 45 mm de longueur.*

Cette architecture offre 4 bénéfices d'ingénierie majeurs :

1. **Plaques de colonne 100% continues** :
   - Aucun trou dans les tôles de 5 mm — la plaque isogrid reste intacte à l'endroit de l'effort maximal (h = 290 mm, M = 131 Nm dynamique).
   - Le tube carbone passe dans le **joint naturel** entre les deux demi-plaques, sans découpe.
2. **Distribution d'effort sur toute la largeur des plaques (120 mm)** :
   - Les ailes en L des brides portent sur toute la largeur des plaques (120 mm dos → ventre).
   - Contrainte de contact divisée par ~6 par rapport à un rebord court de 20 mm.
3. **Pincement fiable sans taraudage dans les brides** :
   - Vis de serrage **traversantes** (bride sup. → bride inf.) avec écrous Nylstop → aucun taraudage en alu sous effort répété.
   - Idem pour la fixation des plaques : vis M4 traversantes + Nylstop dans les ailes en L.
4. **Verrouillage positif par goupille Ø4 mm (axe Z, vertical)** :
   - Anti-rotation ET anti-translation axiale du tube carbone dans les brides.
   - Goupille traversant la Bride Sup, le tube et la Bride Inf de haut en bas en axe Z (60 mm total).

#### Dimensionnement Mécanique du Nœud

| Paramètre | Valeur | Justification |
|:---|:---:|:---|
| **Charge dimensionnante** | 2 400 N (tangentiels) | Torsion Yaw RS-06 : M_yaw = 36 Nm / R_tube = 15 mm |
| **Force de serrage requise** | ~17 000 N (radiale totale) | F_serg = F_tang / µ × S_f = 2 400 / 0,35 × 2,5 |
| **Vis de pincement tube** | **4× M6 traversant + Nylstop** | 2 côté DOS + 2 côté VENTRE — de chaque côté de la plaque (X≈10mm et X≈35mm) — F_total = 4 × 14 500 N = 58 000 N — S_f = ×3.4 ✅ |
| **Longueur de portée tube** | **45 mm** (axe X) | p_contact = 8 500 N / (45 × 30) = 6,3 MPa << 15 MPa adm. composite ✅ |
| **Profondeur sagittale brides** | **120 mm** (axe Y) | Appui pleine largeur des plaques |
| **Vis de fixation plaques** | **4× M4 traversant + Nylstop** par bride | Ailes en L intégrées aux brides |
| **Goupille anti-rotation + centrage** | **Ø4 mm élastique inox, axe Z (vertical)** | Traversante complète : Bride Sup (15mm) + tube (30mm) + Bride Inf (15mm) — 60 mm total — percée en 1 seule passe 3 axes C500 — double cisaillement S_f = ×6,3 ✅ |
| **Espace vertical requis (axe Z)** | ~90 mm | 30 mm tube + 2× 30 mm brides — validé CAO (127 mm dispo.) ✅ |

#### Spécifications des Pièces CNC

**Bride Supérieure (Demi-Coquille Haute) — Alu 6061-T6 :**

| Feature | Dimension | Note |
|:---|:---:|:---|
| **Longueur (axe X, portée tube)** | 45 mm | Pression contact = 6,3 MPa — protège le composite |
| **Profondeur (axe Y, sagittale)** | 120 mm | Appui pleine largeur des plaques |
| **Hauteur corps bride (axe Z)** | ~30 mm | Paroi min. 5 mm au-dessus du demi-alésage R = 15 mm |
| **Demi-alésage tube** | R = 15 mm (demi-Ø30) | Fraisage cylindrique sur toute la longueur 45 mm |
| **Ailes en L (appui plaque sup.)** | 120 mm × 10 mm | Face plane d'appui + rebord centrage épaisseur 5 mm |
| **Vis de pincement (axe Z)** | **4× M6 lisse Ø6,3 mm** | 2 côté DOS (Y≈10mm) + 2 côté VENTRE (Y≈110mm) — à X≈10mm et X≈35mm de chaque bord (de part et d'autre de la plaque) — Nylstop M6 |
| **Vis de fixation plaque (aile L)** | 4× M4 lisse Ø4,2 mm | Traversant plaque + bride — écrou Nylstop M4 |
| **Perçage goupille (axe Z)** | Ø4 mm H7, **Axe Z (vertical)** | Trou vertical de haut en bas — percé en 1 seule passe 60 mm avec Bride Inf. assemblée |
| **Centrage plaque** | Rebord 5 mm (aile L) | Obstacle mécanique biface — pas de réglage à l'assemblage |

**Bride Inférieure (Demi-Coquille Basse) — miroir de la Bride Supérieure :**

| Feature | Dimension | Note |
|:---|:---:|:---|
| **Géométrie générale** | Miroir de la Bride Sup. | 1 seul programme CAM — flip de pièce |
| **Demi-alésage tube** | R = 15 mm, orienté vers le haut | Idem Bride Sup. |
| **Ailes en L (appui plaque inf.)** | 120 mm × 10 mm | Idem Bride Sup. |
| **Vis de pincement (axe Z)** | **4× trous M6 lisse** | Nut-side — écrous Nylstop M6 — positions identiques à Bride Sup. |
| **Vis de fixation plaque (aile L)** | 4× M4 lisse | Idem Bride Sup. |
| **Perçage goupille (axe Z)** | Ø4 mm H7, Axe Z (vertical) | Sortie inférieure du trou vertical 60 mm |

| **Jeu de Pincement (Split Gap)** | **0,8 mm à 1,0 mm** au plan de joint | Dépouille de serrage : évite le contact alu/alu avant le pincement du tube |

> [!IMPORTANT]
> **Règle de l'Art pour l'Usinage des Brides (Dépouille de Pincement / Split Gap)** :
> Si les deux brides étaient usinées avec deux demi-cercles exacts de 15,00 mm de profondeur sans jeu, leurs faces plates entreraient en contact ("butée alu contre alu") **avant** de développer toute la pression radiale sur le tube carbone. Le moindre sous-dimensionnement du tube (ex. Ø29,90 mm) rendrait le serrage inefficace.
>
> **Méthodes d'usinage préconisées sur C500 :**
> - **Option A (Surfaçage CAM — Recommandé)** : Retirer **0,4 mm à 0,5 mm de matière** sur la face plate de joint de chaque demi-bride. La profondeur du demi-alésage passe à **14,5 mm** au lieu de 15,0 mm. À l'assemblage autour du tube Ø30,00 mm, il reste un jeu résiduel garanti de **0,8 mm à 1,0 mm** entre les brides. 100% de la force des vis M6 est transmise en pincement radial direct.
> - **Option B (Usinage avec cale d'épaisseur — Shimmed Boring)** : Assembler les 2 blocs bruts d'alu avec une cale d'épaisseur (shim) de 1,0 mm au centre, puis usiner l'alésage Ø30,00 mm H7 assemblé. Retirer la cale après usinage.
>
> **Sécurité du Serrage vs Écrasement Carbone** :
> - Serrer les 4× vis M6 à un couple maîtrisé de **6 N.m à 8 N.m**.
> - Pression de contact résultante = **15 à 18 MPa** (parfaitement dans la limite admissible de 20 MPa du composite carbone).
> - Force de friction seule = **~12 000 N** (Facteur de sécurité par friction S_f > 5 par rapport aux 2 400 N requis par le moteur RS-06).
> - La goupille Ø4 mm verticale verrouille de surcroît tout mouvement par obstacle positif.

> [!IMPORTANT]
> **La goupille traversante complète — Triple rôle** : Percée à Z = 0 (axe neutre de flexion = affaiblissement minimal du tube) à travers **les deux brides + les deux parois du tube** en une seule passe. Elle assure simultanément : (1) anti-rotation du tube autour de X, (2) anti-translation axiale du tube (axe X), (3) pion de centrage de précision des 2 demi-coquilles entre elles. C'est la solution la plus simple, la plus robuste et la plus équilibrée mécaniquement.

#### Séquence d'Assemblage du Nœud

```
Étape 1 : Insérer le tube carbone dans la Bride Inférieure (demi-alésage orienté vers le haut)
          → Le tube repose dans la demi-coquille

Étape 2 : Poser la Bride Supérieure par-dessus (demi-alésage vers le bas)
          → Les 2 brides forment l'alésage complet Ø30 mm autour du tube

Étape 3 : Insérer les 4× vis M6 traversantes en rectangle
          → 2 côté DOS : une à X≈10mm et une à X≈35mm (de chaque côté de la plaque)
          → 2 côté VENTRE : idem aux mêmes positions en X
          → Serrer les 4 écrous Nylstop M6 au DOIGT uniquement (maintien sans serrage final)

Étape 4 : PERCER la goupille Ø4 mm EN UNE SEULE PASSE VERTICALE (axe Z)
          Percer de haut en bas (60 mm total) à travers : Bride Sup (15mm) + paroi tube haut (2mm) + creux tube (26mm) + paroi tube bas (2mm) + Bride Inf (15mm)
          → La passe unique 3 axes sur C500 garantit l'alignement parfait des alésages
          → Insérer la goupille élastique Ø4 mm × 60 mm (inox) par pression (maillet plastique)
          → Triple rôle : anti-rotation tube + anti-translation axiale + pion de centrage brides ✅

Étape 5 : Serrer les 4× vis M6 au couple final (8 N.m)
          → F_serrage total = 4 × 11 600 N = 46 400 N — S_f = ×2.7 — tube pincé sur 45 mm
          → Appliquer Loctite 243 côté écrou sur chacune

Étape 6 : Placer le sous-ensemble [brides + tube] entre Colonne Supérieure et Colonne Inférieure
          → Les ailes en L des brides viennent enserrer la tôle de 5,0 mm de chaque côté
          → Insérer les 4× vis M4 traversantes par bride et serrer les écrous Nylstop M4 au couple (4 N.m)
```

### B.1 — Stratégie de Fabrication & Montage Hors-Torse sur NestWorks C500

Cette section couvre les opérations de perçage des goupilles sur l'ensemble du sous-système tube carbone. L'approche recommandée est un **montage hors-torse** permettant de réaliser tous les perçages critiques sur CNC C500 avant intégration dans la coque PA12-CF.

#### Récapitulatif des 3 types de goupilles

| Goupille | Position | Direction | Diamètre | Profondeur | Outillage C500 |
|:---|:---|:---:|:---:|:---:|:---|
| **Nœud central** | Brides demi-coquilles (centre torse) | **Axe Z (Vertical)** | Ø4 mm H7 | **60 mm** | **C500 — 3 axes direct (broche Z)** |
| **Ancrage épaule gauche** | Carter alu + tube extrémité gauche | Axe Z (Vertical) | Ø3 mm H7 | 30 mm | C500 — 3 axes direct |
| **Ancrage épaule droit** | Carter alu + tube extrémité droit | Axe Z (Vertical) | Ø3 mm H7 | 30 mm | C500 — 3 axes direct |

---

#### Phase 1 — Usinage CNC C500 : Brides et Carters (3 axes standard)

La C500 (course utile ~230 × 213 × 128 mm) est parfaitement adaptée à toutes les opérations d'usinage des pièces individuelles.

---

#### Phase 2 — Perçage Goupille Nœud Central (Axe Z, 60 mm) — **100% 3 Axes Direct sur C500**

> [!TIP]
> **La goupille étant VERTICALE (axe Z), cette opération s'effectue en 3 axes directs par la broche Z de la NestWorks C500.** Aucun 4ème axe rotatif n'est nécessaire. La profondeur totale de 60 mm laisse une garde Z très confortable de **68 mm** (sur la course de 128 mm de la machine).

**Principe :** Le sous-ensemble [Bride Sup + Tube + Bride Inf] (maintenu par les 4 vis M6 serrées au doigt) est posé à plat sur la table de la C500. La broche descend verticalement selon l'axe Z pour percer de haut en bas sur 60 mm.

**Séquence de perçage vertical Z — CNC C500 :**

```
MONTAGE :

1. Assembler les 2 brides autour du tube (étapes 1-3 de la séquence principale)
   → 4× M6 serrés AU DOIGT (maintien sans serrage final)

2. Poser le sous-ensemble [Bride Sup + Tube + Bride Inf] à plat sur la table CNC (sur cales de précision)
   → Brider les ailes en L sur la table
   → Palper la face supérieure de la Bride Sup avec le Touch Probe 3D (Z = 0 référence)

PERÇAGE CNC (programme CAM 3 axes) :

3. Perçage Ø3,8 mm — cycle peck drilling G83 (dégagement copeaux)
   → Vitesse broche : ~800 tr/min (CFRP + alu)
   → Avance : ~50 mm/min
   → Profondeur : 60 mm exacts (15mm Alu Sup + 2mm CFRP + 26mm vide + 2mm CFRP + 15mm Alu Inf)
   → Pas de peck : 3 mm (évacuation continue des poussières)

4. Alésage Ø4mm H7 (fraise Ø4mm DLC en interpolation hélicoïdale sur les 5mm supérieurs et 5mm inférieurs)
   → Précision CNC ±0,02 mm

5. Insérer la goupille élastique Ø4 mm × 60 mm inox (frappe légère au maillet plastique)

6. Serrer les 4× M6 au couple final (10 N.m + Loctite 243)
```

---

#### Récapitulatif Final — Faisabilité C500

| Opération | Faisable C500 | Mode CNC | Profondeur | Priorité |
|:---|:---:|:---|:---:|:---:|
| Usinage brides (alésage, trous, ailes L) | ✅ Oui | 3 axes standard | 30 mm | Critique |
| **Perçage goupille nœud Ø4mm H7 (axe Z)** | ✅ **Oui** | **3 axes direct (broche Z)** | **60 mm** | **Critique** |
| Usinage carters épaule acier E470 | ✅ Oui | 3 axes standard | 43 mm | Critique |
| Perçage goupilles épaule Ø3mm H7 (axe Z) | ✅ Oui | 3 axes direct | 30 mm | Important |
| Vissage M4 stator RS-04 | ✅ Simplifié | Trous lisses Ø 3,3 mm + vis CHC M4 | — | Simplifié |

> [!IMPORTANT]
> **Conclusion : TOUTES les opérations de perçage du torse sont réalisables en 3 axes direct sur la NestWorks C500**, avec une grande simplicité et sans outillage rotatif 4ème axe.

---

### C. Carter Monobloc CNC (Support RS-04 en Acier E470 & Collet PA12-CF)

Pour maximiser la rigidité, la dissipation thermique et la précision géométrique, l'épaule adopte le carter monobloc **Support RS-04 usiné en Acier E470 (Plan 2D David SERGENT)** :
1. **Le fond d'embase (4,0 mm avec évidement Ø 97 mm)** : Sert de flasque d'ancrage arrière pour le stator et prend l'appui direct des 10× vis CHC M4 × 10 mm.
2. **Le manchon cylindrique de cerclage (1,9 mm)** : Entoure le corps du moteur RS-04 sur 360° (Ø ext 124,0 mm, alésage Ø 120,2 mm H7) pour supprimer l'ovalisation et dissiper les calories.
3. **L'ancrage du tube carbone Ø 30 mm** : Reçoit l'extrémité du tube carbone et la goupille d'arrêt verticale.

#### Vue d'ensemble et Séquence d'assemblage (Schéma Conceptuel & Rendu 3D)

![Vue éclatée schématique coaxiale de l'assemblage carter monobloc](./media/bride_tube_carbone_eclatee.svg)

*Schéma conceptuel coaxial (de gauche à droite) : ① 10× Vis CHC M4 × 10 mm, ② Ancrage tube carbone Ø30 mm avec goupille Ø4 mm, ③ Carter Monobloc Acier E470 (Flasque 4,0 mm évidée Ø97 mm + Cerclage 360° 1,9 mm), ④ Poche du collet PA12-CF de la coque torse, ⑤ Moteur RobStride RS-04 inséré par l'avant (façade extérieure épaule).*

#### Vue en coupe — Détail interne

![Coupe longitudinale A-A du détail interne de l'ancrage carbone dans le carter acier E470](./media/bride_tube_carbone_coupe.svg)

*Coupe longitudinale A-A révisée : le tube carbone (Ø 30 × 26 mm) est renforcé par le **bouchon alu interne anti-écrasement** (Ø 26,0 mm ext, Ø 18,0 mm int, 35 mm de long) collé à l'époxy structurale. L'ensemble s'insère sur **35 mm de longueur de portée** dans le socket du carter monobloc Acier E470 CNC. Il est pincé par la bride fendue (2× vis M4) et verrouillé par la **goupille élastique inox universelle Ø 4,0 mm × 35 mm** (rouge) traversant perpendiculairement l'axe Z.*

#### Orientations des éléments (référentiel)

> [!IMPORTANT]
> **Axes de référence** — Indispensables pour la modélisation Fusion 360 :
>
> | Élément | Orientation | Direction |
> |:---|:---|:---|
> | **Axe du tube carbone** | Horizontal (X) | L'axe principal de la traverse |
> | **Goupille élastique Ø 4,0 mm** | **Perpendiculaire au tube** (Z, Verticale) | Traverse de haut en bas : paroi bride → paroi tube → bouchon alu → paroi tube → paroi bride |
> | **Fente de serrage (Clamp Socket)** | **Axiale** — le long du tube (X) | Fente de 0,8 à 1,0 mm sur la longueur de 35 mm de la bride |
> | **Vis M4 de pincement (×2)** | **Enjambent la fente** perpendiculairement | Compriment les 2 moitiés de la bride pour resserrer la fente à 6 N.m |

#### Conception V1 de la Bride d'Épaule (Pincement + Goupille Ø 4,0 mm)

> [!TIP]
> **Double sécurité retenue en V1 (Pincement + Obstacle Positif)** :
> 1. **Pincement Radial (35 mm de portée)** : 2× vis CHC M4 compriment la fente axiale (0,8 à 1,0 mm). La pression de contact (~12 MPa) sur 35 mm développe plus de 10 000 N de friction, éliminant tout micro-jeu angulaire et amortissant les vibrations.
> 2. **Protection Composite (Bouchon Anti-Écrasement)** : Le bouchon alu creux Ø 26,0 mm ext / Ø 18,0 mm int (longueur 35 mm) absorbe la pression radiale des vis sans déformer les fibres carbone.
> 3. **Verrouillage par Obstacle (Goupille Ø 4,0 mm)** : La goupille Mécanindus Inox Ø 4,0 mm traversante verrouille définitivement la translation et la rotation en cas de choc extrême.

#### Synthèse d'Ingénierie & Dimensionnement CAO (Aluminium 7075-T6)

> [!NOTE]
> **Étude Matériau & Épaisseur Radiale (Aluminium 7075-T6 / Fortal)** :
> - **Propriétés Mécaniques** : Limite d'élasticité $R_e = 500\text{ MPa}$ (+82% vs Alu 6061-T6), Module d'Young $E = 71\text{ GPa}$.
> - **Paroi Radiale Optimale ($t = 5,0\text{ mm}$)** : L'Alu 7075-T6 permet de réduire l'épaisseur radiale à **5,0 mm** (`Ø 40,0 mm ext`) en conservant une rigidité extrême sous le pincement M4 ($SF > 15$).
> - **Flexibilité de Charnière** : La haute limite élastique garantit un pincement de fente fluide et réversible sans risque de déformation plastique ou de fatigue de l'aluminium.

#### Spécifications Cotées pour la Modélisation Fusion 360

| Feature CAO | Dimension Retenue | Tolérance | Note d'Ingénierie Fusion 360 |
|:---|:---:|:---:|:---|
| **Matériau Bride** | **Aluminium 7075-T6** | — | Fortal / Ergal ($R_e = 500\text{ MPa}$) |
| **Alésage intérieur ($D_{\text{int}}$)** | **30,05 mm** | H7 (+0,021/0) | Ajustement glissant doux pour tube carbone Ø 30,0 mm |
| **Longueur de portée ($L_{\text{serrage}}$)** | **35,0 mm** | ±0,2 mm | Portée optimale (1,17 × Ø tube) |
| **Diamètre extérieur ($D_{\text{ext}}$)** | **Ø 40,0 mm** | h8 (-0,039/0) | **Épaisseur de paroi radiale $t = 5,0\text{ mm}$** (Masse ~45 g) |
| **Bouchon interne alu** | **Ø 26,0 ext / Ø 18,0 int** | h6 (-0,013/0) | Longueur **34,5 mm** (jeu d'isostatisme axial de **0,5 mm** au fond), **Alu 7075-T651**, collé époxy (âme anti-écrasement & iso-rigidité $E = 71\text{ GPa}$) |
| **Butée axiale de fond** | **Flasque 5,0 mm monobloc** | ±0,1 mm | **Appui direct du tube carbone (35,0 mm) sur la face avant de la flasque Alu 7075-T6 (5,0 mm)** — Aucun rebord supplémentaire de 3 mm requis, la flasque forme la butée naturelle indéformable |
| **Fente axiale de pincement** | **1,0 mm** | ±0,1 mm | Fente radiale sur toute la longueur (35,0 mm) au sommet (axe Z) |
| **Visserie de pincement** | **2× Vis CHC M4 × 25 mm + Écrous Nylstop** | — | Vis traversantes (Ø 4,3 mm) + écrous frein sur **méplats d'appui parallèles de 10,0 mm** (vis #1 à **8,0 mm** du bord, vis #2 à **25,0 mm** du bord, entraxe **17,0 mm**) |
| **Perçage goupille universelle** | **Ø 4,0 mm traversant** | H7 (+0,012/0) | **Chanfrein d'entrée 0,5 mm × 45° obligatoire** — Axe vertical Z, positionné à **16,0 mm** du bord (entre les vis M4) |

#### D. Directive d'Approvisionnement Matière Première (Blockenstock)

> [!IMPORTANT]
> **Commandes de Matière Première à passer sur Blockenstock** :
> 1. **Carters d'Épaule (Acier E470)** :
>    - Produit : [Ébauche creuse d131 / d88 au cm - Acier E470 - Blockenstock](https://www.blockenstock.fr/d131-d88-au-cm-acier-e470-c2x42431541)
>    - Quantité : **2 pièces de 4 cm (40 mm)** d'épaisseur (laisse 1,0 mm de surépaisseur de surfaçage pour obtenir $H = 39,0\text{ mm}$ net sur la C500).
> 2. **Bouchons Internes Anti-Écrasement (Aluminium 7075-T651)** :
>    - Produit : [Barre ronde Ø 30x500mm Alu 7075-T651 - Blockenstock](https://www.blockenstock.fr/c-30x500mm-alu-7075-file-t651-c2x21035319)
>    - Quantité : **1 barre de 500 mm (50 cm)** d'Aluminium 7075-T651 Ø 30 mm.
>    - **Justification d'Ingénierie** : L'Alu 7075-T651 offre une limite d'élasticité exceptionnelle ($R_e = 500\text{ MPa}$), une masse minimale par bouchon (**27,2 g** vs 76,0 g en acier, soit -97,6 g économisés sur le buste), une usinabilité parfaite sur la C500, et une **iso-rigidité radiale** ($E = 71\text{ GPa}$) identique à la bride extérieure pour une pression de pincement 100% uniforme sans écrasement du tube carbone.
> 3. **Bruts pour Brides d'Épaule (Aluminium 7075-T651)** :
>    - Produit : [Disque Ø 120 x 50mm Alu 7075-T651 - Blockenstock](https://www.blockenstock.fr/c120x-50mm-alu-7075-c2x29739222)
>    - Quantité : **2 disques de 50 mm** de hauteur en Aluminium 7075-T651 Ø 120 mm.
>    - **Justification d'Ingénierie** : La hauteur totale hors-tout de la bride d'épaule monobloc en CAO est de **49,20 mm**. Le disque brut de 50 mm d'épaisseur offre une surépaisseur de surfaçage idéale de **0,80 mm** pour blanchir les deux faces et obtenir la hauteur de 49,20 mm net au centième près sur la CNC C500.

#### Rendu 3D & Dessins d'Ingénierie de la Bride d'Épaule (Alu 7075-T6)

![Rendu 3D de la bride de liaison alu](./media/bride_tube_carbone.png)

*Rendu 3D de la bride de liaison d'épaule en Aluminium 7075-T6.*

![Dessin coté multi-vues de la bride de liaison](./media/bride_tube_carbone_cotee.png)

*Dessin coté multi-vues (avant, arrière, coupe B-B, isométrique) avec tolérances d'usinage.*

![Coupe longitudinale de la bride alu et de l'épaulement de butée axiale](./media/bride_tube_carbone_coupe.svg)

*Coupe axiale vectorielle révisée d'ingénierie montrant la butée axiale de fond (3.0 mm), le bouchon alu 7075, la goupille Inox Ø4.0 mm et les vis M4 traversantes.*

![Vue éclatée schématique de la bride alu](./media/bride_tube_carbone_eclatee.png)

*Vue éclatée coaxiale montrant les composants d'ancrage de la bride.*

![Workflow Fusion 360 pour la bride alu](./media/bride_tube_carbone_fusion360.png)

*Workflow de modélisation CAO sous Fusion 360 en 5 étapes.*

![Coupe axiale d'épaule assemblée finale](./media/coupe_axiale_epaule_finale.png)

*Coupe axiale 3D révisée de l'assemblage complet d'épaule (Acier E470 + RS-04 + Tube carbone).*

#### Guide de Modélisation Fusion 360 (5 étapes)

#### E. Validation d'Ingénierie Finale du Design CAO Fusion 360 (Vérification epaule1 à epaule9)

L'analyse d'ingénierie mécanique des 9 captures d'écran CAO issues de la modélisation sous Fusion 360 valide définitivement le design d'épaule quasi-final pour la fabrication CNC C500.

![Vue d'Ensemble 3D Fusion 360 de l'Assemblage d'Épaule Quasi-Final](./media/epaule_cao_1_vue_ensemble.png)

*Figure 3.1 (epaule1) : Vue d'ensemble 3D de l'assemblage complet d'épaule : les 2 plaques H-bracket identiques (orange) en Aluminium 7075-T6 (5.0 mm), la bride d'ancrage d'épaule monobloc (jaune) en Aluminium 7075-T651 (48.20 mm total), le tube carbone Ø30 mm (bleu) et le moteur RS-04.*

![Vue de Profil du Sandwich Épaule](./media/epaule_cao_2_vue_profil.png)

*Figure 3.2 (epaule2) : Vue de profil de l'assemblage montrant le sandwich axial parfait : Plaque avant orange (5.0 mm) -> Moteur RS-04 (41 mm) -> Plaque arrière orange (5.0 mm) + Bride d'ancrage jaune (48.20 mm).*

![Mesure d'Emprise de 35.00 mm du Tube Carbone](./media/epaule_cao_3_cotation_emprise_35mm.png)

*Figure 3.3 (epaule3) : Cotation CAO de la longueur de portée de l'alésage tube carbone : **35.00 mm net** (ratio L/D = 1.17, supérieur au minimum préconisé ISO 1.0×D = 30.0 mm).*

![Mesure de l'Épaisseur du Flasque Plat de 13.20 mm](./media/epaule_cao_4_cotation_flasque_13.2mm.png)

*Figure 3.4 (epaule4) : Cotation CAO de l'épaisseur de la flasque d'embase de la bride jaune : **13.20 mm net** (garantissant un facteur de sécurité en flexion Sf > 50).*

![Validation de l'Épaisseur de 5.00 mm de la Plaque 7075-T6](./media/epaule_cao_5_cotation_plaque_5mm.png)

*Figure 3.5 (epaule5) : Cotation CAO de l'épaisseur de la plaque H-bracket orange : **5.00 mm net en Aluminium 7075-T6** (Re = 460 MPa). Optimum d'ingénierie mécanique (Sf = 10.7 en bending de couronne et Sf = 53.1 en flexion d'oreilles).*

![Vue Face Avant Bras RS-04 et Vis M5 Stator](./media/epaule_cao_6_vue_face_bras_6xM5.png)

*Figure 3.6 (epaule6) : Vue de face avant (côté bras) du moteur RS-04 montrant les vis M5 sur PCD Ø144 mm et le débouché du stator.*

![Vue Face Arrière Torse et Ancrage Tube Carbone](./media/epaule_cao_7_vue_arriere_torse.png)

*Figure 3.7 (epaule7) : Vue face arrière (côté torse) montrant l'intégration de la bride d'ancrage jaune et de la colonne vertébrale (5.0 mm).*

![Validation de la Hauteur Hors-Tout de 48.20 mm de la Bride Monobloc](./media/epaule_cao_8_hauteur_hors_tout_48.2mm.png)

*Figure 3.8 (epaule8) : Mesure de la hauteur hors-tout axiale de la bride d'épaule monobloc : **48.20 mm net**. Cette hauteur valide parfaitement l'achat du disque brut [Ø 120 × 50 mm Alu 7075-T651 chez Blockenstock](https://www.blockenstock.fr/c120x-50mm-alu-7075-c2x29739222), laissant 0.80 mm de surépaisseur pour un surfaçage parfait des deux faces.*

![Validation de l'Évidement Central Ø95 mm des Plaques H-Bracket](./media/epaule_cao_9_evidement_central_95mm.png)

*Figure 3.9 (epaule9) : Vue axiale de la plaque H-bracket orange montrant l'évidement central **Ø 95.0 mm** (couronne annulaire Ø120/Ø95 mm). Cet évidement procure un **gain de masse massif de -100 g par plaque (-400 g total sur le torse)** tout en dégageant le passage des câbles XT30/CAN-FD et l'aération directe du stator RS-04.*

> [!TIP]
> **Synthèse des 5 Paramètres Clefs Validés (Fusion 360 Quasi-Final)** :
> 1. **Épaisseur des Plaques (5.0 mm)** : Validée à 5.0 mm net en Alu 7075-T6 (2 plaques identiques avant + arrière).
> 2. **Évidement Central Ø 95 mm** : Découpé sur les 2 plaques H-bracket orange, économisant ~400 g sur le torse.
> 3. **Hauteur Hors-Tout Bride (48.20 mm)** : Hauteur totale de 48.20 mm net, permettant un surfaçage idéal de 0.80 mm à partir du disque brut Blockenstock **Ø 120 × 50 mm Alu 7075-T651**.
> 4. **Longueur du Bouchon Alu (34.5 mm)** : Bouchon interne de 34.5 mm de longueur net avec 0.5 mm de jeu axial au fond pour garantir l'appui isostatique du tube carbone (35.0 mm).
> 5. **Reprise de Couple Hybride (120 Nm)** : Pincement radial 2× M4 (89 Nm) + Goupille Ø 4.0 mm Mecanindus (31 Nm résiduel) = 120 Nm max couverts avec Sf = 3.0 en nominal.

---

---

## 4. Carter Monobloc d'Épaule (Acier E470 / Alu 6061-T6) et Collet PA12-CF

### A. Concept : Carter ouvert à l'avant + Flasque arrière intégrée + Insertion par l'extérieur

> [!NOTE]
> **Évolution & alternative retenue (Août 2026)** : La cage H-bracket (2 plaques **7075-T6 5mm identiques**, fixées chacune par 10 vis M4 sur PCD Ø106mm au stator + 2 tirants axiaux M5) **remplace le carter en acier E470**. Ce remplacement permet un gain de masse significatif tout en offrant la rigidité en Roll requise (flèche cou < 0.1 mm).

> [!IMPORTANT]
> **Révision architecturale majeure (Juillet 2026)** : L'ancien concept d'insertion du moteur par l'intérieur (avec lip avant) est remplacé par une **insertion du moteur par l'extérieur (Front-Loading)** dans un **carter monobloc CNC (Acier E470 retenu en secours)** ou dans la **cage H-Bracket 7075-T6 (Retenue V1)**. Ce design offre 4 avantages majeurs :
> 1. **Maintenabilité optimale** : Le RS-04 se monte et se démonte directement par le flanc du robot sans toucher au reste de l'intérieur du torse.
> 2. **Plaquage 100% métal-métal** : La face du stator plaque directement contre la plaque en alu 7075-T6 de 5.0 mm.
> 3. **Appui de vis 100% métal** : Les vis M4 s'appuient sur la plaque alu 7075-T6 (élimination totale du risque de fluage du PA12-CF).
> 4. **Intégration monobloc / cage** : La bride d'ancrage jaune (7075-T651, 48.2mm) vient se fixer par-dessus la plaque arrière orange et assure l'ancrage sur le tube carbone Ø30mm.


### B. Le Carter Monobloc : Option Alu 6061-T6 (Historique) & Plan Officiel Acier E470 (David SERGENT)

Le carter monobloc d'épaule est un **cylindre en acier E470 ouvert à l'avant avec flasque arrière évidée** :

#### 1. Plan de Définition CAO 2D (`Support RS-04` — David SERGENT 03/08/2026)

![Plan de Définition 2D — Support RS-04 en Acier E470 par David SERGENT](./media/plan_2d_support_rs04_acier_e470.png)

*Plan de Définition 2D officiel du Support RS-04 en Acier E470 (par David SERGENT — 03/08/2026) : Ø ext 124,0 mm, alésage Ø 120,2 mm H7, paroi 1,9 mm, fond 4,0 mm évidé à Ø 97,0 mm, 10× perçages Ø 3,3 mm sur PCD Ø 106,0 mm.*

#### 2. Schéma Vectoriel d'Assemblage en Coupe Axiale

![Coupe axiale du carter monobloc acier E470 d'épaule](./media/manchon_acier_e470_coupe_axiale.svg)

*Coupe axiale révisée du Support RS-04 en acier E470 CNC (gris acier) avec sa flasque arrière de 4,0 mm (évidement central Ø 97,0 mm) et sa paroi cylindrique 360° de 1,9 mm (Ø ext 124,0 mm). Le moteur RS-04 (orange) s'insère **par l'avant (extérieur de l'épaule)**. Les 10× vis CHC M4 × 10 mm (rouge) s'insèrent depuis l'intérieur du torse et traversent la flasque acier E470 pour se visser directement dans le stator.*

> [!CAUTION]
> **OUVERT À L'AVANT.** L'avant du carter reste complètement ouvert pour permettre le glissement et l'extraction du moteur RS-04 depuis l'extérieur de l'épaule.

#### 3. Spécifications du Plan CAO Officiel `Support RS-04` (David SERGENT — Révision 04/08/2026)

> [!NOTE]
> **Cotes officielles du Plan de Définition CAO (`Support RS-04`)** :
> - **Matériau** : **Acier E470** (ébauche creuse Blockenstock d131 / d88)
> - **Diamètre extérieur final ($D_{\text{ext}}$)** : **Ø 124,0 mm**
> - **Diamètre intérieur alésage ($D_{\text{int}}$)** : **Ø 120,2 mm H7** ($120,2 + 2 \times 1,9 = 124,0\text{ mm}$)
> - **Épaisseur de paroi cylindrique** : **1,9 mm**
> - **Hauteur axiale totale ($H$)** : **39,0 mm** (Profondeur utiles de la poche alésée = **35,0 mm**)
> - **Épaisseur du fond (flasque d'embase)** : **4,0 mm**
> - **Évidement central arrière** : **Ø 97,0 mm** (ouverture pour connectique et allégement de masse)
> - **PCD Perçages Stator Arrière** : **10× perçages Ø 3,3 mm** sur cercle de **Ø 106,0 mm**

> [!TIP]
> **🛒 Directive d'Approvisionnement Matière Première (Blockenstock)** :
> - **Composant à commander** : **2 pièces de 4 cm (40 mm)** d'épaisseur de [Ébauche creuse d131 / d88 au cm - Acier E470 sur Blockenstock](https://www.blockenstock.fr/d131-d88-au-cm-acier-e470-c2x42431541).
> - **Justification d'usinage C500** : Les tronçons bruts de **40 mm** laissent une surépaisseur idéale de **1,0 mm** pour le surfaçage de la face avant, garantissant l'obtention de la hauteur finale de **39,0 mm** avec une tolérance parfaite sur la CNC C500.

---

#### 4. Étude Comparative d'Ingénierie : Aluminium 6061-T6 vs Acier E470 (Plan Officiel 1,9 mm / Ø 124 mm)

Une étude approfondie d'ingénierie mécanique compare l'option historique Aluminium 6061-T6 aux cotes officielles du plan 2D **Acier E470 (Plan `Support RS-04`)** :

| Critère de Dimensionnement | Option A : Aluminium 6061-T6 (Historique) | Option B : Acier E470 (🏆 PLAN OFFICIEL 2D) | Justification Technique |
|:---|:---:|:---:|:---|
| **Module d'Young (E - Rigidité)** | 69 GPa | **210 GPa** | **L'acier E470 est 3,04× plus rigide** |
| **Limite d'Élasticité (Re)** | 275 MPa | **470 MPa** | **+71% de résistance à la plastification** |
| **Épaisseur de Paroi Cylindrique** | 3,0 mm | **1,9 mm** | **Ø ext final carter = 124,0 mm** |
| **Diamètre Alésage Intérieur** | 120,0 mm H7 | **120,2 mm H7** | **Ajustement d'encastrement idéal RS-04** |
| **Hauteur Axiale Totale** | 52,2 mm | **39,0 mm** (Poche 35 mm) | **Logement ajusté sur 90% du stator** |
| **Épaisseur du Fond (Flasque)** | 6,0 mm | **4,0 mm** (Évidement Ø 97 mm) | **+53% plus rigide en flexion hors-plan** |
| **Rigidité Flexion Paroi Cylindrique** | 1,0 (Référence) | **1,93 (+93% PLUS RIGIDE !)** | **Quasi doublement de la rigidité en flexion** |
| **Masse Totale du Support** | ~220 g (alu plein) | **~344 g** (avec évidement Ø97) | Robustesse extrême pour +124 g par épaule |
| **Perçages Stator Arrière** | 10× Ø 4,5 mm | **10× Ø 3,3 mm sur PCD Ø 106 mm** | Ancrage direct sur le stator RS-04 |
| **Usinabilité C500** | Évidement depuis bloc plein | **Ébauche creuse d131/d88** | **Usinage 4× plus rapide** (déjà creusé à Ø 88 mm !) |

---

#### 5. Spécifications Techniques Retenues (Plan Officiel `Support RS-04`)

| Paramètre | Valeur (Acier E470 — Retenue) | Valeur (Alu 6061-T6 — Secours) |
|:---|:---|:---|
| **Matériau** | **Acier E470** (ébauche creuse Blockenstock d131/d88) | Aluminium 6061-T6 (barre pleine Ø 130 mm) |
| **Forme** | Carter cylindrique ouvert à l'avant, fond 4 mm avec évidement Ø97 mm | Idem |
| **Alésage intérieur (poche)** | **120,2 mm H7** (encastrement RS-04) | 120,05 mm H7 |
| **Épaisseur paroi cylindrique** | **1,9 mm** (Ø ext carter final = **124,0 mm**) | 3,0 mm (Ø ext carter final = 126,0 mm) |
| **Hauteur totale / Poche** | **39,0 mm total** (poche intérieure de 35,0 mm) | 52,2 mm total |
| **Épaisseur du fond (flasque)** | **4,0 mm** (évidement central Ø 97,0 mm) | 6,0 mm |
| **Perçages arrière** | **10× perçages Ø 3,3 mm** sur PCD Ø 106,0 mm | 10× Ø 4,5 mm |
| **Masse unitaire carter** | **~344 g** | ~220 g |

---

#### 6. Directives de Débitage & Usinage C500 (Plan `Support RS-04`)

> [!TIP]
> **Débitage du tube Acier E470 (d131 / d88)** :
> Pour les tronçons d'ébauche creuse d131/d88 de **4 cm (40 mm)** commandés sur Blockenstock, aucun débitage complexe n'est requis. Utiliser la scie à ruban uniquement si l'approvisionnement est fait en barre plus longue (~50 mm de coupe).

> [!IMPORTANT]
> **Paramètres de Coupe C500 pour Acier E470 (Plan 2D — Ø 124,0 mm / H = 39,0 mm)** :
> 1. **Outil** : Fraise carbure monobloc Ø 4 mm ou Ø 6 mm avec revêtement **AlTiN / TiAlN** (spécial acier).
> 2. **Vitesse de broche** : **5 000 à 6 000 tr/min** (ne pas tourner à 18 000 tr/min pour préserver l'outil).
> 3. **Avance & Passes** : Avance de **300 mm/min**, passes en Z de **0,5 mm** en alésage hélicoïdal avec lubrification (huile de coupe / WD-40).
> 4. **Ordre d'usinage anti-broutement** :
>    - Surfaçage de la face avant pour passer de 40,0 mm brut à **39,0 mm net**.
>    - Évidement intérieur de Ø 88,0 mm à **Ø 120,2 mm H7** sur 35,0 mm de profondeur en conservant la masse extérieure brute de Ø 131,0 mm.
>    - Évidement central arrière à **Ø 97,0 mm** et perçage des **10× trous Ø 3,3 mm sur PCD Ø 106 mm**.
>    - Contournage extérieur final à **Ø 124,0 mm** en toute dernière passe.

---

### C. Le Collet PA12-CF (Pièce ② — Intégré à la coque imprimée)

Le collet PA12-CF est directement intégré à la coque du torse (imprimé d'un seul tenant). Il enveloppe le carter monobloc (acier ou alu) :

| Paramètre | Valeur |
|:---|:---|
| **Matériau** | PA12-CF (coque torse, impression FDM) |
| **Forme** | Poche cylindrique traversante |
| **Paroi latérale** | Enveloppe le carter métallique sur toute sa hauteur. Interstice ~0,2 mm rempli de **résine époxy JB Weld** |
| **Côté avant** | S'arrête à la limite du carter métallique (accès direct au RS-04 par l'extérieur) |
| **Côté arrière** | Laisse l'accès libre à la flasque arrière et au trou d'ancrage du tube carbone |
| **Rôle structural** | Transmet les efforts locaux du torse au carter métallique et protège l'ensemble |

### D. Chemin de Fixation et Routage Câbles

> [!IMPORTANT]
> **Chemin des vis M4 (Configuration Acier E470 4.0 mm)** :
> 
> `Intérieur du torse → tête CHC M4 avec rondelle inox → trou lisse Ø4,5 mm de la Flasque Acier E470 (4,0 mm) → DIRECTEMENT dans 10× taraudages borgnes M4 du stator RS-04 (6,0 mm d'implant)`
> 
> **Le vissage est 100% métal-métal.** Les têtes de vis CHC M4 × 10 mm s'appuient sur la flasque rigide en acier E470 (4,0 mm d'épaisseur). Le serrage plaque énergiquement la face arrière du stator contre la flasque en acier avec une rigidité 53% supérieure à l'aluminium.

> [!NOTE]
> **Chemin des câbles** :
> 
> `Connecteurs stator (face arrière) → encoche de la flasque alu → intérieur du torse → routage le long de la plaque isogrid → PDB Matek + bus CAN`

### E. Séquence d'Assemblage

```
Étape 1 : Insérer et coller le Carter Monobloc Acier E470 dans le collet PA12-CF (résine époxy JB Weld)
          → Laisser polymériser 24h

Étape 2 : Connecter et goupiller le tube carbone Ø30 mm dans le socket de la bride d'épaule
          → Insérer la goupille Ø3 mm verticale

Étape 3 : Insérer le moteur RS-04 par l'AVANT (extérieur de l'épaule)
          → Le moteur glisse dans l'alésage Ø120.2 mm H7 de la paroi 1.9 mm en acier E470
          → La face arrière du stator vient en appui direct contre le fond de 4.0 mm en acier E470

Étape 4 : Serrer les 10 vis CHC M4 × 10 mm depuis l'intérieur du torse
          → Les vis traversent les perçages Ø3.3 mm de la flasque acier E470 (4.0 mm) et se vissent dans le stator
          → Appliquer de la Loctite 243 sur chaque vis (implantation 6.0 mm)
```

### F. Illustration Technique — Coupe Axiale Révisée (Acier E470)

![Coupe axiale du carter monobloc acier E470 d'épaule](./media/manchon_acier_e470_coupe_axiale.svg)

*Coupe axiale révisée montrant le carter monobloc en acier E470 CNC (gris acier) avec sa flasque arrière de 4.0 mm (évidement Ø97 mm) et son cerclage 360° de 1.9 mm (Ø ext 124.0 mm). Le moteur RS-04 (orange) s'insère **par l'avant (extérieur de l'épaule)**. Les vis CHC M4 × 10 mm s'insèrent depuis l'intérieur du torse et traversent la flasque acier E470 pour se visser directement dans le stator.*

### G. Avantages du Carter Monobloc Acier E470 avec Insertion par l'Avant

| Critère | Description |
|:---|:---|
| **Maintenabilité** | ✅ **Remplacement du RS-04 par l'extérieur** sans désosser l'intérieur du torse |
| **Interface de vissage** | ✅ **Appui 100% métal-métal** (10× vis M4 → flasque acier E470 4 mm → stator). Zéro fluage plastique |
| **Dissipation thermique** | ✅ Contact 360° latéral + **contact direct face arrière stator contre flasque acier** (1 800× mieux que l'air) |
| **Intégration** | ✅ **1 seule pièce monobloc CNC** usinée depuis une ébauche creuse d131 / d88 Blockenstock |
| **Transmission d'efforts** | ✅ Liaison directe et ultra-rigide entre le RS-04, la flasque acier E470 et le tube carbone Ø30 mm |
| **Résistance à l'ovalisation** | ✅ **Paroi 1.9 mm en acier E470 (+93% de rigidité en flexion vs alu 3mm)** reprend 100% des contraintes radiale |

---

## 5. Orientation d'Impression : Verticale (Debout)

### A. Pourquoi l'orientation change

Avec le squelette cruciforme reprenant tous les efforts structurels, la coque PA12-CF n'est plus la structure porteuse primaire. Le risque de délamination inter-couche au niveau des collerettes d'épaule est **compensé** par les manchons alu internes. Cela autorise l'impression **verticale** (le torse debout), ce qui élimine massivement les supports.

### B. Orientation pour chaque demi-torse

**Coque Abdominale (Bas) — Verticale, taille en bas :**

![Orientation d'impression FDM verticale des demi-torses en PA12-CF](./media/orientation_impression_verticale.svg)

- **Base sur le plateau** : Le plan de coupe (belly) est posé à plat
- **Hauteur Z d'impression** : ~216 mm ✅
- **Collerettes d'épaule** : Se projettent latéralement à environ mi-hauteur → besoin de supports **uniquement sous les collets** (supports arborescents depuis le plateau, hauteur courte ~100 mm au lieu de ~260 mm en orientation horizontale)
- **Dos ouvert** : Pas de surplomb arrière → aucun support nécessaire côté dos

### C. Comparaison des volumes de support

| Zone | Orientation horizontale (ancienne) | Orientation verticale (nouvelle) |
|:---|:---:|:---:|
| **Sous les collerettes** | Supports massifs (piliers de 260 mm de haut) | Supports courts (~100 mm) |
| **Courbes poitrine** | Supports modérés (surplombs organiques) | Quasi nuls (parois verticales auto-supportées) |
| **Dos** | Supports légers | Aucun (ouvert) |
| **Nervures internes** | Supports possibles | Quasi nuls |
| **Volume total estimé** | **~350-500 cm³** | **~80-120 cm³** (÷3 à ÷4) |

> [!TIP]
> **Gain de temps et de matière** : La réduction de 70-80% du volume de supports se traduit par :
> - ~2-4h de temps d'impression en moins
> - ~50-100g de PA12-CF économisé (supports + purge)
> - Retrait des supports beaucoup plus facile (surfaces de contact réduites)
> - État de surface des collerettes amélioré (moins de marques de support)

### D. Impact structural de l'impression verticale

| Critère | Impression horizontale (dos au plateau) | Impression verticale (debout) |
|:---|:---|:---|
| **Collerettes** : cercles continus | ✅ 100% continus (cercles dans le plan XY) | 🟡 Couches coupent le cercle → arcs de ~80% par couche |
| **Résistance collet en hoop stress** | ✅ Excellent (fibres le long du cercle) | 🟡 Moyen (fibres coupent le cercle) |
| **Compensation par manchon alu** | N/A (pas de manchon dans l'ancien design) | ✅ **Le manchon alu reprend 100% du hoop stress** |
| **Résistance axiale du collet** | 🟡 Inter-couche (faible) | ✅ Le long des fibres (fort) |
| **Support nécessaire** | ❌ Massif | ✅ **Minimal** |

### E. Stratégie de Découpe CAO : 2 Parties Horizontales (🏆 RETENUE) vs 4 Parties

Pour imprimer l'intégralité du torse dans le volume d'impression de la **Qidi Plus 4** (305 × 305 × 280 mm), la stratégie de découpe CAO a été rigoureusement analysée :

| Critère d'Ingénierie | Option A : 2 Parties Horizontales (🏆 RETENUE) | Option B : 4 Parties (Haut/Bas + Avant/Arrière) | Justification Technique |
|:---|:---:|:---:|:---|
| **Forme des Pièces** | **Thorax Haut** (0-216 mm) + **Abdomen Bas** (0-190 mm) | 2 Coquilles Hautes (Avant/Arrière) + 2 Coquilles Basses | **2 anneaux fermés 360° monoblocs** |
| **Intégrité de la Ceinture d'Épaule** | ✅ **Ring 360° Monobloc continu** | ❌ Couture verticale passant par le collet d'épaule | **Évite tout risque d'arrachement par torsion** |
| **Centrage sur la Waist Plate** | ✅ **S'appuie directement sur la Waist Plate Alu (6 mm)** | 🟡 Nécessite 4 plans d'appui complexes | **Alignement naturel et rigide sur le squelette** |
| **Supports d'Impression Qidi** | ✅ **Minimaliste** (Tree supports uniquement sous collets) | ❌ Élevé (supports sur les tranches verticales) | **Gain de 70% de PA12-CF et d'état de surface** |
| **Complexité d'Assemblage** | ✅ **1 seul plan de joint horizontal** | ❌ 3 plans de joints croisés | **Assemblage mécanique simplifié** |

#### Spécifications CAO du Plan de Joint (Fusion 360) :

1. **Plan de Coupe Horizontal (Au niveau de la Waist Plate)** :
   - La découpe est effectuée exactement au niveau de la **Waist Plate en Alu 6061-T6 (6 mm)**.
2. **Profilé d'Emboîtement Rainure-Languette (Lip & Groove)** :
   - La tranche d'assemblage comporte une languette radiale de **1,5 mm d'épaisseur par 2,0 mm de hauteur** s'emboîtant dans une rainure correspondante (jeu fonctionnel de **0,2 mm**). Ce profilé garantit un alignement 100% parfait sans aucun décalage de surface à l'extérieur.
3. **Assemblage par Inserts Laiton à Chaud (Heat-Set Inserts M4)** :
   - La liaison n'est pas collée : elle est verrouillée mécaniquement par **6× à 8× vis CHC M4 × 16 mm** traversant la Waist Plate et prenant en prise dans des **inserts en laiton à chaud (Heat-Set Inserts M4 × 8 mm)** noyés dans la paroi du PA12-CF.

---

## 6. Paramètres de Tranchage (Slicing) — Coque Secondaire PA12-CF

### A. Paramètres Globaux (Zone Courante)

La coque étant désormais secondaire (le squelette porte les efforts), les paramètres d'impression sont **allégés** par rapport à l'ancien guide :

| Catégorie | Paramètre (FR) | Slicer Setting Name (EN) | Slicer Tab / Menu Path (EN) | Recommended Value | Ancien | Description & Note |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **Printer** | Diamètre de buse | **Nozzle Diameter** | `Printer settings` ➔ `Extruder` ➔ `Nozzle` | `0.4 mm` | 0.4 mm | Type : **Tungsten Carbide** (Carbure de Tungstène) |
| **Quality** | Hauteur de couche | **Layer Height** | `Process` ➔ `Quality` ➔ `Layer Height` | `0.20 mm` | 0.18 mm | Légèrement plus épais pour accélérer l'impression |
| **Quality** | Largeur d'extrusion | **Line Width / Extrusion Width** | `Process` ➔ `Quality` ➔ `Line Width` | `0.48 mm` | 0.48 mm | Inchangé |
| **Strength** | Nombre de parois | **Wall Loops / Perimeters** | `Process` ➔ `Strength` ➔ `Walls` | **`4`** | ~~6~~ | ⚠️ **Réduit de 6 à 4** — coque secondaire (épaisseur 1,92 mm) |
| **Strength** | Couches sup. / inf. | **Top / Bottom Shell Layers** | `Process` ➔ `Strength` ➔ `Shells` | **`4` / `4`** | ~~6/6~~ | ⚠️ **Réduit** |
| **Strength** | Motif de remplissage | **Infill Pattern** | `Process` ➔ `Strength` ➔ `Sparse infill` | `Gyroid` | Gyroid | Inchangé |
| **Strength** | Taux de remplissage | **Infill Density** | `Process` ➔ `Strength` ➔ `Sparse infill` | **`20%`** | ~~35%~~ | ⚠️ **Réduit de 35% à 20%** — le squelette porte les charges |
| **Filament** | Température de buse | **Nozzle Temperature** | `Filament settings` ➔ `Filament` ➔ `Nozzle temperature` | `290°C - 295°C` | 290-295°C | Inchangé |
| **Filament** | Température plateau | **Bed Temperature** | `Filament settings` ➔ `Filament` ➔ `Bed temperature` | `85°C - 90°C` | 85-90°C | Avec colle Magigoo PA ou PVP |
| **Filament** | Chambre chauffée | **Chamber Temperature** | `Filament settings` ➔ `Filament` ➔ `Chamber temperature` | `60°C` | 60°C | Indispensable pour le PA12-CF |
| **Cooling** | Ventilation pièce | **Part Cooling Fan Speed** | `Filament settings` ➔ `Cooling` ➔ `Part cooling fan` | `0%` | 0% | Max 10% pour ponts |
| **Speed** | Vitesse parois ext. | **Outer Wall Speed** | `Process` ➔ `Speed` ➔ `Walls` | `45 - 55 mm/s` | 40-45 | Légèrement augmentée (coque secondaire tolère + d'imperfections) |
| **Speed** | Vitesse parois int. | **Inner Wall Speed** | `Process` ➔ `Speed` ➔ `Walls` | `55 - 65 mm/s` | 50-55 | Idem |
| **Speed** | Vitesse remplissage | **Sparse Infill Speed** | `Process` ➔ `Speed` ➔ `Infill` | `55 - 65 mm/s` | 50-55 | Idem |
| **Support** | Activer supports | **Enable Support** | `Process` ➔ `Support` ➔ `Support` | `Checked (Yes)` | Yes | Type : **Tree (Organic)** |
| **Support** | Support Build Plate Only | **Support on Build Plate Only** | `Process` ➔ `Support` ➔ `Support` | `Checked (Yes)` | Yes | Aucun support interne |
| **Support** | Angle seuil | **Support Threshold Angle** | `Process` ➔ `Support` ➔ `Support` | `55° - 60°` | 55-60° | Le PA12-CF ponte bien jusqu'à 55° |
| **Support** | Z-Distance sup. | **Support Top Z Distance** | `Process` ➔ `Support` ➔ `Support` | `0.30 - 0.40 mm` | 0.28-0.36 | Augmenté pour faciliter le retrait |
| **Travel** | Saut en Z | **Z-hop when Retracting** | `Printer settings` ➔ `Extruder` ➔ `Retraction` | `0.4 mm` | 0.4 mm | Normal ou Slope |
| **Others** | Couche variable | **Adaptive Layer Height** | `Top Toolbar` ➔ `Variable Layer Height (Icon)` | `Disabled` | Disabled | Inchangé |

### B. Zone d'Épaule : Modifier Volume (Renforcement Local)

> [!CAUTION]
> **Les collerettes d'épaules restent à paramètres MAXIMAUX.** Même avec les manchons alu, la coque PA12-CF doit résister localement au serrage radial du RS-04 et transmettre les efforts au manchon. Il faut créer un **Modifier Volume** dans le slicer pour surcharger les paramètres dans cette zone.

#### Procédure détaillée OrcaSlicer / Qidi Print (en anglais, pas à pas) :

**Étape 1 — Importer et positionner le modèle**
1. Ouvrez **OrcaSlicer** (ou Qidi Print)
2. Importez le fichier STL du Thorax (demi-torse haut)
3. Positionnez-le verticalement (plan de coupe au belly → sur le plateau)

**Étape 2 — Ajouter un Modifier Volume cylindrique**
1. **Clic droit** sur le modèle dans la vue 3D (ou dans le panneau de gauche sur le nom de l'objet)
2. Sélectionnez **`Add Modifier`** → **`Cylinder`**
3. Un cylindre transparent apparaît dans la scène

**Étape 3 — Dimensionner et positionner le Modifier**
1. **Sélectionnez** le cylindre modifier (clic gauche dessus)
2. Dans le panneau de droite, sous **`Object Manipulation`**, ajustez :
   - **`Size X`** : Diamètre du collet d'épaule + 30 mm de marge (ex: si collet = 90 mm → taper `120`)
   - **`Size Y`** : Identique à X (`120`)
   - **`Size Z`** : `80` mm (hauteur de la zone renforcée)
3. **Positionnez** le cylindre exactement sur le logement de l'épaule :
   - Utilisez **`Move`** (touche `M`) pour déplacer le cylindre modifier
   - Centrez-le sur le collet d'épaule visible dans le modèle
   - Ajustez visuellement en vue de face, de côté et de dessus
4. **Répétez** pour l'épaule opposée (Clic droit → `Add Modifier` → `Cylinder` → positionner)

**Étape 4 — Configurer les paramètres du Modifier**
1. **Clic droit** sur le cylindre modifier (dans le panneau de gauche ou dans la vue 3D)
2. Sélectionnez **`Edit modifier settings`** (ou **`Change type`** → `Advanced`)
3. Cochez et configurez les paramètres suivants :
   - ☑️ **`Wall loops`** → valeur : **`6`** (au lieu de 4 global)
   - ☑️ **`Sparse infill density`** → valeur : **`35%`** (au lieu de 20% global)
   - ☑️ **`Top shell layers`** → valeur : **`6`**
   - ☑️ **`Bottom shell layers`** → valeur : **`6`**
4. Cliquez **`OK`** / **`Apply`**

**Étape 5 — Vérifier visuellement**
1. Cliquez sur **`Slice`** (bouton en bas à droite)
2. Utilisez le **curseur de couches** (barre verticale à droite) pour naviguer couche par couche
3. Vérifiez que dans la zone du cylindre modifier :
   - Les parois sont plus épaisses (6 boucles au lieu de 4)
   - Le remplissage est plus dense (35% au lieu de 20%)
   - La transition entre la zone renforcée et la zone allégée est progressive
4. Si le positionnement est incorrect, annulez le slice, ajustez le modifier et re-slicez

### C. Paramètres de Tranchage pour Prototype PLA

Pour valider l'ajustement mécanique avant de lancer l'impression PA12-CF, imprimer un prototype en PLA avec les paramètres accélérés suivants :

| Catégorie | Slicer Setting (EN) | Valeur PLA | Note |
| :--- | :--- | :---: | :--- |
| **Quality** | **Layer Height** | `0.28 mm` | Mode draft rapide |
| **Strength** | **Wall Loops** | `3` | Suffisant pour test d'ajustement |
| **Strength** | **Infill Density** | `10% - 15%` | Remplissage léger |
| **Strength** | **Infill Pattern** | `Grid` | Plus rapide que Gyroid en PLA |
| **Filament** | **Nozzle Temperature** | `210°C - 220°C` | Standard PLA |
| **Filament** | **Bed Temperature** | `55°C - 60°C` | Standard PLA |
| **Filament** | **Chamber Temperature** | **`0°C (OFF)`** | ⚠️ **Éteindre le chauffage + ouvrir le capot** (heat creep) |
| **Cooling** | **Part Cooling Fan** | **`100%`** | Maximum pour PLA |
| **Speed** | **Outer Wall Speed** | `100 - 120 mm/s` | Vitesse CoreXY |
| **Speed** | **Sparse Infill Speed** | `200 - 250 mm/s` | Gain de temps massif |
| **Support** | **Enable Support** | `Yes, Tree` | Se détachent facilement en PLA |

### D. Conditionnement du Filament PA12-CF

> [!WARNING]
> **Le PA12 (Nylon) est extrêmement hydrophile.** Si le filament absorbe de l'humidité, les couches crépitent, la pièce devient cassante et les efforts inter-couches s'effondrent. C'est le **facteur n°1 d'échec** d'impression en PA12-CF.

1. **Séchage initial** : Sécher la bobine au four ou dans un sécheur actif à **90°C pendant 6 à 8 heures** avant de lancer l'impression
2. **Impression sous atmosphère contrôlée** : Imprimer impérativement à partir d'une **boîte sèche hermétique** (*Drybox*) reliée directement à l'imprimante, maintenant un taux d'humidité **inférieur à 10%**
3. **Stockage** : Après impression, remettre immédiatement la bobine dans un sac sous vide avec sachets de gel de silice

---

## 7. Split Abdominal Rigide et Emboîtement (Lap Joint)

Le torse est divisé horizontalement au niveau du ventre pour l'impression. L'assemblage des deux moitiés reste **100 % rigide** grâce à l'emboîtement et au squelette cruciforme traversant :

### A. Lèvre d'Emboîtement (Lap Joint de 3 mm)

La procédure de modélisation du Lap Joint sous Fusion 360 reste identique à celle documentée dans le guide archivé (Section 5.A) :

1. **Bandeau de renfort interne** : Épaissir la coque de 3 mm supplémentaires sur une bande de ±8 mm autour du plan de coupe → épaisseur locale de 4,92 mm (4 périmètres + renfort)
2. **Split Body** : Scinder le torse au plan de coupe abdominal
3. **Lèvre mâle** : Extrusion de +3 mm sur la coque abdominale (bas)
4. **Rainure femelle** : Combine/Cut sur le Thorax (haut)
5. **Tolérances** : Press Pull −0,15 mm radial et −0,10 mm axial sur la rainure femelle

### B. Bossages de Vissage Internes (M4)

- **4 à 6 bossages** (Ø12 mm) répartis le long de la circonférence intérieure
- *Côté Thorax* : Passage lisse Ø4,2 mm lamé pour tête de vis M4
- *Côté Abdomen* : Logement Ø5,8 mm × 9 mm pour insert laiton M4 posé à chaud
- **Éviter** de placer les bossages là où ils interféreraient avec les paniers batterie ou la plaque isogrid

### C. Jonction avec le Squelette Cruciforme

La plaque isogrid sagittale (en 2 parties) se joint **au même niveau** que le split abdominal :
- Les 2 demi-plaques se chevauchent sur 30 mm (éclisse) et se boulonnent par 4 vis M4
- La vis de l'éclisse traverse le plan de coupe → **renforcement supplémentaire** du joint abdominal
- Le squelette rigide + le Lap Joint + les bossages = **triple verrouillage** du plan de coupe

---

## 8. Système de Batteries : 2 Paniers Latéraux avec Hot-Swap

### A. Architecture des Paniers

Le panier unique Asimov (`ASV1_100_10C`) est remplacé par **2 paniers latéraux symétriques**, coulissant depuis le dos (ouvert) vers le ventre :

![Vue de dessus des paniers batteries latéraux](./media/paniers_batteries_hot_swap_vue_dessus.svg)

### B. Système de Coulisses

| Élément | Description |
|:---|:---|
| **Coulisses latérales (existantes)** | Le design Asimov v1 possède déjà des rails de guidage gauche et droite dans la coque PA12-CF → **réutilisés tels quels** (modulo scale +18%) |
| **Coulisses centrales (ajoutées)** | 2 petites coulisses supplémentaires fixées de chaque côté de la plaque isogrid sagittale (1 par face). Usinées dans un profilé alu en L de 10×10×1,5 mm ou imprimées en PA12-CF et collées sur la plaque |
| **Bandes PTFE** | Coller des bandes autocollantes PTFE (0,2 mm d'épaisseur) sur les faces de la plaque isogrid au niveau du passage des paniers → glissement silencieux et sans usure |
| **Jeu latéral** | 1,0 mm entre la paroi du panier et la face de la plaque isogrid de chaque côté |

### C. Verrouillage des Paniers

| Solution | Description | Complexité | Recommandation |
|:---|:---|:---:|:---:|
| **Loquet quart-de-tour (Dzus)** | 1 par panier, accessible depuis l'arrière. Rotation 90° pour verrouiller | ⭐⭐ | ✅ Recommandé |
| **Clips à ressort PA12-CF** | Intégrés dans les rails de la coque, s'enclenchent automatiquement | ⭐⭐⭐ | 🟡 Alternative |
| **Vis papillon M4** | Simple mais lent (outil nécessaire ou serrage à la main) | ⭐ | ❌ Trop lent pour hot-swap |

### D. Spécifications des 2 Batteries

| Paramètre | Batterie unique (ancienne) | 2 Batteries (nouvelle) |
|:---|:---:|:---:|
| **Configuration** | 1× 12S NMC 48V 10Ah | **2× 12S NMC 48V 5Ah** (ou 2× 6Ah) |
| **Énergie totale** | 480 Wh | 480 Wh (2×5Ah) ou **576 Wh** (2×6Ah, +20%) |
| **Tension nominale** | 44,4V | 44,4V (parallèle via diodes ORing) |
| **Masse** | 2,3 kg | ~2,5 kg (+200g pour 2 BMS + câblage + diodes) |
| **Dimensions unitaires** | ~220×100×65 mm | ~220×**50**×65 mm chacune |
| **Hot-swap** | ❌ | ✅ |
| **CdG symétrique** | 🟡 (dépend du placement) | ✅ Parfaitement centré en X |

### E. Circuit Électrique de Hot-Swap (Diode ORing Détaillé)

#### E.1 Principe de fonctionnement

Le hot-swap permet d'**échanger une batterie sans couper l'alimentation du robot**. Le circuit utilise des **diodes ORing** : chaque batterie alimente le bus principal via sa propre diode. Quand une batterie est retirée, l'autre prend instantanément le relais sans coupure ni transitoire dangereux.

![Schéma électrique Hot-Swap ORing avec Diodes Schottky](./media/schema_electrique_hot_swap_oring.svg)

#### E.2 Sélection des composants

| Composant | Référence | Spécifications | Prix unitaire | Quantité |
|:---|:---|:---|:---:|:---:|
| **Diode Schottky** | **MBR4060PT** (ON Semi) | 40A, 60V, V_forward=0.45V, boîtier TO-247 | ~3€ | 2 |
| **BMS 12S** | BMS générique 12S 20A | Protection surcharge/décharge/court-circuit | ~15€ | 2 |
| **Connecteur panier** | **XT60** mâle/femelle | 60A max, détrompé, soudé sur câble 10AWG | ~2€ | 4 (2 paires) |
| **Fusible PTC** | Resettable 40A | Protection du bus principal | ~5€ | 1 |
| **Dissipateur thermique** | Radiateur TO-247 alu | Vissé sur la plaque isogrid ou la waist plate | ~2€ | 2 |
| **LED de statut** | LED bicolore (vert/rouge) | Indicateur visuel de présence batterie + charge | ~1€ | 2 |
| **TOTAL** | | | **~48€** | |

#### E.3 Fonctionnement détaillé

| Situation | Batterie G | Batterie D | Comportement du bus |
|:---|:---:|:---:|:---|
| **Normal** (2 batteries) | ✅ Connectée | ✅ Connectée | La batterie avec la tension la plus haute alimente le bus. L'autre est en standby (diode bloquée car V_G < V_D + V_forward ou vice-versa). En pratique les 2 partagent la charge si leurs tensions sont proches. |
| **Hot-swap** (retrait G) | ❌ Retirée | ✅ Connectée | D2 conduit instantanément. Transitoire : ~0.5 ms (temps de commutation diode). Le bus ne voit qu'une micro-chute de 0.45V → **aucun reset des contrôleurs**. |
| **1 seule batterie** | ❌ Absente | ✅ Connectée | D2 conduit en permanence. Autonomie divisée par 2, mais le robot fonctionne normalement. |
| **Rechargement en place** | 🔌 En charge | ✅ Alimente | Le chargeur externe se branche sur le connecteur XT60 de la batterie G via le panier. La diode D1 empêche le courant de retour vers le bus. |

#### E.4 Option avancée : MOSFET Ideal Diode (Pour minimiser les pertes)

La diode Schottky MBR4060PT dissipe **P = I × V_forward = 20A × 0.45V = 9W** en fonctionnement normal. C'est significatif. Pour réduire cette perte à **<0.5W**, remplacer chaque diode par un **contrôleur de diode idéale MOSFET** :

| Composant | Référence | V_drop | Pertes à 20A | Prix |
|:---|:---|:---:|:---:|:---:|
| Diode Schottky (baseline) | MBR4060PT | 0.45V | **9W** | 3€ |
| **MOSFET Ideal Diode** | **LTC4357** + MOSFET N-CH 60V | **0.020V** | **0.4W** | ~15€ |

> [!TIP]
> Pour la V1, les **diodes Schottky** suffisent. Le 9W de perte est facilement dissipé par un petit radiateur vissé sur la plaque isogrid (l'aluminium est un excellent conducteur thermique). Passer au MOSFET Ideal Diode en **V2** si l'autonomie devient critique.

#### E.5 Montage physique

- Les 2 diodes Schottky (ou modules MOSFET) sont montées sur des **radiateurs alu TO-247** vissés directement **sur la plaque isogrid** (face intérieure)
- Les connecteurs **XT60** sont fixés à l'arrière de chaque panier batterie → branchement/débranchement en coulissant le panier
- Les câbles d'alimentation (10 AWG silicone) cheminent le long de la plaque isogrid vers la PDB Matek située dans le torse

---

## 9. Plaques Structurelles Horizontales (Heritage Asimov v1)

### A. Plaque Supérieure (Cou)

| Paramètre | Valeur |
|:---|:---|
| **Matériau** | Aluminium 6061-T6 |
| **Épaisseur** | 5 mm |
| **Origine** | BOM Asimov v1 (scale +18%) |
| **Rôle** | Fondation pour le collet du cou + ancrage haut de la plaque isogrid + ancrage haut du tube carbone (via nœud) |
| **Usinage** | CNC C500, perçages M4/M5 pour fixation squelette + collet cou RS-05 |

### B. Plaque Inférieure (Waist Plate)

| Paramètre | Valeur |
|:---|:---|
| **Matériau** | Aluminium 6061-T6 |
| **Épaisseur** | 6 mm |
| **Origine** | BOM Asimov v1 (scale +18%) |
| **Rôle** | Fermeture du bas du torse rigide + ancrage bas de la plaque isogrid + interface de liaison avec le roulement de grand diamètre du module Waist Yaw actif |
| **Usinage** | CNC C500, profil extérieur + alésage central pour axe RS-06 |

---

## 10. Liaison Active Waist Yaw (RobStride RS-06)

La rotation en lacet de la taille est assurée par le module Waist d'Asimov v1 (scale +18%), adapté pour le moteur **RobStride RS-06** :

| Paramètre | Valeur |
|:---|:---|
| **Moteur** | RobStride RS-06 (36 N.m pic / 11 N.m nom., Ø88 mm, 621 g) |
| **ID CAN-FD** | 21 |
| **Logement Asimov v1** | Conçu pour Cubemars AK80 (Ø98 mm) → Ø115,6 mm après scale +18% |
| **Bague d'adaptation CNC** | Ø int. 88 mm / Ø ext. 115,6 mm → épaisseur radiale 13,8 mm, alu 6061-T6 |
| **Roulement** | Section fine Ø110 mm (scale +18%), billes à 4 points de contact |
| **Accouplement** | Stator fixé au pelvis inférieur / Rotor accouplé au centre de la Waist Plate du torse rigide |

---

## 10bis. Renfort de Rigidité Roll — Cage H-Bracket d'Épaule (Solution Finale)

> [!IMPORTANT]
> **Problème identifié par l'audit (Août 2026)** : L'inertie en roll de la colonne vertébrale (23 682 mm4) est 21× plus faible que l'inertie en pitch (506 667 mm4). Sans renfort, la flèche latérale au cou atteint ~1.5 mm — inacceptable pour la marche et le trot.

> [!NOTE]
> **Première solution envisagée et abandonnee** : 2 tiges filetées M5 verticales (waist plate → nœud, ±60 mm de la colonne). Abandonée car elle occupe l'espace latéral prévu pour la batterie. La cage H-bracket ci-dessous est **2.15× plus rigide et libère entièrement cet espace**.

### A. Architecture : Cage H-Bracket + Plaque Avant Stator RS-04

![Schéma d'Architecture Vectoriel Blueprint — Cage H-Bracket & Bride Épaule RS-04 D-Bot V1](./media/hbracket_rs04_quasi_final_blueprint.svg)

*Figure 10.1 : Blueprint d'ingénierie 2D de l'assemblage d'épaule quasi-final (Fusion 360 v31). Vue de Face : stator RS-04 Ø120 mm + 2 plaques H-bracket 5 mm 7075-T6 identiques évidées à Ø95mm (10× vis M4 sur PCD Ø106 mm) + 2 tirants M5 axiaux à 23.4° (Z=±66.1 mm, Y=±28.6 mm). Vue Latérale : sandwich axial 49 mm (Plaque AV 5 mm -> Stator RS-04 41 mm -> Plaque AR 5 mm + Bride jaune 48.2 mm).*

> [!IMPORTANT]
> **Évidement Central Ø95 mm (epaule9.png)** : Les plaques 5 mm 7075-T6 sont évidées au centre sous forme de couronne annulaire (Ø ext 120 mm / Ø int 95 mm, largeur radiale 12.5 mm). Cet évidement procure un **gain de masse massif de -100 g par plaque (soit -400 g sur le torse pour les 4 plaques !)** tout en dégageant le passage des câbles XT30/CAN-FD et la ventilation du RS-04.

**Principe** : La plaque arrière (orange) et la plaque avant (orange), toutes deux évidées à Ø95mm et fixées au stator via 10× vis M4 sur PCD Ø106mm, sont reliées par 2 tirants M5 axiaux placés sur la droite à 23.4° de la verticale, à R=72mm du centre moteur.

| Paramètre | Valeur |
|:---|:---|
| **Plaques H-bracket (orange, ×2 par épaule)** | **7075-T6, 5mm** (2 plaques IDENTIQUES : Avant + Arrière, **Évidement central Ø95mm** -> gain -400g total sur torse) → couronne annulaire Ø120/Ø95mm + 2 oreilles cylindriques pour tirants M5 → **10× vis M4 sur PCD Ø106mm** sur stator RS-04 (pince radiale de matière = 3.35 mm, Sf_bearing = 61) |
| **Perçage oreilles M5 (CNC C500)** | **Ø 5.5 mm (ISO 273 — Moyen)** → jeu radial 0.25 mm pour empilement sans contrainte + **chanfreins 0.5 mm × 45°** sur les 2 faces des plaques |
| **Bride fixation tube (jaune)** | **Bride monobloc alu 7075-T651, 48.2mm total** → flasque 13.2mm + socket tube 35mm (L/D=1.17) + bouchon interne alu Ø26/Ø18×34.5mm (ajusté sans colle) + fente pincement 2×M4 + goupille Ø4mm. Se monte **par-dessus la plaque arrière orange**. Sourcing: disque brut Ø120×50mm Blockenstock |
| **Pincement radial tube (×2 vis M4 par bride)** | **Vis CHC M4 × 30 mm (ISO 4762 / DIN 912 classe 8.8 ou 10.9 zingué)** — Traversantes sur méplats 10.0 mm (vis #1 à 8.0 mm du bord, vis #2 à 25.0 mm du bord, entraxe 17.0 mm) |
| **Perçage pincement M4 (CNC C500)** | **Ø 4.3 mm (ISO 273 — Moyen)** → perçage traversant sur méplats + **chanfreins 0.5 mm × 45°** sur les 2 entrées/sorties de méplats |
| **Rondelles pincement (×4 par bride)** | **ISO 7089 / DIN 125A (M4)** → Ø int. 4.3 mm / Ø ext. 9.0 mm, épaisseur 0.8 mm (2 sous tête vis CHC, 2 sous écrou Nylstop M4) |
| **Écrous frein pincement (×2 par bride)** | **ISO 7040 / DIN 985 — M4 (Nylstop)** → écrou hexagonal autofreiné avec bague nylon, hauteur 4.0 mm |
| **Tirants M5 axiaux (×2 par épaule)** | **Vis CHC M5 × 60 mm (ISO 4762 / DIN 912 classe 8.8 ou 10.9 zingué)** — Longueur optimale validée pour empilement 49.0 mm à 51.0 mm (saillie bague nylon = +2.4 mm) |
| **Rondelles tirants (×4 par épaule)** | **ISO 7089 / DIN 125A (M5)** → Ø int. 5.3 mm / Ø ext. 10.0 mm, épaisseur 1.0 mm (2 sous tête vis CHC, 2 sous écrou Nylstop) |
| **Écrous frein tirants (×2 par épaule)** | **ISO 7040 / DIN 985 — M5 (Nylstop)** → écrou hexagonal autofreiné avec bague nylon, hauteur 5.0 mm |
| **Position tirant HAUT** | Z = +66.1 mm, Y = +28.6 mm (R=72mm, angle 23.4° de la verticale) |
| **Position tirant BAS** | Z = -66.1 mm, Y = -28.6 mm (diamétralement opposé) |
| **Marge stator** | R=72mm vs stator R=60mm : +12 mm |
| **Marge limite torse** | R=72mm vs R_max=78mm : +6 mm |
| **Sourcing plaques 5mm 7075-T6** | Blockenstock — chute 5×160×160mm 7075-T6 @ 9.60 EUR/pièce — **4 pièces** (2 avant + 2 arrière) → 38.40 EUR |
| **Sourcing bride jaune 48.2mm** | Blockenstock — disque Ø120×50mm alu 7075-T651 — **2 pièces** (une par épaule) |
| **Épaisseur min théorique plaques** | 7075-T6: 3.2mm, 6061-T6: 4.1mm (Sf=2.5) — **5mm retenu, validé §10 et §11 ETUDE_Dimensionnement** |
| **Couple bride (système complet)** | Pincement 2×M4 (~89 Nm) + Goupille Ø4mm (~31 Nm) = 120 Nm total couverts — voir §11 ETUDE |
| **Masse ajoutée** | ~75 g par plaque 5mm (×2 = 150g) + ~200 g bride jaune = ~350 g par épaule / ~700 g total pour les 2 épaules |

> [!NOTE]
> **Calcul de l'Empilement Axial des Vis de Pincement M4 et des Tirants M5** :
> - **Vis de Pincement Radial (CHC M4 × 30 mm)** : Épaisseur traversée sur méplats 10.0 mm (25.0 mm) + Rondelle sous tête DIN 125A M4 (0.8 mm) + Rondelle sous écrou DIN 125A M4 (0.8 mm) + Écrou Nylstop M4 DIN 985 (4.0 mm) + Saillie 2 filets (1.4 mm) = **32.0 mm**. La vis **ISO 4762 CHC M4 × 30 mm** (ou M4 × 35 mm si méplats usinés à 28.0 mm) garantit la prise parfaite dans la bague nylon.
> - **Vis Tirant M5 (CHC M5 × 60 mm)** : Plaque AV 7075 (5.0 mm) + Corps RS-04 (39.0 mm à 41.0 mm) + Plaque AR 7075 (5.0 mm) = **49.0 mm à 51.0 mm**. Accessoires (2× rondelles 1.0 mm + écrou Nylstop M5 5.0 mm + saillie 1.6 mm) = **7.6 mm**. Longueur totale = $49.0 + 7.6 = \mathbf{56.6\text{ mm}}$ (vis **ISO 4762 CHC M5 × 60 mm** exacte).

> [!TIP]
> **Tutoriel : Importation directe des pièces 3D ISO/DIN dans Fusion 360 (Outil Intégré McMaster-Carr)** :
> 1. **Accéder à l'outil** : Dans le ruban de conception de Fusion 360, aller dans **Insert** $\rightarrow$ **Insert McMaster-Carr Component**.
> 2. **Rechercher les composants tirants M5** :
>    - **Vis CHC M5 × 60 mm (ISO 4762 / DIN 912)** : Rechercher `M5 x 60 Socket Head Screw` $\rightarrow$ Sélectionner *Metric* $\rightarrow$ *M5 Thread* $\rightarrow$ *60 mm Length*.
>    - **Rondelles M5 (DIN 125A / ISO 7089)** : Rechercher `M5 Flat Washer` $\rightarrow$ Sélectionner *Metric* $\rightarrow$ *For M5 Screw Size* (Ø int 5.3 mm, Ø ext 10.0 mm).
>    - **Écrous Nylstop M5 (DIN 985 / ISO 7040)** : Rechercher `M5 Nylon-Insert Locknut` $\rightarrow$ Sélectionner *Metric* $\rightarrow$ *M5 Thread*.
> 3. **Importer dans la scène 3D** :
>    - Dérouler la section *Product Detail* du composant sélectionné.
>    - Sélectionner le format **3D STEP** dans le menu déroulant et cliquer sur **Download**.
>    - La pièce 3D exacte s'insère automatiquement comme composant dans votre modèle. Il suffit ensuite d'appliquer un **Joint** (`J`) coaxial sur le trou Ø 5.5 mm.

### B. Performance Roll

| Solution | I_roll (mm4) | Flèche cou | Espace batterie |
|:---|:---:|:---:|:---:|
| Sans renfort | 23 682 | ~1.5 mm | ✅ Libre |
| Tirants verticaux (abandonnée) | 164 802 | ~0.21 mm | ❌ Occupé |
| Cage H-bracket vertical pur ±65mm | 354 922 | ~0.10 mm | ✅ Libre |
| **Cage H-bracket 23.4°, R=72mm (retenue)** | **366 262** | **~0.097 mm** | ✅ **Libre** |

> [!TIP]
> Voir [ETUDE_Dimensionnement §8 et §9](./ETUDE_Dimensionnement_Colonne_Vertebrale.md) pour les détails de calcul et l'analyse thermique RS-04 en cage ouverte.
> Voir [ETUDE_Dimensionnement §11](./ETUDE_Dimensionnement_Colonne_Vertebrale.md) pour la validation mécanique complète du design quasi-final Fusion 360 (screenshots epaule1-8) : bouchon anti-écrasement alu, pincement radial M4, goupille Ø4mm — design VALIDÉ.

---

## 10ter. Confirmation Architecture Batterie V1 — 2 Paniers Latéraux Hot-Swap (Section 8 Confirmée)

> [!IMPORTANT]
> **Architecture Officielle V1 Confirmée (Août 2026)** : La validation de la cage H-bracket d'épaule (oreilles diagonales à 23.4°, $R = 72\text{ mm}$) confirme que l'espace sous les épaules et le long des flancs du torse est **totalement libre**. 
> 
> En conséquence, la solution initiale de **2 paniers batterie latéraux avec Hot-Swap** (détaillée et spécifiée au **§8**) est **officiellement rétablie comme l'architecture V1 standard de D-Bot**. 
>
> *Voir le **§8** pour l'analyse complète, les schémas vectoriels [paniers_batteries_hot_swap_vue_dessus.svg](./media/paniers_batteries_hot_swap_vue_dessus.svg), le circuit électrique ORing [schema_electrique_hot_swap_oring.svg](./media/schema_electrique_hot_swap_oring.svg) et la nomenclature des composants.*
* ✅ Compatible avec des packs e-bike standard 48V 10Ah




## 11. Workflow de Fabrication Révisé (Plan d'Action)

### Phase 1 — Conception CAO (Fusion 360)

1. ☐ Mettre à l'échelle (+18%) les fichiers originaux du torse et de la taille Asimov v1
2. ☐ Modéliser la **plaque de colonne vertébrale 2D évidée** (Option B, R = 18 mm) en 2 parties avec jonction au Nœud Central
3. ☐ Modéliser les **2 cages H-bracket d'épaule** : **Plaques avant 5mm Alu 7075-T6** (disque Ø~150mm + 4 oreilles cylindriques, 6×M5 sur PCD Ø144mm côté bras RS-04) + **Brides arrière monoblocs 48.2mm Alu 7075-T651** (socket tube 35mm, pincement 2×M4, goupille Ø4mm, bouchon alu Ø26/Ø18×34.5mm) reliées par 2 tirants M5 axiaux à 23.4° (R=72mm).
4. ☐ Modéliser le **nœud d'intersection** à demi-coquilles (Bride Sup. + Bride Inf. CNC alu)
5. ☐ Dessiner les **2 paniers batterie** latéraux + coulisses centrales sur la plaque de colonne
6. ☐ Réaliser le **split rigide abdominal** avec bandeau de renfort, Lap Joint de 3 mm et tolérances
7. ☐ Modéliser la **bague d'adaptation CNC** pour le RS-06 (13,8 mm d'épaisseur radiale)
8. ☐ Vérifier les **dégagements internes** (paniers + squelette + câblage)

### Phase 2 — Usinage CNC (C500)

1. ☐ Usiner les 2 demi-plaques de colonne vertébrale (alu 6061-T6, 5 mm — évidements 2D traversants, R = 18 mm)
2. ☐ Usiner les **2 carters Support RS-04 (H = 39,0 mm, Acier E470)** à partir d'**ébauche creuse d131/d88 Blockenstock** — alésage Ø 120.2 mm H7 sur 35.0 mm, paroi 1.9 mm, Ø ext 124.0 mm, flasque fond 4.0 mm évidée à Ø 97 mm et 10× perçages **Ø 3.3 mm** sur PCD Ø 106 mm (Plan 2D David SERGENT)
3. ☐ Usiner les **2 brides d'épaule arrière monoblocs (H = 48.2 mm)** dans des disques bruts **Ø 120 × 50 mm Alu 7075-T651** (Blockenstock) — alésage Ø 30.05 mm H7 sur 35.0 mm, flasque 13.2 mm, fente pincement 1.0 mm avec 2× M4 traversantes et trou goupille Ø 4.0 mm H7
4. ☐ Usiner les **4 plaques H-bracket (5 mm)** (2 avant + 2 arrière identiques) dans la tôle **Alu 7075-T6 5×160×160 mm** (Blockenstock) — Évidement central Ø 95 mm, 10× vis M4 sur PCD Ø 106 mm + **2 perçages tirants M5 à Ø 5.5 mm (ISO 273 Moyen)** aux oreilles Z=±66.1mm / Y=±28.6mm avec **chanfreins 0.5 mm × 45°** sur les deux faces
5. ☐ Usiner les **2 demi-coquilles du nœud d'intersection** (Bride Sup. et Bride Inf. alu 6061-T6)
6. ☐ Usiner les **2 bouchons internes anti-écrasement (Ø 26.0 mm h6 ext / Ø 18.0 mm int × 34.5 mm de longueur)** dans la **barre ronde Alu 7075-T651 Ø 30 mm** (Blockenstock) — laisse 0,5 mm de jeu d'isostatisme au fond pour l'appui 100% prioritaire du tube carbone sur la marche Ø 24 mm
7. ☐ Usiner la plaque supérieure de cou (alu 6061-T6, 5 mm) — équerres L-Brackets en sandwich
8. ☐ Usiner la Waist Plate (alu 6061-T6, 6 mm) — équerres L-Brackets en sandwich + **2 perçages M5 pour tirants roll (±60 mm)**
9. ☐ Usiner la bague d'adaptation RS-06 (alu 6061-T6)
10. ☐ Couper le tube carbone Ø30 mm à ~260 mm, chanfreiner les extrémités et percer la goupille Ø4 mm verticale à travers le nœud assemblé

### Phase 3 — Impression 3D (Qidi Plus 4)

1. ☐ **Prototype PLA** : Imprimer les 2 demi-coques verticalement en PLA (paramètres § 6.C) → valider les ajustements
2. ☐ **Version finale PA12-CF** : Imprimer les 2 demi-coques verticalement (paramètres § 6.A + Modifier Volume épaules § 6.B)
   - Coque abdominale : taille en bas sur le plateau, ~216 mm de Z
   - Thorax : plan de coupe en bas, cou en haut, ~216 mm de Z
3. ☐ Configurer le **Modifier Volume** cylindrique autour de chaque collet d'épaule (6 périmètres, 35% infill)
4. ☐ Supports arborescents (**Tree**) uniquement sous les collerettes d'épaule du Thorax, **Build Plate Only**

### Phase 4 — Assemblage du Torse Rigide, Serrage Dynamométrique & Insertion Goupilles

> [!NOTE]
> **Protocole d'Insertion des Goupilles Mécanindus (Sans Presse)** :
> - **Pourquoi AUCUNE presse ?** Une presse hydraulique n'offre aucun retour tactile et risquerait de matraquer le tube carbone en cas de léger désalignement des trous.
> - **Outillage requis** : Petit marteau de mécanicien (100 g - 200 g), chasse-goupille Ø 3,5 mm (légèrement inférieur au trou Ø 4,0 mm), tasseau de soutien / V-block percé d'un trou de décharge Ø 6 mm.
> - **Règle d'orientation de la fente** : Orienter impérativement la fente axiale de la goupille **à 90° de la direction de l'effort principal** (fente vers l'avant/arrière axe Y si l'effort est vertical Z) pour offrir 100% de la section pleine à la flexion.
> - **Procédure** : 
>   1. Poser la bride alu à plat sur le tasseau percé (zéro effort sur le tube carbone).
>   2. Appliquer une goutte d'huile fine sur le chanfrein d'entrée de 0,5 mm × 45° du perçage.
>   3. Amorcer la goupille chanfreinée à la main (toujours avec la goupille insérée AVANT le serrage du pincement).
>   4. Enfoncer par de petits coups secs de marteau (100-200g) via le chasse-goupille Ø 3,5 mm jusqu'à ce que la goupille soit parfaitement centrée.

> [!IMPORTANT]
> **Protocole de Serrage Dynamométrique du Pincement Radial (100% Mécanique Sans Loctite)** :
> - **Freinage Mécanique Sans Colle** : Utiliser des **écrous Nylstop M4 (bague nylon)** associés à des **rondelles Nord-Lock M4** ou **Schnorr dentelées**. Zéro Loctite liquide requis.
> - **Valeurs de Couple Clé Dynamométrique** :
>   - **Vis CHC M4 Classe 8.8** : **3.0 N.m** (développe 780 kgf de pression radiale sur le tube, friction pure = 27.0 N.m).
>   - **Vis CHC M4 Classe 10.9** : **3.5 à 4.0 N.m** (développe 1 040 kgf de pression radiale, friction pure = 36.0 N.m).
> - **Procédure de Serrage en 3 Passes Alternées** :
>   1. **Passe 1** : Approcher les vis CHC M4 N°1 et N°2 à **1.5 N.m**.
>   2. **Passe 2** : Élever le serrage des vis N°1 et N°2 à **2.5 N.m**.
>   3. **Passe 3 (Finale)** : Régler la clé à **3.0 N.m** (vis 8.8) ou **3.5 N.m** (vis 10.9) et serrer alternativement jusqu'au déclenchement net sur les deux vis.

1. ☐ Poser les inserts filetés M4 en laiton (Ruthex) dans les coques PA12-CF au fer à souder (260°C)
2. ☐ Assembler les demi-plaques de colonne vertébrale (5.0 mm) et les brides d'épaule jaunes (48.2 mm) sur les 2 plaques H-bracket orange (5.0 mm évidées Ø95mm)
3. ☐ Monter les **2 tirants axiaux M5 par épaule** (vis **CHC M5 × 60 mm ISO 4762 8.8**, 2× rondelles DIN 125A 1.0 mm, écrou Nylstop M5 DIN 985 bague nylon) à travers les perçages Ø 5.5 mm des oreilles Z=±66.1mm / Y=±28.6mm
4. ☐ Insérer les bouchons alu 7075 (Ø26/18×34.5mm) dans les extrémités du tube carbone Ø30mm
5. ☐ Appliquer le protocole d'insertion des goupilles élastiques inox Ø 4,0 mm × 35 mm à travers les brides et les bouchons alu (Nœud central + Épaules)
6. ☐ Appliquer le **Protocole de Serrage Dynamométrique à 3.0 N.m** sur les 2× vis M4 de pincement (avec écrous Nylstop M4 + rondelles Nord-Lock, sans Loctite)
7. ☐ Assembler la plaque de cou (haut) et la Waist Plate (bas) via les équerres L-Brackets en sandwich
8. ☐ Assembler le Thorax et l'Abdomen via le Lap Joint + vis M4 des bossages internes
9. ☐ Insérer les moteurs RS-04 dans les cages H-bracket par l'AVANT (extérieur de l'épaule) et serrer les 10× vis M4 × 10 mm (PCD Ø106 mm). Router les câbles XT30/CAN par l'évidement Ø95 mm vers l'intérieur du torse.

### Phase 5 — Assemblage Batteries + Hot-Swap

1. ☐ Monter les diodes Schottky MBR4060PT sur les radiateurs TO-247
2. ☐ Visser les radiateurs sur la plaque isogrid (face interne)
3. ☐ Câbler les connecteurs XT60 à l'arrière de chaque panier
4. ☐ Câbler le bus principal (sortie diodes → fusible PTC 40A → PDB Matek)
5. ☐ Installer les 2 paniers batterie dans les coulisses (test de coulissement + verrouillage)
6. ☐ Tester le hot-swap : alimenter avec les 2 batteries → retirer une → vérifier que le bus ne coupe pas

### Phase 6 — Assemblage de la Liaison Waist Yaw

1. ☐ Monter la bague d'adaptation alu CNC sur le corps du RS-06
2. ☐ Encastrer le moteur dans le pelvis inférieur
3. ☐ Poser le roulement à section fine Ø110 mm sous la Waist Plate
4. ☐ Accoupler le rotor du RS-06 au centre de la Waist Plate
5. ☐ Câbler le bus CAN-FD (ID 21) et la puissance 48V vers la PDB

---

## 12. Questions Ouvertes (À Résoudre)

1. **Dimensions internes réelles** : Quelle est la largeur interne utile entre les parois du torse (à mi-hauteur) dans le CAD après scale +18% ? Conditionne la largeur maximale des paniers.

2. **Batteries** : Source pour des packs 12S étroits (~50 mm) ? Ou assemblage custom à partir de cellules 21700 ?

3. **Traverse d'épaule** : Tube carbone Ø30 mm (léger, rigide, isolant thermique) ou barre isogrid alu (conductrice thermique, plus lourde) ?

4. **Profondeur du manchon alu d'épaule** : Confirmer la hauteur utile du manchon (30 mm recommandé, collet total = 68,44 mm après scale).

5. **Circuit hot-swap** : Diodes Schottky (V1, simple, 9W de pertes) ou MOSFET Ideal Diode (V2, <0.5W, plus complexe) ?

---

*Document créé en Mai 2026 — Architecture Cruciforme D-Bot v1.0. Remplace le GUIDE_Fabrication_Torse_Asimov_Hybride.md (archivé).*

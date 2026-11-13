# Audit expert : STUDY_Bilan_Masse_Global_et_Opportunite_Waist_Pitch_2DoF.md

**Document audité :** [STUDY_Bilan_Masse_Global_et_Opportunite_Waist_Pitch_2DoF.md](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/STUDY_Bilan_Masse_Global_et_Opportunite_Waist_Pitch_2DoF.md)
**Sources croisées (Niveau 1 en priorité) :** FINAL_CONSOLIDE_Bras_et_Mains.md, FINAL_Architecture_Globale.md, FINAL_BOM_Torse_et_Waist_D-Bot.md, FINAL_Liste_Achats_BOM.md, Audits/AUDIT_METROLOGIQUE_Torse_et_Bassin.json, STUDY_Squelette_Pelvien_Pont_de_Hanches.md, STUDY_Motorisation_QDD_RobStride.md, DOSSIER_TECHNIQUE_Bassin_et_Waist_D-Bot.md.

> [!NOTE]
> La base LightRAG n'a pas pu être interrogée depuis le sandbox (accès refusé à `lightrag_dbot_db/`, qui est hors du workspace). Tous les recoupements ont donc été faits directement par lecture des fichiers sources de Niveau 1 et 2 (grep + lecture des fichiers), ce qui revient au même sur le fond.

---

## Verdict global

| Volet | Verdict |
| :--- | :--- |
| Partie bassin « Pont de Hanches » (sections 1-2) | **Bonne direction**, gain réel de 2 à 3 kg. En revanche, plusieurs chiffres contredisent la STUDY Pont de Hanches dont ils sont tirés. |
| Bilan de masse global (section 3) | **Erreur de méthode critique** : la conclusion repose sur la Grille A, dont le document reconnaît lui-même qu'elle est fausse. La Grille B sous-estime encore les bras d'environ 1,8 kg (écart avec le Niveau 1). |
| Validation locomotion / portage (section 4) | Arithmétique globalement juste, mais sur une masse fausse. Mélange crête et continu, aucune vérification de vitesse ni de puissance, hanche Roll sous-estimée. |
| Opportunité du Waist Pitch (sections 5, 8, 9) | **Prémisse physique fausse** (on suppose que la V1.0 ne peut pas pencher le buste), gains chiffrés sans démonstration, et la décision « GO V1.5 » n'est pas justifiée en l'état. |
| Intégration et quincaillerie (section 6) | **Incompatibilités bloquantes** : inserts M5 alors que le document prévoit des vis M6, et vis M4x30 qui vont au fond des taraudages borgnes du stator RS-04. Plusieurs références McMaster n'ont pas été vérifiées. |
| Forme (sommaire, liens, cohérence interne) | 6 ancres mortes, 1 lien de fichier mort, plage angulaire et position de l'axe contradictoires d'une section à l'autre, statut « VALIDÉ » injustifié. |

---

## A. Erreurs critiques (elles changent les conclusions)

### A1. La conclusion massique s'appuie sur une grille que le document déclare lui-même fausse

- Au §3.1, le document identifie correctement deux sous-estimations : `EPA-03` compté à 551 g par moteur au lieu de 1 420 g (confirmé dans FINAL_BOM ligne 83), et les bras.
- Le §3.2 (Grille A) conserve pourtant ces deux erreurs (bras à 6,50 kg, torse à 13,94 kg avec `EPA-03` à 1,10 kg). On obtient ainsi 37,74 kg, et **c'est cette valeur qui sert de référence V1.0 dans tout le document** (§4, §5.1, §8, §9.4 : « V1.5 = 39,74 kg < 40,4 kg »).
- Autre incohérence dans la Grille A : « 2 jambes = 13,20 kg » alors que les seuls moteurs des jambes pèsent 12,72 kg. Il resterait 0,48 kg pour toute la structure de deux jambes, ce qui est physiquement impossible.

**Correction :** il faut abandonner la Grille A. Seul un bilan physique (de type Grille B) peut servir de référence.

### A2. La Grille B est elle-même fausse sur les bras, la tête et les mains (écart avec le Niveau 1)

| Poste | STUDY audité (Grille B) | Niveau 1 (vérité terrain) | Écart |
| :--- | :--- | :--- | :---: |
| Composition d'un bras | 1 RS-04, 2 RS-03, 1 RS-02, **3 RS-00** | FINAL_CONSOLIDE_Bras_et_Mains §2.1 : 1 RS-04, 2 RS-03, **2 RS-02**, **1 RS-00** | - |
| Masse des 2 bras + mains | **10,98 kg** (cite « 5,49 kg/bras » de FINAL_CONSOLIDE) | FINAL_CONSOLIDE §2.6 : **6 394 g par bras, soit 12,79 kg** | **+1,81 kg** |
| Masse d'un RS-00 | 190 g | 310 g (STUDY_Motorisation) | - |
| Masse d'un RS-02 | 380 g (c'est la masse du RS-01) | 405 g | - |
| Servos des mains | 16x `HLS3830M`, « 38 kg.cm » | 10x `STS3250` + 6x `HL-3915` (FINAL_Architecture_Globale §5, FINAL_Liste_Achats_BOM) | désynchronisation |
| Cou | 3 DOF (2x RS-05 + 1x RS-00 Yaw) | 2x RS-05 (Pan + Tilt) | désynchronisation |
| Nombre de RobStride | annoncé 27, mais le tableau en liste **30** | 27 = 12 jambes + 1 taille + 12 bras + 2 cou | incohérence interne |

> [!NOTE]
> La citation « 5,49 kg par bras » attribuée à FINAL_CONSOLIDE_Bras_et_Mains.md est inexacte : ce document donne ~6,4 kg (ligne 162). Les valeurs de grip (140 N / 438 N) recopiées dans le STUDY ont été calculées pour le `STS3250`, pas pour le `HLS3830M`.

### A3. Bilan global corrigé, et ce que cela implique pour la course

Bilan recalculé avec les données de Niveau 1. Le bassin est pris à 2,67 kg (valeurs de la STUDY Pont de Hanches) ou 2,90 kg (coque réaliste, voir B3) :

| Configuration | Masse corrigée | Écart vs hypothèse 40,4 kg |
| :--- | :---: | :---: |
| V1.0, plastron actuel | **42,3 à 42,6 kg** | +1,9 à +2,2 kg |
| V1.0, plastron évidé R1.5-B | **41,3 à 41,6 kg** | +0,9 à +1,2 kg |
| V1.5 (+1,89 à 2,00 kg), plastron évidé | **43,2 à 43,6 kg** | **+2,8 à +3,2 kg** |
| V1.5, plastron actuel | **44,2 à 44,6 kg** | +3,8 à +4,2 kg |

Calcul effectué **avec le propre modèle linéaire du document** (§4.4 : 118,9 N.m de hanche Pitch à 40,4 kg sous 2,5 g, soit 2,94 N.m/kg) :

- Hanche Pitch en course, V1.0 évidé (41,3 kg) : environ **121,7 N.m**, soit 101 % de la crête du RS-04. On est déjà à saturation.
- Hanche Pitch en course, V1.5 évidé (43,2 kg) : environ **127,2 N.m**, soit **106 % de la crête**.
- Cheville en course, V1.5 (43,2 kg) : environ **111 N.m**, soit **93 % des 120 N.m**. Il ne reste quasiment aucune marge.

> [!WARNING]
> L'affirmation centrale « la V1.5 tient dans l'enveloppe 40,2-40,4 kg sans compromettre aucune capacité » est **fausse**, y compris d'après la Grille B du document (41,53 kg). Le seul élément qui compense, ce sont les « -16,5 N.m de hanche grâce au Waist Pitch actif ». Or ce chiffre n'est démontré nulle part (voir A4).

### A4. Prémisse physique fausse : la V1.0 peut pencher le buste avec les hanches

Tout l'argumentaire des §5.3, §8.2 et §9.3 compare une V1.5 au buste penché à une V1.0 « tronc bloqué à 0 deg » qui serait obligée de faire un squat profond. C'est faux : **les deux RS-04 de hanche Pitch inclinent l'ensemble bassin + torse** (la flexion de hanche avec dos droit, ou hip hinge). C'est ainsi que H1, K-Bot et la plupart des humanoïdes sans waist pitch ramassent un objet ou contre-balancent une charge.

Conséquences en quasi-statique (lois de Newton) :

1. **Le couple de hanche ne dépend que de la position horizontale du CoM du haut du corps par rapport à l'axe de hanche**, et pas de l'articulation qui produit la posture. Exemple avec le buste penché de 20 deg et le bassin vertical en V1.5 : le CoM du buste avance de `0,24 * sin(20) = 82 mm`. Les hanches portent donc exactement le même moment que celui fourni par le Waist Pitch. **Le RS-04 de taille ajoute un actionneur chargé en série, il ne soulage pas les hanches.**
2. Pour un même placement du CoM au-dessus des pieds, **le couple de genou est identique en V1.0 (hip hinge) et en V1.5**. Le gain annoncé « 142 N.m vers 94 N.m » n'est pas propre à la V1.5.
3. Pour pencher le buste, la V1.0 répartit le moment sur **2 RS-04** en double appui (environ 16 N.m chacun à 20 deg). La V1.5 le concentre sur **un seul RS-04** (environ 20 à 24 N.m). Pour le portage bimanuel lourd, la V1.5 crée donc un maillon faible supplémentaire.
4. Dans le tableau du §9.3, le couple de hanche Pitch **diminue** quand le buste se penche (de 52 à 27 N.m). C'est physiquement l'inverse quand le bassin reste fixe. Les colonnes Genou, Hanche et Cheville de ce tableau ne sont pas dérivées. Elles sont affirmées.

Les seuls vrais différentiateurs de la V1.5 sont :
- (a) une limite d'amplitude de flexion de hanche, à vérifier ;
- (b) la possibilité d'orienter le torse indépendamment du bassin, qui sert à la manipulation et à la caméra ;
- (c) la redistribution du moment cinétique en dynamique.

Ces trois points sont réels, mais aucun n'est chiffré dans le document.

### A5. Gains chiffrés présentés comme démontrés sans dérivation

Les valeurs suivantes n'ont aucun calcul derrière elles et doivent être requalifiées en « hypothèses à valider en simulation » :

- « -16,5 N.m hanche / -18 N.m genou en course » ;
- « -18 % de push-off cheville » ;
- « Push Recovery +28 % » ;
- « marge ZMP +45 % » ;
- « 85 % localisation / 15 % valeur scalaire » (attribué à Featherstone et Kajita : ces ouvrages ne contiennent pas ce résultat) ;
- « -6 mm de CoG global ».

---

## B. Erreurs de calcul et incohérences chiffrées

### B1. Tableau §2.1 (pièces supprimées)
- Sous-total des volumes : `2 835,2 + 761,2 + 191,8 + 251,3 = 4 039,5 cm3`, et non 3 943,6.
- Sous-total FDM : `2 315,6 + 2 055,2 + 187,2 + 135,1 + 193,9 = 4 887,0 g`, et non 4 413,0. La valeur 4 277,5 g reprise au §2.4 n'est pas traçable.
- Désynchronisation de référence : la Traverse est `ASV1_200_16A` dans la CAO (JSON), la FINAL_BOM et le DOSSIER, et non `02C`. *(Résolution `Torse-123 v42` : masse réelle CAO évidée = `566,74 g` dans [`Audits/AUDIT_METROLOGIQUE_Torse_et_Bassin.json`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/01_Mecanique_et_Chassis/Torse_et_Bassin/Audits/AUDIT_METROLOGIQUE_Torse_et_Bassin.json), vs `617,39 g` en géométrie historique pré-évidement ; le `247 g` erroné provenait d'un ancien parsing `RB8016`/`Traverse` obsolète et a été corrigé.)*

### B2. Tableau §2.2 (squelette), comparé à la STUDY Pont de Hanches
| Élément | STUDY audité | STUDY Pont de Hanches / calcul | Commentaire |
| :--- | :--- | :--- | :--- |
| Tube central | `60 x 60 x 3`, 155,8 g | `60 x 60 x 2` ; 155,8 g correspond bien à une paroi de 2 mm | Coquille dans le texte. En paroi de 3 mm, il pèserait 229,6 g. |
| Brides v87 | `Ø 116 x 20,5` | `Ø 120 x 33,2` | Désynchronisation |
| Taraudage des inserts | M6 | **M5** (FHC M5x25, engagement de 15 mm) | Incompatible avec le §6.3 |
| Visserie | 158 g (M6x25, M5x16, M4x16...) | `136,78 g` en CAO `v42` (`2x M5x80 [91290A276]`, `4x M5x35 [91290A661]`, `4x M5x20 [92290A242]`, `4x FHC M5x18 [92125A213]`, `8x M4x25`) | Liste de vis réconciliée (`v42`) |
| Masse « hors visserie » (§1.1) | 1,38 kg | `1 436,2 - 158 = 1 278 g` | Incohérence interne |
| Insert 25x25 | 16,1 g | Volume plein d'environ 8 cm3, soit environ 22 g en 7075 | Évidement à justifier |
| RS-04 | `Ø 116 x 52` | `120 x 120 x 56` (STUDY_Motorisation) | Désynchronisation |

### B3. Coque PA12-CF (§2.3) sous-estimée
- Une paroi de 2,5 mm avec 3 périmètres de 0,6 mm est **quasiment pleine** : la densité apparente se situe autour de 0,85 à 1,0 g/cm3, et non 0,55. Le chiffre de 0,55 vient du capot 15C, qui est une pièce épaisse avec du remplissage.
- Avec `2 650 cm2 x 0,25 cm = 662 cm3`, la coque principale pèse environ 560 à 660 g, contre 380 g annoncés. La STUDY Pont de Hanches retient elle-même ~680 g pour l'habillage.
- **Correction : compter environ 750 à 900 g d'habillage complet, et non 550 g.**

### B4. Portage des bras (§4.1), comparé à FINAL_CONSOLIDE_Bras_et_Mains §2.6
- Bras tendu : le facteur limitant est le **poignet RS-00 (4,1 kg en continu / 11,7 kg en pic)**, et non l'épaule. Le pic de 14,6 kg est faux.
- Bras fléchi, d = 0,25 m, coude RS-03 : `20 / (9,81 * 0,25) = 8,15 kg` **avant** le poids de l'avant-bras. Les 8,6 kg (continu) et 29 kg (pic, qui donnerait 71 N.m > 60 N.m) sont impossibles.
- Portage bimanuel : 16 à 20 kg en continu dépasse 2 coudes RS-03. Le plafond réaliste est d'environ 14 à 15 kg.
- L'abduction (épaule Roll limitée à ~1,7 kg) n'est pas mentionnée.
- « Stabilité ZMP améliorée par l'allègement » : c'est l'inverse. Un robot plus léger subit un **plus grand** déplacement de CoM pour une même charge portée.

### B5. Locomotion (§4.2-4.4)
- **Mélange entre crête et continu** : au §4.2, le genou est comparé à sa crête (300 N.m) alors qu'en marche à vide, 113 à 119 N.m dépassent déjà le continu (100 N.m). Au §9.3, c'est au contraire le continu qui sert de critère. Il faut un critère unique : **couple RMS sur le cycle de marche** pour la thermique, **crête** pour la saturation.
- **Pas de vérification de vitesse** : la réduction GT3 2,5:1 limite le genou à `200 / 2,5 = 80 tr/min = 8,4 rad/s` à vide (environ 7 rad/s au régime nominal de 167 tr/min). En course à 5-8 km/h, le genou en phase de balancement dépasse couramment 10 rad/s. **La course reste limitée par la vitesse du genou**, ce que FINAL_Architecture_Globale signale d'ailleurs (« vitesse marche max ~7 km/h, limite RS-04 vitesse »).
- **Hanche Roll** (§4.3) : l'hypothèse d'un déport latéral résiduel `d_lat = 35 mm` est très optimiste. L'axe de hanche Roll se trouve à environ 90-100 mm du plan médian. Une estimation réaliste en appui unipodal donne environ 30 à 40 N.m, soit 50 à 67 % de la crête et plus que le continu de 20 N.m. Pour comparaison, le Unitree G1 (~35 kg) déclare environ 139 N.m en hanche Roll dans son URDF.
- « Saturation magnétique » : le terme est impropre. Il s'agit d'une limite de courant ou de couple crête du variateur.

### B6. Waist Pitch (§5.2, §5.4, §9.2)
- **`M_upper = 20 kg` est sous-estimé.** Au-dessus de l'axe Pitch se trouvent : torse 4,4 à 5,4 + bras 12,8 + tête 0,8 + énergie 3,8 (si les batteries sont dans le torse) + module Yaw 1,6 + Traverse 0,6 + bras du berceau 0,3, **soit environ 24 à 25 kg**. Avec `h_CoM = 0,24 m`, cela donne `M_0 ~ 57 N.m` au lieu de 47 N.m (+22 %).
- §5.4 cas B : le terme avant-bras (~10 N.m) est compté à 0 deg puis disparaît à -7 deg. Le couple corrigé avec la géométrie du document est d'environ **36,5 N.m** (Sf ~ 1,10), et non 26,4 N.m. Le recul de la charge vaut aussi `0,20 * sin(7) = 24 mm` avec le `h_charge` du §9.2, et non 45 mm.
- §8.2 ligne 6 : la contre-inclinaison de -7 deg déplace le CoM global d'environ 18 mm, et non de 58 à 12 mm.
- §9.2 : ce qui compte pour la chute arrière, c'est le **CoM global**, pas celui du buste seul. À -20 deg, le CoM global recule d'environ `20/39,7 * 82 = 41 mm`, ce qui reste loin du talon (-75 mm). L'argument « chute dorsale irrécupérable » est faux. La borne de -12 deg peut rester valable, mais pour d'autres raisons (harnais, coque).
- §5.2 : à 0 deg, en marche ou en course, le couple de Waist Pitch n'est pas de « ~5 N.m ». Il est dominé par les accélérations horizontales du bassin : `M_upper * a_x * h = 24,5 * (5 à 10) * 0,24`, soit **environ 30 à 60 N.m** en course.

### B7. « Optimum Pareto à +23 deg » (§9.3)
- L'égalisation de deux facteurs de sécurité correspond à un critère **max-min**, pas à un front de Pareto. La logique max-min se défend, mais seulement si les courbes sont justes, ce qui n'est pas le cas de celle du genou (A4).
- Le résultat est très sensible aux hypothèses. Avec `M_upper = 24,5 kg`, l'égalisation tombe vers **19-20 deg**, et le maintien statique de 10 kg à +23 deg exige environ **41,8 N.m, au-delà des 40 N.m continus**.
- Les longueurs de tronc ne sont pas cohérentes entre sections : 0,44 m au §5.3, 0,375 m au §9.3.
- Qualifier ce résultat de « certifié » est abusif.

### B8. Incohérences internes (le document n'a pas été consolidé après le §9)

| Paramètre | Valeurs rencontrées |
| :--- | :--- |
| Plage utile | ±20 (titre, synthèse) / -10 +20 (§5.1) / -12 +23 (§9) |
| Butées | ±22 (§5.1) / -12 +22 (§6.2) / -14 +25 (§9) |
| Axe Pitch Z | -102 mm (§6.2) / -95 mm (§9.4) |
| Épaisseur des joues | 12 mm (§5.1, §6.2) / 15 mm (§9.4) |
| Berceau | U fermé de 340 g (§5.1, §6.2) / berceau ouvert à 2 bras (§9.4) |
| Pièces CNC ajoutées | 3 (§8.3) / 4 (§9.4) |
| Montants V1.5 | 60 mm / 65 à 70 mm |
| Vis berceau-Traverse | 8x M5x16 (§6.3) / 6x M5x20 (§9.4, sans référence) |

- §9.4 : « toutes les pièces de la V1.5 dans une seule plaque de 15 mm » est impossible pour les **inserts** (hauteur `3 + 15 = 18 mm`, section 25x25) et pour les **brides v87** (33,2 mm).

---

## C. Intégration mécanique et quincaillerie (§6)

### C1. Incompatibilités bloquantes
1. **Joues fixées sur les inserts avec des vis M6x25**, alors que les inserts du Pont de Hanches sont taraudés **M5**. Montage impossible.
2. **Stator du RS-04 de taille fixé par des vis M4x30 + écrous Nylstop** à travers une joue de 12 mm. Or le stator du RS-04 a des **taraudages borgnes** (pénétration maximale de 6 mm d'après la STUDY Pont de Hanches). Avec ces vis, la pénétration atteindrait environ 17 mm : **le carter du moteur serait détruit**. La longueur à retenir est `12 + 1,8 (Nord-Lock) + ~5 = ~19-20 mm`, sur le même modèle que les montages M4x12 et M4x25 du Pont de Hanches.
3. **Couple M4 dans le stator : 4,0 N.m**, alors que le DOSSIER impose **3,0 N.m** (vis dans l'alu du carter RobStride).

### C2. Références McMaster
| Référence | Statut |
| :--- | :--- |
| `91290A180`, `91290A242`, `93625A150`, `93475A230` | Déjà présentes dans les documents du projet |
| `91595A354` (goupille Ø5 x 16) | Correspond bien à une goupille Ø5 x 16. Matière et tolérance m6 à confirmer |
| `91290A174` (M4x16), `91290A332` (M6x25) | Présentes uniquement dans des documents STUDY. 6 critères à vérifier. `91290A332` devient de toute façon caduque (M5 et non M6) |
| `91812A413`, `91812A253` (Nord-Lock M6/M5) | **Non vérifiées**, et elles n'appartiennent pas à la famille déjà certifiée dans le projet (Nord-Lock M4 = `92620A203`). Risque d'hallucination de référence |

Référence Nord-Lock M4 déjà certifiée dans le projet (à réutiliser pour le stator) :
```text
92620A203
```

### C3. Points d'intégration à vérifier en CAO
- **Encombrement en Y du RS-04 de taille** : sa largeur fait 56 mm et son axe est à Z -95/-102 avec un rayon de 60 mm. Il dépasse donc **au-dessus** de la face inférieure de la Traverse, qui mesure environ 175 x 175 mm dans le JSON. Il doit être placé hors de l'emprise de la Traverse, ce qui le met dans la même bande Y (environ 95 à 151 mm) que les RS-04 de hanche, à seulement ~17 mm au-dessus d'eux, et au-delà de la demi-largeur de coque (132 mm). **Ce point n'est étudié nulle part.**
- **Débattement du RS-06** : seul le point bas central se déplace de 3 à 5 mm. Les arêtes du carter à r ~ 48 mm balaient environ **20 mm** à +25 deg. Il faut vérifier le jeu avec les bras du berceau et avec la coque.
- **Harnais** : `R = 65 mm` respecte `R >= 10 x Ø` seulement pour un câble de 6,5 mm ou moins. Un 8 AWG silicone fait environ 7 mm, donc la règle n'est pas respectée. Il faut prévoir `R >= 75-80 mm`, ou passer à 2 x 10 AWG en parallèle.
- **6807-2RS « déjà acquis »** : la FINAL_Liste_Achats_BOM (ligne 80, et non L33) l'affecte aux RS-04 de hanches et genoux. Les quantités sont à revoir.

---

## D. Points de physique système absents du document

1. **Mode souple tronc/bassin.** Inertie du haut du corps autour de l'axe Pitch : environ 1,9 kg.m2. Avec une raideur d'asservissement QDD réaliste de 300 à 1 000 N.m/rad, la fréquence propre est d'environ **2 à 3,6 Hz**, c'est-à-dire **dans la bande de la cadence de pas (1,8 à 2,2 Hz)**. En V1.0, le tronc est rigide (mode au-delà de 30 Hz). Ce point est capital pour le sim2real et l'estimation d'état : il faut une IMU dans le torse en plus de celle du bassin.
2. **Ordre des axes.** Le document empile bassin, puis Pitch, puis Yaw, puis torse. Si le torse est tourné de 90 deg en lacet, une flexion « avant » penche alors le buste **sur le côté** par rapport à la poitrine. Les humanoïdes à taille multi-DOF (par exemple le G1 29-DoF : yaw, puis roll, puis pitch) placent le Pitch **au-dessus** du Yaw. Il s'agit d'un vrai compromis avec la modularité recherchée, qui doit être explicité.
3. **Coupure d'alimentation.** Le RS-04 n'a pas de frein : le tronc (~24 kg) tombe sur la butée. Prévoir un mode de freinage par court-circuit des phases si le driver le permet, et dimensionner les butées PU pour environ 4 J.
4. **Thermique en maintien.** En manipulation au sol ou en portage, le Waist Pitch tient 30 à 37 N.m en continu, soit 75 à 92 % de son couple nominal. Il faut un modèle thermique I²R avec la constante de temps du bobinage.
5. **Provision de croissance de masse.** En phase CAO, la pratique industrielle applique une réserve de +10 à 15 % (connecteurs, câblage réel, IMU, refroidissement). La cible réaliste en sortie d'assemblage est donc plutôt de **46 à 48 kg** si rien n'est fait.

---

## E. Forme et règles projet
- **Ancres mortes dans le Sommaire (6)** : §1.2, §2, §5, §8.2, §9, §9.1. Elles sont dues au `+/-` : le slug réel contient `---` et non `--`.
- **Lien mort** : `DOSSIER_TECHNIQUE_Waist_et_Bassin_D-Bot_V2.md` n'existe pas. Le fichier réel est `DOSSIER_TECHNIQUE_Bassin_et_Waist_D-Bot.md`.
- Aucun `$` ni LaTeX : conforme. Les deux SVG existent et sont intégrés, mais ils affichent des valeurs à réaligner après correction (37,74 kg, ±20 deg, berceau en U).
- Le statut « VALIDÉ — RÉFÉRENTIEL DE DÉCISION » n'est pas justifié pour un document de Niveau 2 contenant ces erreurs. Il faudrait le passer en « EN RÉVISION ».

---

## F. Recommandations d'architecte

1. **Garder le Pont de Hanches**, mais recaler ses chiffres sur la STUDY source : tube 60x60x2, brides Ø120 x 33,2, inserts M5, coque à environ 0,8 kg.
2. **Remplacer les Grilles A et B par un bilan de masse unique**, construit depuis la CAO et le Niveau 1 (bras 12,79 kg, servos STS3250/HL-3915, cou 2x RS-05), avec une réserve de croissance affichée. Masse V1.0 réaliste : environ 41,5 à 42,5 kg.
3. **Traiter en priorité les deux vrais points durs du bas du corps**, qui comptent davantage que le Waist Pitch :
   - la **hanche Pitch en course**, à saturation dès la V1.0 d'après le modèle du document lui-même ;
   - la **hanche Roll** (RS-03, 60 N.m crête).

   Il faut en parallèle lancer une campagne de réduction de masse : plastron évidé R1.5-B, structure des bras, harnais.
4. **Décision sur le Waist Pitch : ne pas engager la V1.5 dès le premier jet ; concevoir une V1.0 qui la prévoit.** Le document affirme lui-même que la V1.5 est « plug-and-play sans aucune retouche » (§6.1, §7), ce qui contredit son argument « GO direct pour éviter le double travail » (§8.4). Concrètement :
   - imprimer dès maintenant la coque du bassin compatible avec la V1.5 (biseau de 18 mm et lèvre TPU) ;
   - réserver l'encombrement en Y et les perçages de la Traverse pour les bras du berceau ;
   - fixer une **porte de décision** fondée sur une simulation MuJoCo/Isaac V1.0 contre V1.5 (couples RMS et crête hanche/genou/cheville sur marche, course, ramassage et portage, avec politique RL entraînée pour chacune) et sur la masse réellement pesée.
5. **Si la V1.5 est retenue** : revoir l'ordre des axes (Pitch au-dessus du Yaw) ou documenter la limitation, corriger les fixations (M5 sur les inserts, vis M4 d'environ 20 mm + Nord-Lock dans le stator à 3,0 N.m), recalculer `M_upper` et `h_CoM` depuis la CAO, puis refaire l'optimisation d'angle. Avec les masses corrigées, la plage se situe plutôt vers **-12 / +20 deg**. Enfin, vérifier l'amplitude de flexion de la hanche Pitch : c'est le vrai critère qui différencie la V1.5 pour le ramassage au sol.

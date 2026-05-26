# Guide de Montage Complet : Doigts & Tendons ORCA (Traduit & Adapté D-Hand)

> **Source officielle :** [orcahand.com/legacy/files#assembly](https://www.orcahand.com/legacy/files#assembly)
> **Vidéo de montage officielle :** [YouTube — Assemblage ORCA (t=3s)](https://youtu.be/va7ZUgVrn84?t=3)
> **Vidéo de présentation :** [YouTube — Release ORCA Hand](https://www.youtube.com/watch?v=WNtlUViSrPg)
>
> ⚠️ *Ce guide est localement traduit et adapté pour la D-Hand Hybrid (8 DOF). Les étapes concernant la motorisation ORCA (17 servos Feetech dans la tour imprimée, étapes 08 à 25) sont mentionnées mais non détaillées, car remplacées par notre architecture **Feetech Hybrid Premium** (5× STS3250 + 3× HL-3915) avec spools CNC usinés.*

---

## Étape 00 — Introduction : Tendons et Nœuds

### Principes Fondamentaux

Le **Nœud Ashley Stopper** (aussi appelé "Oysterman's Stopper") est utilisé massivement à travers tout le montage. Il constitue la méthode de fixation officielle de tout tendon dans la main ORCA.

🔗 **[Tutoriel animé : Comment réaliser un nœud Ashley Stopper](https://www.animatedknots.com/ashley-stopper-knot)**
▶️ **[Vidéo de montage complète sur YouTube](https://youtu.be/va7ZUgVrn84?t=3)** *(à regarder en premier pour se familiariser avec les gestes)*

### Règles impératives avant de commencer :

1. **Serrez toujours les nœuds fermement** en tirant des deux côtés. Utilisez des pinces à bec plat pour appliquer une tension supplémentaire. Un nœud lâche se défait à l'usage répété.
2. **Laissez toujours une courte queue (~0.5 cm)** après la coupe du tendon excédentaire. Cette queue empêche le nœud de se défaire dans le temps.
3. **Lame de rasoir ou scalpel obligatoire** pour couper le Dyneema. Appliquer une tension sur le fil et couper en un seul mouvement net (sans va-et-vient). Ne jamais utiliser de ciseaux ni de lames émoussées : les brins se séparent, rendant l'insertion dans les canaux impossible.
4. **Si l'insertion du tendon dans un canal échoue plusieurs fois**, couper à nouveau l'extrémité du fil pour avoir une coupe nette, et recommencer. Les tolerances sont serrées, mais un bout propre passera.
5. **Utilisez des brucelles (tweezers)** pour appliquer une pression uniforme et guider le tendon. Elles ne sont pas représentées dans les photos des étapes pour la lisibilité, mais elles sont **vivement recommandées**.

![Knot step 1](Images_ORCA/Assembly_2_00_About_tendons_and_knots_substep_01.png)
![Knot step 2](Images_ORCA/Assembly_2_00_About_tendons_and_knots_substep_02.png)
![Knot step 3](Images_ORCA/Assembly_2_00_About_tendons_and_knots_substep_03.png)
![Knot step 4](Images_ORCA/Assembly_2_00_About_tendons_and_knots_substep_04.png)
![Knot step 5](Images_ORCA/Assembly_2_00_About_tendons_and_knots_substep_05.png)
![Knot step 6](Images_ORCA/Assembly_2_00_About_tendons_and_knots_substep_06.png)
![Knot step 7](Images_ORCA/Assembly_2_00_About_tendons_and_knots_substep_07.png)

> [!NOTE]
> *Adaptation D-Hand :* Le matériau officiel ORCA est du Dyneema Ø0.40–0.41 mm. **La D-Hand Hybrid Premium utilise du Vectran LCP Ø0.80 mm** (fluage quasi nul, résistance à la rupture ~950 N) pour supporter le couple 2× supérieur des STS3250 (50 kg·cm stall) et éliminer le recalibrage périodique.

---

## Étape 01 — Routage du Tendon de la Pulpe Distale (Fingertip)

Passez un tendon d'environ **0.5 m de long** avec un nœud Ashley Stopper à une extrémité par le trou situé sur le côté de l'assemblage IP (phalange distale). Suivez précisément les images pour l'ordre de passage dans les canaux internes. Vérifiez que le nœud est bien encastré dans le logement interne en tirant fermement.

*Répétez pour tous les doigts, y compris le pouce.*

![Fingertip step 1](Images_ORCA/Assembly_2_01_Fingertip_Tendon_Routing_substep_01.png)
![Fingertip step 2](Images_ORCA/Assembly_2_01_Fingertip_Tendon_Routing_substep_12.png)

---

## Étape 02 — Routage du Tendon de la Phalange Proximale (PP)

Insérez d'abord les **goupilles cylindriques (2×6 mm acier)** qui serviront d'axes des articulations. Aidez-vous d'une autre goupille ou d'un tournevis fin pour les guider en tapotant doucement depuis le côté opposé avec un maillet.

⚠️ **Attention critique :** La goupille doit rentrer parfaitement droite. Une insertion en angle la rend inamovible et peut forcer la casse de la phalange imprimée.

Une fois la goupille en place, insérez le tendon depuis le trou lateral et réalisez le même nœud Ashley que pour l'étape 01.

*Répétez pour tous les doigts, y compris le pouce.*

![PP step 1](Images_ORCA/Assembly_2_02_PP_Tendon_Routing_substep_01.png)
![PP step 2](Images_ORCA/Assembly_2_02_PP_Tendon_Routing_substep_07.png)

---

## Étape 03 — Routage des Tendons d'Abduction (Écartement des Doigts)

Prenez **2 tendons de 50 cm** (sans nœuds initiaux) et insérez-les sur le coté de la pièce articulation de'abduction (base du doigt, pièce en "T"). Une fois passés à travers les trous traversants, réalisez un nœud Ashley à l'extrémité de **chacun** des deux tendons sortants. Tirez les deux tendons vers l'arrière pour verrouiller les nœuds dans leurs logements.

*Répétez pour tous les doigts, sauf le pouce (qui a son propre système — voir Étape 06).*

![Abd step 1](Images_ORCA/Assembly_2_03_Abduction_Routing_substep_01.png)
![Abd step 2](Images_ORCA/Assembly_2_03_Abduction_Routing_substep_09.png)

---

## Étape 04 — Coulée de la Peau en Silicone (Skin Casting)

> [!IMPORTANT]
> **Cette étape est mécaniquement obligatoire, pas seulement cosmétique.** L'ORCA n'utilise **aucun ressort métallique**. C'est l'élasticité naturelle de la peau en silicone qui assure le **retour passif primaire des doigts en position ouverte** quand le moteur relâche le câble fléchisseur. La D-Hand ajoute un **ressort à lame en PA12-CF** comme sécurité secondaire anti-fatigue (voir §2.4 du GUIDE_COMPLET).

Imprimez les moules négatifs (ORCA_Molds.zip dans `Ressources 3D/ORCA_Hand`). Coulez-y un silicone de type EcoFlex 00-30 ou Dragon Skin 10. Laissez polymériser selon les instructions du fabricant (généralement 4h à température ambiante). Démoulez avec précaution.

---

## Étape 05 — Assemblage Final du Doigt

Vous pouvez code-couleur vos tendons au marqueur pour vous repérer.
- Le tendon **extenseur** (celui qui ouvre le doigt) passe par le **trou supérieur** de l'assemblage PP.
- Le tendon **fléchisseur** (celui qui fermera le doigt, relié au spool moteur) passe par le **trou inférieur**.

Emboîtez l'assemblage de la phalange distale sur l'assemblage PP en l'enfonçant jusqu'au déclic d'emboîtement. Les roulements **MR84ZZ** (4×8×3 mm) s'emboîtent à ce stade dans les logements de la phalange pour y éliminer toute friction axiale.

*Répétez pour tous les doigts sauf le pouce.*

![Finger asm 1](Images_ORCA/Assembly_2_05_Finger_Assembly_substep_01.png)
![Finger asm 2](Images_ORCA/Assembly_2_05_Finger_Assembly_substep_13.png)

---

## Étape 06 — Routage du Tendon d'Abduction du Pouce

Même procédure que l'Étape 03, mais appliquée à la pièce spécifique d'abduction du pouce (géométrie différente car le pouce pivote sur un plan différent). Deux tendons de 50 cm, nœud Ashley à chaque extrémité sortante, tirez pour verrouiller.

Vérifiez le routage : tirez manuellement sur chaque tendon et observez que l'articulation tourne de façon fluide dans les deux sens avant de clore l'assemblage.

![Thumb abd 1](Images_ORCA/Assembly_2_06_Thumb_Abduction_Tendon_Routing_substep_01.png)

---

## Étape 07 — Assemblage du Pouce Complet

Faites passer tous les tendons du pouce à travers le grand canal d'accès prévu. Emboîtez ensuite les composants du pouce en les enfonçant jusqu'à l'enclenchement. Le pouce a une cinématique avec opposition (DOF 5) et flexion (DOF 4), ses tendons rejoindront deux sorties dédiées sur la paume CNC.

![Thumb asm 1](Images_ORCA/Assembly_2_07_Thumb_Assembly_substep_01.png)

---

## Étape 26 — Enroulement des Tendons sur les Spools (Poulies CNC)

> [!NOTE]
> *Adaptation D-Hand :* L'ORCA enroule les tendons sur les spools plastiques fixés sur les servos Feetech. **Sur la D-Hand Hybrid Premium,** les tendons Vectran LCP Ø0.80mm s'enroulent sur nos **poulies CNC usinées en aluminium 7075-T6 (Ø14mm, gorge hélicoïdale 0.75mm, 1.5 tour, roulement MR84ZZ intégré)** montées sur les axes des moteurs STS3250/HL-3915. Le tendon est bridé par vis sans tête M1.6 radiale (aucun nœud).

Procédure générique :
- Saisir le tendon libre qui sort de la paume (côté avant-bras).
- L'introduire dans la gorge hélicoïdale de la poulie CNC.
- Faire 1.5 tour d'enroulement dans la gorge.
- Tirer fermement pour établir une pré-tension de 10–15 N, puis serrer la vis sans tête M1.6 pour brider le câble (voir §Étape 7 du GUIDE_COMPLET).

![Spool step 1](Images_ORCA/Assembly_2_26_Tendon_spooling_substep_01.png)
![Spool step 2](Images_ORCA/Assembly_2_26_Tendon_spooling_substep_18.png)

---

## Étape 31 — Assemblage Final et Calibration

Félicitations, l'assemblage physique est complet !

La dernière étape consiste à **calibrer les tensions des tendons** en utilisant le script officiel, adapté pour nos 8 servos :

```bash
# ORCA officiel (à adapter pour D-Hand 8 DOF)
uv run python scripts/tension.py orca_core/models/orcahand_v1_right
uv run python scripts/calibrate.py orca_core/models/orcahand_v1_right
```

Vérifiez que :
- Chaque doigt peut se fermer et s'ouvrir complètement sans accroc.
- La peau en silicone ramène correctement les doigts en position ouverte quand la tension est relâchée.
- L'eFlesh est correctement sécurisé sous la peau silicone à la pulpe de chaque doigt.

![Finish 1](Images_ORCA/Assembly_2_31_Complete_Assembly_substep_01.png)

---

*Source : Guide officiel ORCA Hand (ETH Zurich / SRL) — orcahand.com — Traduction et adaptation D-Hand Hybrid, Mars 2026.*

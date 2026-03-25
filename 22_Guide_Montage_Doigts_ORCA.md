# Guide de Montage Local : Doigts ORCA (Base D-Hand Hybrid)

Ce document compile et traduit les étapes officielles critiques d'assemblage de la main ORCA. **Seules les étapes concernant la mécanique des doigts, des tendons et de la paume ont été conservées**, puisque la motorisation (étapes 08 à 30 de l'ORCA originale) est remplacée par notre système Dynamixel D-Hand personnalisé.

---

## Étape 00 : À propos des tendons et des nœuds

Les nœuds **Ashley Stopper (Oysterman's stopper)** sont utilisés massivement tout au long de l'assemblage. 
- Serrez toujours les nœuds fermement en tirant des deux côtés. Utilisez des pinces pour appliquer une tension supplémentaire.
- Lors de la coupe du tendon excédentaire après le nouage, laissez toujours une courte queue (~0,5 cm).
- **Important :** Utilisez toujours une lame bien aiguisée pour couper les tendons (ex: scalpel ou cutter X-Acto). N'utilisez pas de ciseaux ou de lames émoussées, car ils effilocheraient les extrémités du fil Dyneema.
- L'utilisation de petites pinces brucelles (tweezers) vous aidera considérablement à appliquer une pression uniforme et à guider le tendon lors de son insertion dans les canaux.

![Technique Ashley Stopper 1](https://storage.googleapis.com/orca-a25f9.firebasestorage.app/Assembly_2/00_About_tendons_and_knots/substep_01.png)
![Technique Ashley Stopper 2](https://storage.googleapis.com/orca-a25f9.firebasestorage.app/Assembly_2/00_About_tendons_and_knots/substep_02.png)
![Technique Ashley Stopper 3](https://storage.googleapis.com/orca-a25f9.firebasestorage.app/Assembly_2/00_About_tendons_and_knots/substep_03.png)

---

## Étape 01 : Routage du Tendon de la Pulpe (Fingertip)

Prenez un tendon d'environ **0,5 m de long**, réalisez un nœud Ashley Stopper à une extrémité. Passez le tendon par le trou situé sur le côté de l'assemblage de la phalange distale (IP). 
Assurez-vous que le nœud est bien sécurisé en tirant fortement sur le fil à travers le routage interne.

![Insertion IP 1](https://storage.googleapis.com/orca-a25f9.firebasestorage.app/Assembly_2/01_Fingertip_Tendon_Routing/substep_01.png)
![Insertion IP 2](https://storage.googleapis.com/orca-a25f9.firebasestorage.app/Assembly_2/01_Fingertip_Tendon_Routing/substep_02.png)

---

## Étape 02 : Routage du Tendon de la Phalange Proximale (PP)

Insérez les **goupilles métalliques (pins 2x6mm)** pour verrouiller les articulations. Vous pouvez utiliser une autre goupille ou un petit tournevis pour vous aider en tapotant doucement depuis le côté opposé avec un marteau. 
**Attention :** Assurez-vous que la goupille rentre parfaitement droite, sans forcer un angle.

Insérez ensuite le tendon depuis le trou latéral et répétez la procédure de blocage (nœud) vue à l'Étape 01. 
*Répétez cette opération pour tous les doigts, y compris le pouce.*

![Insertion PP 1](https://storage.googleapis.com/orca-a25f9.firebasestorage.app/Assembly_2/02_PP_Tendon_Routing/substep_01.png)
![Insertion PP 2](https://storage.googleapis.com/orca-a25f9.firebasestorage.app/Assembly_2/02_PP_Tendon_Routing/substep_02.png)

---

## Étape 03 : Routage de l'Abduction (Écartement des doigts)

Prenez **deux tendons de 50 cm** (sans nœuds préalables) et insérez-les sur le côté de la pièce d'abduction (à la base du doigt). Une fois les tendons passés à travers les trous traversants, faites un nœud Ashley au bout de chacun d'eux. Tirez les deux tendons en arrière pour encastrer et sécuriser les nœuds dans la pièce d'abduction.
*Répétez pour les autres doigts (sauf le pouce qui a son propre mécanisme).*

![Routage Abduction 1](https://storage.googleapis.com/orca-a25f9.firebasestorage.app/Assembly_2/03_Abduction_Routing/substep_01.png)
![Routage Abduction 2](https://storage.googleapis.com/orca-a25f9.firebasestorage.app/Assembly_2/03_Abduction_Routing/substep_02.png)

---

## Étape 05 : Assemblage final du Doigt

Afin de ne pas s'y perdre, vous pouvez marquer vos tendons avec des codes couleurs (au marqueur) :
- *Rappel D-Hand : Nous n'utilisons que des extenseurs passifs en silicone, mais le routage de l'ORCA utilise deux canaux antagonistes.* 
Passez le tendon extenseur par le trou supérieur et le tendon fléchisseur (celui qui fermera le doigt) par le trou inférieur de l'assemblage de la Phalange Proximale (PP). 

Poussez l'assemblage de la phalange distale (fingertip) sur l'assemblage PP jusqu'à ce qu'ils s'enclenchent ("snap"). C'est ici que les roulements **MR84ZZ** entrent en jeu pour garantir une articulation sans friction.

![Assemblage Doigt 1](https://storage.googleapis.com/orca-a25f9.firebasestorage.app/Assembly_2/05_Finger_Assembly/substep_01.png)
![Assemblage Doigt 2](https://storage.googleapis.com/orca-a25f9.firebasestorage.app/Assembly_2/05_Finger_Assembly/substep_02.png)

---

## Étape 06 : Routage de l'Abduction du Pouce

La procédure est similaire à l'Étape 03, mais s'applique à la base spécifique d'abduction du pouce. Deux tendons de 50 cm sont insérés sur le côté.
Faites un nœud Ashley et tirez en arrière pour verrouiller. **Validez toujours le routage** : tirez fermement sur chaque tendon à la main pour vous assurer que l'articulation tourne de façon fluide avant de clore l'assemblage.

![Abduction Pouce 1](https://storage.googleapis.com/orca-a25f9.firebasestorage.app/Assembly_2/06_Thumb_Abduction_Tendon_Routing/substep_01.png)

---

> [!NOTE]
> **Fin du guide localisé pour la D-Hand :** Les étapes suivantes de l'ORCA (08 à 30) consistent à empiler et visser les 17 moteurs Feetech dans la grande tour d'impression 3D. Cette partie est ignorée puisque les câbles de nos doigts rejoindront directement notre paume CNC en aluminium et nos 8 moteurs Dynamixel XC430/XC330 fixés sur la bride d'avant-bras D-Bot.

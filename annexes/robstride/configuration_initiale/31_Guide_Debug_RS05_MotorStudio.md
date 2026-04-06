# 31 — Guide : Debug RS-05 avec le Module de Debug CAN-to-USB et MotorStudio

> *Document créé Mars 2026 — Sources : Manuel officiel EL05-EN (RobStride / Lingfoot Times Technology), GitHub RobStride/MotorStudio, Doc 04 Câblage CAN.*

Ce guide décrit comment connecter un moteur **RobStride 05 (RS-05)** au **module de debug CAN-to-USB**, alimenter l'ensemble avec la **Wanptek DPS605U**, et piloter le moteur depuis le logiciel **MotorStudio** sur PC.

---

## 1. Matériel Requis

| Composant | Modèle | Role |
| :--- | :--- | :--- |
| **Moteur** | RobStride RS-05 | Actionneur CAN FOC |
| **Module debug** | Module de Debug CAN-to-USB (RobStride) | Interface PC ↔ Bus CAN |
| **Alimentation labo** | Wanptek DPS605U (60V/5A) | Puissance 24V moteur |
| **PC Windows** | — | Héberger MotorStudio |
| **Câble USB-C** | — | Relier le module de debug au PC |
| **Câble JST-GH 4 pins** | Holybro Ø1.25mm | Relier le moteur au module |
| **Câble puissance** | XT30 mâle/femelle | Relier le moteur à la Wanptek |

> [!NOTE]
> Le module de debug CAN-to-USB fonctionne **uniquement sur Windows** avec le logiciel MotorStudio officiel. Pour une intégration Linux/ROS2 (production), utiliser l'InnoMaker USB2CAN-C avec SocketCAN (voir Doc 05).

---

## 2. Le Module de Debug CAN-to-USB — Description Physique

![Photo réelle du module de debug CAN-to-USB RobStride montrant les bornes GND, CANH, CANL et les 2 DIP switches](../../../assets/img_rlink_module_photo.png)

Le module de debug CAN-to-USB est une petite carte noire (version 2025/6/17/V02) composée de :

### Côté Gauche — Interface Moteur (bornes à vis)

```
┌─────────────────────────────────────────────────────┐
│  ● GND   ← Masse commune (CRITIQUE)                 │
│  ● CANH  ← Signal CAN High vers moteur              │
│  ● CANL  ← Signal CAN Low vers moteur               │
│                                                      │
│  [○ CAN ]  ← DIP Switch 2 : Résistance 120Ω        │
│  [○ BOOT]  ← DIP Switch 1 : Mode bootloader         │
│                                                      │
│  [DIO][CLK][GND][3V3] ← SWD (usage usine, NE PAS   │
│                           connecter au moteur)       │
└─────────────────────────────────────────────────────┘
                                    [USB-C] → PC
```

### Côté Droit — Port USB-C vers PC

Connexion standard USB-C vers votre ordinateur.

---

## 3. Les 2 DIP Switches — Rôle et Configuration

Le manuel officiel (EL05-EN, page 4) précise explicitement :

> *"When DIP switch 1 is in the ON position, the module enters Boot mode and cannot establish a connection with the host computer. When DIP switch 2 is in the ON position, a 120Ω terminal resistor is connected to the module port, allowing normal communication with the host computer."*

| Switch | Label PCB | **Position ON** | **Position OFF** | **Votre réglage** |
| :---: | :---: | :--- | :--- | :---: |
| **1** | **BOOT** | Mode Bootloader (mise à jour firmware du module) — **le module ne répond plus à MotorStudio** | Mode normal de communication CAN | ⬛ **OFF** |
| **2** | **CAN** | Active la résistance de terminaison **120Ω** intégrée (obligatoire si le module est en bout de bus) | Pas de résistance (si une autre terminaison existe déjà sur le bus) | ⬜ **ON** |

> [!IMPORTANT]
> **Piège classique n°1** : Si Switch 1 (BOOT) est sur ON, MotorStudio ne trouvera jamais le moteur. Vérifiez ce switch en tout premier lieu si la connexion échoue.
>
> **Règle** : Pour un test avec un seul moteur sur table (votre cas), réglez **SW1=OFF** et **SW2=ON**. C'est la configuration "banc de test" standard.

---

## 4. Pinout du Connecteur JST-GH du RS-05

Le moteur RS-05 dispose de deux ports :

### Port Puissance (XT30PB)
```
XT30 Mâle côté moteur :
  Rouge (+) → Borne (+) Wanptek (24V)
  Noir  (-) → Borne (-) Wanptek (GND)
```

### Port Communication (Petit connecteur CAN 2 fils)

> [!IMPORTANT]
> Le connecteur CAN du moteur RS-05 est physiquement un JST-GH 4 broches, mais **seuls 2 fils sont câblés** dans le harnais standard livré :

```
Fil rouge (fin)  → CANH (CAN High)
Fil noir  (fin)  → CANL (CAN Low)
```

Les broches GND (pin 3) et BOOT (pin 4) **ne sont pas câblées** dans le harnais standard. Le GND de référence CAN est déjà assuré par le fil noir épais de la puissance (XT30 -).

---

## 5. Schéma de Câblage Complet

```
                    ┌─────────────────────────────────────────┐
      WANPTEK        │            RS-05 MOTEUR                 │
      DPS605U        │                                         │
                    │  ┌──────────┐    ┌──────────────────┐   │
   (+) 24V ─────────┼──┤ XT30     │    │ CAN (2 fils)     │   │
   (-) GND ─────────┼──┤ Puissance│    │ Rouge: CANH ────┼───┼──→ CANH [module debug]
       │            │  └──────────┘    │ Noir : CANL ────┼───┼──→ CANL [module debug]
       │            │                  └──────────────┘   │
       │            └─────────────────────────────────────────┘
       │
       └──── GND commun (via XT30 -) ────→ GND [module debug] (bornes à vis)

                                         [module de debug]
                                  SW1(BOOT)=OFF ●○
                                  SW2(CAN) =ON  ○●
                                         │
                                      [USB-C]
                                         │
                                      [PC Windows]
                                      MotorStudio
```

---

## 6. Séquence d'Allumage (à respecter impérativement)

Référence : Doc 04 — Électronique & Câblage (Section Sécurité).

**Étape 1 — Préparer la Wanptek (Procédure de Sécurité)**
Le modèle DPS605U nécessite une vigilance particulière car il ne possède pas de bouton "Output ON/OFF" physique dédié. Suivez scrupuleusement cet ordre :
1. **Mise sous tension à vide** : Allumez l'alimentation sans aucun moteur branché.
2. **Réglage Tension** : Vérifiez et ajustez la tension (**24.0V** pour les tests banc, **48.0V** pour la production).
3. **Réglage Limite Courant** : 
   - Désactivez la sortie si possible.
   - Court-circuiter brièvement les pinces (+) et (-) pour régler le courant max (ex: **1.0A** ou **2.0A** selon le moteur).
4. **Activation du Mode OCP** (Overcurrent Protection) : Appuyez sur le bouton de réglage de courant jusqu'à voir "OCP". L'alimentation coupera d'elle-même la sortie en cas d'appel de courant anormal (ex: branchement inversé).
5. **Vérification finale** : La tension est stable, le courant est limité, l'OCP est armé.
6. **Bouton Output** : Si votre version possède un bouton "ON/OFF", laissez-le sur **OFF** jusqu'au branchement complet.

**Étape 2 — Câbler (tout hors tension)**
1. Brancher le JST-GH du moteur sur les bornes GND/CANH/CANL du module de debug CAN-to-USB.
2. Brancher le **GND du module** au **GND (-)** de la Wanptek (masse commune).
3. Brancher le XT30 puissance du moteur sur la Wanptek.
4. Vérifier les DIP switches : SW1=OFF, SW2=ON.

**Étape 3 — Mettre sous tension**
1. ✅ Allumer la Wanptek / activer la sortie → 24V → le moteur est alimenté.
2. ✅ Brancher le câble USB-C du module de debug CAN-to-USB sur le PC.
3. ✅ Lancer MotorStudio.

> [!CAUTION]
> Ne jamais modifier la tension de la Wanptek alors que le moteur est branché et activé. Les fluctuations peuvent détruire les MOSFETs internes du driver.

---

## 7. Installation de MotorStudio

### Téléchargement

Le logiciel est distribué sur GitHub :

**→ [https://github.com/RobStride/MotorStudio/releases](https://github.com/RobStride/MotorStudio/releases)**

Télécharger la dernière version : **`motor_toolV13.zip`** (v1.0.3 — Latest — 20.4 MB, Fév 2026).

![Page GitHub des releases MotorStudio montrant la version v1.0.3 (Latest)](../../../assets/img_motorstudio_github_releases.png)

> **Note Linux** : La version v1.0.1 précédente avait une version Linux (AppImage). La v1.0.3 est Windows uniquement. Pour Linux, utilisez directement l'InnoMaker USB2CAN + SocketCAN (voir Doc 05).

### Prérequis — Driver CH340

Le module de debug CAN-to-USB utilise la puce série **GD32F303** (la même puce que dans le driver CH340 de nombreuses cartes Arduino). Si le module n'est pas reconnu par Windows :

1. Ouvrir le Gestionnaire de Périphériques.
2. Si vous voyez un point d'exclamation sur un port COM → installer le driver CH340.
3. Télécharger : [https://www.wch.cn/download/CH341SER_EXE.html](https://www.wch.cn/download/CH341SER_EXE.html)
4. Après installation, débrancher/rebrancher l'USB-C du module.

---

## 8. Connexion dans MotorStudio — Procédure Pas-à-Pas

### Interface de connexion

```
┌─────────────────────────────────────────────┐
│  MotorStudio v1.0.3                         │
│                                             │
│  Connect Motor                              │
│  ┌─────────────────┐  ┌──────────────────┐ │
│  │  COM7  ▼        │  │  Refresh COM     │ │
│  └─────────────────┘  └──────────────────┘ │
│  ┌──────────────────────────────────────┐  │
│  │  Open COM                            │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  [Detection Devices]  [Enable]  [Stop]     │
└─────────────────────────────────────────────┘
```

### Étapes de connexion

1. **Lancer MotorStudio** (après avoir mis le moteur sous tension).
2. Cliquer sur **"Refresh COM"** → la liste des ports COM se met à jour.
3. **Sélectionner le port COM** correspondant au module de debug CAN-to-USB (généralement COM3 à COM10 selon le PC). Si vous ne savez pas lequel, vérifiez dans le Gestionnaire de Périphériques Windows → "Ports (COM et LPT)".
4. Cliquer **"Open COM"** → le port s'ouvre.
5. Cliquer **"Detection Devices"** → MotorStudio scanne le bus CAN et trouve l'ID du moteur (par défaut ID=1 sur un RS-05 neuf).
6. Le moteur apparaît dans la liste → cliquer dessus pour accéder à ses paramètres.
7. Cliquer **"Enable"** pour activer le moteur (il sort de l'état idle).

### Paramètres importants à vérifier lors du premier allumage

| Paramètre | Valeur attendue | Note |
| :--- | :---: | :--- |
| **Motor ID** | 1 (par défaut) | À changer si plusieurs moteurs sur le même bus |
| **Baud Rate CAN** | 1 Mbps | Standard RobStride |
| **Mode** | MIT (position/vitesse/couple) | Mode le plus complet pour les tests |
| **Zero Position** | 0.0 | À recalibrer si le moteur a tourné pendant le stockage |

---

## 9. Dépannage

| Symptôme | Cause probable | Solution |
| :--- | :--- | :--- |
| Module non reconnu par Windows | Driver CH340 absent | Installer le driver CH340 |
| "Detection Devices" ne trouve rien | SW1 (BOOT) sur ON | Mettre SW1 sur **OFF** |
| Erreur "Bus Off" dans les logs | GND non partagé | Relier GND du module de debug CAN-to-USB au GND (-) Wanptek |
| Connexion instable / perte de trames | CANH/CANL inversés | Inverser les deux fils CAN |
| OCP déclenche dès "Enable" | Limite courant trop basse (1A) | Augmenter à 2A sur la Wanptek |
| Moteur chaud mais ne bouge pas | Pas d'ordre de mouvement | Vérifier que le mode est correct (MIT vs Position) |
| Position parasite au démarrage | Offset d'encodeur | Recalibrer le zero dans MotorStudio |

---

## 10. Liens et Ressources

| Ressource | URL | Notes |
| :--- | :--- | :--- |
| **MotorStudio** (GitHub) | https://github.com/RobStride/MotorStudio/releases | Télécharger `motor_toolV13.zip` |
| **Manuel EL05-EN** (officiel) | https://lsleg.feishu.cn/wiki/Hkp4wjuXmiYxpRkFc2HciqOpnNh | Manuel complet 40 pages (Feishu, nécessite compte) |
| **Driver CH340** | https://www.wch.cn/download/CH341SER_EXE.html | Si module non reconnu par Windows |
| **Seeed Studio Wiki** | https://wiki.seeedstudio.com/robstride_actuator_modules/ | Tutoriel complémentaire |
| **Doc 04** | [04_Electronique_Cablage.md](./04_Electronique_Cablage.md) | Architecture CAN et Sécurité |

---

## 11. Spécifications RS-05 (Rappel)

Source : Manuel EL05-EN, page 4 — Driver Product Specifications.

| Paramètre | Valeur |
| :--- | :--- |
| Tension nominale | **48V DC** |
| Tension max. admissible | **60V DC** |
| Courant de phase nominal | 2.6A peak |
| Courant de phase max. | 11.0A peak |
| Courant en veille | ≤18 mA |
| Débit bus CAN | **1 Mbps** |
| Diamètre | Ø41mm |
| Température fonctionnement | -20°C à +50°C |
| Résolution encodeur | **14 bits** (tour absolu) |
| Rapport de réduction | 9:1 |
| Mode de contrôle | FOC |

> Pour les premiers tests (banc), utiliser **24V** au lieu de 48V nominal. Couple et vitesse seront réduits de ~50%, mais le risque en cas d'erreur est divisé par 2.

---

## 12. Tests de Fonctionnement — Séquence Banc (Wanptek 24V)

Procédure progressive du moins risqué au plus dynamique. **À effectuer avec l'arbre du moteur libre, rien de fixé dessus.**

---

### Test 0 — Pré-requis avant tout test

Avant d'activer quoi que ce soit, vérifier :

- [ ] Wanptek : **24.00V**, limite courant **1.0A** (ou 2.0A), **OCP activé**
- [ ] Module de Debug CAN-to-USB : **SW1=OFF**, **SW2=ON**
- [ ] Moteur posé sur la table, arbre vers le haut, **zone dégagée autour**
- [ ] Moteur détecté dans MotorStudio (**"Detection Devices"** → ID visible dans la liste)

---

### Test 1 — Lecture Télémétrie (passif, zéro risque)

Moteur alimenté, **non activé** (avant tout "Enable") — vérifier les valeurs en temps réel :

| Paramètre affiché | Valeur normale à 24V, moteur au repos |
| :--- | :--- |
| **Position** (pos / angle) | Stable (±0.01 rad). Si elle dérive, il y a un problème d'encodeur. |
| **Vitesse** (vel / speed) | ≈ 0 rad/s |
| **Courant** (cur / current) | ≈ 0 à 0.05A (holding passif minimal) |
| **Température** | Température ambiante (20–25°C) |
| **Tension bus** (bus voltage) | 22–24V (chute normale dans les câbles) |

> ✅ **Résultat attendu** : Toutes les valeurs sont stables et cohérentes avec les conditions ambiantes. Si la température dépasse 30°C au repos → problème de court-circuit partiel dans le câblage puissance.

---

### Test 2 — Enable / Disable (sans ordre de mouvement)

1. Cliquer **"Enable"** dans MotorStudio.
2. Observer la **Wanptek** : le courant monte légèrement → **50 à 200 mA** (holding torque FOC actif). C'est normal.
3. Essayer de tourner l'**arbre à la main** → vous devez sentir une **résistance magnétique**. C'est le couple de maintien (Holding Torque). Plus la résistance est franche, mieux c'est.
4. Cliquer **"Stop"** ou **"Disable"** → l'arbre redevient **libre immédiatement**.

> ⚠️ Si l'OCP de la Wanptek se déclenche à l'Enable (courant > limite) → augmenter la limite à **2A** sur la Wanptek. Cela peut arriver si le moteur "cherche" sa position home au démarrage.

> ✅ **Résultat attendu** : Résistance magnétique perceptible sous "Enable", arbre libre sous "Disable". Courant Wanptek < 0.3A au repos.

---

### Test 3 — Premier Mouvement en Mode MIT (position douce)

> [!WARNING]
> L'arbre doit être **absolument libre**. Ne pas tenir le moteur par l'arbre pendant ce test. Posez-le sur une surface stable.

En mode **MIT** dans MotorStudio, saisir les paramètres suivants pour un déplacement **très lent et contrôlé** :

```
Position target (pos)  :  +1.0  rad   (≈ 57°, un ~1/6 de tour)
Vitesse max (vel)       :   1.0  rad/s  (très lent)
Rigidité (Kp)           :   5.0
Amortissement (Kd)      :   0.5
Couple feedforward (T)  :   0.0  N.m
```

Envoyer la commande → le moteur doit **tourner lentement de ~57° et s'immobiliser**.

**Ajustements si nécessaire :**

| Symptôme | Ajustement |
| :--- | :--- |
| Rotation trop rapide | Réduire `vel` à 0.5 rad/s |
| Moteur tremble / oscille | Augmenter `Kd` à 1.0 |
| OCP de la Wanptek déclenche | Passer la limite à 2A (normal à basse vitesse) |
| Moteur n'atteint pas la cible | Augmenter `Kp` à 10.0 (plus rigide) |

Pour revenir au point de départ : envoyer `pos = 0.0 rad`.

> ✅ **Résultat attendu** : Rotation douce et précise de ~57°. Position finale stable. Pas de vibration ni d'oscillation.

---

### Test 4 — Test de Vitesse (Mode Vitesse)

Si MotorStudio propose un mode **Velocity Control** :

```
Vitesse cible   :  5.0  rad/s  (≈ 0.8 tour/s — vitesse modérée)
Limite courant  :  1.0  A
Durée           :  2 secondes maximum
```

Observer :
- Le moteur doit tourner **régulièrement** sans à-coups.
- Le courant Wanptek doit rester **< 1.5A** à vide.
- La température ne doit **pas dépasser 40°C** pendant ce test court.

Stopper le moteur (`vel = 0`) puis **Disable**.

---

### Test 5 — Calibration du Zéro Mécanique

Si la position affichée n'est pas 0.0 alors que vous souhaitez définir la position actuelle comme origine :

1. Positioner manuellement l'arbre à la position mécanique souhaitée comme "zéro".
2. Dans MotorStudio, chercher le bouton **"Set Zero"** ou **"Zero Position"** (parfois dans un menu "Calibration").
3. Confirmer → la position affichée repasse à **0.0 rad**.
4. **Sauvegarder** (bouton "Save" ou "Write to Flash") → le zéro est persisté dans la mémoire flash du moteur.

> [!IMPORTANT]
> Cette calibration du zéro **est obligatoire après chaque mise à jour du firmware** (le flash efface la position de référence). Ne pas oublier cette étape après toute opération de mise à jour.

---

### Tableau de Synthèse des Tests

| Test | Risque | Courant Wanptek attendu | Résultat attendu |
| :--- | :---: | :---: | :--- |
| **T1 - Télémétrie** | Nul | ~0 mA | Valeurs cohérentes affichées |
| **T2 - Enable/Disable** | Très faible | 50–200 mA | Résistance magnétique à la main |
| **T3 - Position MIT** | Faible | < 500 mA | Rotation précise de 57°, stable |
| **T4 - Vitesse** | Modéré | < 1.5A | Rotation régulière à vide |
| **T5 - Calibration zéro** | Nul | ~0 mA | pos affichée = 0.0 rad |

---

## 13. Mise à Jour du Firmware RS-05

> [!CAUTION]
> La mise à jour firmware est une opération à **risque de "brick"** si elle est interrompue (coupure secteur, perte USB). Assurez-vous que la Wanptek est bien alimentée et que le câble USB-C est stable avant de commencer.

---

### 13.1 Méthode Standard — Via MotorStudio (moteur fonctionnel)

C'est la méthode normale si le moteur répond encore au bus CAN.

**Étape 1 — Télécharger le firmware RS-05**

Le firmware est distribué sur GitHub (dépôt séparé de MotorStudio) :

**→ [https://github.com/RobStride/Product_Information/releases](https://github.com/RobStride/Product_Information/releases)**

Télécharger le fichier **`.bin`** correspondant au **RS-05** (vérifier le nom du fichier — il doit contenir "RS05" ou "EL05").

**Étape 2 — Connexion et préparation**

1. Connecter et allumer le moteur normalement (suivre §6).
2. Dans MotorStudio, ouvrir le COM et détecter le moteur (**"Detection Devices"**).
3. Sélectionner le moteur dans la liste.

**Étape 3 — Lancer la mise à jour**

1. Dans MotorStudio, chercher l'onglet ou le bouton **"Firmware Update"** / **"升级"** (mise à niveau).
2. Cliquer **"Open File"** → sélectionner le fichier `.bin` téléchargé.
3. Cliquer **"Erase"** → le logiciel efface le firmware actuel et place le moteur en **"Upgrade Mode"**. Le moteur ne répond plus aux commandes pendant cette phase, c'est **normal**.
4. Cliquer **"Start Update"** → la barre de progression doit avancer de 0 à 100%.
5. Une fois à 100%, le moteur redémarre automatiquement.

**Étape 4 — Post-flash obligatoire**

> [!IMPORTANT]
> Après chaque mise à jour firmware, le zéro position est **effacé**. Refaire impérativement le **Test 5 - Calibration du Zéro** (§12) avant toute utilisation du moteur.

Vérifier également que le Motor ID est toujours correct (parfois remis à 1 par défaut après un flash).

---

### 13.2 Méthode d'Urgence — Via Pin BOOT du Moteur (moteur muet/corrompu)

À utiliser **uniquement si le moteur ne répond plus du tout** au bus CAN (firmware corrompu, moteur "brick").

Le connecteur JST-GH 4-pin du moteur dispose d'un pin **BOOT (pin 4)** qui, relié au GND pendant la mise sous tension, force le moteur en mode bootloader SWD (récupération bas niveau).

**Procédure :**

1. **Couper l'alimentation** du moteur.
2. Sur le câble JST-GH, **court-circuiter le Pin 4 (BOOT) avec le Pin 3 (GND)** à l'aide d'un cavalier ou d'un fil fin.
3. **Remettre sous tension** → le moteur démarre en mode bootloader (l'arbre ne tourne pas, aucune led active sur le driver).
4. Dans MotorStudio, lancer la procédure de flash comme en §13.1 (Erase + Start Update).
5. Une fois le flash terminé, **couper l'alimentation**, retirer le court-circuit BOOT/GND.
6. Remettre sous tension normalement → le moteur démarre avec le nouveau firmware.
7. Refaire la **calibration du zéro** (Test 5, §12).

```
Câble JST-GH moteur — Mode Bootloader Urgence :

  Pin 1 : CANH  → CANH module de debug CAN-to-USB
  Pin 2 : CANL  → CANL module de debug CAN-to-USB
  Pin 3 : GND   → GND module de debug CAN-to-USB
  Pin 4 : BOOT  → [cavalier] → Pin 3 GND  ← ACTIVER SEULEMENT pour flash urgence
```

> ⚠️ Retirer le cavalier BOOT/GND immédiatement après le flash. Si le moteur démarre à nouveau avec ce cavalier en place, il entrera encore en bootloader et ne fonctionnera pas.

---

### 13.3 Tableau de Décision — Quelle Méthode Utiliser ?

| Situation | Méthode |
| :--- | :--- |
| Moteur fonctionne, mise à jour de confort | **§13.1** — Via MotorStudio (standard) |
| Moteur détecté mais instable / bogué | **§13.1** — Via MotorStudio (standard) |
| Moteur ne répond plus du tout au CAN | **§13.2** — Pin BOOT (urgence) |
| Moteur répond mais firmware très ancien | **§13.1** — Via MotorStudio (standard) |


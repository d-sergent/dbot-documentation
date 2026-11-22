# Notes de Mise à Jour du Firmware (Mai 2026 — Release V26.05.19) — Moteurs RobStride

Ce document consolide le changelog officiel des firmwares RobStride (`V26.04.07` et `V26.05.19`, issu de `default.pdf`), les binaires archivés en local, ainsi que la procédure de flash OTA sous Linux (SocketCAN) et les points de vigilance matériels (CAN-FD 5 Mbps, module de décharge).

---

## 0. Inventaire des Firmwares Archivés & Matrice `V26.05.19`

> [!NOTE]
> Les binaires `.bin` et `.hex` sont hébergés dans les **Release Assets** GitHub (`https://github.com/RobStride/Product_Information/releases`), en dehors de l'historique `git clone`.

En local, les archives sont rangées sous `/Users/Shared/Mon Google Drive Physique/k-bot/robstride/firmware/` :
- **`122025/` (`V25.12.09`)** : Inclut les `.bin` et les `.hex` usine (`_FAC_`) pour récupération bas niveau.
- **`042026/` (`V26.04.07`)** : Release d'avril 2026 (`update.pdf`).
- **`V26.05.19/` (Release du 19 mai 2026 — Dernière version)** : Inclut `default.pdf` et les 9 binaires `.bin` ci-dessous :

| Moteur | Usage D-Bot | Binaire `042026` (`V26.04.07`) | Binaire `V26.05.19` (Recommandé) |
| :--- | :--- | :--- | :--- |
| **RS00** | Poignet Pitch (x2) | `rs00-0.0.3.27.bin` | `rs00_0.0.3.36.bin` |
| **RS01** | *(Non retenu — max 48V)* | `rs01-0.1.3.14.bin` | `rs01_0.1.3.21.bin` |
| **RS02** | Épaule Yaw (x2), Supination (x2) | `rs02-0.2.3.32.bin` | `rs02_0.2.3.36.bin` |
| **RS03** | Épaule Roll, Hanche Roll/Yaw, Cheville | `rs03-0.3.1.41.bin` | `rs03_0.3.1.50.bin` |
| **RS04** | Hanche Pitch, Genou, Épaule Pitch | `rs04-0.4.1.29.bin` | `rs04_0.4.1.38.bin` |
| **RS05** | Cou Pan + Tilt (x2) | `rs05_0.5.0.13.bin` | `rs05_0.5.0.17.bin` |
| **RS06** | Taille (Waist Yaw) | `rs06_0.6.0.11.bin` | `rs06_0.6.0.18.bin` |
| **EL05** | *(Gamme Edulite 242g)* | `EL05_1.0.5.0.4.bin` | `el05_1.0.5.0.6.bin` |
| **RS10P** | *(Planétaire 25:1 — 42 Nm)* | *(absent)* | `rs10_0.10.0.6.bin` |

---

## 1. Moteurs RS00

| Version | Notes de Mise à Jour |
| :--- | :--- |
| **0.0.3.3** | 1. Compatibilité avec les protocoles CANopen et MIT. Bascule possible via commande.<br>2. Réajustement des bits de données pour les trames de changement de baudrate, de sauvegarde de données, et rapport actif (type de retour passé à 24, nécessite une commande spécifique).<br>3. Restauration de la fonctionnalité "Configuration d'Usine". |
| **0.0.3.4** | 1. Protection contre le rétro-entraînement (amortissement hors tension) désormais désactivable.<br>2. Ajout de journaux d'erreurs (logs). |
| **0.0.3.5** | 1. Ajout de la possibilité de calibrer le zéro (标零) en modes CSP et Contrôle de mouvement. Calibrage interdit en mode PP.<br>2. Ajout de l'offset de position (`add_offset`=1 pour décaler le zéro de +1).<br>3. Correction du bug d'overflow (dépassement de variable) en fonctionnement unidirectionnel prolongé à très haute vitesse.<br>4. Ajout de variables d'erreurs PLC.<br>5. Tous les paramètres deviennent accessibles en lecture et écriture. |
| **0.0.4.1** | OVP (Protection Surtension) modifiée : déclenchement après 0.5s à partir de 60V (au lieu de 65V immédiat). |
| **0.0.3.6** | 1. Correction de la désynchronisation PDO vis-à-vis des délais.<br>2. Ajout d'une zone morte autour de la position Zéro.<br>3. L'identifiant `canopenid` est rendu cohérent avec le `canid` privé. |
| **0.0.4.2** | Purge des registres d'états au démarrage, corrigeant les signalements intempestifs d'erreurs. |
| **0.0.3.15** | 1. Optimisation logique de synchronisation (Sync).<br>2. Modèle thermique : calcul précis de la chaleur par phase à basse vitesse.<br>3. Vitesse et Accélération modifiables "à la volée" lors du fonctionnement PP.<br>4. `add_offset` devient modifiable sous le type 18.<br>5. Optimisation de la détection de zone morte au Zéro.<br>6. OVP endurci : protection immédiate dès détection de 65V.<br>7. Correction de l'impossibilité d'écrire 4 variables sur un unique PDO.<br>8. Résolution finale des fausses alertes à l'allumage.<br>9. Optimisation de l'algorithme d'estimation de la position initiale.<br>10. CANopen : Les Modes 5 et 8 déclenchent désormais tous les deux le mode CSP. |
| **0.0.3.16** | Optimisation du timing d'initialisation, évitant les bonds brutaux de position causés par des démarrages impurs. |
| **0.0.3.17** | 1. Courbe de compensation de couple optimisée.<br>2. L'OVP revient à **60V strict et immédiat** pour harmoniser toute la gamme de moteurs. |
| **0.0.3.19** | 1. Mode PP : La vitesse maximale limite s'ajuste dynamiquement selon la tension d'alimentation, prévenant la désynchronisation entre planification de trajectoire et suivi réel.<br>2. CANopen : le mode Vitesse inclut un port de config d'accélération. En cas de valeurs non renseignées (Accel/Couple en Position, or Couple en Vitesse), les paramètres se reportent sur les valeurs par défaut. |
| **0.0.3.21** | 1. Blindage contre les interférences induites par l'usage des Trames Étendues (Extended frames) en bus partagé CANopen.<br>2. Correction d'échec occasionnel de calibrage zéro au moment de porter une charge.<br>3. Remède aux échecs de premier "Enable" imputables à une rampe d'alimentation (montée en tension) trop lente.<br>4. Optimisation détermination du Zéro au démarrage.<br>5. CANopen : Fix du silence radio après l'usage de "reset" en état Actif (Enabled).<br>6. Suppression de l'amortissement persistant qui subsistait après acquittement matériel d'un défaut.<br>7. CANopen : Fix de l'impossibilité d'émettre 4 TPDO simultanés.<br>8. CANopen : Vitesses, accélérations, et limites disposent désormais de pré-valeurs de démarrage en interne.<br>9. L'identifiant constructeur (Manufacturer Code) validé sans rejets initiaux. |
| **0.0.3.22** | Renseigne et active des valeurs initiales de Vitesse pour le mode Position. |
| **0.0.3.27** | 1. Protocole MIT : Ajout des rapports actifs de statut, de sauvegarde asynchrone des paramètres, des lectures/écritures et champs d'états dans les trames.<br>2. Optimisation des conflits réseau entre rapports actifs et trames de retour (Feedbacks).<br>3. CANopen : La trame de quittance (Feedback) d'Activation/Désactivation est envoyée APRÈS exécution mécanique, fiabilisant le retour d'état du bus.<br>4. **Calibrage Initialisation Précise :** Actionné via `iq_test=1`. Au redémarrage, l'échantillonnage de courant est stabilisé, réduisant le "jitter" mécanique (tremblements).<br>5. **Calibrage Cogging (Couple de Détente) :** Activable via `alveolous_open=1` pour corriger les irrégularités de denture. Nécessite au préalable d'avoir fait un `iq_test` suivi d'un redémarrage à vide pour acquisition parfaite.<br>6. CANopen PP : Planification des arrêts d'urgence corrigée lors des modes combinés.<br>7. **Watchdog :** Via Index CANopen `0x6099` Sous-index 1. Toute valeur non nulle l'approuve.<br>8. **Protection NVRAM :** Lors d'un Disable, le moteur attend une tension stricte pour enregistrer ses données en ROM et utilise un bloc Mémoire de Secours Backup. S'il y a coupure durant l'écriture, le moteur boote sur le backup et remonte un code d'Alerte requérant une sauvegarde manuelle saine.<br>9. Profile Position (PP) : Découplage de la rampe en réglant `acc_status=1` (permettant la Décélération à `0x702E` indépendamment de l'accélération). |
| **0.0.3.32 -> .36** | *(Release `V26.05.19`)*<br>1. **Filtrage MIT par mode :** En mode MIT, le moteur ignore désormais les trames de commande ne correspondant pas au mode actif.<br>2. **Diagnostic driver :** Ajout du bit de défaut driver dans les trames d'erreur MIT et protocole privé.<br>3. Suppression de déclenchements intempestifs d'avertissements.<br>4. CANopen : Ajout de la lecture de température et du bit de défaut driver.<br>5. `.36` : Mise à jour firmware finale `V26.05.19` (`rs00_0.0.3.36.bin`). |

---

## 2. Définitions Détaillées sur Les Fonctions Clés (Toute Gamme)

- **Protection Rétro-Entraînement / Amortisseur Damping (`0x2023`)** : Auparavant, les moteurs non-alimentés induisaient un fort frein électrique (damping) s'ils étaient forcés mécaniquement, afin d'empêcher les régénérations survoltées de détruire les MOSFETS. Ce verrou peut être libéré (mise en roue libre douce) la valeur the `damper=1`.
- **Comportement de Calibrage du Zéro** : Historiquement, la commande "SET ZERO" impliquait un saut brutal de position car la consigne de mouvement visait l'ancien référentiel. Désormais en modes contrôles (CSP/Vitesse), imposer le Zéro efface le tampon de consigne, évitant les tressautements (Interdit volontairement en mode Profile Position).
- **Offset manuel de Zéro (`add_offset`)** : Permet au logiciel de l'architecture robot de désigner qu'au point bloquant mécanique où un recalibrage par l'utilisateur est fait, le zéro virtuel n'est pas "0" mais décalé (Par exemple calibrer que cette butée = +1.0 rad). Modification permanente.
- **Paramètre CAN_ID Unifié** : Les moteurs disposent d'un identifiant par défaut à 1, il ne se modifie qu'à travers le flux classique de paramétrage ID sans exiger de config parallèle CANopen.
- **Réglages du Cogging** : Optimise un profil inverse pour gommer la sensation magnétique pas-à-pas (Cogging). 

---

## 3. Moteurs RS01 et RS02

Les versions **RS01 (0.1.3.x)** et **RS02 (0.2.3.x)** héritent du même cycle de correctifs majeurs (CANopen, M.I.T., Overshoot protection, Cogging, Watchdog, OVP-60V).

### Différences notables :
* **Moteur RS01 (v0.1.3.4)** : L'algorithme de contrôle PID interne de la puce de driver était faussé par un facteur de `1.4167` sur le couple de réaction Kp/Kd. L'équation de contrôle du couple en Mode Continous (`t_ref`) a été purement nettoyée de ces artefacts (Devenu : `t_ref=Kd*(v_set-v_actual)+Kp*(p_set-p_actual)+t_ff`).
* **Moteur RS01 (v0.1.3.10)** : Tension OVP bridée à **50V** stricte pour protection d'encombrement thermique.
* **Moteur RS02 (v0.2.3.9)** : Suite à des révisions internes PCB (Hardware), la résistance 120Ω interne CAN n'existe plus de facto. Le registre en lecture seule `0x3048 can_status` indique désormais le design carte :
   - `0` : Résistance classique 240/120Ω Poursuivie sur carte.
   - `1` : **Absence de résistance**. La terminaison 120Ω DOIT être externalisée (voir guide montage).
* **Moteur RS02 (v0.2.3.20)** : Correction d'une anomalie du sens de rotation MIT (Refus d'engager le reverse).
* **Développement** : Les dernières mises à jour (.41 ou .32 selon le firmware) comportent l'algorithme qui réduit de **plusieurs degrés l'échauffement normal** de la carte interne du driver aux courants de maintien stationnaires.

---

## 4. Moteurs RS03 et RS04

Les moteurs à fort couple suivent les optimisations fonctionnelles globales, avec des protections durcies spécifiques aux pics intenses d'usage sur les bras/cuisses.

### RS03 Actuel (v0.3.1.41)
* **Calibration Absolue Obligatoire** : Les mises à jour depuis 0.3.1.3 ont significativement re-paramétré la granularité du codec optique/magnétique. Il foudra physiquement **Refaire vos calibrations du zéro mécaniques** pour ce moteur.
* **Résistance de Terminaison** : L'état d'existence de la résistance physique s'interroge sur `0x3041` pour le RS03. (0 = R-Existante, 1 = R-Absente).

### RS04 Actuel (v0.4.1.29)
* **Surcharge de Phase Précise** (Dès v0.4.1.11) : Les alertes matérielles de blocage moteur ou surcharge d'axe remontent désormais un flux de télémétrie ultra granulaire indiquant au contrôleur avec exactitude quelle phase (U, V ou W) vient d'enregistrer l'emballement thermique.
* Le reste des apports englobe l'entièreté des patchs MIT/CANopen/OVP limitées à 60V, le Watchdog de sûreté `0x6099`, et le couple résiduel anti-sauts d'activation, au même titre que l'évolution originelle des RS00.27.

---

## 5. Moteurs RS05 (Cou/Pan-Tilt) et RS06

| Version | Évolutions Importantes des derniers modules (Avril 2026) |
| :--- | :--- |
| **0.5.0.5 <br> 0.6.0.3** | - Refonte des modes thermiques protecteurs adaptatifs qui compensent mathématiquement le dégagement joule du stator, idéal pour les efforts d'immobilité des hanches et fixations.<br>- Tous les variables du module Registres 17 et 18 sont en mode Read-Write.<br>- Verrouillage absolu OVP à 60 Volts sans tolérance de temps d'abaissement. |
| **0.5.0.6 <br> 0.6.0.4** | - Planificateur de vitesse de profilé adaptatif (Désynchronisation gérée vis-à-vis des chutes de courants de batterie).<br>- RS06 : Implémentation des remontées CANopen ERREURS sur un octet transparent exclusif. |
| **0.5.0.13 <br> 0.6.0.11** | Apport des fonctionnalités majeures d'avril 2026 : sauvegarde M.I.T. protégée des crashs de tension, étalonnage initial avancé `iq_test`, rattrapage Cogging `alveolous_open`, et découplage accélération/décélération en mode PP (`0x702E`). |
| **0.5.0.14 -> .17 <br> 0.6.0.12 -> .18** | *(Release `V26.05.19` — également appliqué à RS01 `.18->.21`, RS02 `.34->.36`, RS03 `.34/.50` et RS04 `.32->.38`)*<br>1. Filtrage strict des trames de commande MIT si le moteur n'est pas dans le mode correspondant.<br>2. Bit de défaut driver ajouté aux trames d'erreur MIT et protocole privé.<br>3. Correction d'alertes/avertissements parasites.<br>4. Remontée température et bit de défaut driver sous CANopen. |

---

## 6. Flash OTA sous Linux (`ota_update.py`) & Notes Matérielles 2026

### 6.1 Procédure OTA Linux / Jetson (SocketCAN 1 Mbps)
Le dépôt officiel `RobStride/Product_Information` fournit le script `OTA/OTA.py` (adapté pour D-Bot dans [`Code/scripts/motors/ota_update.py`](../../../Code/scripts/motors/ota_update.py)) utilisant les trames CAN étendues Types `0`, `11`, `12`, `13`, `14` :

```bash
export PYTHONPATH="/Users/Shared/Mon Google Drive Physique/Documentation/Code"
python3 Code/scripts/motors/ota_update.py --id 1 --channel can1 --bin "/Users/Shared/Mon Google Drive Physique/k-bot/robstride/firmware/V26.05.19/rs05_0.5.0.17.bin"
```

* **Exigence stricte :** Le bus CAN doit être configuré à **1 Mbps** pendant toute l'opération OTA.
* **Post-flash obligatoire :** Toute mise à jour efface le zéro mécanique et peut réinitialiser l'ID CAN. Vérifier l'ID puis recalibrer le zéro (ex. `calib_neck_zero.py`).
* **Compatibilité macOS (À réaliser plus tard) :** `ota_update.py` utilise `SocketCAN` (Linux/Jetson uniquement, non supporté par le noyau macOS). L'ajout d'un mode natif macOS via `gs_usb` (`CANable Pro` / `InnoMaker USB2CAN-C` avec `libusb` + `pyusb` + `gs_usb`) ou via le Module de Debug série `AT` (`pyserial`) est **à réaliser plus tard**, lors de la phase de mise à jour globale des moteurs.

### 6.2 Variantes CAN-FD (Manuels `CANFD/` jusqu'à 5 Mbps) & Module de Décharge
* **CAN-FD :** Les manuels `Manuels/CANFD/` documentent les variantes CAN-FD (RS00..RS06 + RS10P) configurables via Type 23 (`0x17`) jusqu'à **5 Mbps** (`F_CMD = 05`, `06`=4M, `07`=3M, `08`=2M, `01`=1M — note : certaines éditions anglaises `260529` mentionnent encore `1Mbps` par coquille, la fiche chinoise `260826` et le manuel `RS10PCANFDUser Manual261016.pdf` confirment `5Mbps`). Le format applicatif reste en ID étendu 29 bits / 8 octets de données, avec connectique spécifique (`XT30PB(2+2)-M.G.B` / `GH1.25-2PWT`).
* **Vigilance Module de Décharge (`DischargeModule`) :** La révision V1.0 EN (`Manuels/Discharge Module User Manual V1.0.pdf`) indique un seuil d'amorçage 48V à `64 V` (coupure `59 V`), tandis que la révision V1.1 CN abaisse ce seuil à `53.5 +/- 0.5 V` (coupure `50.5 +/- 0.5 V`). En cas d'utilisation sur la batterie 13S NMC du D-Bot (`54.6 V` pleine charge), vérifier impérativement le seuil calibré sur le module avant raccordement.

---

> [!TIP]
> **Action pour D-Bot :** Privilégiez les binaires de la release **`V26.05.19`** (`rs00_0.0.3.36.bin` à `rs06_0.6.0.18.bin`) via `MotorStudio` (`motor_toolV14L.zip`) ou `Code/scripts/motors/ota_update.py` afin d'homogénéiser l'ensemble des 27 moteurs (lissage thermique à froid, OVP 60V unifiée, filtrage des trames MIT hors-mode et bit de défaut driver).

*Note : Ce document est classé avec le matériel de support d'acquisition matérielle.*

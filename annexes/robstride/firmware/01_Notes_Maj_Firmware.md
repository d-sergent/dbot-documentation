# Notes de Mise à Jour du Firmware (Avril 2026) — Moteurs RobStride

Ce document est la traduction exhaustive du changelog officiel des firmwares (Avril 2026) équipant la gamme de moteurs RobStride. Il couvre les modifications, corrections et ajouts fonctionnels vitaux pour l'opération via les protocoles CANopen et MIT.

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
| **0.0.3.27** | 1. Protocole MIT : Ajout des rapports actifs de statut, de sauvegarde asynchrone des paramètres, des lectures/écritures et champs d'états dans les trames.<br>2. Optimisation des conflits réseau entre rapports actifs et trames de retour (Feedbacks).<br>3. CANopen : La trame de quittance (Feedback) d'Activation/Désactivation est envoyée APRÈS exécution mécanique, fiabilisant le retour d'état du bus.<br>4. **Calibrage Initialisation Précise :** Actionné via `iq_test=1`. Au redémarrage, l'échantillonnage de courant est stabilisé, réduisant le "jitter" mécanique (tremblements).<br>5. **Calibrage Cogging (Couple de Détente) :** Activable via `alveolous_open=1` pour corriger les irrégularités de denture. Nécessite au préalable d'avoir fait un `iq_test` suivi d'un redémarrage à vide pour acquisition parfaite.<br>6. CANopen PP : Planification des arrêts d'urgence corrigée lors des modes combinés.<br>7. **Watchdog :** Via Index CANopen `0x6099` Sous-index 1. Toute valeur non nulle l'approuve.<br>8. **Protection NVRAM :** Lors d'un Disable, le moteur attend une tension stricte pour enregistrer ses données en ROM et utilise un bloc Mémoire de Secours Backup. S'il y a coupure durant l'écriture, le moteur boote sur le backup et remonte un code d'Alerte requérant une sauvegarde manuelle saine.<br>9. Profile Position (PP) : Découplage de la rampe en réglant `acc_status=1` (permettant la Décélération à `0x702E` indépendamment de l'accélération).<br> |

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
| **0.5.0.13 <br> 0.6.0.11** | Dernière révision. C'est ici que l'arsenal final apparaît (Sauvegarde M.I.T. protégée des crashs de tension, étalonnage initial avancé de filtrage du courant "jitter", rattrapages Cogging pour un glissement pur en vitesse base non bruitée, et désynchronisation des temps d'accélération et de décélération pour des robots bi-pédiques plus organiques). |

---

> [!TIP]
> **Action pour D-Bot / OpenClaw** : Assurez-vous d'utiliser `MotorStudio` pour garantir que toute l'équipe de vos moteurs (de la série RS02 des chevilles au RS05 du cou) soit actualisée avec les `.bin/.hex` d'avril 2026 afin de profitez du lissage des paramètres thermiques du courant à froid (réduit considérablement la température au repos), de la protection OVP de 60V universelle et du Calibrage automatique pré-mouvement (éliminant la vibration induite au Disable).

*Note: Ce document est classé avec le matériel de support d'acquisition matérielle.*

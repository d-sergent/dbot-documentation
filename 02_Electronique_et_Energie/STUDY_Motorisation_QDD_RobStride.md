# Étude : Motorisation QDD (Quasi-Direct Drive) & Actionneurs RobStride

Ce document détaille les justifications physiques du choix des moteurs QDD (Quasi-Direct Drive), les fiches techniques électriques et CAN de la gamme RobStride, ainsi que les contraintes thermiques et d'alimentation associées à la motorisation du D-Bot.

## 1. Pourquoi choisir les moteurs QDD (Quasi-Direct Drive) ?

Les moteurs QDD tels que les **RobStride** de notre inventaire sont devenus le standard *de facto* pour la robotique agile (bipèdes, quadrupèdes) parce qu'ils réussissent là où les servos traditionnels échouent dans l'interaction avec le monde physique :

1.  **La Réversibilité (Backdrivability)** : Le "Secret Sauce". Grâce à une très faible réduction (autour de 9:1), le moteur offre peu de résistance s'il est poussé de l'extérieur. Lors d'un impact au sol en courant, la mécanique "cédera" souplement au lieu d'exploser les engrenages (contrairement à un servo dynamique bloqué par un ratio de 100:1).
2.  **Contrôle d'Impédance (Transparence)** : L'absence de frottement lourd permet de déduire la force externe simplement en lisant la consommation de courant (sans installer de capteurs d'efforts coûteux). Le robot peut "sentir" le sol.
3.  **Densité de Couple Extraordinaire** : Orientés "Outrunner" (le rotor est à l'extérieur tel un volant d'inertie), les RobStride génèrent un couple d'arrachement pharaonique dans une taille de galette plate (ex: 60 N.m pour 880g sur le RS-03).
4.  **Intégration "Tout-en-un"** : ESC intégré, doubles encodeurs gérant le "backlash", et communication avec un simple bus CAN/Alimentation (seulement 4 fils parcourant le membre).

> [!WARNING]
> **Le point faible à maîtriser : La chauffe**
> Les servos traditionnels ont un frottement énorme freinant naturellement la chute. Les RobStride n'ayant aucun frein passif, s'ils doivent stabiliser 40 kg à l'arrêt, ils consommeront de l'énergie en courant continu et **chaufferont considérablement**. Une excellente dissipation thermique (interfaces en aluminium usinées à la CNC) est cruciale.

---

## 2. Spécifications Moteurs RobStride (Gamme Complète)

Voici les données techniques consolidées pour l'ensemble de la gamme RobStride (Février 2025).  
*Prix officiels RobStride ou sources vérifiées (OpenELAB, AiFitLab) - Hors taxes/livraison.*

| Modèle | Pic (N.m) | Nom. (N.m) | V.Nom/Max (RPM) | Poids (g) | Dim. (mm) | Ratio | Prix ($) | Volt. (V) | Usage D-Bot |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **RS-05** | **5.5** | 1.6 | 100 / 480 | **191** | 46×46×44 | 7.75:1 | **$120** | 48V (15-60V) | **Cou**, Doigts (futur) |
| **RS-00** | **14.0** | 5.0 | 260 / 315 | **310** | 57×57×51 | 10:1 | **$135** | 48V (24-60V) | **Poignet** (Compact, fort couple) |
| **RS-01** | **17.0** | 6.0 | 275 / 315 | **380** | 78.5×78.5×40 | 7.75:1 | **$140** | 36V (24-48V) | Alternative RS-02 (36V) |
| **RS-02** | **17.0** | 6.0 | 360 / 410 | **405** | 78.5×78.5×45.5 | 7.75:1 | **$160** | 48V (24-60V) | **Coude**, Biceps, Poignet |
| **RS-06** | **36.0** | 11.0 | — / 480 | **621** | 88×88×49 | 9:1 | **$230** | 48V (15-60V) | Entre-deux (Épaule légère) |
| **RS-03** | **60.0** | 20.0 | 180 / 195 | **880** | 106×106×56 | 9:1 | **$250** | 48V (15-60V) | **Épaule**, Hanche rot. |
| **RS-04** | **120.0** | 40.0 | 167 / 200 | **1420** | 120×120×56 | 9:1 | **$280** | 48V (15-60V) | **Hanche**, Genou, Cheville |

### 2.1 Analyse Comparative Électrique & Intégration

#### ⚡ RS-01 vs RS-02 : Élimination du RS-01
*   **Comparaison Mécanique** : Le RS-01 est plus léger (-25g) et plus fin (-5.5mm) que le RS-02 à couple égal (17 N.m).
*   **Comparaison Électrique (Défaut Éliminatoire)** : L'électronique du RS-01 plafonne à **48V max**. L'électronique du RS-02 encaisse **60V max**. Le bus batterie 12S du D-Bot monte à **50.4V** en pleine charge.

> [!CAUTION]
> **Élimination Définitive du RS-01 (Incompatible bus 12S)**
> Brancher un RS-01 sur le bus 12S (50.4V) du D-Bot présente un risque de destruction matérielle immédiate par surtension. Lors d'un freinage régénératif, les pics de tension dépasseront les 52V, ce qui détruira l'ESC du RS-01. Le RS-02 reste le seul standard valide pour les couples moyens.

#### 🌡️ Analyse Thermique Statique (Charge de 40 kg - Maintien debout)
Pour maintenir le robot de 40 kg debout avec les genoux légèrement fléchis ("crouch stance"), chaque hanche et genou requiert environ **20.6 N.m** de couple de maintien permanent.
*   **Avec le RS-03** (Résistance interne 0.39 Ω, Constante $K_t$ 2.36 N.m/A) : Consomme ~8.5 A continus. La dissipation thermique par effet Joule ($P=R \cdot I^2$) s'élève à **~28 Watts**. Le moteur est à 100% de son nominal et surchauffera rapidement jusqu'à la coupure de sécurité.
*   **Avec le RS-04** (Résistance interne 0.16 Ω, Constante $K_t$ 2.10 N.m/A) : Consomme ~9.5 A. La dissipation thermique chute à **~14.5 Watts**. Le RS-04 dissipe deux fois moins de chaleur et possède 61% de masse métallique en plus pour absorber les calories.
*   **Verdict** : Le **RS-04** est obligatoire pour les hanches et genoux pour prévenir la surchauffe statique. Les plaques d'interface en aluminium CNC sont critiques pour dissiper les 14.5W restants.

#### 🔌 Système de Verrouillage Statique (SVS) - Perspectives
Pour éliminer les 14.5W dissipés inutilement au repos, deux concepts anti-effondrement sont étudiés pour les évolutions futures :
1.  **SVS Électromagnétique (Solenoid Pin Lock)** : Un micro-solénoïde tubulaire pousse une broche métallique (pin) dans un trou borgne du rotor du RS-04 lorsque le robot est immobile. L'alimentation peut être coupée à 0A sans effondrement.
2.  **SVS Servo-Cliquet (Ratchet & Pawl)** : Remplacement de la broche par un cliquet hélicoïdal sur la couronne du moteur, engagé par un micro-servo.

---

## 3. Communication, Connectique & Alimentation

Tous les actionneurs RobStride partagent l'architecture système suivante :
*   **Bus de Données** : CAN 2.0B @ 1 Mbps (SocketCAN sous Linux, daisy-chain).
*   **Tension d'Alimentation** : 48V DC Nominal (Gamme de fonctionnement réelle : 15V-60V pour RS-02/03/04).
*   **Câblage** : 
    *   **Data** : Connecteurs JST-GH 1.25mm 4-broches (CAN_H, CAN_L, GND, VCC logique).
    *   **Power** : Connecteurs XT60 ou XT30 (selon le calibre de courant) montés en parallèle sur le bus de puissance principal.
*   **Double Encodeur** : Encodeur magnétique 14-bit absolu sur le rotor et encodeur sur l'axe de sortie, gérant automatiquement le jeu mécanique (backlash).
*   **Indice de Protection** : IP52 standard pour le châssis, IP67 en option sur spécification spécifique.

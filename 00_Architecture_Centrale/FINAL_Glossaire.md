# 28 — Glossaire Technique Robotique

Ce document centralise et définit les termes techniques, cinématiques et architecturaux employés tout au long de l'ingénierie du **D-Bot**.

## Définitions

| Terme | Catégorie | Définition |
| :--- | :---: | :--- |
| **Pitch** | Axe de rotation | **Tangage** — Rotation autour de l'axe médio-latéral (Y, gauche↔droite). À l'épaule, c'est le mouvement de **lever ou abaisser le bras devant/derrière soi**. Analogue au mouvement de "oui" de la tête. C'est l'axe qui subit le couple gravitationnel maximal car il lutte directement contre le poids du bras tendu. |
| **Roll** | Axe de rotation | **Roulis** — Rotation autour de l'axe antéro-postérieur (X, avant↔arrière). À l'épaule, c'est le mouvement d'**écarter le bras latéralement** (abduction/adduction). Analogue au mouvement de pencher la tête sur le côté. |
| **Yaw** | Axe de rotation | **Lacet** — Rotation autour de l'axe vertical (Z, haut↔bas). À l'épaule, c'est la **rotation interne/externe du bras sur lui-même** (comme tourner un tournevis). L'axe qui nécessite le moins de couple car il ne lutte pas contre la gravité. |
| **Backdrivability** | Mécanique | **Réversibilité mécanique** — Capacité d'un actionneur à être "poussé" manuellement lorsqu'il n'est pas alimenté. Un moteur backdrivable permet au bras de retomber naturellement sous l'effet de la gravité quand il est éteint, et de céder face à un obstacle (compliance passive). Les moteurs RobStride (RS-03, RS-02) sont **backdrivable** grâce à leur faible rapport de réduction. À l'inverse, un moteur avec un réducteur Harmonic Drive ou à vis sans fin n'est PAS backdrivable — il reste figé en position même sans courant. La backdrivability est essentielle pour la **sécurité** (le robot ne blesse pas un humain en cas de collision) et pour le **contrôle en impédance** (le robot peut "sentir" les forces externes et s'adapter). |
| **Axes concourants** | Cinématique | Configuration où les 3 axes de rotation d'un joint à 3 DOF (Pitch, Roll, Yaw) **se croisent en un point unique**. Cela reproduit le comportement d'une **rotule sphérique** parfaite. Plus les axes sont concourants, moins il y a de couples parasites dus aux bras de levier. C'est le standard visé par tous les robots haut de gamme (Unitree, Tesla, Atlas). |
| **Gimbal Lock** | Cinématique | **Blocage cardanique** — Perte temporaire d'un degré de liberté qui survient quand deux des trois axes de rotation d'un joint cardanique s'alignent. En pratique, cela signifie que le robot ne peut momentanément plus tourner dans une direction. Résolu en logiciel par l'utilisation de **quaternions** au lieu des angles d'Euler. |
| **Stacked Perpendicular** | Architecture | Architecture d'épaule/hanche où les 3 moteurs sont **empilés en série**, chacun monté perpendiculairement au précédent. Le stator de chaque moteur est fixé au rotor du moteur précédent via un bracket. C'est l'architecture la plus simple et la plus reproductible pour les robots utilisant des moteurs off-the-shelf. |
| **Direct-Drive** | Motorisation | Configuration où le rotor du moteur est **directement connecté** à la charge, sans réducteur ni engrenage intermédiaire. Avantages : zéro backlash, backdrivable, contrôle en couple précis. Inconvénient : couple limité au couple natif du moteur. Les moteurs RobStride sont **quasi direct-drive** (réducteur planétaire à faible ratio ~9:1). |
| **Bracket** | Pièce mécanique | Pièce de liaison (équerre, support) reliant le **rotor d'un moteur** au **stator du moteur suivant** dans un empilement série. Usiné en Alu 6061-T6 sur CNC (C500) pour le D-Bot. Sa compacité détermine directement le décalage inter-axe. |

---

*Dernière mise à jour : Mars 2026. Document évolutif basé sur les analyses architecturales (Hanche, Épaule, Cheville).*

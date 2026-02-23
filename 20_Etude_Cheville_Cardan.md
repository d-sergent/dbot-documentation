# Étude et Conception de la Cheville du D-Bot (Architecture Cardan)

Ce document résume l'étude détaillée concernant la reconception de la cheville du robot bipède (approx. 35 kg), basée sur les analyses mécaniques récentes et visant à remplacer la rotule radiale GE12UK par un système de cardan (Gimbal) couplé à une cinématique différentielle.

## 1. Contexte et Problématique Initiale

La rotule radiale **GE12UK** initialement envisagée pour le pivot central de la cheville présente une forte limite cinématique. Son **débattement maximal de 15°** (en Pitch et Roll) est un "goulot d'étranglement". 
Pour un humanoïde de 35 kg, ce débattement est insuffisant pour monter des pentes, s'accroupir ou simplement marcher de façon fluide. Le mécanisme risque d'arriver rapidement en butée mécanique, ce qui pourrait briser les pièces imprimées en 3D (PA12-CF) ou griller les moteurs sous l'effort.

## 2. La Nouvelle Architecture : Cheville Différentielle à Cardan

L'étude conclut sans appel qu'il faut séparer les axes de liberté (Pitch et Roll) en utilisant un **joint de cardan (Gimbal)** comme pivot central.
La cheville fonctionnera en "Trépied" avec un mécanisme à tringlerie parallèle différentiel (type Optimus) :
- **Le Pivot Central (Cardan)** : Supporte 100% du poids du robot (35 kg). Permet un débattement très élevé (ex: +30°/-45° en Pitch) sans butée structurelle précoce.
- **Les 2 Bielles (Pushrods) à l'arrière** : Reliées aux moteurs. Un mouvement synchrone crée le tangage (Pitch), un mouvement asynchrone crée le roulis (Roll).

### Le Choix des Moteurs
Pour un robot de 35 kg, la configuration recommandée est : **2 x Moteurs RobStride RS-03 par cheville**. 
Bien que plus lourds, ils offrent ensemble un **couple de pointe en Pitch de 120 N.m**, une réserve vitale pour la stabilisation dynamique et pour compenser l'énorme charge d'impact lors d'un pas (jusqu'à 870 N). L'utilisation de petits moteurs RS-02 (34 N.m max en paire) ou RS-06 est jugée insuffisante ou trop juste pour ce poids.

## 3. Achats et Recommandations de Montage

### A. Le Joint de Cardan 
Il est crucial d'utiliser un modèle industriel en acier haute résistance (type Acier C45) pour un axe de 12 mm.
- **Modèle Recommandé** : Joint de cardan simple **Série G** (douilles lisses, plus résistantes aux chocs que les aiguilles de la Série H). Norme DIN 808.
- **Où acheter en France** :
  - **Michaud Chailly** (Référence : A5-473-12, qualité premium).
  - **HPC Europe** (Référence : UJ-12).

### B. Fixation et Maintien Axial de l'Axe de 12 mm
L'axe en acier rectifié (12mm h6) ne doit ni tourner à l'intérieur du cardan (transmission du couple), ni glisser sous l'effet des vibrations (maintien axial).
1. **Transmission du Couple** : Privilégier un modèle avec **vis de pression (Set Screws)**. L'axe de 12 mm devra être aplani (création d'un méplat) pour l'appui de la vis. Mettre impérativement du **Frein filet bleu** (Loctite). Une autre option est la rainure de clavette.
2. **Maintien Axial** : La vis de pression et la clavette ne suffiront pas pour encaisser les chocs latéraux (Roll). Il faut ajouter des **Bagues d'arrêt (Shaft Collars)** en acier, en deux parties (fendues), de chaque côté du cardan.
   - **Où acheter** : **HPC Europe** (BAG2-012) ou **Michaud Chailly / Ruland** (F2-39-12). Vis de classe 12.9.

### C. Entretien et Protection (Soufflet)
- **Le Soufflet** : Acheter un petit **soufflet de protection en néoprène** (souvent vendu en option avec le cardan sur RS, Michaud ou HPC). Il est indispensable pour protéger l'articulation (située au ras du sol) de la poussière et pour qu'elle ne prenne pas de jeu prématurément.

### D. Les Bielles (Pushrods) et Rotules Arrière
- **Bielles** : Tubes en de Carbone 3K (Ø ext 10mm / Ø int 8mm) pour une excellente rigidité sous pression sans flambement.
- **Rotules d'extrémités** : Embouts M5. **EBRM-05** d'Igus (très léger, polymère) ou **SAK 5 C** (acier/PTFE sur 123Roulement) pour absorber les vibrations.

## 4. Conclusion

Pour garantir la durabilité du D-Bot (35 kg et 10 kg de charge utile), le passage d'une simple rotule radiale GE12UK à un **joint de cardan DIN 808 industriel couplé à un système d'actionneurs différentiels (2x RS-03)** est indispensable. 
Le montage de la cheville doit rigoureusement intégrer des bagues d'arrêt en acier usiné pour empêcher la dislocation axiale, du frein filet pour parer aux vibrations, et des tubes de carbone rigides pour les bielles de transmission. L'ajout de 4 capteurs de force plantaire (FSR) sous le pied imprimé en PA12-CF finalisera alors l'aptitude du robot à s'équilibrer de manière autonome.

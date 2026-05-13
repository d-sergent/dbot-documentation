# 22 — Usinage CNC : NestWorks C500

Afin d'usiner les composants vitaux du robot humanoïde D-Bot (y compris les brackets moteurs, l'avant-bras et la série d'actuateurs cycloïdaux de la *D-Hand*), le projet s'appuie **exclusivement** sur la **[CNC NestWorks C500 (Kickstarter)](https://www.kickstarter.com/projects/959480926/nestworks-c500-next-gen-smartest-cnc-with-industrial-power?ref=6kxkib&gad_source=1&gad_campaignid=23219605599&gbraid=0AAAABB43OIjDJ9r7f4_PShKb-aiRTG1WU&gclid=Cj0KCQiA5I_NBhDVARIsAOrqIsarYDgeND2akM2atrgBpf3fPrG1im0h9fJHcixW_bDDwAAOqZZsyK4aAvDOEALw_wcB)**.

Cette fraiseuse professionnelle "Desktop" est la machine de référence unique pour tout l'aluminium du robot, offrant une synergie parfaite avec notre impression 3D (Qidi).

---

## 1. Spécifications Techniques (NestWorks C500)

La C500 n'est pas un jouet de bureau, c'est une fraiseuse de classe industrielle miniaturisée :
- **Broche Haute Puissance** : **800W** (AC Servo motorisée, jusqu'à 18 000 tr/min). Permet d'attaquer directement des blocs d'Aluminium 6061 ou 7075-T6, offrant un couple bien supérieur aux petites broches de 200W courantes sur les CNC de bureau.
- **Changeur d'Outil Auto (ATC)** : Carrousel 10+ outils avec puces RFID pour la configuration automatique de la longueur d'outil.
- **Précision Industrielle** : Guidages linéaires (Linear Rails & Ballscrews), suffisante pour garantir la tolérance **ISO H7 (±0.02 mm)** vitale pour l'insertion de nos roulements.
- **Palpage 3D** : Touch probe sans fil intégré pour le repérage parfait des origines pièces.

---

## 2. Le 4ème Axe Rotatif (Tournage CNC)

L'acquisition du **Module 4ème Axe** de la NestWorks C500 change la donne sur l'ingénierie globale du D-Bot. Il permet de traiter les pièces non seulement en "fraisage plat" (3 axes), mais aussi en "tournage" :

### Applications critiques pour le D-Bot :
1. **Les Inserts de Tibia (Bouchons Alu/PA12)** : Au lieu d'usiner un bloc plat et de passer un temps infini à détourer un cylindre en 3D, le 4ème axe tourne la pièce. C'est idéal pour créer parfaitement le cylindre Ø12 mm et ses **gorges de circlips** inférieures.
2. **Taraudage et Filetage Externes** : La puissance de la C500 permet de tailler des pas de vis complexes sur de longs axes de transmission (ex: fileter l'embout d'un bras de levier en titane ou acier) grâce à la rotation couplée de l'axe A.
3. **Bras et Phalanges** : Usinage multi-faces sans devoir démonter et repositionner la pièce dans l'étau. La machine fait pivoter la pièce pour usiner dessus, dessous, et sur les côtés dans la même opération (réduisant le fameux "setup time").

---

## 3. Outils Métal (Professional Metal Tool Kit)

Le choix du kit professionnel orienté métal avec revêtement **DLC (Diamond-Like Carbon)** est le pilier de tous nos développements sur de l'Aluminium 7075-T6 pour éviter que l'alu chaud ne "colle" à la fraise.

| Type d'outil | Utilisation sur le D-Bot |
| :--- | :--- |
| **Flat End Mill (1/4")** | Fraise plate (6.35 mm). L'outil "de force" pour ébaucher les gros brackets moteurs (RS-04/05). |
| **O-Type End Mill** | Fraise à 1 dent. Évacuation très rapide des copeaux (idéal poches profondes). |
| **Chamfer Cutter (90°)** | **Indispensable pour le H7.** Permet de casser les angles une fois alésés pour ne pas rayer les micro-roulements à l'insertion. |
| **Ball Nose** | Pour usiner des congés internes dans les phalanges afin de prévenir la rupture sous charge. |

> [!TIP]
> **Règle d'Usinage H7** : Une passe d'ébauche avec une Flat End Mill usée, suivie *impérativement* d'une passe terminale micrométrique avec un outil DLC neuf pour la cote finale.

---

## 4. Tolérances et Pinces ER11 (Alerte de Sécurité)

La NestWorks C500 utilise un système de pince de serrage industriel **ER11**. Le kit de base est souvent livré en métrique américain (fraises de *1/4"* soit 6.35 mm et de *1/8"* soit 3.175 mm). 

**Règle absolue :**
1. **Ne jamais forcer** une fraise métrique de 6 mm dans une pince impériale de 1/4" (6.35 mm).
2. Ce désalignement engendre un "runout" (voile) asymétrique. Un battement de juste **0.02 mm** ruine le fraisage d'un logement de roulement H7, et abîme prématurément la broche de 800W.
3. **Solution** : Ranger les collets NestWorks impériaux séparément. Si vous achetez des fraises européennes (6 mm, 4 mm), commandez les pinces ER11 métriques strictes correspondantes.

---

## 5. Gestion ATC Spécifique (RFID)

Le système ATC de NestWorks opère avec des puces RFID collées sur les **Bit Tool Holders** (les porte-outils, pas directement sur la fraise). 
- **Bénéfice** : La puce n'est pas exposée à la chaleur ou aux vibrations de la coupe. 
- **Maintenance** : Si une fraise casse, il suffit de changer la partie coupante dans le collet. La puce numérotée reste fixée au haut du Tool Holder, conservant ses propriétés et sa longueur pré-calibrée dans le logiciel NestWorks Studio.

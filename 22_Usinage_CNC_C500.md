# Usinage CNC C500 - Consignes pour le D-Bot

Afin d'usiner les composants vitaux du robot humainoïde D-Bot (y compris l'avant-bras et la série d'actuateurs cycloïdaux de la *D-Hand*), nous nous appuyons sur la **CNC NestWorks C500**.
Cette annexe recense les consignes clés issues de l'analyse initiale pour préserver la machine, garantir la précision vitale du H7 exigée par le montage moteur, et maximiser l'emploi des fournitures existantes.

## 1. Outils Métal (Professional Metal Tool Kit)

Le choix du kit professionnel orienté métal avec revêtement **DLC (Diamond-Like Carbon)** est le pilier de tous nos développements sur de l'Aluminium 7075-T6.
Ce revêtement réduit drastiquement les frictions et empêche le métal "de coller" à la fraise naissant d'alliages tendres (arête rapportée).

### Application des outils à la fabrication du robot :

| Nom Fourni | Traduction / Type | Utilisation sur le D-Bot |
| :--- | :--- | :--- |
| **O-Type End Mill** | Fraise "O-Flute" à 1 dent | Évacuation très rapide des copeaux. Outil idéal pour creuser dans les blocs pleins de 30mm dédiés aux châssis. |
| **Flat End Mill (1/4")** | Fraise plate à 2 dents (6.35 mm) | L'outil "de force". Principalement utilisé pour retirer massivement (ébauche) de la surface de travail sur les pièces larges. |
| **Chamfer Cutter** | Fraise à chanfreiner (90°) | **Indispensable pour nos tolérances H7.** Permet de casser les angles une fois alésés. Sans cet ébavurage CNC, les insertions de micro-roulements seront bloquées ou rayées. |
| **Taper Ball Nose / Ball Nose** | Fraises hémisphériques (divers angles) | Utilisées pour les congés afin d'arrondir les arrêtes internes des phalanges/pièces 3D pour prévenir les ruptures sous charge. |
| **V-Shape Engraving Bit** | Fraise à graver (30°) | Pour les gravures des numéros de série de pièces (indexage lors de l'assemblage complexe). |

*Note de précision* : En usinage H7, une passe d'ébauche avec une Flat End Mill usée, suivie impérativement d'une passe terminale micrométrique avec un des outils DLC neufs est systématiquement recommandée.

## 2. Attention Particulière aux Collets (Pinces de Serrage ER11) : Impérial vs Métrique

C'est ici que se trouve le plus grand risque de casse matérielle si les standards sont confondus.
L'équipement livré avec la fraiseuse NestWorks se repose intégralement sur le système impérial américain (fraises de *1/4 pouce* soit $6.35\text{ mm}$ et de *1/8 pouce* soit $3.175\text{ mm}$). 

**Règle absolue :**
1.  **NE JAMAIS** insérer une fraise métrique de dimension proche (exemple : une fraise européenne de $6\text{ mm}$) dans une pince ER11 impériale de $1/4\text{ pouce}$ ($6.35\text{ mm}$), même si cela semble possible "en forçant sur l'écrou".
2. Cela engendre un "runout" (voile) asymétrique. Un battement de juste $0.02\text{ mm}$ suffit à ruiner un fraisage pour roulement H7, et abîme de façon permanente la broche principale.

**Gestion de l'Atelier :**
- Les outils NestWorks et leurs collets respectifs ($1/4$ et $1/8$) sont marqués et rangés séparément sur le râtelier A (Impérial).
- À l'achat de fraises complémentaires sur le marché européen ($6\text{ mm}$, $4\text{ mm}$, $3\text{ mm}$), **nous devrons commander avec les collets ER11 métriques stricts correspondants** (Râtelier B - Métriques).

## 3. Gestion ATC et durabilité des Puces RFID

Le système ATC (Automatic Tool Changer) opère avec **20 Puces RFID** fournies, agissant comme identifiants incontestables auprès de NestWorks Studio afin de sécuriser le changement automatique d'outils et ses spécifications métiers.

*   Elles ne se posent **pas** sur la surface coupante, mais se collent sur les *Bit RFID Tool Holders* dédiés à ce système râtelier, protégeant ainsi la puce des vibrations et de la chaleur d'usinage.
*   **Réaffectation Libre :** Si une fraise est détériorée ou vient à céder, extraire seulement son corps cassé. Conserver la partie supérieure (le *Bit Tool Holder*) : la puce conserve sa lisibilité absolue !
*   Dans l'interface logicielle de la C500, elle peut être effacée numériquement, ou réassignée à un nouvel outil instantanément. C'est un stock permanent de clés numériques sécurisant le process.

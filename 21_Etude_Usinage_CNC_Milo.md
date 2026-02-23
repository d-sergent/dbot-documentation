# 21 - Étude et Acquisition CNC Milo (Usinage Aluminium)

## 1. Contexte et Nécessité d'une CNC Aluminium

Pour les robots de la gamme k-bot (actionneurs quasi-direct drive à fort couple) et d-bot (cinématique rapide), l'impression 3D montre ses limites physiques :
- **Fluage (Creep) des plastiques** : Même avec des matériaux haute performance comme le PA-CF (Nylon Carbone) ou le PC, les logements de roulements soumis à une tension radiale ou thermique constante finissent par se dilater (ovalisation), créant un jeu inacceptable.
- **Tolérances H7** : Pour des liaisons mécaniques sans jeu (ajustement glissant "juste" pour un roulement), l'impression FDM nécessite des ajustements empiriques lourds (*Hole Expansion*) et manque de la fiabilité offerte par le métal.

**Impact direct sur l'étude** : 
> [!IMPORTANT]
> À partir de cette étape du projet, il est acté que **certaines pièces critiques structurelles et de transmission (supports moteurs, jonctions de bras) devront impérativement être usinées en aluminium** (nuance 6061-T6 ou 7075).
> **La conception de ces pièces sous CAO doit dès à présent intégrer les contraintes d'usinage sur CNC 3 axes** (dégagements d'outils, évidements accessibles par le haut, surfaçage). 

## 2. Le Choix Matériel : Millennium Milo v1.5

Face aux options du marché (Carbide Nomad 3, Shapeoko), le projet **Millennium Machines Milo v1.5** (Open-Source) s'impose comme la solution idéale pour la robotique DIY avancée :

- **Rigidité Industrielle** : Architecture renforcée (Mod FMJ - Full Metal Jacket) conçue spécifiquement pour absorber les vibrations (chatter) lors de l'usinage du métal.
- **Puissance de Broche** : Broche de 1.5 kW avec pince ER16 (permet de monter des fraises jusqu'à 9mm) contre 130W ER11 pour une Nomad 3. Cela autorise des passes d'ébauche significatives dans l'aluminium 6061.
- **Micro-précision intégrée** : Le kit officiel (LDO Motors) inclut le "Long John" (palpeur automatique de longueur d'outil pour recalibrer l'axe Z au micron près) et la "Fixtated Plate" (plaque continentale taraudée M5 pour un bridage répétable indispensable).
- **Synergie Impression 3D / CNC** : Construire la Milo nécessitera ~3 kg d'impressions 3D en **ASA / ABS** (le PLA fluant sous la chaleur des moteurs), tâche qui sera confiée à la **Qidi Plus 4** du d-Bot.

## 3. Stratégie d'Achat (Milo v1.5 / v2.0)

La Milo étant produite par "batches" (lots de production LDO Motors), elle est fréquemment en rupture de stock.
*Budget estimé (Machine finie)* : ~1 600€ (Kit LDO à ~1 350€ + Étau de précision à ~150€ + Consommables Alu/Fraises).

### 3.1. Comment acquérir la machine dans les mois à venir :

1. **Surveillance du Discord Officiel Millennium Machines** :
   - [Lien Discord: discord.gg/dhBHRfws6G](https://discord.gg/dhBHRfws6G)
   - C'est le point névralgique pour être notifié des **restocks** et des **annonces concernant la future V2.0**.
   - Canaux clés : `#announcements` (informations officielles), `#milo-v_1_5`, et utiliser la recherche sur le mot "restock".

2. **Revendeurs Européens Prioritaires (Éviter les frais de douane US)** :
   - **3DJake** : Partenaire historique LDO, très fiable, activer l'alerte de réapprovisionnement.
   - **Desktop Machine Shop (UK)** : Revendeur très impliqué, vend souvent la broche et l'électronique en pack.
   - À défaut (USA) : Fabreeko (si le budget permet l'import).

3. **La question de la V2** : Vérifier sur Discord l'imminence de la V2 avant l'achat d'un kit v1.5. Si les délais de la V2 sont trop longs, la v1.5 reste parfaitement dimensionnée et évolutive (upgrade possible en ré-usinant les nouvelles pièces).

### 3.2. Comparatif V1.5 vs Future V2.0

L'attente pour la V2.0 (ou la recherche des restocks de kits V1.5) dépendra de votre niveau d'urgence. La V2.0 passe d'une machine "bricolée de passionnés" à un produit beaucoup plus abouti, professionnel et facile à calibrer.

Voici les évolutions majeures annoncées pour la V2.0 :
- **Volume d'usinage agrandi** et introduction d'une variante compacte "Miley v2.0" (axe X fixe).
- **Ajustement automatique du jeu** : Écrous Anti-Backlash auto-ajustables (correction d'un point noir de la V1.5).
- **Protection accrue** : Couvertures magnétiques (Way Covers) pour protéger les rails des copeaux d'aluminium.
- **Ergonomie ("Quality of Life")** : Alignement de la machine (Tramming) ultra-simplifié grâce à de nouvelles plaques "Easy tram plates".
- **Électronique dédiée** : Nouvelle carte (partenariat BigTreeTech) intégrant directement les drivers (jusqu'à 4.75A) et la commande du VFD, éliminant le besoin de cartes filles.

> [!NOTE]
> À cause des énormes changements structurels, il n'est pas possible d'upgrader directement et totalement une v1.5 en v2.0. Cependant, un kit d'amélioration "v1.6" sera proposé pour apporter certaines améliorations de confort de la V2 aux possesseurs actuels de V1.5.

## 4. Équipements Indispensables et Méthodes d'Atelier

L'usinage de pièces de k-bot en aluminium ne s'improvise pas sans méthodologie. Oubliez la fonderie artisanale (problèmes de porosité et retrait de 1 à 2%) et misez sur l'usinage dans la masse (Billet 6061-T6 depuis *Blockenstock* ou *Matière Détail*).

### 4.1. L'Outillage de Fraisage
- **Fraises Spécifiques** : Utiliser impérativement des fraises à **1 dent (Single Flute) pour l'aluminium** (ex: diamètres 6mm, 3.175mm, 2mm). Cela garantit l'évacuation rapide du copeau avant qu'il ne fonde.
- **Lubrification** : Adjonction d'un système "Mist Coolant" ou à minima lubrification manuelle (Huile de coupe/WD-40). L'alu à sec a tendance à coller sur la fraise (gummification) et à la détruire.

### 4.2. Les Taraudages (M3, M4, M5)
La Milo n'a pas de couple à base vitesse pour du taraudage mécanique classique (Rigid Tapping).
- **Méthode Hybride (Débutants)** : Percer précisément avec la CNC (ex: 2.5mm pour M3), puis tarauder manuellement avec des tarauds HSS-E Cobalt machine (Gühring ou Format) lubrifiés.
- **Méthode Thread Milling (Pro)** : Utiliser une fraise à fileter universelle (carbure) qui tourne en hélice dans le trou CNC. Plus délicat sur le CAM mais infiniment plus fiable (pas de taraud cassé dans la pièce).

### 4.3. L'Acquisition du H7 (Logements Roulements)
- On ne génère pas un H7 à la fraiseuse du premier coup : l'aluminium fléchit sous l'effort de la broche.
- **La méthode reine** : Ébauche à la fraiseuse (ex: percage à 7.8mm), passe de finition (*spring pass*), puis passage final avec un **Alésoir Machine** (ex: 8.00 mm) pour obtenir un trou géométriquement parfait sans ovalisation, où le roulement s'insèrera "press-fit" sans besoin de bridage.

### 4.4. Chaîne Logicielle CAM : FreeCAD vs Fusion 360
Pour piloter la Milo (sous RepRapFirmware) :
- **FreeCAD (Atelier Path)** : Entièrement gratuit, il lève les limites des changements d'outils automatiques. Idéal avec le palpeur "Long John" pour enchaîner perçage / ébauche / filetage en un seul lancement de fichier.
- **Fusion 360 (Licence gratuite)** : Très puissant, mais bride l'export complet : il faut exporter un programme (Gcode) par outil (soit plusieurs fichiers à lancer consécutivement).

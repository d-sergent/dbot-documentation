# 12b - Bibliothèque C500 & Vitesses de Coupe (Fusion 360)

Ce document récapitule les réglages et "Feeds & Speeds" (Vitesses et Avances) recommandés par la communauté NestWorks pour usiner l'aluminium (6061/7075) sur la **CNC C500** avec des fraises revêtues **DLC**.

## 1. Configuration de la Bibliothèque (Tool Library)

Dans Fusion 360 (Espace *Manufacture*), importez le fichier `.json` officiel depuis le Discord NestWorks (`#Downloads`) via `Manage > Tool Library > Local > Import libraries`.

> [!IMPORTANT]
> **Puces RFID et Numéros d'Outils** : La C500 utilise des tags RFID sur les porte-outils. Assurez-vous impérativement que le **Numéro d'outil** (Tool Number) assigné dans Fusion 360 correspond exactement à l'emplacement physique de cet outil dans le râtelier de l'ATC.

### Paramètres Manuels (Fraises DLC)
Si vous devez recréer un outil manuellement (Matériau: Carbide, Revêtement: DLC) :
*   **Flat End Mill (1/4")** : Dia. 6.35mm, Longueur de coupe 19mm, 2 dents (Two Flutes).
*   **O-Type End Mill (1/8")** : Dia. 3.175mm, Longueur de coupe 12mm, 1 dent (Single Flute).

---

## 2. Fiche de Coupe Aluminium (Cheat Sheet C500)

Ces valeurs sont des points de départ fiables pour l'Aluminium 6061 ou 7075 :

| Outil | RPM (Vitesse) | Avance (Feed Rate) | Passes (DOC) | Cas d'usage |
| :--- | :---: | :---: | :---: | :--- |
| **Flat End Mill (1/4")** | 15 000 tr/min | 1500 mm/min | 0.5 à 1.0 mm | Ébauche & Structure (vidage rapide) |
| **O-Type (1/8")** | 18 000 tr/min | 900 mm/min | 0.3 à 0.6 mm | Rainurage & Détails (1 dent = pas de bourrage) |
| **Ball Nose (Finition)** | 12 000 tr/min | 800 mm/min | 0.2 mm (Stepover)| Surfaces 3D et courbes lisses |
| **Chamfer Cutter** | 10 000 tr/min | 600 mm/min | 0.5 mm (Unique) | Finition et ébavurage des perçages |

> [!WARNING]
> **Le bruit de broutement (Chatter)** : Si lors d'un usinage profond (blocs de 30mm) vous entendez un fort sifflement/vibration résonnante :
> 1.  Réduisez l'avance (Feed) de 10% sur la manette C500.
> 2.  Augmentez légèrement la vitesse (RPM).
> 3.  **Vérifiez rigoureusement le serrage de vos brides (Top Clamps)** : sur 30mm d'épaisseur, le moindre jeu ruine la précision.

---

## 3. L'Astuce d'Expert : Ajustements H7 (Logements Roulements)

Pour les articulations majeures du D-Bot, vos roulements doivent s'insérer en force légère (k6/m6) sans jeu radial, avec une tolérance cible de **+0.005 à +0.015 mm** par rapport au diamètre extérieur du roulement. Sur la C500, voici la recette idéale :

1.  **Stock to Leave** : N'usinez jamais l'alésage final d'un seul coup. Lors de la passe d'ébauche, laissez obligatoirement **0.1 mm** de matière radiale.
2.  **Spring Pass (Passe de ressort)** : Utilisez la grosse fraise plate 1/4" (la plus rigide) pour la passe de contournage de finition. Répétez cette même trajectoire finale une seconde fois à vide sans aucun décalage. Cela permet à l'outil de couper uniquement sa propre déflexion mécanique résiduelle (flexion de l'arbre).
4.  **Lubrification MQL** : Obligatoire sur l'aluminium. Réglez le brouillard pour obtenir une pellicule d'huile constante mais fine. Associé au revêtement DLC, cela laissera un fini "miroir" à l'intérieur de l'alésage (capital pour la portée du roulement).

---

## 4. Sécurité & Précision : Filetage M3 (Thread Milling)

Pour vos fixations de cou et d'articulations, le pire cauchemar est de briser un taraud manuel (HSS) dans une pièce usinée durant 4 heures. La méthode "Pro" pour la C500 est le **Fraisage de filet** (Thread Milling) :

1. **L'Outil** : Achetez une **Micro-fraise à fileter M3 à 1 dent (Single Point)** en carbure avec revêtement DLC (trouvable chez *CncFraises* en France, à queue de 4mm pour s'adapter à vos collets).
2. **Le Perçage** : L'outil demande un avant-trou parfait. Utilisez un foret en carbure de **2.5 mm** avant de passer la fraise à fileter.
   *   *Force* : La broche 800W de la C500 peinerait avec une fraise multi-dents, le modèle à 1 dent coupe en douceur.
   *   *Sécurité* : La fraise tourne sans forcer et ne reste jamais bloquée.
   *   *Ajustement* : Vous pouvez régler finement l'offset (compensation au centième près) dans Fusion 360 pour obtenir un couple de serrage M3 exactement comme vous le souhaitez.

---

## 5. La "Startup Card" d'usinage Aluminium (Spécial C500)

Cette checklist (à imprimer/plastifier sous forme de carte) est essentielle pour standardiser la sécurité et ne jamais rater un alésage de précision (ex: tolérance H7) dans les pièces massives du robot.

### 1. Check-up Machine (Énergie & Fluides)
- [ ] **AIR** : Compresseur activé (Cible : 90-100 PSI).
- [ ] **MQL** : Niveau d'huile OK + Buse bien orientée vers la pointe de l'outil.
- [ ] **PROPRETÉ** : Cône de broche immaculé (essuyer au chiffon sec).
- [ ] **WARM-UP** : Lancer la broche 5 min à 6 000 tr/min pour la chauffer.

### 2. Setup Pièce (Stabilité & Origine)
- [ ] **BRIDE** : Serrage maximal des *Top Clamps* sur le bloc brut.
- [ ] **ZÉRO (WCS)** : Palper le Z-Zero exactement sur le sommet du brut.
- [ ] **COLLISION** : Vérifier que les brides ne gênent pas le passage du portique ou de l'outil.
- [ ] **TOOLS** : Vérifier l'ordre physique des outils dans le râtelier de l'ATC.

### 3. Usinage (Objectif "H7")
- [ ] **G-CODE** : L'hauteur de dégagement (Retract Height) est d'au moins 30 mm.
- [ ] **STRATÉGIE** : *Adaptive Clearing* activé pour l'ébauche.
- [ ] **SPRING PASS** : Passe de finition ("contour") doublée à vide programmée pour la cote H7.
- [ ] **OVERRIDE** : Garder la main sur le bouton Speed/Feed de la machine pour le 1er tour.

### 4. Shutdown (Maintenance Préventive)
- [ ] **ASPIRATION** : Retirer 100% des copeaux d'aluminium du plateau.
- [ ] **SOIN** : Essuyer les queues d'outils (notamment revêtement DLC) pour éviter l'oxydation.
- [ ] **PURGE** : Vider l'humidité de la cuve du compresseur d'air.

> 💡 **L'Astuce du "D-Bot" (Acoustique)** : Lors de l'usinage profond (ex: blocs de 30mm d'épaisseur), si vous entendez un "cri" aigu, la fraise vibre. Réduisez immédiatement l'avance de 10% sur le contrôleur. Un usinage aluminium sain doit produire un bourdonnement continu ("shhhhhh").

---

## 6. L'Astuce ATC : Le "G-code Joiner" (Fusion 360 Gratuit)

La version gratuite personnelle de Fusion 360 bloque l'exportation d'un G-code contenant de multiples outils (nécessaire pour utiliser l'ATC de la C500 en totale autonomie). La solution prisée de la communauté est la fusion manuelle de fichiers (le "Joiner").

### 1. Le Principe
Puisque le logiciel vous oblige à générer un fichier `.nc` par outil, le but est de les "coller" bout à bout via un éditeur de texte (ex: Notepad++, VS Code).

### 2. Procédure étape par étape
* **Fichier 1 (Outil T1)** : Conservez tout le code, MAIS supprimez impérativement la toute **dernière ligne** (souvent `M30` ou `M2`, qui ordonne l'arrêt total définitif de la machine).
* **Fichier 2 (Outil T2)** : Supprimez les **premières lignes** de l'en-tête de paramétrage. Ne gardez le code qu'à partir du bloc appelant le nouvel outil (ligne contenant `M6`).
* **Ligne Clé de Jonction** : Le raccord entre le fichier 1 et 2 doit toujours faire figurer la ligne `T[numéro] M6` (ex: `T2 M6`). C'est elle qui commande au bras de la C500 d'aller prendre le 2ème outil dans le râtelier.

### 3. Précautions critiques
* **Mesure de l'outil (Probing)** : Assurez-vous que la ligne commandant la mesure automatique de la hauteur d'outil (qui suit le `M6`) n'a pas été effacée ni écrasée au collage.
* **Vitesse de déplacement (Rapids)** : Attention, Fusion gratuit bride les mouvements rapides (`G0`). Vos G-code fusionnés fonctionneront, mais les déplacements de sécurité entre deux zones d'usinage s'effectueront à la vitesse d'avance de coupe (beaucoup plus lentement).
* **Simulateur** : Testez toujours votre super-code fusionné dans un visualiseur comme **NC Viewer** en ligne avant de l'injecter dans la CNC pour détecter les trajectoires aberrantes.
* **Automatisation (Niveau 2)** : Pour éviter les oublis de nettoyage des `M30`, une fois l'astuce bien maîtrisée, utilisez des scripts utilitaires GitHub (tapez "*G-code Joiner*") qui nettoieront et raccorderont les fichiers à votre place pour lancer des nuits entières d'usinage.

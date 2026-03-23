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
3. **Les Avantages (Robot 39 kg)** :
   *   *Force* : La broche 800W de la C500 peinerait avec une fraise multi-dents, le modèle à 1 dent coupe en douceur.
   *   *Sécurité* : La fraise tourne sans forcer et ne reste jamais bloquée.
   *   *Ajustement* : Vous pouvez régler finement l'offset (compensation au centième près) dans Fusion 360 pour obtenir un couple de serrage M3 exactement comme vous le souhaitez.

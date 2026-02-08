# Guide Technique : Installation & Optimisation Buse Carbure de Tungstène

Ce document détaille l'installation de la buse haute performance en **Carbure de Tungstène**, recommandée pour les filaments chargés carbone (PETG-CF, PA12-CF) du projet D-Bot.

## 1. Pourquoi cette Upgrade ?
*   **Résistance Extrême** : Inusable face à l'abrasion du carbone (contrairement au laiton qui se creuse en quelques heures et à l'acier trempé qui s'use lentement).
*   **Conductivité Thermique** : Proche du cuivre. Permet de chauffer aussi vite et stablement que le laiton, contrairement à l'acier trempé qui isole et demande de surchauffer (+10°C).
*   **Fluidité** : Réduit drastiquement les risques de bouchage (clogs).

## 2. Procédure d'Installation (Critique)
Le carbure de tungstène est ultra-dur mais **cassant** aux chocs. Manipulez avec précaution.

### Étape 1 : Le Serrage à Chaud
1.  Montez la buse à la main (à froid).
2.  Chauffez la tête d'impression à **250°C** (ou plus, temp d'impression max).
3.  **Serrez impérativement à chaud**. Cela garantit l'étanchéité métal-métal avec le heatbreak.
    *   *Couple de serrage* : 1.5 Nm à 2.0 Nm (ne pas forcer comme une brute).

### Étape 2 : Calibration PID (Indispensable)
La thermique de la tête change radicalement. L'imprimante doit réapprendre à chauffer.
1.  Menu Qidi > Configuration > **PID Calibration**.
2.  Sélectionnez la buse et lancez le cycle. Sauvegardez les valeurs.

### Étape 3 : Recalibration Z-Offset
La géométrie de la nouvelle buse peut varier de quelques dixièmes de millimètre.
1.  Lancez un **Auto-Leveling** complet du plateau.
2.  Réglez le **Z-Offset** avec une feuille de papier. **Attention** : Si la buse tungstène crashe dans le plateau, elle ne s'usera pas, c'est le plateau PEI qui sera détruit.

## 3. Paramètres d'Impression (Différences)
Avec cette buse, vous pouvez **baisser** légèrement vos températures par rapport à l'acier trempé.

| Paramètre | Buse Acier Trempé (Standard) | Buse Carbure Tungstène (Upgrade) |
| :--- | :--- | :--- |
| **Temp. PA12-CF** | 290°C - 300°C | **280°C - 290°C** (Meilleure conductivité) |
| **Temp. PETG-CF** | 260°C | **250°C - 255°C** |
| **Risque Bouchage** | Moyen | Très Faible |

## 4. Maintenance
*   **Nettoyage** : Le plastique n'adhère pas au tungstène. Un coup de brosse laiton à chaud suffit.
*   **Durée de vie** : Virtuellement infinie pour ce projet. Elle survivra à l'imprimante.

> **Conseil D-Bot** : Installez-la **AVANT** de lancer la production massive des pièces critiques (Hanches RS-04, Fémurs) pour garantir une extrusion constante sur 40h+ d'impression.

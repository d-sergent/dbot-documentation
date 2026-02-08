# Guide Technique : Installation & Optimisation Buse Carbure de Tungstène

Ce document détaille l'installation de la buse haute performance en **Carbure de Tungstène**, recommandée pour les filaments chargés carbone (PETG-CF, PA12-CF) du projet D-Bot.

## 1. Pourquoi cette Upgrade ?
*   **Résistance Extrême** : Inusable face à l'abrasion du carbone (contrairement au laiton qui se creuse en quelques heures et à l'acier trempé qui s'use lentement).
*   **Conductivité Thermique** : Proche du cuivre. Permet de chauffer aussi vite et stablement que le laiton, contrairement à l'acier trempé qui isole et demande de surchauffer (+10°C).
*   **Fluidité** : Réduit drastiquement les risques de bouchage (clogs).

## 2. Procédure de Remplacement (Critique)
Le carbure de tungstène est ultra-dur mais **cassant** aux chocs. De plus, le bloc de chauffe est fragile.

### Matériel Requis
*   Clé plate fournie.
*   **Pince multiprise** (Indispensable pour le contre-appui).
*   Gants thermiques.

### Étape 1 : Démontage Sécurisé
1.  **Chauffe** : Montez la température à **250°C**. (À froid, le plastique colle et vous casserez le heatbreak).
2.  **Videz l'extrudeur** (Unload).
3.  **Contre-Appui (Règle d'Or)** : Maintenez **fermement** le bloc de chauffe carré avec la pince. Il ne doit **jamais** tourner sur lui-même pendant le dévissage.
4.  Dévissez la buse d'origine.

### Étape 2 : Montage et Serrage à Chaud
1.  **Nettoyage** : Vérifiez que le filetage est propre.
2.  **Vissage** : Vissez la buse Tungstène à la main (avec gant) pour sentir le filetage. Ne forcez pas si ça résiste.
3.  **Serrage Final** : Toujours à **250°C** et avec la pince en contre-appui, serrez fermement (1.5 - 2.0 Nm).
    *   *Contrôle Visuel* : Il doit rester un espace de **0.5mm à 1mm** entre la tête de la buse et le bloc. Si elle touche le bloc, elle ne scelle pas le heatbreak -> Fuite garantie.

## 3. Calibration Machine (Obligatoire)
La thermique de la tête change radicalement. L'imprimante doit réapprendre.

1.  **PID Calibration** : Menu Qidi > Configuration > PID Tuning. (Stabilisation thermique).
2.  **Auto-Leveling** : La nouvelle buse peut être plus longue de quelques microns. Refaites le niveau.
3.  **Z-Offset** : Vérifiez la première couche. Ajustez si nécessaire.

## 4. Paramètres Slicer (QIDI Print / Orca)
Il n'y a pas de case "Tungstène". Modifiez vos profils existants :

| Paramètre | Ajustement vs Acier Trempé | Pourquoi ? |
| :--- | :--- | :--- |
| **Température** | **-5°C à -10°C** | Le tungstène conduit mieux la chaleur. |
| **Flow Ratio (Débit)** | **-1% à -2%** | Ça glisse mieux ! Surveillez la sur-extrusion. |
| **Volumetric Speed** | **+2 à +3 mm³/s** | Permet d'imprimer plus vite sans sous-extrusion. |

**Exemple PA12-CF** : Passez de 300°C à **290°C**.

## 5. Maintenance
*   **Nettoyage** : Le plastique n'adhère pas au tungstène. Un coup de brosse laiton à chaud suffit.
*   **Durée de vie** : Virtuellement infinie pour ce projet.

> **Conseil D-Bot** : Installez-la **AVANT** de lancer la production massive des pièces critiques (Hanches RS-04, Fémurs) pour garantir une extrusion constante sur 40h+ d'impression.

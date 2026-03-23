# 15h — Alternatives de Transmission (Genou)

> **Série Biomécanique :**
> - [15a] [Locomotion Baseline](./15a_Analyse_Locomotion_Baseline.md)
> - [15b] [Configurations Moteurs & Évolutions](./15b_Configurations_Moteurs.md)
> - [15c] [Révision Configuration Cardan 39 kg](./15c_Revision_Cardan_39kg.md)
> - [15d] [Genou & Course — Solutions](./15d_Genou_et_Course.md)
> - [15e] [Alternatives Moteurs Genou](./15e_Alternatives_Moteurs_Genou.md)
> - [15f] [Portage de Charges & Marche](./15f_Portage_Charges_et_Marche.md)
> - [15g] [Solution S6 : Courroie GT3](./15g_Solution_S6_Courroie_GT3_Genou.md)
> - [15h] **Alternatives Transmission** ← *vous êtes ici*
> - [16] [**Conclusions & Architecture Finale D-Bot**](./16_Conclusions_Architecture_DBot.md)

Ce document archive les analyses et les débats architecturaux concernant la transmission de puissance entre le moteur **RS-04** et l'axe du genou.
Bien que la configuration retenue pour la **Phase V1** soit la [Courroie GT3 (Ratio 2.5:1)](./15g_Solution_S6_Courroie_GT3_Genou.md), plusieurs autres technologies (vérins, chaînes, mécanismes à géométrie variable) ont été sérieusement étudiées.

---

## 1. Vérin Linéaire vs Courroie GT3 (Le Débat Optimus)

Le Tesla Optimus utilise des vérins linéaires haute performance basés sur des **Vis à rouleaux planétaires (Inverted Roller Screw)**. Cette approche a été étudiée pour le D-Bot.

| Critère | Courroie GT3 (RS-04 x2.5) | Vérin Linéaire (Thomson/Firgelli) | Gagnant |
| :--- | :--- | :--- | :---: |
| **Couple Genou** | 300 N.m (120 × 2.5) | 400-600 N.m (5000N × bras levier 1.8) | Vérin |
| **Masse Ajoutée** | +250 g (Courroie + Pignons Alu) | +1.2 à 2.0 kg (Vérin + Linkage) | Courroie |
| **Coût (DIY)** | ~50 € | 800 à 1500 € (Modèles qualité type Thomson HD) | Courroie |
| **Backdrivability**| Excellente (Idéal pour l'impédance) | Quasi-nulle (Frottement autobloquant) | Courroie |
| **Self-Locking** | NON (Le moteur chauffe en statique) | OUI (Zéro électricité à l'arrêt) | Vérin |
| **Vitesse Angulaire**| 60-80°/s (Course possible) | 40-60°/s (Vis trop lente pour course explosive) | Courroie |

> [!CONCLUSION]
> **Décision :** La **Courroie GT3** est largement supérieure pour le D-Bot V1. Le vérin linéaire coûte 20 fois plus cher, ajoute un poids critique (+1.5kg) qui détruit l'inertie de la jambe, et complique la backdrivability indispensable à la marche dynamique (sauf à intégrer de très onéreux capteurs de force F/T). Le vérin linéaire reste une option théorique de "Phase 2" uniquement si le robot a un rôle purement statique ou de portage ultra-lourd continu.

---

## 2. Chaîne à Rouleaux vs Courroie GT3

L'utilisation de petites chaînes à rouleaux (type industriel 08B ou 06B) a été envisagée pour garantir l'indestructibilité de la transmission face aux chocs de la marche.

*   **Avanta de la Chaîne** : Capacité de charge démesurée (>400 N.m).
*   **Les Failles Inacceptables** :
    *   **Bruit** : 60-80 dB de cliquetis métallique, invivable pour un robot domestique ou de recherche.
    *   **Masse** : Ajoute 400 à 800 g de métal pur.
    *   **Backlash (Jeu)** : 2 à 5°, ce qui rend l'algorithme de contrôle PID très instable lors des changements de direction d'effort (pied en l'air vs pied au sol).
    *   **Entretien** : Nécessite un graissage permanent.

> [!CONCLUSION]
> **Décision :** La **Courroie GT3** (9mm ou 15mm avec renfort kevlar/acier) l'emporte haut la main. Elle est silencieuse (<40dB), nécessite zéro entretien, son backlash est négligeable (0.5 à 1.5°) et elle encaisse facilement les 300 N.m du genou avec une bonne tension. Une chaîne ne se justifierait que dans la boue ou pour un robot de plus de 80 kg.

---

## 3. "Les OVNIs" : Changement de Ratio à Géométrie Variable

Pour imiter une "boîte de vitesse" de manière mécanique (permettant au robot de choisir entre un grand débattement ou un très fort couple selon la tâche), trois concepts innovants — usinables sur la NestWorks C500 — ont été théorisés (impliquant un arrêt momentané du robot pour le "changement de rapport") :

1.  **Pivot à Géométrie Variable (Levier Motorisé)** :
    *   *Principe* : Le moteur RS-04 actionne une bielle (Push-Rod). Le point de jonction sur le tibia n'est pas fixe : il glisse sur un mini-rail linéaire actionné par un servomoteur lent (NEMA 11).
    *   *Fonctionnement* : En rapprochant le pivot du genou = Mode Vitesse (Course, faible bras de levier). En l'éloignant = Mode Force (Portage lourd, fort bras de levier).
    *   *Avantage* : Extrêmement robuste car c'est un pur calcul de levier mathématique ($T = F \times d$), usinable à l'aluminium CNC sans risque d'usure de dentures.
2.  **Boîte à Crabots (Dog-Clutch)** :
    *   *Principe* : L'arbre du moteur accueille deux courroies GT3 de longueurs différentes (ex: ratio 1:1 pour la vitesse, 3:1 pour la force). Un servomoteur déplace un "crabot" (bague cannelée) qui verrouille l'une ou l'autre poulie sur l'arbre principal.
    *   *Complexité* : Demande un ajustement parfait (H7) entre l'arbre et le crabot sur la C500.
3.  **Réducteur Modulaire à Broche** :
    *   *Principe* : Un disque multi-rayons. Un solénoïde verrouille une broche en acier trempé de gros diamètre dans un trou correspondant au ratio souhaité (Vitesse ou Force).

**Bilan de ces OVNIs** : Bien que mécaniquement brillantes et faisables avec la fraiseuse C500, ces solutions imposent d'ajouter entre 300g et 500g par genou (moteurs secondaires d'actionnement). Le gain ne compense pas (pour l'instant) l'hyper-complexité logicielle requise pour le changement d'état "en vol". Elles sont archivées ici pour un éventuel "D-Bot Heavy Duty" V3.

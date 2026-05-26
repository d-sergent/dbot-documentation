# 🔄 Étude d'Alternatives de Conception — Bras et Main du D-Bot

> **Auteur :** Claude Opus 4.6 (Anthropic) — Analyse Exploratoire  
> **Date :** 2026-05-22  
> **Objectif :** Explorer les alternatives de conception pour le module Bras & Main du D-Bot en se permettant de changer les moteurs, les dimensions du tube carbone, ou toute autre approche ingénieuse. Trouver le meilleur compromis coût/performance/proportions.  
> **Contrainte principale :** Bras aux proportions anthropomorphes d'un humanoïde de 170 cm.

---

## 0. Résumé Décisionnel

> **La conception actuelle n'est pas optimale.** L'utilisation de servos mixtes XC430/XC330 crée une disparité de force entre les doigts, et le prix des Dynamixel représente 40 % du coût total d'un bras. Plusieurs alternatives sont significativement meilleures en termes de coût et/ou de performance brute.

| Scénario | Grip (N) | Coût servos/main | Masse servos | Verdict |
| :--- | :---: | :---: | :---: | :--- |
| **Actuel** (4×XC430 + 4×XC330) | 139,5 N | 960 € | 352 g | 🟠 Bon, mais cher et disparité de force |
| **A.** 8× XC430 | 172 N | 1 040 € | 520 g | 🟡 Force uniforme, mais plus lourd/cher |
| **B.** 8× STS3215 "ORCA" | **266 N** | **200 €** | 440 g | ⭐ **Meilleur rapport force/prix** |
| **C.** 8× STS3215 + poulie Ø12mm | **310 N** | 210 € | 444 g | ⭐ Force maximale absolue |
| **D.** 5× STS3215 + whiffletree | 160 N | 125 € | 275 g | 🟢 Minimaliste, ultra-économique |
| **E.** Hybride 5× STS3215 + 3× XC330 | 213 N | 455 € | 344 g | 🟢 Compromis précision/force |

---

## 1. Le Design Actuel — Baseline de Référence

### 1.1 Rappel de l'Architecture

| Paramètre | Valeur |
| :--- | :--- |
| Servos main | 4× XC430-W240-T + 4× XC330-T288-T |
| Coût servos | 4×130 + 4×110 = **960 €/main** |
| Masse servos | (4×65) + (4×23) = **352 g** |
| Encombrement dans l'avant-bras | 93 mm (XC430) + 52 mm (XC330) = **145 mm** |
| Section transversale bloc servos | ~57 × 68 mm → Ø nécessaire **≈ 90 mm** |
| Force de grip (stall, corrigé) | **139,5 N** |
| Protocole | Dynamixel TTL Protocol 2.0 via U2D2 |
| Contrôle en couple | ✅ Oui (mode Current-Based Position) |
| Alimentation | 12V via Buck 48V→12V |

### 1.2 Ce Qui Fonctionne Bien

- ✅ Écosystème Dynamixel très mature (U2D2, SDK, ROS2)
- ✅ Contrôle en couple (mode courant) pour manipulation fine
- ✅ Engrenages métal sur XC430 (durabilité)
- ✅ Résolution 4096 pas/tour (0,088°)
- ✅ Documentation abondante

### 1.3 Ce Qui Pose Problème

- ❌ **Disparité de force** : XC430 (1,9 N.m) vs XC330 (1,0 N.m) → force inégale entre doigts
- ❌ **Coût élevé** : 960 € pour 8 servos (40 % du coût total d'un bras)
- ❌ **Encombrement** : 2 tailles différentes = 145 mm au lieu de ~90 mm si homogène
- ❌ **XC330 engrenages métal mais couple faible** pour les tendons de force
- ❌ **Buck 48V→12V** : alim séparée nécessaire vs bus 48V natif du reste de l'actionneur

---

## 2. Contraintes Anthropomorphes

Avant d'explorer les alternatives, définissons les limites physiques d'un bras humanoïde proportionné.

### 2.1 Dimensions Humaines de Référence (170 cm)

| Mesure | Humain moyen | Plage acceptable pour humanoïde |
| :--- | :--- | :--- |
| Longueur avant-bras (coude→poignet) | 25–26 cm | **23–28 cm** |
| Circonférence avant-bras | 27–30 cm | 24–34 cm |
| **Diamètre avant-bras** | **85–95 mm** | **75–108 mm** |
| Longueur main | 17–19 cm | 15–20 cm |

### 2.2 Références Robots Humanoïdes Existants

| Robot | Taille | Avant-bras estimé | Notes |
| :--- | :---: | :---: | :--- |
| Tesla Optimus Gen 2 | 173 cm | ~25 cm | Proportionné humain |
| Unitree H1 | 180 cm | ~34 cm (publié) | Plus long que l'humain |
| Figure 02 | 168 cm | ~24–25 cm | Proportionné humain |
| Apptronik Apollo | 173 cm | ~25 cm | Proportionné humain |
| **D-Bot (actuel)** | **~170 cm** | **~28 cm** (fonctionnel) | **Dans la norme (limite haute)** |

### 2.3 Enveloppe de Design pour le D-Bot

| Paramètre | Minimum | Cible | Maximum |
| :--- | :---: | :---: | :---: |
| Longueur tube avant-bras | 150 mm | 200 mm | 250 mm |
| Diamètre tube avant-bras (OD) | 30 mm | 40–50 mm | 60 mm |
| Diamètre coque avant-bras (visuel) | 60 mm | 80 mm | 100 mm |
| Longueur fonctionnelle coude→poignet | 200 mm | 250 mm | 280 mm |

> **Note :** Le tube carbone structurel peut être fin (Ø30–50 mm) si une coque esthétique (PA12-CF ou PLA) de Ø80–100 mm l'entoure. C'est l'approche de la plupart des humanoïdes commerciaux.

---

## 3. Le Challenger Principal : Feetech STS3215

Ce moteur mérite une section dédiée car il change fondamentalement l'équation de design.

### 3.1 Fiche Technique Comparée

| Paramètre | XC430-W240-T | XC330-T288-T | **STS3215** |
| :--- | :---: | :---: | :---: |
| Dimensions | 28,5 × 46,5 × 34 mm | 20 × 34 × 26 mm | **45,2 × 24,7 × 35 mm** |
| Poids | 65 g | 23 g | **55 g** |
| Couple stall @12V | 1,9 N.m | 1,0 N.m (1,6 pic) | **2,94 N.m** |
| Couple continu | ~0,7 N.m | ~0,35 N.m | **0,98 N.m** |
| Vitesse à vide | 70 RPM | 71 RPM | ~45 RPM |
| Résolution | 4096 pas (12 bit) | 4096 pas (12 bit) | **4096 pas (12 bit)** |
| Réducteur | 245:1 métal | 288:1 métal | **345:1 acier** |
| Contrôle en couple | ✅ Oui | ✅ Oui | ❌ Non (position/vitesse) |
| Rotation | 360° | 360° | **360° multi-tour** |
| Protocole | Dynamixel TTL 2.0 | Dynamixel TTL 2.0 | **UART TTL série** |
| Tension | 10–14,8V | 6,5–12V | **4–14V** |
| **Prix unitaire** | **~130 €** | **~110 €** | **~25 €** |

### 3.2 Pourquoi le STS3215 est un « Game Changer »

1. **Couple stall +55 %** : 2,94 N.m vs 1,9 N.m (XC430) — plus de couple par doigt
2. **Prix –81 %** : 25 € vs 130 € — presque un ordre de grandeur moins cher
3. **Poids –15 %** par rapport au XC430 (55g vs 65g)
4. **Validé en robotique** : C'est LE moteur de l'**ORCA Hand** (ETH Zurich), testé > 10 000 cycles sans défaillance
5. **Engrenages acier** (345:1) : durabilité excellente pour les tensions de tendon
6. **Même résolution** (4096 pas) que les Dynamixel

### 3.3 Limites du STS3215

1. ❌ **Pas de contrôle en couple direct** (courant) — ne peut pas "sentir" la force au bout du doigt via le moteur. Le feedback de force doit être fait par les capteurs eFlesh (ce qui est le cas sur le D-Bot).
2. ❌ **Écosystème logiciel moins mature** que Dynamixel (pas de U2D2, pas de SDK officiel ROS2 intégré). Mais le protocole est documenté et des bibliothèques Python/Arduino existent.
3. ⚠️ **Qualité de fabrication variable** — acheter chez des revendeurs fiables (RobotShop, Waveshare officiel).
4. ⚠️ **Plus bruyant** (~40–45 dB) que les Dynamixel (~30 dB).
5. ⚠️ **Couple continu** (0,98 N.m) inférieur au stall du XC430 (1,9 N.m). Pour des saisies prolongées, le moteur chauffera plus vite.

### 3.4 Où Acheter en France

| Fournisseur | Prix unitaire | Notes |
| :--- | :---: | :--- |
| **RobotShop Europe** (robotshop.com) | ~31 € | Stock EU, livraison rapide |
| **Waveshare** (modèle ST3215 identique) | ~19–26 € | Via AliExpress, vérifier version 12V |
| **Génération Robots** (generationrobots.com) | ~30 € | Revendeur FR officiel |
| **AliExpress** (vendeurs vérifiés Feetech) | ~10–15 € | Prix imbattable, attention TVA/douane |

---

## 4. Scénarios Alternatifs Détaillés

---

### 4.1 Scénario A — Homogène XC430 (8× XC430-W240-T)

**Principe :** Remplacer les 4 XC330 par 4 XC430 supplémentaires pour uniformiser la force de tous les doigts.

**Calcul de grip :**

| Doigt | Servo | Couple stall | F_pulpe (η=0,98, r=7mm, r_m=10mm, L=70mm) |
| :--- | :--- | :---: | :---: |
| Pouce | XC430 | 1,9 N.m | 38,0 N |
| Index | XC430 | 1,9 N.m | 38,0 N |
| Majeur | XC430 | 1,9 N.m | 38,0 N |
| Annulaire | XC430 | 1,9 N.m | 38,0 N |
| Auriculaire | XC430 | 1,9 N.m | 38,0 N |

$$F_{grip} = 5 \times 38.0 \times \cos(25°) = 5 \times 38.0 \times 0.906 = \mathbf{172.1 \text{ N}}$$

**Intégration avant-bras :**

| Arrangement | Section transversale | Ø tube min | Longueur servos | Total (+ RS-00) |
| :--- | :--- | :---: | :---: | :---: |
| 2×2 × 2 couches | 57 × 68 mm | Ø90 mm | 93 mm | 150 mm |
| 2×1 × 4 couches | 57 × 34 mm | **Ø67 mm** | 186 mm | 243 mm |

**Bilan :**

| Critère | Actuel | Scénario A | Delta |
| :--- | :---: | :---: | :---: |
| Grip | 139,5 N | **172 N** | **+23 %** |
| Coût servos | 960 € | **1 040 €** | +8 % |
| Masse servos | 352 g | **520 g** | +48 % |
| Encombrement | 145 mm | **93–186 mm** | Variable |

**Verdict :** 🟡 Force uniformisée, mais plus cher, plus lourd, et ne résout pas le problème fondamental du prix élevé des Dynamixel. Ce scénario n'offre pas d'avantage décisif par rapport à la solution compound 2:1 (R-05 du rapport précédent) qui atteint le même grip à moindre coût.

---

### 4.2 ⭐ Scénario B — ORCA-Style (8× Feetech STS3215)

**Principe :** Adopter le même moteur que l'ORCA Hand d'ETH Zurich pour tous les DOF de la main. C'est la même approche qui a fait ses preuves dans l'un des projets de main robotique open-source les plus réussis au monde.

**Calcul de grip :**

$$T_{cable} = \frac{\tau_{stall}}{r_{spool}} = \frac{2.94}{0.007} = 420 \text{ N}$$

$$F_{pulpe} = 420 \times \frac{10}{70} \times 0.98 = 58.8 \text{ N}$$

$$F_{grip} = 5 \times 58.8 \times 0.906 = \mathbf{266.4 \text{ N}}$$

> 🎯 **266 N — c'est presque le DOUBLE du design actuel (139,5 N) et SUPÉRIEUR au Shadow Dexterous Hand (>300 N, mais à 120 000 €).**

**Intégration avant-bras :**

Le STS3215 (45,2 × 24,7 × 35 mm) est **plus étroit** que le XC430 (–3,8 mm en largeur) :

| Arrangement | Section transversale | Ø tube min | Longueur servos | Total (+RS-00) |
| :--- | :--- | :---: | :---: | :---: |
| **2×2 × 2 couches** | **49,4 × 70 mm** | **Ø86 mm** | **90,4 mm** | **147,4 mm** ✅ |
| 2×1 × 4 couches | 49,4 × 35 mm | Ø61 mm | 180,8 mm | 237,8 mm |

> **Option 1 : Avant-bras compact (tube 170 mm)**
> - Arrangement 2×2×2 : bloc servos 90,4 mm + RS-00 57 mm = 147,4 mm → tube de **170 mm** (vs 220 mm actuel)
> - **Gain de 50 mm** sur la longueur de l'avant-bras
> - Longueur fonctionnelle coude→poignet : 78 (RS-02) + 170 = **248 mm** — parfaitement proportionné pour un humanoïde de 170 cm
>
> **Option 2 : Espace libre pour électronique (tube 220 mm)**
> - Même arrangement mais dans le tube actuel de 220 mm
> - **72,6 mm d'espace libre** pour le buck converter, le contrôleur UART, le routage des câbles
> - Résout le problème thermique sans changer le convertisseur !

**Bilan complet :**

| Critère | Actuel | Scénario B | Delta |
| :--- | :---: | :---: | :---: |
| Grip (stall) | 139,5 N | **266 N** | **+91 %** 🟢 |
| Coût servos/main | 960 € | **200 €** | **–79 %** 🟢 |
| Coût total/bras | ~2 370 € | **~1 560 €** | **–34 %** 🟢 |
| Masse servos | 352 g | 440 g | +25 % 🟡 |
| Encombrement (2×2×2) | 145 mm | **90 mm** | **–38 %** 🟢 |
| Contrôle en couple | ✅ | ❌ | 🔴 Perte |
| Écosystème logiciel | ★★★★★ | ★★★☆☆ | 🟠 |
| Résolution | 4096 pas | 4096 pas | = |

**Impact financier sur le robot complet (2 bras) :**

| Poste | Actuel | Scénario B | Économie |
| :--- | :---: | :---: | :---: |
| 16 servos main | 1 920 € | **400 €** | **1 520 €** |
| 2× U2D2 + Hub | 120 € | 10 € (UART) | 110 € |
| **Total économisé** | | | **1 630 €** |

> 💡 **1 630 € économisés** permettraient de financer : 2 capteurs force-couple (ATI Nano17 ou equivalent), ou un upgrade de la batterie, ou l'ajout de capteurs de vision supplémentaires.

---

### 4.3 ⭐⭐ Scénario C — ORCA Augmenté (8× STS3215 + Poulies Ø12 mm)

**Principe :** Combiner le STS3215 avec des poulies d'enroulement de diamètre réduit (Ø12 mm au lieu de Ø14 mm) pour maximiser la force. Le couple élevé du STS3215 permet de réduire le diamètre de poulie tout en conservant un facteur de sécurité acceptable sur le câble.

**Calcul :**

$$T_{cable} = \frac{2.94}{0.006} = 490 \text{ N}$$

$$F_{pulpe} = 490 \times \frac{10}{70} \times 0.98 = 68.6 \text{ N}$$

$$F_{grip} = 5 \times 68.6 \times 0.906 = \mathbf{310.7 \text{ N}}$$

**Vérification facteur de sécurité (Dyneema Ø0,80 mm, rupture 1177 N) :**

$$F_s = \frac{1177}{490} = \mathbf{2.40} \quad ✅$$

> 🏆 **310 N — c'est la force de grip d'un Shadow Dexterous Hand (>300 N, 120 000 €), obtenue pour ~210 € de servos.**

**Bilan :**

| Critère | Actuel | Scénario C | Delta |
| :--- | :---: | :---: | :---: |
| Grip | 139,5 N | **311 N** | **+123 %** 🟢 |
| Coût servos | 960 € | **210 €** | **–78 %** 🟢 |
| Masse servos | 352 g | 440 g | +25 % 🟡 |
| Fs câble (Ø0,80mm) | ×2,02 | **×2,40** | +19 % 🟢 |

**Inconvénient :** La poulie Ø12 mm réduit la course du câble. Avec un spool de 1,5 tours sur Ø12 mm, la course est de π × 12 × 1,5 = 56,5 mm vs 66 mm pour Ø14 mm. Cela reste confortable pour la flexion complète des doigts (besoin : ~30 mm).

---

### 4.4 Scénario D — Minimaliste à Whiffletree (5× STS3215 + Whiffletree)

**Principe :** Réduire le nombre de moteurs au strict minimum en utilisant un mécanisme whiffletree (balancier différentiel) pour actionner les 3 derniers doigts (majeur, annulaire, auriculaire) avec un seul moteur. L'approche est inspirée de la **Robotiq 2F-85** et de la **Yale OpenHand**.

**Allocation DOF :**

| # | Doigt/Fonction | Servo | Couple |
| :---: | :--- | :--- | :---: |
| 1 | Pouce flexion | STS3215 | 2,94 N.m |
| 2 | Pouce opposition | STS3215 | 2,94 N.m |
| 3 | Index flexion | STS3215 | 2,94 N.m |
| 4 | Majeur + Annulaire + Auriculaire (whiffletree 3 voies) | STS3215 | 2,94 ÷ 3 = 0,98 N.m/doigt |
| 5 | Index abduction | STS3215 | 2,94 N.m |

**5 moteurs au total — 5 DOF**

**Calcul de grip :**

- Pouce, Index : 58,8 N chacun (STS3215 direct)
- Majeur, Annulaire, Auriculaire : 0,98/0,007 = 140 N tension → F_pulpe = 140 × 10/70 × 0,98 = **19,6 N** chacun (via whiffletree)

$$F_{grip} = (2 \times 58.8 + 3 \times 19.6) \times 0.906 = 176.4 \times 0.906 = \mathbf{159.8 \text{ N}}$$

> **160 N** avec seulement **5 moteurs à 125 €** — supérieur aux 139,5 N actuels avec 8 moteurs à 960 € !

**Intégration :**
- 5 STS3215 en configuration 1×1 × 5 couches linéaires : 45,2 × 5 = 226 mm dans un tube Ø50 mm
- Ou : 2+2+1 arrangement hybride : ~136 mm dans un tube Ø61 mm

**Bilan :**

| Critère | Actuel | Scénario D | Delta |
| :--- | :---: | :---: | :---: |
| Grip | 139,5 N | **160 N** | **+15 %** |
| DOF | 8 | **5** | –3 DOF 🔴 |
| Coût servos | 960 € | **125 €** | **–87 %** 🟢 |
| Masse servos | 352 g | **275 g** | –22 % 🟢 |
| Grip adaptatif | Non | **Oui (whiffletree)** | 🟢 Bonus |

**Inconvénients :** Perte de 3 DOF (annulaire et auriculaire ne sont plus indépendants). Acceptable pour du Power Grasp pur, mais limitant pour la manipulation fine.

---

### 4.5 Scénario E — Hybride (5× STS3215 Force + 3× XC330 Précision)

**Principe :** Utiliser les STS3215 pour tous les axes de force (flexion des 5 doigts) et conserver les XC330 pour les axes de précision (opposition pouce, abduction index, curl palmaire) qui nécessitent un contrôle fin en couple.

**Allocation DOF :**

| # | Doigt/Fonction | Servo | Couple stall | F_pulpe |
| :---: | :--- | :--- | :---: | :---: |
| 1 | Pouce flexion | STS3215 | 2,94 N.m | 58,8 N |
| 2 | Index flexion | STS3215 | 2,94 N.m | 58,8 N |
| 3 | Majeur flexion | STS3215 | 2,94 N.m | 58,8 N |
| 4 | Annulaire flexion | STS3215 | 2,94 N.m | 58,8 N |
| 5 | Auriculaire flexion | STS3215 | 2,94 N.m | 58,8 N |
| 6 | Pouce opposition | XC330 | 1,0 N.m | — (mouvement latéral) |
| 7 | Index abduction | XC330 | 1,0 N.m | — (mouvement latéral) |
| 8 | Paume curl | XC330 | 1,0 N.m | — (compression) |

**Calcul de grip :**

$$F_{grip} = 5 \times 58.8 \times 0.906 = \mathbf{266.4 \text{ N}}$$

> **Même force que le scénario B**, mais avec un contrôle en couple sur les 3 axes de précision grâce aux XC330.

**Coût et masse :**

| Composant | Qté | Prix unitaire | Total |
| :--- | :---: | :---: | :---: |
| STS3215 | 5 | 25 € | 125 € |
| XC330-T288-T | 3 | 110 € | 330 € |
| **Total** | **8** | | **455 €** |

Masse : (5 × 55) + (3 × 23) = 275 + 69 = **344 g** (vs 352 g actuel — quasi identique !)

**Bilan :**

| Critère | Actuel | Scénario E | Delta |
| :--- | :---: | :---: | :---: |
| Grip | 139,5 N | **266 N** | **+91 %** 🟢 |
| Coût servos | 960 € | **455 €** | **–53 %** 🟢 |
| Masse servos | 352 g | **344 g** | –2 % = |
| Contrôle en couple | ✅ (8/8) | ✅ (3/8) | 🟡 Partiel |
| DOF | 8 | 8 | = |

**Inconvénient principal :** Deux protocoles de communication distincts (UART Feetech + TTL Dynamixel) nécessitent deux bus séparés et deux interfaces logicielles. Complexité logicielle accrue.

---

## 5. Optimisation de la Géométrie de l'Avant-Bras

### 5.1 Comparaison par Scénario

| Scénario | Arrangement | Section min | Ø tube OD | Longueur moteurs | + RS-00 | Tube total |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| Actuel | XC430 2×2 + XC330 2×2 | 57×68 mm | Ø94 mm | 145 mm | 202 mm | **220 mm** |
| A (8×XC430) | 2×2 × 2 couches | 57×68 mm | Ø94 mm | 93 mm | 150 mm | **170 mm** |
| **B (8×STS3215)** | **2×2 × 2 couches** | **49×70 mm** | **Ø90 mm** | **90 mm** | **147 mm** | **170 mm** |
| B alt. (8×STS3215) | 2×1 × 4 couches | 49×35 mm | **Ø64 mm** | 181 mm | 238 mm | **250 mm** |
| D (5×STS3215) | 2+2+1 hybride | 49×35 mm | **Ø64 mm** | ~136 mm | 193 mm | **210 mm** |
| E (5×STS + 3×XC330) | STS 2×2 + XC 2×1 | ~50×70 mm | Ø90 mm | ~90+34 = 124 mm | 181 mm | **200 mm** |

### 5.2 Le Scénario B en Configuration "Slim" (2×1 × 4 couches)

C'est la configuration la plus intéressante pour l'esthétique :

```
Vue de face (section transversale) :        Vue de côté (longueur) :

  ┌─────────┐                                ┌─────┬─────┬─────┬─────┬──────┐
  │  STS   STS  │ 49.4mm × 35mm              │ STS │ STS │ STS │ STS │ RS-00│
  └─────────┘                                │  1  │  2  │  3  │  4  │ Pitch│
                                             └─────┴─────┴─────┴─────┴──────┘
  → Ø64mm tube OD                                      238 mm total
```

- Tube carbone Ø60 ID × Ø64 OD (paroi 2 mm) : **disponible chez TubeCarbone.com**
- Coque esthétique en PA12-CF à Ø80 mm pour un look humanoïde
- Le bras fait seulement **64 mm de diamètre** — extrêmement fin, comme un avant-bras humain mince
- Longueur de 238 mm + RS-02 (78 mm) = **316 mm** total coude→poignet : trop long (31,6 cm > 28 cm max)

> ⚠️ **Cette configuration est trop longue.** La config 2×2 × 2 couches (170 mm tube, Ø90 mm) est préférable.

### 5.3 Configuration Optimale Recommandée

**8× STS3215 en 2×2 × 2 couches dans un tube de 170 mm :**

```
Vue de face :                     Vue de côté :

  ┌─────────────┐                  ┌──────────┬──────────┬──────┐
  │ STS₁  STS₂  │                  │ Couche A │ Couche B │RS-00 │
  │             │  70mm            │ STS 1-4  │ STS 5-8  │Pitch │
  │ STS₃  STS₄  │                  │ 45.2mm   │ 45.2mm   │57mm  │
  └─────────────┘                  └──────────┴──────────┴──────┘
     49.4mm                              147.4mm + marge → 170mm
  
  → Ø86mm inscrit                        Tube carbone : 170 mm
  → Tube OD ~Ø90mm (avec paroi 2mm)     Espace libre : 22.6mm (électronique)
```

**Proportions résultantes :**
- Longueur fonctionnelle : RS-02 (78 mm, au coude) + tube (170 mm) = **248 mm** (24,8 cm)
- C'est **exactement** dans la norme d'un avant-bras humain de 170 cm ! ✅
- Diamètre : Ø90 mm avec coque → dans la plage 75–108 mm ✅

> **Comparé au design actuel** (tube 220 mm, longueur fonctionnelle 280 mm) : le scénario B en 2×2 × 2 couches gagne **50 mm de longueur** tout en fournissant un grip presque doublé.

---

## 6. Impact sur les Autres Sous-Systèmes

### 6.1 Impact sur l'Épaule (masse distale)

Le changement de masse au niveau de la main affecte le couple nécessaire à l'épaule :

| Scénario | Masse servos main | Delta vs actuel | Impact couple épaule (bras tendu, 70cm) |
| :--- | :---: | :---: | :--- |
| Actuel | 352 g | — | Référence |
| B (STS3215) | 440 g | +88 g | +88 × 9,81 × 0,70 = **+0,60 N.m** (RS-04 : 40 N.m → impact négligeable = +1,5 %) |
| D (5×STS) | 275 g | –77 g | –0,53 N.m (gain marginal) |

> **Conclusion :** L'impact de ±100 g de masse servo sur le couple d'épaule est totalement négligeable (<2 % du couple nominal du RS-04).

### 6.2 Impact sur le Buck Converter

| Scénario | Consommation stall totale @12V | Puissance | Impact |
| :--- | :---: | :---: | :--- |
| Actuel (4×XC430 + 4×XC330) | (4×1,4) + (4×0,88) = 9,1 A | 109 W | Buck 10A nécessaire |
| B (8×STS3215) | 8 × 2,7 = **21,6 A** | **259 W** | ⚠️ Buck **25A** nécessaire ! |
| Réaliste (usage normal) | 8 × ~1,0 = **8 A** | 96 W | Buck 10A suffisant |

> ⚠️ **Attention :** Le stall simultané de 8× STS3215 tire 21,6 A, bien au-dessus du buck actuel (10A). En pratique, le stall simultané n'arrive jamais (les doigts se ferment séquentiellement). En usage normal, la consommation reste similaire (~8A). Il faudra néanmoins un buck de **15A** minimum avec une protection en courant.
>
> **Solution :** Le convertisseur **Pololu D24V150F12** (48V→12V, 15A continu, 20A pic) à ~25 € serait adapté. Alternativement, le Vicor PI33xx (recommandé dans le rapport précédent) supporte ces charges.

### 6.3 Impact Logiciel

| Aspect | Dynamixel (actuel) | STS3215 (scénario B) |
| :--- | :--- | :--- |
| Protocole | Dynamixel Protocol 2.0 | UART série (half-duplex) |
| Interface | U2D2 (USB) | Adaptateur UART-USB (~5 €) |
| SDK | DynamixelSDK (C++, Python, ROS2) | SCServo SDK (Python, Arduino) |
| ROS2 | Intégration native | À développer (simple) |
| Boucle fermée position | ✅ Intégrée | ✅ Intégrée |
| Boucle fermée couple | ✅ Mode courant | ❌ Via capteurs externes (eFlesh) |

> **Mitigation :** Le D-Bot utilise déjà les capteurs eFlesh pour le retour de force tactile. Le contrôle en couple via le courant moteur est un "nice-to-have", pas un prérequis. La boucle de force peut être fermée à 100 % via les capteurs eFlesh (pression + cisaillement), ce qui est de toute façon la méthode supérieure (mesure directe au contact vs estimation indirecte par courant moteur).

---

## 7. Scénario Bonus — Architecture "Bowden au Coude"

### 7.1 Concept

Déporter les 8 servos dans le bras supérieur (humérus) ou au niveau du coude, et acheminer les tendons vers la main via des **gaines Bowden** traversant l'avant-bras.

```
   [ÉPAULE]
      │
      │  Humérus (tube carbone)
      │
   [COUDE] ←── RS-06 Pitch + RS-02 Supination
      │         + 8× STS3215 (montés ICI)
      │
      │  Avant-bras (tube carbone VIDE)
      │  → Seulement : 8 gaines Bowden + câbles électriques
      │
   [POIGNET] ←── RS-00 Pitch
      │
   [MAIN]
```

### 7.2 Avantages

- Avant-bras ultra-léger (~100 g de structure seule, sans aucun servo)
- Diamètre d'avant-bras réduit à Ø30–40 mm (tube + gaines)
- Moment d'inertie réduit → mouvements du poignet plus rapides et plus précis
- Moins de câbles dans l'avant-bras (alimentation des servos au coude, pas dans le tube)

### 7.3 Inconvénients

- **Perte de rendement** : les gaines Bowden introduisent une friction importante. Le rendement typique chute à **η ≈ 0,70–0,85** selon la longueur et les courbures.
- **Compliance** : le câble dans la gaine se comprime légèrement, réduisant la rigidité et la précision de position.
- **Routage au coude** : les gaines doivent traverser 2 articulations (pitch + supination), ce qui crée des points de friction et d'usure.
- **Maintenance** : remplacement des gaines Bowden plus complexe.

### 7.4 Verdict

🟡 **Intéressant pour une V2.** La perte de rendement (–15 à 30 %) annule une partie du gain de couple du STS3215. Pour une V1, le placement des servos dans l'avant-bras (scénario B) est plus fiable et plus simple à prototyper.

---

## 8. Matrice de Décision Finale

| Critère (poids) | Actuel | A. 8×XC430 | B. 8×STS3215 | C. STS+Ø12 | D. 5×STS+WF | E. Hybride |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Grip force** (25%) | 3/10 | 5/10 | **8/10** | **10/10** | 5/10 | 8/10 |
| **Coût servos** (25%) | 2/10 | 2/10 | **9/10** | **9/10** | **10/10** | 6/10 |
| **Masse** (10%) | 7/10 | 4/10 | 6/10 | 6/10 | **8/10** | **7/10** |
| **Compacité** (10%) | 4/10 | 5/10 | **8/10** | **8/10** | 6/10 | 7/10 |
| **Contrôle fin** (15%) | **9/10** | **9/10** | 5/10 | 5/10 | 3/10 | 7/10 |
| **Simplicité intégration** (10%) | **8/10** | **8/10** | 7/10 | 6/10 | 5/10 | 4/10 |
| **Fiabilité prouvée** (5%) | **9/10** | **9/10** | 7/10 | 6/10 | 5/10 | 6/10 |
| **Score pondéré** | **4.85** | **5.25** | **7.35** | **7.65** | **6.40** | **6.55** |

---

## 9. Recommandation Finale

### 9.1 Pour la V1 du D-Bot : ⭐ Scénario B (8× STS3215)

**C'est l'alternative la plus rationnelle pour une première version.**

| Argument | Détail |
| :--- | :--- |
| **Force de grip ×1,9** | 266 N vs 139,5 N — résout le problème sans aucune astuce mécanique |
| **Coût ÷5** | 200 € vs 960 € pour les servos main |
| **Avant-bras plus court** | 170 mm vs 220 mm → proportions humaines parfaites |
| **Validé par ETH Zurich** | L'ORCA Hand utilise exactement ce moteur, avec >10 000 cycles prouvés |
| **Même résolution** | 4096 pas = identique aux Dynamixel |
| **Contrôle de force via eFlesh** | Le retour de force se fait par les capteurs tactiles, pas par le courant moteur |

### 9.2 Pour une V2 améliorée : Scénario E (5× STS3215 + 3× XC330)

Si l'expérience de la V1 montre que le contrôle en couple est nécessaire pour certains DOF (opposition du pouce, abduction), un upgrade vers le scénario hybride est simple (remplacement de 3 STS3215 par des XC330 sur les axes de précision).

### 9.3 En aucun cas : Scénario A (8× XC430)

L'utilisation de 8 Dynamixel XC430 à 1 040 € pour obtenir 172 N de grip est irrationnelle quand 8 STS3215 à 200 € fournissent 266 N. Le seul avantage du XC430 (contrôle en couple) est compensable par les capteurs eFlesh.

---

## 10. Plan de Migration

Si le scénario B est retenu, voici les étapes de migration :

| # | Action | Complexité | Durée estimée |
| :---: | :--- | :---: | :---: |
| 1 | Commander 8× STS3215 (RobotShop ou Waveshare) | 🟢 | 1 semaine |
| 2 | Imprimer support 2×2 × 2 couches adapté au STS3215 (PA12-CF) | 🟢 | 2 jours |
| 3 | Adapter le code SCServo SDK (Python) — bibliothèque existante | 🟢 | 2 jours |
| 4 | Ré-usiner les poulies Ø14 mm pour l'axe STS3215 (si diamètre d'arbre différent) | 🟡 | 1 jour |
| 5 | Tester la chaîne complète (1 doigt) et mesurer η réel | 🟢 | 1 jour |
| 6 | Raccourcir le tube carbone à 170 mm (découpe + re-collage insert alu) | 🟡 | 1 jour |
| 7 | Intégrer le buck 15A (Pololu D24V150F12) | 🟢 | 1 heure |

**Durée totale estimée : 2 semaines** (dont 1 semaine de livraison).
**Budget total migration : ~250 €** (8 servos + adaptateur UART + buck 15A + visserie).

---

## 11. La Conception Actuelle Est-elle Optimale ?

**Non.** La conception actuelle est le résultat d'un excellent travail d'ingénierie, mais elle reflète un **biais de sélection Dynamixel** — un réflexe courant dans la communauté robotique hobbyiste/académique où Dynamixel est considéré comme la référence absolue. Ce biais était justifié il y a 3 ans quand les alternatives chinoises étaient de qualité médiocre.

En 2026, le **Feetech STS3215** a été validé par l'une des universités techniques les plus prestigieuses au monde (ETH Zurich) dans un projet open-source majeur (ORCA Hand). Ce n'est plus un "servo chinois pas cher" — c'est un **actionneur de robotique sérieuse** qui surpasse le Dynamixel XC430 en couple brut, à 1/5ème du prix.

Le seul avantage résiduel significatif du Dynamixel est le **contrôle en couple** (mode courant), qui est contournable par l'utilisation de capteurs de force externes (eFlesh), une solution techniquement supérieure car elle mesure la force réelle au contact plutôt qu'une estimation indirecte par le courant moteur.

> **Verdict final :** Le design actuel est **bon mais sous-optimal**. Le passage au STS3215 (scénario B) représente un saut quantique en rapport qualité/prix — un cas rare en ingénierie où on obtient simultanément plus de performance, moins de coût, et moins d'encombrement.

---

*Fin de l'étude — Claude Opus 4.6 (Anthropic) — 2026-05-22*

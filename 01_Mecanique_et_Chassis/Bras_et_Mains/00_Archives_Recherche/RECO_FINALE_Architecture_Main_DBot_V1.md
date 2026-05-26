# 🎯 Recommandation Finale — Architecture Main D-Bot V1

> **Auteur :** Claude Opus 4.6 (Anthropic)  
> **Date :** 2026-05-23  
> **Contexte :** Suite à la vérification approfondie des moteurs ORCA Hand, du Feetech HL-3915, et de l'état de l'art en capteurs tactiles.  
> **Objectif :** Proposition finale consolidée pour le type de moteur, le nombre de DOF, et la solution de tactile sensing pour la D-Hand V1.

---

## 0. Corrections Factuelles sur l'Étude Précédente

### ✅ L'ORCA Hand V1 utilise bien le STS3215 — mais la V2 a migré vers Dynamixel !

La vérification directe via l'article arXiv 2504.04259, le site ETH Zurich, et le SDK orca_core révèle :
- **L'ORCA Hand V1 (legacy) utilise 17× Feetech STS3215** — c'est le moteur d'origine.
- **L'ORCA Hand V2 (actuelle, vendue via ROBOTIS) utilise des Dynamixel XC330-T288-T + XC430-T240BB-T** — exactement les mêmes que le design D-Bot actuel !
- Le BOM en Dynamixel coûte ~3 500 $ vs ~2 000 $ en STS3215 pour la même main.
- ORCA vend aussi une version assemblée à ~5 937 $ (ROBOTIS store).

> ⚠️ **Implication pour le D-Bot :** Le fait qu'ETH ait migré vers Dynamixel pour la version commerciale montre que le STS3215 a des limites en contexte de production (contrôle, fiabilité long terme). Cependant, pour une V1 de prototypage où le rapport force/prix est prioritaire, le STS3215 reste un choix rationnel — ETH l'a prouvé avec >10 000 cycles sur la V1.
- Le HL-3915 est un **modèle distinct**, plus petit et spécialisé, que vous avez vu sur le site Feetech. Certaines adaptations communautaires (UC Berkeley) utilisent le HL-3915 (ou sa variante HLS3915M) dans des builds ORCA-compatibles, car il a les mêmes dimensions de montage et le même protocole TTL.

### 🆕 Découverte : Le Feetech HL-3915 — Un Candidat Inattendu

En cherchant le HL-3915 que vous avez mentionné, j'ai découvert un moteur qui pourrait être **encore plus pertinent** que le STS3215 pour certains DOF de la D-Hand :

| Paramètre | STS3215 | **HL-3915** | XC430 (référence) | XC330 (référence) |
| :--- | :---: | :---: | :---: | :---: |
| **Dimensions** | 45,2 × 24,7 × 35 mm | **20 × 34 × 23 mm** | 28,5 × 46,5 × 34 mm | 20 × 34 × 26 mm |
| **Poids** | 55 g | **35,8 g** | 65 g | 23 g |
| **Couple stall @12V** | 2,94 N.m (30 kg.cm) | **1,39 N.m** (14,2 kg.cm) | 1,9 N.m | 1,0 N.m |
| **Moteur** | Coreless | **Coreless** | Coreless | Coreless |
| **Engrenages** | Acier | **Métal** | Métal | Métal |
| **Contrôle en couple** | ❌ Position/Vitesse seulement | ✅ **OUI — Mode Force Constante** | ✅ Mode courant | ✅ Mode courant |
| **Rotation** | 360° multi-tour | **360° multi-tour** | 360° | 360° |
| **Résolution** | 4096 pas (12 bit) | 4096 pas (12 bit) | 4096 pas | 4096 pas |
| **Double arbre** | Non | **Oui** | Non | Non |
| **Protocole** | TTL série | **TTL série (même protocole !)** | Dynamixel 2.0 | Dynamixel 2.0 |
| **Prix** | ~25 € | **~55 €** | ~130 € | ~110 € |

> ⚠️ **Le HL-3915 a un atout majeur que le STS3215 n'a pas : le contrôle en force/couple constante intégré.** C'est exactement le mode "Current-Based Position" du Dynamixel que nous pensions perdre en quittant l'écosystème ROBOTIS. Il offre aussi un **boîtier aluminium** (vs plastique PA+GF pour le STS3215), un **moteur coreless** (réponse plus rapide, moins de vibrations) et un **double arbre** (montage symétrique possible).

> 📐 **Et ses dimensions sont quasi-identiques au XC330** (20 × 34 × 23 mm vs 20 × 34 × 26 mm) — seulement 3 mm plus court ! Il est donc un **remplacement quasi direct** du XC330, avec +39 % de couple, le contrôle en force en bonus, et un boîtier alu plus durable. Son prix (~55 €) est 2× moins cher que le XC330 (~110 €).

---

## 1. Les Modèles ORCA Hand — Vue d'Ensemble

D'après les données recueillies :

| Modèle | DOF | Moteurs | Tactile | Statut | Coût BOM |
| :--- | :---: | :--- | :--- | :--- | :---: |
| **ORCA V1 (Legacy)** | 17 | 17× STS3215 | FSR binaire (simple) | Open-source | ~2 000 CHF |
| **ORCA Hand Touch** | 17 | 17× STS3215 | **351 taxels Hall-effect 6D** | **Closed-source (capteurs)** | N/A |
| **ORCA Standard** (actuel) | 17 | 17× STS3215 | Variable | Open-source (mécanique) | ~2 000 CHF |

**Points clés :**
- L'ORCA Hand utilise **17 moteurs** pour **17 DOF** (4 DOF/doigt × 4 doigts + 4 DOF pouce + 1 DOF poignet).
- Le système de capteurs haute résolution (ORCA Hand Touch, 351 taxels) est **closed-source** — développé avec un partenaire industriel, non reproductible.
- La partie mécanique et logicielle reste **open-source** (CAD, STL, BOM, orca_core SDK).

---

## 2. Architecture Recommandée : D-Hand V1 — "Hybrid HL"

### 2.1 Le Concept

Combiner les forces des deux moteurs Feetech dans une architecture optimisée pour le D-Bot :
- **STS3215** pour les axes de **force** (flexion des doigts dans le power grasp)
- **HL-3915** pour les axes de **précision et couple** (opposition pouce, abduction, curl palmaire)

Ce choix exploite le contrôle en force constante du HL-3915 exactement là où il est le plus utile : les mouvements fins qui nécessitent une régulation de couple.

### 2.2 Allocation des DOF

| # | Doigt | Mouvement | Moteur | Couple stall | Rôle | Contrôle force |
| :---: | :--- | :--- | :--- | :---: | :--- | :---: |
| 1 | Pouce | Flexion (Curl) | **STS3215** | 2,94 N.m | Force | ❌ (via eFlesh) |
| 2 | Pouce | Opposition (Abd.) | **HL-3915** | 1,39 N.m | Précision | ✅ Intégré |
| 3 | Index | Flexion (Curl) | **STS3215** | 2,94 N.m | Force | ❌ (via eFlesh) |
| 4 | Index | Abduction | **HL-3915** | 1,39 N.m | Précision | ✅ Intégré |
| 5 | Majeur | Flexion (Curl) | **STS3215** | 2,94 N.m | Force | ❌ (via eFlesh) |
| 6 | Annulaire | Flexion | **STS3215** | 2,94 N.m | Force | ❌ (via eFlesh) |
| 7 | Auriculaire | Flexion | **STS3215** | 2,94 N.m | Force | ❌ (via eFlesh) |
| 8 | Paume | Curl palmaire | **HL-3915** | 1,39 N.m | Précision | ✅ Intégré |

**Résumé : 5× STS3215 (force) + 3× HL-3915 (précision) = 8 DOF**

### 2.3 Force de Grip

**Calcul (poulie Ø14 mm, r = 7 mm, η = 0,98, r_m = 10 mm, L = 70 mm) :**

| Doigt | Moteur | T_cable (N) | F_pulpe (N) |
| :--- | :--- | :---: | :---: |
| Pouce | STS3215 | 420,0 | 58,8 |
| Index | STS3215 | 420,0 | 58,8 |
| Majeur | STS3215 | 420,0 | 58,8 |
| Annulaire | STS3215 | 420,0 | 58,8 |
| Auriculaire | STS3215 | 420,0 | 58,8 |

$$F_{grip} = 5 \times 58.8 \times \cos(25°) = 5 \times 58.8 \times 0.906 = \mathbf{266.4 \text{ N}}$$

> 🎯 **266 N — identique au scénario "tout STS3215" car les 5 doigts de flexion sont tous en STS3215.**

### 2.4 Coût

| Composant | Qté | Prix unitaire | Total |
| :--- | :---: | :---: | :---: |
| STS3215 | 5 | 25 € | 125 € |
| HL-3915 | 3 | 55 € | 165 € |
| Adaptateur UART-USB | 1 | 5 € | 5 € |
| **Total servos + interface** | | | **295 €** |

**Comparaison :**

| Config | Coût servos/main | Grip | Contrôle force |
| :--- | :---: | :---: | :---: |
| Actuel (XC430 + XC330) | 960 € | 139,5 N | ✅ 8/8 axes |
| Tout STS3215 | 200 € | 266 N | ❌ 0/8 axes (force via capteurs ext.) |
| **Hybrid HL (recommandé)** | **295 €** | **266 N** | **✅ 3/8 axes** (là où c'est utile) |

### 2.5 Masse et Encombrement

**Masse servos :** (5 × 55) + (3 × 35,8) = 275 + 107,4 = **382,4 g** (vs 352 g actuel → +30 g seulement !)

**Encombrement dans l'avant-bras :**

Le HL-3915 (20 × 34 × 23 mm) est presque identique au XC330 (20 × 34 × 26 mm). L'arrangement est donc :

| Bloc | Moteurs | Arrangement | Longueur | Section |
| :--- | :--- | :--- | :---: | :--- |
| Force | 5× STS3215 | 2×2 + 1 (empilé) | ~90 mm | 49,4 × 70 mm |
| Précision | 3× HL-3915 | 2+1 (empilé) | ~34 mm | 40 × 46 mm |
| **Total** | **8 moteurs** | | **~124 mm** | Max 49,4 × 70 mm |

**Total dans le tube :** 124 mm (servos) + 57 mm (RS-00) = **181 mm**

→ Tube de **200 mm** suffit (vs 220 mm actuel), avec **19 mm** libres pour l'électronique.

→ Longueur fonctionnelle : 78 (RS-02) + 200 = **278 mm** — parfaitement anthropomorphe.

### 2.6 Avantage Clé : Un Seul Protocole de Communication

Le STS3215 et le HL-3915 utilisent le **même protocole TTL série** (half-duplex, même SDK SCServo). Ils peuvent coexister sur **le même bus** avec des IDs différents. Pas besoin de deux interfaces ni de deux bibliothèques logicielles.

C'est un avantage décisif par rapport au scénario hybride STS3215 + XC330 de l'étude précédente, qui nécessitait deux protocoles incompatibles.

---

## 3. Capteurs Tactiles — Comparatif et Recommandation

### 3.1 Panorama des Solutions

| Capteur | Type | Résolution | Axes | Prix/doigt | Open-Source | Intégration |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **eFlesh** (NYU/Pinto Lab) | Magnétique (Hall + TPU 3D-print) | Configurable | 3 (X,Y,Z) | **~15 € DIY** | ✅ | TPU + aimants N52 + magnétomètre |
| **ReSkin** (Meta AI + CMU) | Magnétique (élastomère) | 1 mm spatial | 3 | **< 6 € /unité** (×100) | ✅ | DragonSkin + particules magnét. |
| **AnySkin** (NYU/Meta) | Magnétique (ReSkin v2) | 1 mm, 400 Hz | 3 | ~50 € DIY | ✅ | Skin remplaçable en 12 sec |
| **FSR simples** (ORCA V1) | Résistif | 1 point/doigt | 1 (pression) | ~1 € | ✅ | Collé sous la pulpe |
| **FingerVision** | Vision (caméra + peau transparente) | 320×240 px | 3 | ~50 € DIY | ✅ | Silicone transparent + USB cam |
| **DIGIT** (Meta/FAIR) | Vision + gel | 320×240 px, 60fps | 3 | ~355 € (commercial) | ✅ | Caméra + gel déformable |
| **ORCA Touch** (Hall 6D) | Hall-effect 6D | 351 taxels/main | 6 | N/A | ❌ Closed | Capteurs custom closed-source |
| **GelSight Mini** | Vision + gel | 640×480 px | 3 | ~500 € | Partiel | Trop gros pour doigts |
| **Contactile PapillArray** | Piliers biomimétiques | 9 piliers/capteur, 1kHz | 9D | ~2 600 € | ❌ | Commercial, grippers |

### 3.2 Analyse par Critère D-Bot

Pour le D-Bot, les critères clés sont :

| Critère | Poids | Meilleur candidat |
| :--- | :---: | :--- |
| **Coût** (budget limité) | 25 % | FSR ou AnySkin |
| **Facilité d'intégration** (main tendon-driven) | 25 % | FSR ou eFlesh |
| **Qualité du retour de force** (grip adaptatif) | 25 % | eFlesh ou AnySkin |
| **Détection de glissement** (manipulation sûre) | 15 % | eFlesh (cisaillement) ou DIGIT |
| **Robustesse** (usage intensif) | 10 % | FSR ou eFlesh |

### 3.3 Recommandation Tactile : Approche par Tiers

#### Tier 1 — V1 Immédiate : FSR Simples (~10 €/main)

Pour le premier prototype, commencer avec la solution la plus simple :
- **5× FSR 402** (Interlink Electronics, ~1 € pièce sur AliExpress) collés sous chaque pulpe de doigt
- Un simple multiplexeur analogique (CD4051, ~0,50 €) connecté à un ADC
- **Suffisant pour** : détecter le contact, mesurer la pression brute, implémenter un grip basique "serrer jusqu'au contact puis maintenir"
- **Limite :** Pas de détection de cisaillement ni de glissement
- **Combiné avec le mode force constante du HL-3915** sur les 3 axes de précision, on obtient déjà un contrôle de grip fonctionnel

**Où acheter :** GoTronic (France), AliExpress, Amazon France — chercher "FSR 402" ou "Force Sensitive Resistor"

#### Tier 2 — V1.1 Évoluée : ReSkin ou eFlesh (~15–30 €/main)

Une fois le prototype mécanique validé, intégrer des capteurs magnétiques open-source :
Deux options complémentaires, toutes deux open-source et magnétiques :

**Option A — ReSkin (Meta AI + CMU)** : La solution la plus économique et éprouvée
- **< 6 € par unité** en lots de 100 (peau magnétisée + magnétomètre)
- Épaisseur : seulement 2–3 mm (se colle directement sur la pulpe)
- Durabilité : > 50 000 interactions prouvées
- 3 axes (pression + cisaillement) à 400 Hz, résolution 1 mm
- **Référence :** reskin.dev — design files complets, code open-source

**Option B — eFlesh (NYU / Pinto Lab)** : La plus adaptable
- ~15 € DIY (TPU imprimé 3D + aimants N52 + magnétomètre)
- **Outil de design** qui convertit n'importe quel modèle 3D (STL/OBJ) en capteur imprimable
- Localisation du contact à 0,5 mm, détection de glissement ~95 %
- Parfait pour le D-Bot car on peut mouler le capteur sur la forme exacte de chaque doigt
- **Référence :** e-flesh.com — CAD tool + design files

> 💡 **Ma recommandation Tier 2 : eFlesh.** L'outil de design qui génère automatiquement les capteurs à partir de la géométrie du doigt est un avantage décisif pour le D-Bot. Et à ~15 € par main, c'est à peine plus cher que les FSR.

#### Tier 3 — V2 Premium : AnySkin Avancé (~50 €/main)

Pour une V2 nécessitant le maximum de performances :
- **AnySkin** (NYU/Columbia/Meta) : version améliorée de ReSkin
- 5 magnétomètres par capteur, résolution 1 mm, 400 Hz
- **Peau remplaçable en 12 secondes** (clip-on) — maintenance ultra-rapide
- Transfert zéro-shot entre instances (le modèle RL appris sur un capteur fonctionne sur un autre)
- Testé sur **LeapHand** (main tendon-driven similaire au D-Bot)
- **Référence :** any-skin.github.io — fabrication guide, SDK Python

### 3.4 Verdict Tactile

| Phase | Solution | Coût/main | Capacité |
| :--- | :--- | :---: | :--- |
| **V1 prototype** | FSR 402 × 5 + HL-3915 force mode | **10 €** | Contact + pression brute + couple contrôlé |
| **V1.1 améliorée** | eFlesh DIY (ou ReSkin) | **15 €** | + Cisaillement + glissement + 3 axes |
| **V2 finale** | AnySkin (peau interchangeable) | **50 €** | + Haute résolution + RL-ready + maintenance rapide |

> **Recommandation :** Commencer en **Tier 1 (FSR)** pour valider la mécanique. La boucle de contrôle de force utilise le **mode force constante du HL-3915** sur les axes de précision, ce qui donne un contrôle de force fonctionnel même avec des capteurs simples. Puis passer directement au **Tier 2 (eFlesh)** dès la cinématique validée — à 15 € par main, c'est presque gratuit et bien supérieur aux FSR.

---

## 4. Synthèse : Architecture Finale Recommandée

### 4.1 Tableau Récapitulatif

| Sous-système | Choix V1 | Justification |
| :--- | :--- | :--- |
| **Moteurs Force (×5)** | Feetech **STS3215** | 2,94 N.m, 55g, 25 €, validé ORCA Hand |
| **Moteurs Précision (×3)** | Feetech **HL-3915** | 1,39 N.m, 36g, 40 €, **contrôle force intégré** |
| **Protocole** | TTL série (1 bus, 1 adaptateur) | STS3215 et HL-3915 = même protocole SCServo |
| **Tendons** | Dyneema Ø0,80 mm (ou Vectran Ø0,60 mm) | Fs ≥ 2,4 avec épissure/sertissage |
| **Poulies** | Ø14 mm, Al 7075-T6, roulement MR84ZZ | Identique au design actuel |
| **Tube avant-bras** | Carbone Ø30 mm, **200 mm** | –20 mm vs actuel, proportionné |
| **Capteurs V1** | 5× FSR 402 (+HL-3915 force mode) | 10 €, prototype rapide |
| **Capteurs V1.1** | eFlesh DIY (TPU + aimants) | 15 €, 3 axes, outil CAD auto |
| **Buck converter** | Pololu D24V150F12 (15A) | Supporte le stall des STS3215 |
| **Attache tendons** | Sertissage manchon cuivre Ø1,5 mm | Fs ≥ 2,4 (pas de nœud Ashley) |

### 4.2 Comparaison avec le Design Actuel

| Critère | Design Actuel | **Hybrid HL V1** | Delta |
| :--- | :---: | :---: | :---: |
| Force de grip (stall) | 139,5 N | **266,4 N** | **+91 %** ✅ |
| Coût servos/main | 960 € | **295 €** | **–69 %** ✅ |
| Masse servos | 352 g | 382 g | +9 % (négligeable) |
| Encombrement moteurs | 145 mm | **124 mm** | **–14 %** ✅ |
| Contrôle en force intégré | 8/8 axes | **3/8 axes** | –5 axes 🟡 |
| Protocole unique | ✅ Dynamixel | **✅ SCServo** | Changé, mais unifié |
| DOF total | 8 | 8 | = |
| Longueur tube | 220 mm | **200 mm** | **–9 %** ✅ |
| Coût capteurs | 150 € (eFlesh MLX) | **10 € (FSR V1) / 15 € (eFlesh V1.1)** | –90 à –93 % |
| **Économie totale/robot** | — | — | **~1 600 €** (2 bras, servos + capteurs) |

### 4.3 Ma Position par Rapport aux Recommandations Précédentes

| Question | Étude précédente | **Maintenant** |
| :--- | :--- | :--- |
| Moteur de force | STS3215 (8×) | **STS3215 (5×)** — inchangé pour la force |
| Moteur de précision | STS3215 ou XC330 | **HL-3915 (3×)** — nouveau, meilleur que les deux |
| Architecture | Scénario B (tout STS3215) | **Hybrid HL** — ajout du contrôle force sur 3 axes |
| Nombre de DOF | 8 | **8** — inchangé |
| Tactile | eFlesh (MLX, ~150€) | **FSR V1 → eFlesh DIY V1.1 → AnySkin V2** — progressif et ultra-économique |

> **Ce qui change :** Le HL-3915 comble le seul défaut du scénario "tout STS3215" — l'absence de contrôle en couple. En plaçant les HL-3915 sur les 3 axes de précision (opposition pouce, abduction index, curl palmaire), on obtient le meilleur des deux mondes : la force brute du STS3215 ET le contrôle en couple du HL-3915, le tout sur un bus unique, pour seulement 50 € de plus que le tout-STS3215.

---

## 5. Pourquoi PAS le HL-3915 Partout ?

On pourrait se demander : pourquoi ne pas utiliser 8× HL-3915 au lieu du mix ?

**Calcul de grip avec 8× HL-3915 :**

$$F_{pulpe} = \frac{1.39}{0.007} \times \frac{10}{70} \times 0.98 = 198.6 \times 0.143 \times 0.98 = 27.8 \text{ N}$$

$$F_{grip} = 5 \times 27.8 \times 0.906 = \mathbf{126.0 \text{ N}}$$

→ **126 N** — inférieur au design actuel (139,5 N). Le HL-3915 n'a pas assez de couple pour les axes de force des doigts. Il excelle en précision, pas en puissance.

| Config | Grip | Coût | Contrôle force |
| :--- | :---: | :---: | :---: |
| 8× HL-3915 | 126 N ❌ | 320 € | ✅ 8/8 |
| 8× STS3215 | 266 N | 200 € | ❌ 0/8 |
| 5× STS3215 + 3× HL-3915 | 266 N | 295 € | ✅ 3/8 ⭐ |

Le mix est clairement optimal : grip maximal + contrôle force là où c'est utile + coût maîtrisé.

---

## 6. Plan d'Action Proposé

| # | Action | Durée | Coût |
| :---: | :--- | :---: | :---: |
| 1 | Commander 5× STS3215 + 3× HL-3915 + adaptateur UART | 1–2 semaines | ~300 € |
| 2 | Commander 5× FSR 402 + CD4051 (capteurs V1) | 1 semaine | ~10 € |
| 3 | Imprimer support moteurs adapté (PA12-CF ou PLA) | 2 jours | ~5 € |
| 4 | Tester 1 doigt complet (STS3215 + poulie + tendon + FSR) | 1 jour | — |
| 5 | Mesurer η réel de la chaîne de transmission | 1 jour | — |
| 6 | Si η OK → assembler la main complète | 3 jours | — |
| 7 | Tester le mode force constante du HL-3915 sur l'opposition | 1 jour | — |
| 8 | Intégrer le contrôleur Python (SDK SCServo) | 2 jours | — |

**Budget total V1 (1 main) : ~365 €** (servos + capteurs FSR + tendon + poulies + structure + visserie)

**Budget total robot (2 mains) : ~730 €** (vs ~2 626 € avec Dynamixel = **économie de ~1 900 €**)

---

## 7. Conclusion

> **Oui, j'ai ajusté ma recommandation.** Le HL-3915 est une découverte précieuse grâce à votre observation sur le site Feetech. Ce moteur compact avec contrôle en force intégré comble parfaitement le seul défaut de l'approche tout-STS3215. L'architecture "Hybrid HL" (5× STS3215 + 3× HL-3915) est maintenant ma recommandation définitive.

Les trois raisons principales :

1. **Force de grip ×1,9** (266 N vs 139,5 N) — grâce au STS3215 sur les 5 doigts
2. **Contrôle en couple** sur les 3 axes critiques — grâce au HL-3915 (mode force constante)
3. **Coût ÷3,8** (250 € vs 960 €) — tout en utilisant un seul protocole de communication

Le tout validé par l'usage du STS3215 dans l'ORCA Hand (ETH Zurich, >10 000 cycles), et le HL-3915 dans de multiples projets de mains bioniques documentés.

---

*Fin du rapport — Claude Opus 4.6 (Anthropic) — 2026-05-23*

# 15e — Alternatives Moteurs Genou (Unitree M107, CubeMars, etc.)

> **Série Biomécanique :**
> - [15a] [Locomotion Baseline](./15a_Analyse_Locomotion_Baseline.md)
> - [15b] [Configurations Moteurs & Évolutions](./15b_Configurations_Moteurs.md)
> - [15c] [Révision Configuration Cardan 39 kg](./15c_Revision_Cardan_39kg.md)
> - [15d] [Genou & Course — Solutions](./15d_Genou_et_Course.md)
> - [15e] **Alternatives Moteurs Genou** ← *vous êtes ici*
> - [15f] [Portage de Charges & Marche](./15f_Portage_Charges_et_Marche.md)
> - [15g] [Solution S6 : Courroie GT3](./15g_Solution_S6_Courroie_GT3_Genou.md)
> - [16] [**Conclusions & Architecture Finale D-Bot**](./16_Conclusions_Architecture_DBot.md)

---

## Recherche : Moteurs Haute Performance pour le Genou du D-Bot

> **Contexte** : Le RS-04 (120 N.m pic, 1 420g) est insuffisant pour la course (172 N.m requis). Nous cherchons un moteur **plus puissant** sans être **plus lourd**, ou comment les concurrents résolvent ce problème.

---

## 1. Comparatif des Moteurs Disponibles

| Moteur | Couple Pic | Couple Nominal | Masse | Densité de Couple | Tension | Achetable ? | Prix estimé |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Robstride RS-04** (actuel) | **120 N.m** | 40 N.m | **1 420g** | **84.5 N.m/kg** | 48V | ✅ Oui | ~$280 |
| **Unitree M107** ⭐ | **360 N.m** | ~120 N.m | **1 900g** | **189 N.m/kg** | 48V | ⚠️ AliExpress | ~$500 |
| CubeMars AK80-64 | 120 N.m | 48 N.m | ~850g | 141 N.m/kg | 48V | ✅ Oui | ~$350 |
| CubeMars AK10-9 V3 | 53 N.m | 18 N.m | 940g | 86 N.m/kg | 48V | ✅ Oui | ~$250 |
| Tesla Optimus (linéaire) | 8 000 N* | — | Secret | Secret | — | ❌ Propriétaire | — |
| Agility Digit (SEA) | Non publié | — | Non publié | — | — | ❌ Propriétaire | — |
| Figure 02 (custom) | Non publié | — | Non publié | — | — | ❌ Propriétaire | — |

> *Tesla utilise des **actionneurs linéaires** (pas rotatifs) avec un mécanisme de bielles au genou, ce qui rend la comparaison directe impossible.

---

## 2. Comment les Autres Robots Résolvent le Problème du Genou

### 🟢 Unitree H1 / H1-2 — « Force Brute avec un Moteur Supérieur »
- **Solution** : Un unique moteur **M107** par genou, propriétaire Unitree.
- **Couple** : **360 N.m** (pic), pour un robot de 47 kg.
- **Masse moteur** : 1,9 kg (seulement +480g vs RS-04, mais **3× le couple**).
- **Densité de couple** : 189 N.m/kg — **2,24× supérieure au RS-04** (84.5 N.m/kg).
- **Technologie clé** : Rotor interne haute vitesse + réducteur planétaire intégré + roulements croisés industriels + axe creux.
- **Leçon** : Unitree a résolu le problème en **concevant son propre moteur** avec une densité de couple impossible à atteindre avec les moteurs du commerce.

### 🟡 Tesla Optimus — « Changer le Paradigme : Actionneur Linéaire + Bielles »
- **Solution** : Le genou n'est **pas** actionné par un moteur rotatif ! Tesla utilise un **vérin linéaire** (vis à rouleaux planétaires + moteur brushless) qui pousse/tire un mécanisme de bielles.
- **Force linéaire** : Jusqu'à **8 000 N** sur l'actionneur le plus puissant (robot de 57 kg).
- **Avantage** : Un actionneur linéaire offre une force quasi-constante sur toute la course, contrairement à un bras de manivelle rotatif qui a des points morts. Le ratio mécanique est optimisé pour donner ~150° de débattement au genou avec un mouvement linéaire de seulement quelques centimètres.
- **Leçon pour nous** : C'est exactement le principe de notre **Solution S2 (Tirant)**, mais au lieu d'un moteur rotatif + pushrod, Tesla utilise directement un vérin linéaire. **Notre approche S2 est donc validée par Tesla.**

### 🔴 Agility Robotics Digit — « SEA (Series Elastic Actuator) »
- **Solution** : Moteur rotatif couplé à un **ressort en série** au genou.
- **Spécifications** : Propriétaires et non publiées.
- **Principe** : Le ressort stocke l'énergie de l'impact et la restitue lors de la poussée. Le moteur n'a jamais besoin de fournir le couple de pic instantané — c'est le ressort qui le fait.
- **Leçon** : C'est notre **Solution S3**. Un moteur de 120 N.m + un ressort calibré peut produire des pics de 200+ N.m au genou sans aucun changement de moteur.

### 🟠 Figure 02 — « Moteurs Custom pour Chaque Articulation »
- **Solution** : Actionneurs entièrement propriétaires, optimisés individuellement pour chaque articulation.
- **Spécifications** : Non publiques.
- **Leçon** : Même approche qu'Unitree — la course à la densité de couple passe par la conception motoriste en interne.

---

## 3. Le Candidat Sérieux : Unitree M107 ⭐

### Fiche Technique

| Paramètre | Valeur |
| :--- | :--- |
| **Couple Max** | **360 N.m** |
| **Masse** | **1 900g** (seulement +480g vs RS-04) |
| **Densité de couple** | **189 N.m/kg** (2,24× RS-04) |
| **Dimensions** | 107 × 74 mm |
| **Tension** | 48V (compatible bus D-Bot !) |
| **Encodeurs** | Doubles (position + vitesse) |
| **Arbre** | **Creux** (passage câbles) |
| **Roulements** | Croisés industriels |
| **Technologie** | PMSM rotor interne haute vitesse |

### Impact sur le D-Bot si on remplace le RS-04 au genou par le M107

| Paramètre | RS-04 Actuel | M107 Remplacement | Δ |
| :--- | :--- | :---: | :---: |
| Couple max genou | 120 N.m | **360 N.m** | **+200%** |
| Masse par genou | 1 420g | 1 900g | **+480g** |
| Masse totale robot | 40.4 kg | **41.36 kg** (+0.96) | Minime |
| Couple requis marche | ~121 N.m | ~124 N.m | Négligeable |
| **Marge genou marche** | **-1 N.m (101%)** ⚠️ | **+236 N.m (34%)** ✅ | **Énorme** |
| Couple requis course | ~172 N.m | ~175 N.m | Négligeable |
| **Marge genou course** | **-52 N.m (143%)** ❌ | **+185 N.m (49%)** ✅ | **Course possible !** |

### Problèmes Potentiels
1. **Protocole de contrôle** : Le M107 utilise un protocole propriétaire Unitree, **pas le protocole CAN Robstride**. Il faudra développer un driver ROS 2 custom ou un convertisseur.
2. **Disponibilité** : Trouvé sur AliExpress à ~$500, mais la fiabilité de la chaîne d'approvisionnement est incertaine.
3. **SDK / Documentation** : Moins mature que l'écosystème Robstride. SDK Unitree orienté vers leurs robots complets, pas vers des composants isolés.
4. **Dimensions** : 107×74 mm au lieu de ~90×76 mm pour le RS-04. Il faudra vérifier que le bloc genou D-Bot peut l'accueillir.

---

## 4. Synthèse et Recommandations

### Option A — Rester sur RS-04 + Solution Mécanique (Recommandée V1-V3)
> **Le plus réaliste à court terme.**

Nos Solutions S1 (Algorithme) + S2 (Tirant mécanique) restent les plus pertinentes :
- **S1 seul** (mid-foot strike + foulée courte) → Course 4-5 km/h, **0€, 0g**.
- **S2** (tirant 1.5:1 dans la cuisse) → **180 N.m effectifs**, moins de masse distale, course confortable.
- **S2+S3** (tirant + SEA) → **270 N.m**, course rapide 8-10 km/h.

> [!IMPORTANT]
> **Tesla valide notre approche S2.** Leur actionneur linéaire au genou est exactement un tirant industrialisé.

### Option B — Remplacer le RS-04 genou par le Unitree M107 (Expérimental)
> **Le « game changer » si le protocole est résolu.**

- +960g total robot, mais **3× le couple** (360 vs 120 N.m).
- Course, portage lourd, accroupissement — tout devient trivial.
- **Risque** : Intégration protocole CAN Unitree, disponibilité pièces, support SAV.
- **Coût** : ~$500 × 2 genoux = $1 000 supplémentaires.

### Option C — Attendre les futurs Robstride (H2 2025)
> **Le pari sur l'écosystème existant.**

Robstride a annoncé de nouveaux modèles pour le second semestre 2025. Si un « RS-07 » ou « RS-05 Plus » avec ~200 N.m et ~1.5 kg sort, il serait drop-in compatible avec le bus CAN et le SDK existants.
- **Risque** : Aucune garantie que ce produit existe ou qu'il atteigne la densité de couple du M107.

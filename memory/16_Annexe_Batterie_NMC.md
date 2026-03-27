# Annexe — Recherche Batteries NMC 21700 pour K-Bot/D-Bot

> **Source** : Recherche Perplexity AI — Février 2026
> **Objectif** : Identifier les meilleurs packs Li-ion NMC 21700 48V disponibles depuis la France pour un robot humanoïde type K-Bot.

---

## 1. Cible Énergétique et Topologie

Les specs K-Scale parlent d'un pack hot-swappable 48V 15 Ah (~720 Wh). Pour le D-Bot :
- **Cible** : 2 × 48V 10 Ah ≃ 960 Wh total
- **Masse** : ~4.5–5 kg avec du 21700 NMC de qualité
- **Topologie** : Bus 48V (13S Li-ion), DC-DC pour 24V/12V/5V
- **Usage des 2 packs** :
  - 1 en service + 1 spare hot-swappable, ou
  - 2 en parallèle via ORing MOSFET

## 2. Chimies Comparées

### NMC/NCA (21700) — ✅ Recommandé
- Densité : 200–220 Wh/kg → masse minimale
- Sécurité correcte avec cellules de marque (LG/Samsung) + BMS sérieux
- **Exemple** : AT WEY 48V 10 Ah = 480 Wh pour 2.3 kg

### LiFePO4 — ⚠️ Trop lourd
- Densité 130–160 Wh/kg → 30-40% plus lourd
- Pack 48V 10 Ah LFP ≃ 3–4 kg (vs 2.3 kg NMC)
- Usage : prototypage stationnaire uniquement

## 3. Option Recommandée : AT WEY NMC 48V 10 Ah

| Paramètre | Valeur |
| :--- | :--- |
| **Chimie** | Li-ion NMC 21700 LG M50LT |
| **Tension** | 48V nominale (13S) |
| **Capacité** | 10 Ah (480 Wh) |
| **Poids** | 2.3 kg par pack |
| **BMS** | 13S NMC, 20-50A continu, 100A pic |
| **Connectique** | Personnalisable (Anderson SB50, XT, etc.) |
| **Usage** | Robotique, industrie, modélisme |
| **Fabrication** | Assemblé en France |
| **Lien** | [atwey.fr](https://atwey.fr/accueil/94-batterie-generique-48v-10ah.html) |

### Configuration Robot (2 packs)
- **Énergie totale** : 960 Wh
- **Masse totale** : ~4.6 kg
- **Courant** : 40–100A continu selon BMS (vérifier avec AT WEY)

### Topologies possibles
1. **1 pack en service + 1 spare** : Trappe batterie, connecteur Anderson SB50, fusible 80A
2. **2 packs en parallèle** : Packs identiques, même âge, ORing MOSFET, connecteur/déconnexion à SoC ~50-60%

## 4. Autres Fournisseurs NMC FR

| Fournisseur | Modèle | Chimie | Capacité | Note |
| :--- | :--- | :--- | :--- | :--- |
| **Smolt & Co** | Li-ion 48V 10 Ah | Samsung/LG | 10 Ah | Bonne qualité, BMS avec sonde temp. |
| **B-Volt** | Custom 48V | Samsung 35E | Variable | Ultra-léger, fabrication FR, Anderson |
| **CMBatteries** | 48V 20 Ah | Samsung 50E | 20 Ah | Haute densité mais BMS limité à 30A |
| **OZO** | Custom 48V | Sur mesure | Variable | Bureau d'étude FR, custom forme/BMS |
| **Li-Tech** | Standard 48V LFP | LiFePO4 | 30-40 Ah | Sécurité max, mais très lourd |

## 5. Sur-Mesure FR (Meilleur Compromis)

Stratégie recommandée :
1. Partir du pack **AT WEY NMC 48V 10 Ah** comme base
2. Contacter AT WEY pour **2 modules plus fins** montables de chaque côté du torse
3. Connecteur Anderson SB50/QS8 + câble vers powerboard centrale

## 6. Intégration (Schéma Électrique 48V)

- **Par pack** : BMS interne 13S → Fusible 60-80A → Connecteur Anderson SB50
- **Bus robot** : Powerboard 48V + CAN vers membres, buck vers compute
- **Sécurité** :
  - Packs fermés avec BMS dédié (jamais de cellules nues)
  - Espace d'air autour de la batterie
  - Cloisonnement en matériaux ignifugés (PC/ABS, alu)
  - Sortie de dégazage "vers l'arrière"
  - Charge avec chargeur 54.6V (13S) CC/CV dédié

## 7. Résumé Achats

1. **2 × AT WEY 48V 10 Ah NMC 21700** (~€300/pack) — [Lien](https://atwey.fr/accueil/94-batterie-generique-48v-10ah.html)
2. **1 × Chargeur 48V Li-ion 13S (54.6V) 4-5A**
3. **Connectique** : Anderson SB50 + fusibles 60-80A
4. **Optionnel** : Contact OZO/AT WEY pour double pack sur-mesure

---

> **Sources principales** : [AT WEY](https://atwey.fr), [B-Volt](https://www.b-volt.com), [CMBatteries](https://cmbatteries.com), [OZO Industries](https://ozo-industries.com), [Li-Tech](https://www.li-tech.fr), [K-Scale Docs](https://docs.kscale.dev/robots/k-bot/electrical/)

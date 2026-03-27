# Annexe — État des Lieux Batteries Semi-Solides (Février 2026)

> **Source** : Recherche Perplexity AI — Février 2026
> **Objectif** : Évaluer la viabilité des batteries semi-solides / solides pour un robot humanoïde type K-Bot.

---

## 1. Situation du Marché

**Conclusion directe** : Pour un humanoïde type K-Bot (48V, <1 kWh, <5 kg), **aucun pack semi-solide compact et léger n'est disponible à l'achat** en février 2026. Les options existantes sont :

- Des **gros modules 48V de 5+ kWh** pour solaire/bateau (40-50 kg)
- Des **stations énergie AC plug-and-play** (Zendure, Indevolt)
- Des **cellules B2B** à intégrer soi-même (MOQ élevé, aucune documentation maker)

## 2. Produits Semi-Solides Disponibles depuis la France

### 2.1 Modules 48V Stationnaires

| Produit | Techno | Capacité | Poids | Usage | Pertinence Robot |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **Moteurs-Verts 48V 100Ah** | LFP solid-state | 5.12 kWh | 45 kg | Bateau/solaire | ❌ |
| **Energy Eco 48V 5.12 kWh** | Semi-solid | 5.12 kWh | ~40 kg | Off-grid/marine | ❌ |

→ Absolument inutilisables à bord d'un humanoïde.

### 2.2 Stations Énergie Grand Public

| Produit | Techno | Capacité | Usage | Pertinence Robot |
| :--- | :--- | :--- | :--- | :---: |
| **Indevolt SolidFlex 2000** | LFP semi-solide | 2 kWh extensible | Autoconsommation, onduleur AC | ❌ embarqué / ✅ alim labo |
| **Zendure SuperBase V** | Semi-solid 228 Wh/kg | 6.4-64 kWh | Backup, camping | ❌ embarqué / ✅ alim labo |

→ Trop massifs pour l'embarqué, mais utiles comme **alimentation de développement**.

### 2.3 Cellules B2B (Import)

| Fournisseur | Densité | Cycles | Accès |
| :--- | :--- | :--- | :--- |
| **HereWin** | 275-300 Wh/kg | MOQ industriel | Contact B2B |
| **Welion** | 350 Wh/kg (annoncé) | 6000+ | Contact B2B |

→ Nécessite conception pack complet (13S, BMS, mécanique, sécurité). Trop ambitieux pour un projet DIY.

## 3. Pertinence pour le D-Bot

### ❌ Pourquoi ça ne colle pas (aujourd'hui)

- **Poids** : Les modules commerciaux font 40-50 kg
- **Format** : Conçus pour rester au sol (IP65, coffret métal)
- **BMS** : Dimensionnés pour stationnaire, pas pour les pointes de courant brutales d'un bipède
- **Aucun pack "robotique légère"** n'existe en semi-solide dans le format 48V / 500-1000 Wh / <10 kg

### ✅ Usage pertinent : Alimentation de Labo

Utiliser une **Indevolt SolidFlex 2000** ou **Zendure SuperBase V** comme grosse batterie externe :
- Robot en "fil à la patte" (umbilical 48V) pendant le développement
- Sécurité extrême (tests de perçage OK, 8000 cycles)
- Et garder des packs NMC classiques pour l'embarqué autonome

## 4. Perspectives 2027+

Le marché évolue rapidement :
- Apparition prévisible de **modules 48V semi-solides 1-2 kWh** (15-20 kg) pour RV/camping-car
- Puis éventuellement des **versions robotique** (AGV, AMR) avec BMS haute puissance
- Densité cellule prévue : +35%, prix : /2

**Action** : Réévaluer en 2027 quand des packs <5 kg existeront.

---

> **Sources** : [HereWin](https://www.herewinpower.com), [Welion](https://welion-energy.com), [Indevolt](https://fr.indevolt.com), [Zendure](https://zendure.com), [Moteurs-Verts](https://moteurs-verts.fr), [Energy Eco](https://www.energyeco.com.au)

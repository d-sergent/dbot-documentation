# Annexe — Comparatif Batteries et Scénarios d'Usage

> **Source** : Recherche Perplexity AI — Février 2026
> **Contexte** : Robot bipède D-Bot (48V bus, ~24 RobStride + Jetson Orin Nano, 200-400W moyen, pics ~1 kW, autonomie cible 20-30 min)

---

## 1. Tableau Comparatif (48V / 10 Ah)

| Batterie | Chimie | Densité (Wh/kg) | Cycles (80% DoD) | Prix (€) | Autonomie | Avantages | Inconvénients |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **AT WEY 48V 10Ah** | NMC 21700 | 200-220 | 800-1000 | 250-350 | 20-25 min | Léger (2.3 kg), 50A cont., robot-ready | Sensible au feu si mal intégré |
| **PowerTech 48V** | LiFePO4 | 130-160 | 4000-6000 | 400-500 | 20-25 min | Très sûr, robuste industriel | +30-40% masse (3-4 kg) |
| **Indevolt SolidFlex** | LFP semi-solide | 180-230 | 6000-8000 | 800-1200 | 20-25 min | Sécurité max, endurance | 40-50 kg/module, pas léger |
| **Tattu HD Semi-Solid 6S** | NMC semi-solide | 275-350 | 300-1000 | 500-650 | 30-40 min | Ultra-léger, zéro gonflement | Pas natif 48V, stock limité |

> **Note autonomie** : Basée sur ~300 Wh/h conso moyenne. Doubler les packs pour 40-60 min.

## 2. Scénarios d'Usage

### Court-terme (1-6 mois) — Test/Prototype
✅ **NMC 21700** (AT WEY 2 × 10 Ah, ~600€ total)
- Masse mini (4.6 kg total)
- Courant OK pour pics
- Facile à intégrer
- Budget test bas, scalable en parallèle

### Moyen-terme (6-24 mois) — Marche Stable
✅ **LiFePO4 industriel** (PowerTech ou Li-Tech custom, ~900€ total)
- Équilibre masse/sécurité
- 4× plus de cycles que NMC
- Masse +1-2 kg tolérable

### Long-terme (2027+)
⏳ **Semi-solide** quand modules <10 kg arriveront
- Autonomie + endurance pour runs longues
- Surveiller Indevolt/Tattu évolutions (~1500€ total prévu)

## 3. Recommandation Immédiate

> **Démarrer avec 2 × AT WEY NMC 48V 10 Ah** (~600€)
> - Connecteur Anderson SB50 (à préciser à la commande)
> - BMS 60A + fusibles 80A
> - Tester runtime réel via monitoring courant/volt sur Jetson
> - Upgrade semi-solide en 2027 quand les packs robotiques apparaîtront

**Lien d'achat** : [AT WEY — Batterie générique 48V 10Ah](https://atwey.fr/accueil/94-batterie-generique-48v-10ah.html)

Si >30 min d'autonomie visé dès maintenant → custom LiFePO4 chez [OZO Industries](https://ozo-industries.com/prestation/batteries/) (~1000€).

---

> **Sources** : [AT WEY](https://atwey.fr), [PowerTech](https://www.powertechsystems.eu), [Indevolt](https://fr.indevolt.com), [OZO](https://ozo-industries.com), [Li-Tech](https://www.li-tech.fr)

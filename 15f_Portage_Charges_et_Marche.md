# 15f — Portage de Charges & Marche : Capacités et Limitations du Genou

> **Série Biomécanique :**
> - [15a] [Locomotion Baseline](./15a_Analyse_Locomotion_Baseline.md)
> - [15b] [Configurations Moteurs & Évolutions](./15b_Configurations_Moteurs.md)
> - [15c] [Révision Configuration Cardan 39 kg](./15c_Revision_Cardan_39kg.md)
> - [15d] [Genou & Course — Solutions](./15d_Genou_et_Course.md)
> - [15e] [Alternatives Moteurs Genou](./15e_Alternatives_Moteurs_Genou.md)
> - [15f] **Portage de Charges & Marche** ← *vous êtes ici*
> - [15g] [Solution S6 : Courroie GT3](./15g_Solution_S6_Courroie_GT3_Genou.md)
> - [16] [**Conclusions & Architecture Finale D-Bot**](./16_Conclusions_Architecture_DBot.md)

---

## 1. Le Diagnostic : Sollicitation du Genou à Vide

Pour comprendre l'impact du portage de charges, il faut rappeler la situation de base du genou du robot **sans charge** :

- **Masse estimée D-Bot (Config Hybride)** : ~40.4 kg
- **Couple requis au genou (marche 2-3 km/h)** : ~121 N.m
- **Couple maximal du RS-04** : 120 N.m
- **Utilisation** : **101%** (Le moteur opère déjà sur ses pics transitoires).

Il n'y a donc **aucun budget de couple résiduel** (headroom) disponible pour ajouter du poids sans sortir de la zone nominale du moteur à la vitesse de 2-3 km/h.

---

## 2. Capacité de Portage Effective

### ⚖️ Calcul du Surplus
En marchant à un rythme nominal (2-3 km/h), toute charge $X$ rajoutée applique un multiplicateur direct :
$$\tau_{genou} = \frac{Masse_{robot} + X}{Masse_{robot}} \times 121\text{ N.m}$$

Pour ne pas dépasser les 120 N.m du moteur, la charge ajoutée $X$ doit être de $0\text{ kg}$. 

### 🐢 Modulation par la Vitesse de Marche
Le couple dépend massivement de la dynamique (accélération/vitesse). En ralentissant, le facteur dynamique diminue, ce qui **libère du couple pour le portage**.

| Vitesse | Facteur dynamique | $\tau_{genou}$ (vide) | Capacité de portage |
| :---: | :---: | :---: | :---: |
| **2.5 km/h** | $\times 1.76$ | **121 N.m (101%)** | **$\approx 0\text{ kg}$** ⚠️ |
| **1.5 km/h** | $\times 1.40$ | **96 N.m (80%)** | $\approx 10\text{ kg}$ |
| **1.0 km/h** | $\times 1.15$ | **79 N.m (66%)** | $\approx 20\text{ kg}$ |
| **0.5 km/h** | $\times 1.05$ | **72 N.m (60%)** | $\approx 26\text{ kg}$ |

> 💡 **Règle d'or** : Plus le robot porte lourd, plus il doit marcher lentement (marche statique).

---

## 3. Stratégies et Solutions Correctrices

Pour transformer le D-Bot en véritable robot logistique capable de porter du lourd à vitesse normale, 3 options s'offrent à nous :

### 🕹️ A. Algorithme de Marche Adaptatif (Soft)
Le contrôleur doit surveiller la consommation de courant des bras. S'il perçoit une charge de $5\text{ kg}$, il réduit automatiquement et dynamiquement la vitesse de translation maximale de la marche pour décharger le genou.

### ⚙️ B. Solution S2 : Le Tirant Mécanique (Mécanique)
L'utilisation d'un **tirant 1.5:1** déporte le RS-04 dans la cuisse et monte le couple effectif au genou à **180 Nm**.
- **Avantage** : Permet de marcher à 2.5 km/h avec **$+20\text{ kg}$ dans les bras** sans dépasser les limites.
- **Inconvénient** : Complexité mécanique accrue.

### 🔄 C. Swap Moteur : Unitree M107 (Matériel)
Le remplacement du RS-04 par un moteur de type **Unitree M107** déploie **360 N.m** au genou.
- **Bilan** : Marcher à 3 km/h avec $30\text{ kg}$ de charge devient trivial (opération à seulement 56% de charge).

---

## 📋 Tableau Synthèse de Performance

| Configuration | Vitesse de marche | Charge Maximale Utile (Estimée) |
| :--- | :---: | :---: |
| **V1 (RS-04 Direct)** | 2.5 km/h | $\approx 0\text{ kg}$ ⚠️ |
| **V1 (RS-04 Direct)** | $< 1.5\text{ km/h}$ | $\approx \mathbf{10\text{ kg}}$ |
| **V3 (+ Tirant S2)** | 2.5 km/h | $\approx \mathbf{20\text{ kg}}$ ✅ |
| **V4 (+ M107)** | 3.0 km/h | $\mathbf{30\text{ kg et +}}$ 🔥 |

# Comparaison des moteurs pour l'actuation du poignet : Robstride RS-00 vs Dynamixel XC430-T240BB

## Tableau comparatif des spécifications

| Critère | Robstride RS-00 | Dynamixel XC430-T240BB | Avantage |
|---------|----------------|------------------------|----------|
| **Couple nominal** | 14.0 N.m | 1.9 N.m | **RS-00** (+637%) |
| **Couple crête/stalle** | Non spécifié explicitement (mais ≥14 N.m) | 2.6 N.m | **RS-00** |
| **Couple continu** | 5.0 N.m | 1.9 N.m | **RS-00** (+163%) |
| **Poids** | 310g | 65g | **XC430** (-79%) |
| **Dimensions** | 57×57×51 mm | Non spécifié exactement (mais compact) | **XC430** (plus compact) |
| **Ratio de réduction** | 10:1 | 245:1 (d'après doc 21) | Différent |
| **Tension d'alimentation** | 48V (24-60V) | 12V (via buck 48V→12V) | **RS-00** (plus simple) |
| **Courant continu** | ~1.5A | ~0.5A/servo | **XC430** (-67%) |
| **Courant de crête** | ~4A | Non spécifié | ? |
| **Prix** | ~135$ | Non spécifié exactement (mais ~130$ selon doc 21) | Similaire |
| **Interface de communication** | CAN | TTL half-duplex (U2D2) | Différent |
| **Utilisation actuelle dans D-Bot** | Poignet Pitch et Roll | Main (D-Hand Hybrid) | - |
| **Backdrivable** | Oui (quasi direct-drive) | Non (réducteur 245:1) | **RS-00** |
| **Holding torque mécanique** | Faible (nécessite courant pour maintenir position) | Élevé (mécaniquement bloqué) | **XC430** |

## Analyse de la pertinence pour l'actuation du poignet

### Pour le poignet Pitch (inclinaison main) :

**Avantages du RS-00 :**
- Couple élevé (14 N.m nominal) permettant de porter des charges importantes sans fléchir
- Backdrivable permettant un contrôle en impédance et une interaction sûre
- Utilisé actuellement dans l'architecture D-Bot V1 pour cette fonction
- Alimentation directe en 48V sans besoin de convertisseur supplémentaire

**Inconvénients du RS-00 :**
- Poids élevé (310g) placé à l'extrémité distale, augmentant l'inertie
- Consommation de courant plus élevée
- Plus volumineux que le XC430

**Avantages du XC430 :**
- Très léger (65g), réduisant considérablement l'inertie distale
- Consommation de courant faible
- Holding torque mécanique permettant de maintenir une position sans consommation
- Déjà utilisé et qualifié dans la main D-Hand

**Inconvénients du XC430 :**
- Couple nettement insuffisant (1.9 N.m vs 14 N.m requis pour le poignet)
- Nécessite un réducteur rendant le moteur non-backdrivable
- Nécessite un buck converter 48V→12V supplémentaire
- Pas adapté pour porter des charges importantes au poignet

### Pour le poignet Roll (rotation de la poignée de porte) :

Les mêmes considérations s'appliquent, bien que le couple requis puisse être légèrement inférieur pour le Roll que pour le Pitch selon certaines analyses.

## Conclusion et recommandation

**Le Robstride RS-00 est nettement supérieur au Dynamixel XC430-T240BB pour l'actuation du poignet (tant Pitch que Roll) dans le contexte du robot D-Bot.**

Les raisons principales sont :
1. Le couple du RS-00 (14 N.m) est plus de 7 fois supérieur à celui du XC430 (1.9 N.m), ce qui est essentiel pour porter des charges au niveau du poignet sans fléchir
2. L'architecture actuelle du D-Bot place déjà le RS-00 au poignet avec succès
3. Bien que plus lourd, le RS-00 reste dans des limites acceptables pour cette application (310g vs 65g pour le XC430)
4. La nature backdrivable du RS-00 est préférable pour un contrôle en impédance et une interaction sûre

Le XC430-T240BB, malgré ses avantages en termes de poids et de consommation, ne fournit simplement pas assez de couple pour être utilisé comme actionneur principal du poignet dans un robot destiné à manipuler des objets du quotidien.

Cependant, dans l'architecture actuelle où la supination/pronation est assurée par le RS-02 au niveau du coude (comme documenté dans 22b_Etude_Poignet_Tesla_Optimus.md), le poignet ne nécessite que 2 DOF (Pitch et éventuellement Yaw), ce qui renforce la pertinence du RS-00 pour ces fonctions.

**Recommandation :** Conserver le Robstride RS-00 pour l'actuation du poignet Pitch (et Roll si nécessaire) dans l'architecture D-Bot, comme c'est actuellement le cas.
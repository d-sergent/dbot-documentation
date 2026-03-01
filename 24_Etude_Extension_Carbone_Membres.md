# 24 — Étude : Extension de l'Architecture Carbone (Fémur & Bras)

Suite à la validation de l'architecture "Tube Carbone + Insert + Goupille Mécanindus" pour le tibia (réduisant drastiquement l'inertie distale), il est naturel de se demander si cette solution peut être généralisée aux autres membres du D-Bot : le fémur (cuisse), le bras et l'avant-bras.

Voici l'analyse d'ingénierie mécanique comparative.

---

## 1. Extension aux Bras et Avant-Bras : Un Grand OUI 🏆

**L'application du tube carbone aux membres supérieurs est extrêmement pertinente et fortement recommandée.**

### 🦾 Avant-Bras (Coude → Poignet)
- **Contexte** : Relie le moteur du coude (RS-02) à la main (D-Hand avec moteurs XC330).
- **Inertie** : Le poignet/main est au bout d'un long bras de levier. Réduire le poids de l'avant-bras améliore drastiquement la réactivité du poignet et réduit la charge constante sur le moteur de l'épaule et du coude.
- **Efforts** : Le portage maximal cible étant de ~2 kg (voire 3-4 kg), les efforts transmis (torsion, flexion, arrachement) sont **très faibles** comparés à ceux des jambes du robot.
- **Verdict** : Un **Tube Carbone de Ø25 mm ou Ø30 mm** avec la même méthode (Insert Alu/PA12 + Goupille Mécanindus de Ø2 mm ou Ø2.5 mm) est la solution parfaite.

### 💪 Bras / Humérus (Épaule → Coude)
- **Contexte** : Relie l'épaule (RS-03) au coude (RS-02).
- **Efforts** : Principalement de la flexion (porter la charge) et de la torsion.
- **Verdict** : Un **Tube Carbone de Ø35 mm ou Ø40 mm** est tout à fait applicable. Les inserts CNC en aluminium (avec goupille Mécanindus travaillant en cisaillement) feront parfaitement la liaison avec les faces planes des moteurs RS.

**Bénéfice global pour les bras** : En marche dynamique, le balancement des bras agit comme un pendule d'équilibrage pour contrecarrer le lacet du bassin. Des bras plus légers permettent une oscillation beaucoup plus rapide sans générer de forces perturbatrices massives sur le buste.

---

## 2. Extension au Fémur (Cuisse) : Mitigé / Complexe ⚠️

L'application du tube carbone au fémur semble intuitive pour gagner du poids, mais elle se heurte à plusieurs défis d'architecture de haut niveau.

### 🚫 Problème 1 : L'encombrement et la géométrie des interfaces
- Le fémur doit relier la **Hanche** (gros bloc de 2 moteurs orientés à 90°) au **Genou** (Moteur RS-04, potentiellement doublé d'un mécanisme SEA ou d'une poulie).
- Ces articulations demandent des points de fixation très larges (les "Brackets" de hanche et de genou en forme de "U" ou "H").
- **Conséquence** : Transférer l'effort de ces immenses brackets vers un tube cylindrique étroit (Ø40 ou Ø50 mm) au centre demanderait des inserts massifs en forme d'entonnoir en aluminium usiné CNC. Le poids gagné par le tube carbone risque d'être totalement perdu par le poids des énormes adaptateurs en aluminium haut et bas.

### 🚫 Problème 2 : L'intégration globale (câblage, électronique)
- Le fémur n'est pas qu'un os : dans les robots bipèdes modernes, c'est l'endroit idéal pour loger les contrôleurs moteurs, acheminer les nappes de câbles (hanche → genou → cheville) cachées sous des coques de protection.
- Un simple tube cylindrique rond empêche tout montage propre d'électronique et rend le "cable routing" (routage des câbles) affreux (tout courrait à l'extérieur, exposé aux chocs).

### 📐 Les vraies solutions pour le Fémur : "Poutre en U" ou "Treillis 3D"
Pour résoudre ces problèmes, l'ingénierie biomimétique privilégie deux architectures robustes :

#### Solution 1 : La Poutre en U (Aluminium CNC)

![Fémur : Poutre en U Aluminum](./img_femur_poutre_u.png)

Un profilé large et évidé en Aluminium 6061-T6 usiné à la CNC (C500). 
*   **Rigidité** : Extrêmement rigide en flexion.
*   **Intégration** : Il offre de très larges surfaces planes en haut et en bas pour visser les énormes brackets des moteurs de Hanche et de Genou.
*   **Électronique** : Sa cavité interne est parfaite pour loger les PCB de puissance et faire passer les câbles proprement, protégés des chocs par une coque d'habillage externe en impression 3D (PA12-CF).

#### Solution 2 : L'Exosquelette Treillis (Plaques Carbone + Aluminium)

![Fémur : Exosquelette Treillis Carbone](./img_femur_treillis.png)

Plutôt qu'un tube rond, on utilise des matériaux composites plats pour former une "boîte" ou 3D Truss :
*   **Structure** : Deux épaisses plaques parallèles (gauche/droite) en Fibre de Carbone (usiné à la CNC), reliées entre elles par des entretoises horizontales en aluminium.
*   **Interfaces** : Des blocs massifs (inserts) en Aluminium usiné sont pris en sandwich entre les plaques en haut et en bas pour fournir l'ancrage rigide aux moteurs.
*   **Avantage** : Ultra-léger, très rigide en torsion, tout en préservant un espace vide central pour le cheminement des câbles.

**Verdict Fémur** : Le tube carbone rond est inadapté à la cuisse. Si l'on veut utiliser du carbone, il faudra concevoir le fémur avec **des plaques de carbone planes (Solution 2)**, ou privilégier l'usinage monolithique d'une **poutre en U en aluminium (Solution 1)**.

---

## Conclusion

| Membre | Recommandation | Argument principal |
|---|---|---|
| **Tibia (Sous Genou)** | **Tube Carbone (approuvé)** | Réduction drastique inertie distale, géométrie tubulaire idéale et efforts rectilignes. |
| **Bras / Humérus** | **Tube Carbone (très recommandé)** | Réduction du poids en pendule, efforts modérés, brackets CNC simples avec goupille. |
| **Avant-Bras** | **Tube Carbone (très recommandé)** | Géométrie droite simple (coude → poignet), portage ~2 kg ne stressant pas la goupille. |
| **Fémur (Cuisse)** | **Déconseillé (Profilé U ou treillis préférable)** | Interfaces de genou/hanche trop larges pour un tube. Impossible d'y loger câbles/électronique proprement. |

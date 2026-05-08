# SYNTHÈSE : Architecture Bras & Avant-Bras (Biomimétique)

## 1. Concept de "Supination Déportée"
Le D-Bot adopte une architecture inspirée du Tesla Optimus Gen 3, où la rotation de la main (Roll) est effectuée en amont de l'avant-bras pour éviter le vrillage des tendons.

| Composant | Modèle | Fonction | Justification |
| :--- | :--- | :--- | :--- |
| **Coude Pitch** | **RS-06** | Flexion du bras | 36 N.m pour manipuler 8-10 kg bras plié |
| **Supination (Roll)** | **RS-02** | Rotation avant-bras | Situé juste après le coude. Fait tourner tout l'avant-bras. |
| **Poignet Pitch** | **RS-00** | Inclinaison main | 14 N.m. Seul moteur situé à l'extrémité distale. |

## 2. Découplage Mécanique (Palier de support)
L'avant-bras est une structure rotative indépendante de l'axe moteur :
- **Support** : Un roulement à section fine (Thin Section Bearing) encaisse 100% des contraintes de levier et de poids.
- **Torsion** : Le moteur **RS-02** ne transmet que le couple de rotation via un accouplement flexible.
- **Résultat** : Protection totale des roulements internes du moteur contre les charges radiales (>10 N.m).

## 3. Avantages Cinématiques
- **DOF** : 6 DOF par bras (Épaule 3 + Coude 1 + Supination 1 + Poignet 1).
- **Esthétique** : Poignet extrêmement fin (proche de l'humain).
- **IA/RL** : Parfaite compatibilité avec les modèles d'apprentissage "sim-to-real" (structure isomorphique à Optimus).
- **Inertie** : Recentrage des masses lourdes vers le coude, facilitant le balancement des bras.

## 4. Intégration D-Hand
- Les 8 servomoteurs de la main (**4× XC430 + 4× XC330**) sont logés *à l'intérieur* de la structure rotative de l'avant-bras.
- Ils tournent avec l'avant-bras, garantissant que les tendons Dyneema ne se vrillent jamais.

---
*Dernière mise à jour : Mai 2026*

# SYNTHÈSE : Architecture Cheville (D-Bot)

## 1. Actionneurs & Différentiel (RobStride)
La cheville abandonne le montage direct pour une architecture différentielle déportée, libérant le bas du tibia de toute masse morte.

| Composant | Modèle | Couple Combiné (Pic) |
| :--- | :--- | :---: |
| **Moteurs (2x)** | **RobStride RS-03** | **120 N.m** (Pitch & Roll) |

## 2. Transmission (Cardan & Bielles)
- **Cœur Mécanique** : **Joint de Cardan DIN 808 Série G** (Acier C45, axe 12mm).
- **Liaison** : Deux bielles parallèles (carbone Ø10/8mm) reliant les moteurs au plateau du pied.
- **Différentiel** : 
    - Mouvements identiques = **Pitch** (flexion/extension, +30°/−45°).
    - Mouvements opposés = **Roll** (inversion/éversion, ±25°).

## 3. Conception Mécanique
- **Masse distale** : Gain de **-310g** en bas de jambe par rapport au K-Bot.
- **Composants** : Rotules **Igus EBRM-05**, Cardan Michaud Chailly.
- **Structure** : Montage par bagues d'arrêt et axes 12.9 pour encaisser les 120 N.m.

## 4. Performances & Limites
- **Marge Statique** : **+167%** (120 N.m dispo vs 38.3 N.m requis pour 39 kg).
- **Vitesse** : Capacité de marche rapide jusqu'à 6-9 km/h théoriques.
- **Stabilité** : Couple de Roll exceptionnel (×8 vs K-Bot) pour le rattrapage d'équilibre.

---
### 🔗 Études Complètes
- **[20 — Étude Cheville Cardan](../20_Etude_Cheville_Cardan.md)**
- **[15c — Révision Cardan (Impact 39 kg)](../15c_Revision_Cardan_39kg.md)**
- **[16 — Conclusions Architecture Finale](../16_Conclusions_Architecture_DBot.md)**

*Dernière mise à jour : Mars 2026*

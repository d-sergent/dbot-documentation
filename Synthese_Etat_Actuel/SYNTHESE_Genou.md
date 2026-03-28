# SYNTHÈSE : Architecture Genou (D-Bot)

## 1. Actionneur & Amplification (RobStride + GT3)
Le genou utilise une solution de relocalisation du moteur pour amplifier le couple et réduire l'inertie de balancement (Swing Inertia).

| Composant | Modèle | Caractéristique |
| :--- | :--- | :--- |
| **Moteur** | **RobStride RS-04** | Relocalisé en haut de cuisse (sous la hanche) |
| **Transmission** | **Courroie GT3 (9mm)** | Réduction synchrone |
| **Rapport** | **2.5 : 1** | Pignon 20 dents (moteur) / 50 dents (genou) |
| **Couple Final** | **300 N.m (Pic)** | Amplification massive (+150% vs direct-drive) |

## 2. Cinématique & Dynamique
- **Entraxe** : ~250mm entre le moteur et l'axe du genou.
- **Vitesse Max** : 67 RPM (suffisant pour une marche rapide à 5-6 km/h et course légère).
- **Inertie** : Le déplacement du moteur RS-04 (1.4 kg) vers le haut de la cuisse transforme radicalement la dynamique du robot.

## 3. Conception Mécanique
- **Composants** : Pignons Alu GT3, Courroie fermée Gates/Continental.
- **Tension** : Galet tendeur à ressort permanent pour annuler le backlash (~0.5-1°).
- **Structure** : Double flasque de cuisse en carbone ou sandwich Alu prenant en charge les pignons.

## 4. Performances & Limites
- **Marche normale** : Opère à seulement 39% du couple nominal (thermique négligeable).
- **Portage** : Capable de marcher avec **20 kg de payload** additionnelle.
- **Sécurité** : Marge de 42% même lors des pics de course saccadée (172 N.m requis).

---
### 🔗 Études Complètes
- **[15g — Solution S6 : Courroie GT3 Genou](../15g_Solution_S6_Courroie_GT3_Genou.md)**
- **[15d — Genou et Course : Solutions](../15d_Genou_et_Course.md)**
- **[16 — Conclusions Architecture Finale](../16_Conclusions_Architecture_DBot.md)**

*Dernière mise à jour : Mars 2026*

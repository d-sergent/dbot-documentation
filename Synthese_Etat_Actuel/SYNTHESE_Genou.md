# SYNTHÈSE : Architecture Genou (D-Bot)

## 1. Actionneur & Amplification (RobStride + GT3)
Le genou utilise une solution de relocalisation du moteur pour amplifier le couple et réduire l'inertie de balancement (Swing Inertia).

| Composant | Modèle | Caractéristique |
| :--- | :--- | :--- |
| **Moteur** | **RobStride RS-04** | Relocalisé en haut de cuisse via la courroie GT3 |
| **Transmission** | **Courroie GT3 (9mm)** | Réduction synchrone |
| **Rapport** | **2.5 : 1** | Pignon 20 dents (moteur) / 50 dents (genou) |
| **Couple Final** | **300 N.m (Pic)** | Amplification massive (+150% vs direct-drive) |

## 2. Cinématique & Dynamique
- **Entraxe** : ~400mm entre le moteur (haut cuisse) et l'axe du genou.
- **Vitesse Max** : 67 RPM (suffisant pour marche rapide 5-6 km/h et course légère).
- **Inertie** : Le déplacement du RS-04 Knee (1.4 kg) vers le haut de la cuisse réduit significativement l'inertie de balancement. Note : en architecture **F-A-R**, le RS-04 Hip Pitch est situé **dans le bassin** (Maillon 1). Le RS-04 Knee est le seul moteur relocalisé dans le haut de la cuisse — les deux RS-04 sont dans des zones distinctes, sans conflit d'encombrement.

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
- **[15d — Genou — Analyse & Solution GT3](../15d_Genou_et_Course.md)** ← document principal — 15d+15g fusionnés (Avril 2026)
- **[16 — Conclusions Architecture Finale](../16_Conclusions_Architecture_DBot.md)**

*Dernière mise à jour : Mars 2026*

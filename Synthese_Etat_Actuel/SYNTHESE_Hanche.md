# SYNTHÈSE : Architecture Hanche (D-Bot)

## 1. Actionneurs (RobStride)
La hanche adopte une architecture séquentielle (type Tesla Optimus) pour maximiser la robustesse et la simplicité de fabrication.

| Axe | Moteur | Couple (Pic) | Couple (Nominal) | Rôle |
| :--- | :--- | :---: | :---: | :--- |
| **Yaw (Z)** | **RobStride RS-03** | 60 N.m | 20 N.m | Rotation interne/externe (Fixé au bassin) |
| **Roll (X)** | **RobStride RS-03** | 60 N.m | 20 N.m | Stabilité latérale |
| **Pitch (Y)** | **RobStride RS-04** | **120 N.m** | 40 N.m | Propulsion et levage fémur |

## 2. Transmission & Cinématique
- **Type** : Séquentiel à 3 DOF (Maillon 1: Yaw → Maillon 2: Roll → Maillon 3: Pitch).
- **Liaison Fémur** : Le dernier moteur (RS-04 Pitch) est pris en "sandwich" par les plaques latérales du fémur hybride.
- **Concentration des masses** : Moteurs regroupés au plus près du centre de gravité pour minimiser l'inertie de balancement.

## 3. Conception Mécanique
- **Matériau** : Aluminium **7075-T6** (haute résistance) pour les brackets de liaison.
- **Usinage** : Fabrication CNC sur C500.
- **Structure** : Squelette en équerre ultra-rigide pour encaisser les 120 N.m de propulsion.

## 4. Performances & Limites
- **Stabilité** : Couple de Roll (60 N.m) très supérieur au standard K-Bot.
- **Propulsion** : Le RS-04 Pitch permet des accélérations franches pour la marche rapide (5-7 km/h).

---
### 🔗 Études Complètes
- **[26 — Étude Bloc Pelvien Hanche](../26_Etude_Bloc_Pelvien_Hanche.md)**
- **[16 — Conclusions Architecture Finale](../16_Conclusions_Architecture_DBot.md)**

*Dernière mise à jour : Mars 2026*

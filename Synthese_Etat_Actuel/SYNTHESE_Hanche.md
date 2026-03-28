# SYNTHÈSE : Architecture Hanche (D-Bot)

## 1. Actionneurs (RobStride)
La hanche adopte une architecture séquentielle (type Tesla Optimus) pour maximiser la robustesse et la simplicité de fabrication.

| Axe | Moteur | Couple (Pic) | Couple (Nominal) | Rôle |
| :--- | :--- | :---: | :---: | :--- |
| **Yaw (Z)** | **RobStride RS-03** | 60 N.m | 20 N.m | Rotation interne/externe (Fixé au bassin) |
| **Roll (X)** | **RobStride RS-03** | 60 N.m | 20 N.m | Stabilité latérale |
| **Pitch (Y)** | **RobStride RS-04** | **120 N.m** | 40 N.m | Propulsion et levage fémur |

## 2. Transmission & Cinématique
- **Type** : Séquentiel à 3 DOF.
- **Liaison Fémur** : Le dernier moteur (RS-04 Pitch) est pris en "sandwich" par les plaques latérales du fémur hybride.
- **Concentration des masses** : Les moteurs sont regroupés au plus près du centre de gravité du bassin pour réduire l'inertie des jambes.

## 3. Conception Mécanique
- **Matériau** : Aluminium **7075-T6** (haute résistance) pour les brackets de liaison.
- **Usinage** : Fabrication CNC sur C500 (Brackets courts de 5-8 cm).
- **Structure** : Équerres de type "Yaw-Roll" et "Roll-Pitch" ultra-rigides.

## 4. Performances & Limites
- **Stabilité** : Couple de Roll (60 N.m) très supérieur au standard K-Bot, garantissant un excellent équilibre dynamique.
- **Propulsion** : Le RS-04 Pitch permet des accélérations franches pour la marche rapide.

---
*Dernière mise à jour : Mars 2026*

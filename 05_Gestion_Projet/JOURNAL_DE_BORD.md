# 📓 JOURNAL DE BORD DU PROJET D-BOT

Ce document répertorie l'historique chronologique et détaillé des sessions de travail, des tests physiques réalisés, des bugs identifiés et des validations sur le robot D-Bot.

---

## 📅 2026-07-20 — Consolidation Master V1, Web UI Motorbridge & Formalisation RAG

### 🎯 Objectif de la session
1. Analyser et valider le document maître `FINAL_Architecture_Master_V1_Hybride.md`.
2. Restructurer le suivi du projet via un **Journal de Bord** et une **Roadmap de dépendances logiques**.
3. Développer et qualifier le serveur Web UI Motorbridge pour l'asservissement et le diagnostic des 2 moteurs RS-05 du cou.

### 📝 Réalisations & Évolutions
1. **Audit de l'Architecture Master V1 Hybride** :
   - Confirmation de la répartition "Réflexe Local (Jetson Orin Nano 8 Go) ↔ Cognition Déportée (Mac M1 Max 64 Go)".
   - Validation de la marge VRAM Jetson à 32 % (2,9 Go alloués sur 5,5 Go utiles).
2. **Création des Documents de Suivi Inter-Session** :
   - [`05_Gestion_Projet/JOURNAL_DE_BORD.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/05_Gestion_Projet/JOURNAL_DE_BORD.md) : Historique daté.
   - [`05_Gestion_Projet/ROADMAP_STRATEGIQUE_V1.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/05_Gestion_Projet/ROADMAP_STRATEGIQUE_V1.md) : Graphe des niveaux de dépendance 0 à 4.
   - Marge des règles `.agents/AGENTS.md` pour imposer la lecture/mise à jour du Journal et de la RAG à chaque session.
3. **Développement du Serveur Motorbridge Web UI ([Code/dbot/motors/web_ui.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/motors/web_ui.py))** :
   - Développement d'un serveur HTTP multithreadé non-bloquant sur le port `8080` de la Jetson.
   - Interface Web HTML5/CSS/JS (Dark mode / Glassmorphism) accessible depuis le Mac via `http://ubuntu.local:8080`.
   - Télémétrie CAN en temps réel (Positions Pan/Tilt, Vitesses, Voltage Vbus 48V, statut des moteurs ID:1 et ID:2).
   - Commandes interactives : Sliders bornés aux limites mécaniques de `config.py` (Pan: [-80°, +80°], Tilt: [-20°, +30°]), Bouton Recentrer, et Bouton d'Arrêt d'Urgence (**E-STOP**).

### 📌 Statut Matériel Actuel
- **Moteurs branchés** : 2x RobStride RS-05 (Cou Pan ID:1 & Tilt ID:2) connectés à la carte InnoMaker `can0`.
- **Serveur Web UI** : Qualifié et compilé avec succès (`web_ui.py`).

### ➡️ Prochaine Étape Immédiate
1. Exécuter `python3 Code/dbot/motors/web_ui.py` sur la Jetson (ou via SSH).
2. Ouvrir `http://ubuntu.local:8080` sur le Mac pour vérifier le retour télémétrique des 2 RS-05.
3. Démonter le casque et tester le mouvement contrôlé sans obstacle.

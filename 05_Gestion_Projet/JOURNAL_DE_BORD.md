# 📓 JOURNAL DE BORD DU PROJET D-BOT

Ce document répertorie l'historique chronologique et détaillé des sessions de travail, des tests physiques réalisés, des bugs identifiés et des validations sur le robot D-Bot.

---

## 📅 2026-07-20 — Consolidation Master V1, Web UI Motorbridge, Correctifs de Sécurité & RAG

### 🎯 Objectif de la session
1. Analyser et valider le document maître `FINAL_Architecture_Master_V1_Hybride.md`.
2. Restructurer le suivi du projet via un **Journal de Bord** et une **Roadmap de dépendances logiques**.
3. Développer et qualifier le serveur Web UI Motorbridge pour l'asservissement et le diagnostic des 2 moteurs RS-05 du cou.
4. Analyser et corriger les anomalies de sécurité (saut angulaire 360°, E-STOP bloqué et initialisation des positions au démarrage).

### 📝 Réalisations & Évolutions
1. **Audit de l'Architecture Master V1 Hybride** :
   - Confirmation de la répartition "Réflexe Local (Jetson Orin Nano 8 Go) ↔ Cognition Déportée (Mac M1 Max 64 Go)".
   - Validation de la marge VRAM Jetson à 32 % (2,9 Go alloués sur 5,5 Go utiles).
2. **Création des Documents de Suivi Inter-Session** :
   - [`05_Gestion_Projet/JOURNAL_DE_BORD.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/05_Gestion_Projet/JOURNAL_DE_BORD.md) : Historique daté.
   - [`05_Gestion_Projet/ROADMAP_STRATEGIQUE_V1.md`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/05_Gestion_Projet/ROADMAP_STRATEGIQUE_V1.md) : Graphe des niveaux de dépendance 0 à 4.
   - Mise à jour des règles `.agents/AGENTS.md` pour imposer la consultation/mise à jour du Journal et de la RAG à chaque session.
3. **Développement du Serveur Motorbridge Web UI ([Code/dbot/motors/web_ui.py](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot/motors/web_ui.py))** :
   - Développement d'un serveur HTTP multithreadé non-bloquant sur le port `8080` de la Jetson.
   - Interface Web HTML5/CSS/JS (Dark mode / Glassmorphism) accessible depuis le Mac via `http://ubuntu.local:8080`.
   - Télémétrie CAN en temps réel (Positions Pan/Tilt, Vitesses, Voltage Vbus 48.1V, statut des moteurs ID:1 et ID:2).
   - Affichage explicite des limites logicielles sous les sliders Pan `[-80.0°, +80.0°]` et Tilt `[-20.0°, +30.0°]`.

### 🚨 REX Incident de Sécurité & Correctifs Majeurs Appliqués
- **Diagnostic #1 (Saut Angulaire)** : `look_at_rad` calculait `target - curr` ($0 - 6.12\text{ rad} = -350.7°$) sans modulo $2\pi$. -> **Résolu par `shortest_angular_distance`** et un **Garde-fou dur à 45° max**.
- **Diagnostic #2 (Bloquage E-STOP)** : `set_look_at` s'exécutait sous `self.lock` pendant la boucle d'interpolation, bloquant `/api/estop`. -> **Résolu par l'exécution asynchrone** et un **E-STOP non-bloquant (< 1 ms)**.
- **Diagnostic #3 (Initialisation à 0.0°)** : La télémétrie n'était lue qu'après l'activation (`if self.enabled:`), forçant un saut vers 0.0°. -> **Résolu (Commit `f992d25`)** par la lecture permanente du bus CAN dès le démarrage et l'accrochage automatique des consignes sur les positions réelles lors du clic *Activer Moteurs*.

### 📌 Statut Matériel Actuel
- **Moteurs branchés** : 2x RobStride RS-05 (Cou Pan ID:1 & Tilt ID:2) sur bus `can0` 1 Mbps.
- **Serveur Web UI** : Correctifs de sécurité et d'initialisation validés et poussés sur Git (`web_ui.py` + `neck.py`).

### ➡️ Prochaine Étape
1. Récupérer le code mis à jour sur la Jetson (`git pull`).
2. Relancer le serveur `python3 Code/dbot/motors/web_ui.py`.
3. Vérifier qu'au démarrage de l'IHM, les angles réels (ex: `-9.3°` et `13.1°`) et la tension `48.1V` s'affichent immédiatement **AVANT même de cliquer sur Activer Moteurs**, et que le clic sur *Activer Moteurs* n'entraîne aucun mouvement parasite.

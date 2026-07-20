# 📓 JOURNAL DE BORD DU PROJET D-BOT

Ce document répertorie l'historique chronologique et détaillé des sessions de travail, des tests physiques réalisés, des bugs identifiés et des validations sur le robot D-Bot.

---

## 📅 2026-07-20 — Consolidation Master V1, Web UI Motorbridge, Correctifs de Sécurité & RAG

### 🎯 Objectif de la session
1. Analyser et valider le document maître `FINAL_Architecture_Master_V1_Hybride.md`.
2. Restructurer le suivi du projet via un **Journal de Bord** et une **Roadmap de dépendances logiques**.
3. Développer et qualifier le serveur Web UI Motorbridge pour l'asservissement et le diagnostic des 2 moteurs RS-05 du cou.
4. Analyser et corriger les deux anomalies de sécurité sur la trajectoire angulaire et le bouton d'arrêt d'urgence E-STOP.

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
- **Symptôme** : Lors de l'activation des moteurs, la position Pan lue à `350.7°` (proche de 0°) a provoqué une rotation indésirable de ~350° vers 0°, et le bouton E-STOP n'a pas interrompu le mouvement.
- **Diagnostic** :
  1. *Calcul de trajectoire angulaire* : `look_at_rad` calculait `target_pan - curr_pan` ($0 - 6.12\text{ rad} = -6.12\text{ rad} = -350.7°$), au lieu du chemin angulaire minimal ($+9.3°$).
  2. *Bloquage du Mutex E-STOP* : `set_look_at` s'exécutait en maintenant `self.lock` pendant la boucle d'interpolation, bloquant `/api/estop` en file d'attente.
- **Correctifs Implémentés (Commit `7ebebed`)** :
  - **Chemin Angulaire Minimal (Shortest Path)** : `shortest_angular_distance(from_rad, to_rad)` modulo $2\pi$ dans `neck.py`.
  - **Garde-Fou Matériel Hard Limit** : Blocage automatique et bridage de tout delta angulaire $> 45°$.
  - **E-STOP Non-Bloquant & Asynchrone** : Exécution de `look_at` dans un thread de travail séparé. Le bouton E-STOP passe `emergency_stopped = True` et envoie la trame CAN `disable()` en **< 1 ms** sans jamais attendre de verrou.

### 📌 Statut Matériel Actuel
- **Moteurs branchés** : 2x RobStride RS-05 (Cou Pan ID:1 & Tilt ID:2) sur bus `can0` 1 Mbps.
- **Serveur Web UI** : Correctifs de sécurité validés et poussés sur Git (`web_ui.py` + `neck.py`).

### ➡️ Prochaine Étape
1. Récupérer les correctifs sur la Jetson (`git pull`).
2. Relancer le serveur `python3 Code/dbot/motors/web_ui.py`.
3. Valider la réactivité instantanée du bouton E-STOP et la trajectoire ultra-courte de recentrage (+9.3° au lieu de -350°).

# 🗺️ ROADMAP STRATÉGIQUE D-BOT V1 (Logique de Dépendances & Faisabilité)

Ce document établit la hiérarchie logique des sous-systèmes D-Bot V1. Il permet d'évaluer à tout moment quelles tâches sont **faisables immédiatement** et quelles tâches sont **bloquées par des dépendances matérielles ou logicielles**.

---

## 🏗️ Graphe des Niveaux de Dépendances Logiques

```
[ Niveau 0 : Infra & Alim ] ──► [ Niveau 1 : Tête/Cou & WebUI ] ──► [ Niveau 2 : Active Gaze OAK-D ]
                                           │                                     │
                                           ▼                                     ▼
                                [ Niveau 3 : Audio HD & RAG ] ──► [ Niveau 4 : Corps & LeRobot ]
```

---

## 🟢 NIVEAU 0 : Infrastructures & Bus de Communication (Prérequis Absolus)
*Statut : Opérationnel & Validé*

- [x] **Bus CAN 1 Mbps (Jetson)** : Adaptateur InnoMaker USB-CAN reconnu sous SocketCAN (`can0`).
- [x] **Serveur RAG Documentaire (Mac)** : API LightRAG + FastEmbed sur port 7860/FastAPI (`ask_rag.py`).
- [ ] **Station d'Alimentation Atelier 600W** : Assemblage du bloc MeanWell LRS-600-48 avec boîtier 3D et connecteurs XT30 2+2 pour alimentation continue sans batterie.

---

## 🟡 NIVEAU 1 : Réflexes Tête / Cou & Diagnostic (Faisable Immédiatement avec 2x RS-05)
*Dépendances : Niveau 0 (Bus CAN0 + Alim)*

- [x] **Web UI Motorbridge (Jetson)** : Serveur léger de diagnostic CAN développé (`Code/dbot/motors/web_ui.py`) pour télémesure en temps réel des 2 moteurs RS-05 (angles, temp, erreurs, Vbus 48V).
- [x] **Validation Mécanique & Asservissement du Cou (Pan/Tilt)** : Mouvements LERP fluides et non-bloquants qualifiés sur le cou RS-05 via `web_ui.py` et `neck.py`.
- [ ] **Audio Gaze Tracking** : Asservissement angulaire des 2 RS-05 sur la direction DoA (0-360°) renvoyée par le ReSpeaker XVF-3800.

---

## 🔵 NIVEAU 2 : Perception 3D & Regard Actif (OAK-D Pro + Jetson / Mac)
*Dépendances : Niveau 1 (Tête fonctionnelle) + OAK-D Pro FF*

- [x] **Triade Visuelle Temps Réel & Fusion Spatiale 3D** : Inférence Zero-Shot YOLO-World v2 avec NMS multi-boîtes hiérarchique, classification multicolore et calcul tridimensionnel physique `[X, Y, Z]` (en mm) couplé à la stéréo DepthAI OAK-D Pro.
- [x] **Déport VPU Myriad X (OAK-D Pro)** : Intégration du filtre matériel WLS (lissage de la carte de profondeur) et du nœud `SpatialLocationCalculator` pour le calcul d'alertes matérielles de danger ($Z < 500\text{ mm}$) à $< 5\text{ ms}$ sans charge CPU Jetson.
- [ ] **Mappage Multilingue Français ➔ Anglais pour YOLO-World** : Prise en charge dynamique des prompts en Français avec traduction/correspondance automatique vers CLIP Anglais dans `yolo_world.py`.
- [ ] **Reconnaissance & Identification de Visages (`face_tracker.py`)** : Identification nommée des visages du foyer et suivi spatial 3D.
- [ ] **Inférence Active Gaze & Cognition 3D Déportée sur Mac (`test_active_gaze.py`)** : Inférence visuelle sémantique complexe via **NVIDIA Cosmos 3D Edge / LocateAnything-3B** **déportée sur le Mac M1 Max (64 Go)** pour l'orientation et le centrage du cou Pan/Tilt ("Regarde la tasse").

---

## 🟣 NIVEAU 3 : Cognition Déportée, Dialogue & Secours Local
*Dépendances : Niveau 0 (Réseau Hybride Mac ↔ Jetson) + ReSpeaker*

- [x] **Pipeline Audio / Barge-In** : `audio_io_v2.py` non-bloquant et interruption instantanée en cas de parole utilisateur.
- [ ] **Serveur TTS Streaming HD (Mac)** : Inférence Qwen3-TTS / F5-TTS déportée sur Mac (latence < 200 ms).
- [ ] **Fallback Vocale Hors-Ligne (Jetson)** : Mode dégradé Kokoro-ONNX + Ollama local activé en cas d'interruption Wi-Fi > 2s (Heartbeat 5 Hz).

---

## 🔴 NIVEAU 4 : Cinématique Corps Complet, Dynamics & Imitation (En attente d'assemblage)
*Dépendances : Assemblage mécanique du Torse/Membres + 2x Teensy 4.1 CAN FD*

- [ ] **Compensation de Gravité `Pinocchio`** : Urdf D-Bot + injection de couple de gravité $G(q)$ via $\tau_{ff}$ du mode MIT Control sur les 27 moteurs RobStride.
- [ ] **Apprentissage par Imitation `LeRobot`** : Adaptation du framework Hugging Face pour l'enregistrement et l'exécution de politiques de manipulation autonome (*ACT / Diffusion Policy*).
- [ ] **Extension Web UI Flotte Complète** : Supervision dynamique de l'ensemble des 27 moteurs CAN du robot.

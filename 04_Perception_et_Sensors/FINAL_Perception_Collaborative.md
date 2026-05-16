# FINAL - Perception Collaborative (Cascade de Vision)

Le D-Bot utilise une architecture de vision en "cascade" pour optimiser la sécurité sans saturer les processeurs.

## 1. Niveaux de Perception

### Niveau 1 : Détection Réflexe (Spresense)
*   **Capteur** : Caméra HDR (Bassin).
*   **Algorithme** : Modèle CNN léger (TensorFlow Lite Micro) entraîné sur la segmentation du sol.
*   **Fonctionnement** : Analyse locale en basse résolution (96x96 ou 224x224).
*   **Seuil d'alerte** : Si un objet inconnu occupe >10% de la zone "Proche" (0-40cm des pieds).
*   **Action immédiate** : Envoi d'un flag d'interruption à la Jetson via USB-Serial.

### Niveau 2 : Confirmation Cognitive (Jetson & OAK-D)
*   **Réception de l'alerte** : La Jetson reçoit le flag `OBSTACLE_NEAR`.
*   **Pilotage du Cou** : La Jetson commande le moteur RS-05 (Tilt) pour incliner la tête vers la zone signalée par la Spresense.
*   **Validation HD** : L'OAK-D Pro effectue une analyse de profondeur (Active Stereo IR) pour vérifier la matérialité de l'obstacle.
    *   *Cas A (Réel)* : Obstacle confirmé en 3D -> Recalcul de trajectoire (Navigation).
    *   *Cas B (Faux Positif)* : Ombre ou reflet -> La Spresense est réinitialisée, la marche continue.

### Niveau 3 : Réflexe de Survie (Watchdog)
Si la Spresense détecte que la distance à l'obstacle tombe sous un seuil critique (**< 15cm**) alors que le robot est en mouvement, elle peut forcer un **Arrêt d'Urgence (E-Stop)** via le Bus CAN sans attendre la confirmation de la Jetson. C'est la protection ultime contre les collisions.

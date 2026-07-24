# 🛠️ dbot_next.scripts — Scripts de Gestion & Boucle Conversationnelle

Ce dossier regroupe les scripts d'administration du serveur Mac et la boucle conversationnelle interactive autonome de la Jetson.

---

## 📄 Fichiers & Rôles

| Fichier | Cible | Description |
| :--- | :--- | :--- |
| **[`start_companion_server.sh`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot_next/scripts/start_companion_server.sh)** | **Mac** | Gestionnaire de service du serveur compagnon (`--start`, `--restart`, `--stop`, `--status`, `--logs`). Gère la rotation des logs et l'attente du démarrage. |
| **[`test_companion_streaming.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/dbot_next/scripts/test_companion_streaming.py)** | **Jetson** | Boucle conversationnelle interactive autonome. Mesure le bruit ambiant, applique la VAD RMS adaptative (150 RMS min), gère le pre-roll et la VAD anti-auto-interruption pendant la réponse du robot. |

---

## ⚡ Exécution

### Sur le Mac Compagnon
```bash
./Code/dbot_next/scripts/start_companion_server.sh --restart
```

### Sur la Jetson Orin Nano
```bash
python3 code/dbot_next/scripts/test_companion_streaming.py
```

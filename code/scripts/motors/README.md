# ⚙️ scripts/motors — Scripts de Qualification des Moteurs RobStride

Ce dossier regroupe les scripts de test et de qualification physique des actionneurs RobStride du cou (RS-05) et du corps.

---

## 📄 Fichiers & Procédures

| Script | Utilisation & Commande |
| :--- | :--- |
| **[`test_neck.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/motors/test_neck.py)** | **Test dynamique du cou Pan/Tilt**. Valide les rotations de la tête sans casque, avec vitesse max limitée à 20°/s et vérification des butées logicielles.<br>`python3 code/scripts/motors/test_neck.py` |
| **[`ota_update.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/motors/ota_update.py)** | **Mise à jour firmware OTA via SocketCAN (Linux / Jetson)**. Adapte le script officiel `OTA.py` (1 Mbps obligatoire pendant l'OTA).<br>`python3 Code/scripts/motors/ota_update.py --id 1 --bin <fichier.bin>` |

---

## ⚡ Test Rapide du Cou

```bash
python3 code/scripts/motors/test_neck.py
```

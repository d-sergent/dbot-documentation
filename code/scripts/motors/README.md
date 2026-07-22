# ⚙️ scripts/motors — Scripts de Qualification des Moteurs RobStride

Ce dossier regroupe les scripts de test et de qualification physique des actionneurs RobStride du cou (RS-05) et du corps.

---

## 📄 Fichiers & Procédures

| Script | Utilisation & Commande |
| :--- | :--- |
| **[`test_neck.py`](file:///Users/Shared/Mon%20Google%20Drive%20Physique/Documentation/Code/scripts/motors/test_neck.py)** | **Test dynamique du cou Pan/Tilt**. Valide les rotations de la tête sans casque, avec vitesse max limitée à 20°/s et vérification des butées logicielles.<br>`python3 code/scripts/motors/test_neck.py` |

---

## ⚡ Test Rapide du Cou

```bash
python3 code/scripts/motors/test_neck.py
```

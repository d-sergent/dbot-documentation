# 46 — Analyse SDK Officiel ReSpeaker XVF3800 & Feuille de Route

*Date d'analyse : 10 Mai 2026 — Basé sur les sources officielles Seeed Studio*

---

## Sources de Référence

- **[Wiki Introduction](https://wiki.seeedstudio.com/respeaker_xvf3800_introduction/)** : Guide de démarrage, hardware, firmware, GPIO.
- **[Wiki Python SDK](https://wiki.seeedstudio.com/respeaker_xvf3800_python_sdk/)** : SDK Python via pyusb pour contrôler le chip XMOS.
- **[GitHub officiel](https://github.com/respeaker/reSpeaker_XVF3800_USB_4MIC_ARRAY)** : Firmwares, scripts Python de contrôle.

---

## 1. État de notre Implémentation vs Wiki Officiel

### ✅ Ce que nous faisons correctement (validé par le wiki)

| Notre implémentation | Recommandation officielle |
| :--- | :--- |
| `arecord -D plughw:X,0 -c 2 -r 16000 -f S16_LE` | Commande identique sur Raspberry Pi/Linux |
| Détection dynamique du numéro de carte via `arecord -l` | Approche recommandée par Seeed |
| Activation de l'ampli via `amixer -c X cset numid=3 on` | Confirmé nécessaire |
| Branchement sur port **USB-A** (pas USB-C) | **USB-C = port XMOS réservé au firmware uniquement** |

> [!IMPORTANT]
> Notre stack audio validée le 10/05/2026 est parfaitement conforme aux recommandations du constructeur pour la capture audio de base.

---

## 2. Informations Clés du Wiki Non Présentes dans notre Documentation

### 2.1 Variantes de Firmware USB

Le firmware USB existe en deux variantes (téléchargeables sur le GitHub officiel) :

| Firmware | Canaux | Fréquence | Usage |
| :--- | :---: | :---: | :--- |
| `usb_dfu_firmware_v2.0.x.bin` | **2 ch** | 16 kHz / 32-bit | ✅ Notre configuration actuelle |
| `usb_dfu_firmware_6chl_v2.0.x.bin` | **6 ch** | 16 kHz / 32-bit | Accès aux micros bruts individuels |

> [!NOTE]
> Le firmware 6 canaux est utile uniquement pour du beamforming personnalisé. Pour D-Bot, le firmware 2 canaux est optimal.

### 2.2 Procédure Safe Mode (Recovery d'urgence)

> [!CAUTION]
> Si le firmware se corrompt ou que le ReSpeaker n'est plus détecté, voici la procédure de récupération :
> 1. Éteindre complètement le robot (débrancher USB).
> 2. **Maintenir le bouton MUTE** enfoncé.
> 3. Rebrancher le câble USB tout en maintenant MUTE.
> 4. La **LED rouge clignote** → le Safe Mode est actif.
> 5. Re-flasher le firmware via DFU : `sudo dfu-util -R -e -a 1 -D firmware.bin`

### 2.3 Bouton MUTE Physique

> [!WARNING]
> Le bouton MUTE **coupe les micros au niveau matériel**. Si l'utilisateur l'actionne accidentellement, le robot devient sourd sans aucun message d'erreur dans les logs Python. Prévoir une surveillance de l'état MUTE dans le code futur.

### 2.4 Bouton RESET Hardware

Un bouton RST permet de redémarrer le chip XVF3800 sans débrancher l'USB. Utile en cas de gel du driver. À utiliser avant de débrancher/rebrancher si le robot semble sourd sans raison.

---

## 3. La Grande Opportunité : SDK Python via pyusb

### 3.1 Principe

Le constructeur expose une **API USB de contrôle direct** du chip XMOS, accessible via la bibliothèque Python `pyusb`. Cette API permet de lire des registres internes du chip en temps réel, **sans passer par ALSA ou PulseAudio**.

```bash
# Installation
pip install pyusb
```

### 3.2 Fonctionnalités Disponibles

| Registre | Type | Description |
| :--- | :---: | :--- |
| `DOA_VALUE` | Lecture | **Angle de la voix** (0-359°) + **Flag VAD** (0 ou 1) |
| `AEC_AZIMUTH_VALUES` | Lecture | Azimuts de beamforming (16 flottants) |
| `VERSION` | Lecture | Version du firmware |
| `REBOOT` | Écriture | Redémarre le chip |
| `led_effect` / `led_color` | Écriture | Contrôle des LEDs RGB |

### 3.3 Impact sur D-Bot

> [!IMPORTANT]
> Le **DOA (Direction of Arrival)** est une fonctionnalité **stratégique pour D-Bot** :
> - Il donne l'angle (0-359°) d'où provient la voix détectée.
> - En le reliant au contrôleur du **cou Pan/Tilt**, le robot peut automatiquement **tourner la tête vers la personne qui lui parle**.
> - Le **VAD matériel** (on-chip) est plus fiable que `webrtcvad` car il intègre déjà l'AEC.

---

## 4. Feuille de Route des Améliorations

### Priorité HAUTE — VAD Matériel + DOA

**Objectif** : Remplacer `webrtcvad` (logiciel) par le VAD on-chip du XVF3800.

**Fichiers créés** (sans modifier l'existant) :
- `code/dbot/audio/respeaker_sdk.py` : Classe d'interface USB avec le chip XMOS.
- `code/dbot/audio/audio_io_v2.py` : Nouvelle version de AudioIO utilisant le SDK.
- `code/scripts/audio/test_respeaker_sdk.py` : Script de validation du SDK.

**Bénéfices** :
- VAD plus précis (AEC intégré dans le chip)
- DOA disponible pour orientation du cou
- Moins de CPU utilisé
- LEDs RGB pilotables pour le feedback visuel

### Priorité MOYENNE — Surveillance de l'état MUTE

**Objectif** : Détecter si le bouton MUTE physique est pressé et logguer un avertissement.

### Priorité BASSE — Firmware 6 canaux

**Objectif** : Explorer le firmware 6 canaux pour accéder aux signaux bruts individuels des 4 micros. Utile pour un beamforming plus avancé à terme.

---

## 5. Comparatif Stack Actuelle vs Stack v2 (SDK)

| Critère | Stack Actuelle (v1) | Stack SDK v2 |
| :--- | :---: | :---: |
| **Capture audio** | `arecord` → stéréo → sox | `arecord` → stéréo → sox (inchangé) |
| **Détection de voix** | `webrtcvad` (logiciel) | VAD on-chip XMOS (matériel) |
| **Direction de la voix** | ❌ Non disponible | ✅ DOA 0-359° |
| **Feedback LEDs** | ❌ Non géré | ✅ Contrôle RGB programmatique |
| **État MUTE** | ❌ Non surveillé | ✅ Détection possible |
| **Dépendances** | `webrtcvad`, `sox` | `pyusb`, `sox` |
| **Stabilité prouvée** | ✅ Testée et validée | 🧪 À valider |

---

*Document créé le 10/05/2026 — À mettre à jour après validation de la stack v2.*

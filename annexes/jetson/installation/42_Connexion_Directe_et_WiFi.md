# Accès Direct (USB/Ethernet) et Configuration Wi-Fi

Il arrive fréquemment, lors de déplacements ou de changements de routeur, que la Jetson perde sa connexion Wi-Fi. Étant un système embarqué sans écran (Headless), il est crucial de savoir s'y connecter directement pour reconfigurer le réseau.

## 1. Accès direct de secours (Sans Wi-Fi)

Si vous ne connaissez plus l'IP de la Jetson, vous pouvez la relier directement à votre ordinateur (Mac/PC) sans passer par une box internet.

### Méthode A : Câble USB-C (Mode "Device") — Recommandé
La NVIDIA Jetson Orin Nano dispose d'une fonction *Device Mode* qui transforme son port USB-C de données en une carte réseau virtuelle.

1. **Branchement :** Reliez le port USB-C de la Jetson (situé sur la tranche arrière) à un port USB de votre Mac/PC avec un câble de **données** (pas un simple câble de charge).
2. **Démarrage :** Allumez la Jetson et patientez environ 1 minute.
3. **Détection :** Votre ordinateur va détecter une nouvelle interface réseau "RNDIS/Ethernet over USB".
4. **Connexion :** La Jetson aura **toujours l'IP fixe `192.168.55.1`** sur ce port.
   Ouvrez votre terminal et tapez :
   ```bash
   ssh david@192.168.55.1
   ```
*(Note : Si vous utilisez NoMachine, vous pouvez entrer cette IP `192.168.55.1` dans l'interface).*

### Méthode B : Câble Ethernet en direct
Si le mode USB ne fonctionne pas, utilisez un câble réseau RJ45 classique.

1. Branchez le câble Ethernet directement entre le Mac et la Jetson.
2. Les deux systèmes vont utiliser une auto-configuration "Link-Local" (Bonjour / mDNS).
3. Connectez-vous via le nom d'hôte local :
   ```bash
   ssh david@ubuntu.local
   ```
   *(Remplacez `ubuntu` par le nom de la machine si vous l'avez changé).*

---

## 2. Configurer le Wi-Fi depuis le terminal

Une fois connecté à la Jetson via l'une des méthodes de secours ci-dessus, vous pouvez la reconnecter à votre nouveau réseau Wi-Fi en utilisant l'outil réseau de ligne de commande Linux (`nmcli`).

### Étape 1 : Activer le Wi-Fi (si éteint)
```bash
sudo nmcli radio wifi on
```

### Étape 2 : Scanner les réseaux disponibles
Pour voir la liste des box et routeurs autour de vous :
```bash
sudo nmcli device wifi list
```
Repérez le nom de votre réseau (le **SSID**).

### Étape 3 : Se connecter au nouveau réseau
Utilisez la commande suivante en remplaçant `<NOM_DU_WIFI>` par le SSID et `<MOT_DE_PASSE>` par la clé de sécurité.
```bash
sudo nmcli device wifi connect "<NOM_DU_WIFI>" password "<MOT_DE_PASSE>"
```

*Exemple :*
`sudo nmcli device wifi connect "Livebox-ABCD" password "1234567890"`

### Étape 4 : Vérifier la connexion et trouver la nouvelle IP
Une fois connecté, vérifiez l'état de la connexion et lisez l'adresse IP attribuée par le réseau Wi-Fi (l'interface s'appelle généralement `wlan0` ou `wlP1p1s0` sur Jetson Orin) :
```bash
# Pour voir toutes les interfaces et chercher la carte Wi-Fi :
ip a

# Ou cibler directement si vous connaissez le nom (ex: wlan0 ou wlP1p1s0) :
ip a s wlP1p1s0
```
Cherchez la ligne contenant `inet 192.168.X.X`. C'est la nouvelle adresse IP Wi-Fi de votre Jetson ! Vous pouvez maintenant débrancher le câble USB/Ethernet et vous connecter sans fil.

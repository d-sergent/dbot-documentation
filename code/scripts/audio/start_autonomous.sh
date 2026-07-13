#!/bin/bash
# =================================================================
# D-Bot : Démarrage en Mode AUTONOME (Headless)
# =================================================================

# Détermination du dossier du script (chemin absolu)
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# Recherche et export du fichier .env pour les clés API
ENV_FILE=""
SEARCH_DIR="$SCRIPT_DIR"
for i in {1..4}; do
    if [ -f "$SEARCH_DIR/.env" ]; then
        ENV_FILE="$SEARCH_DIR/.env"
        break
    fi
    SEARCH_DIR=$(dirname "$SEARCH_DIR")
done

if [ -n "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
    echo "✅ Clés API exportées depuis $ENV_FILE"
else
    echo "⚠ Attention : Fichier .env non trouvé. Le robot risque de rester en mode local."
fi

echo "🚀 [D-Bot] Passage en mode Headless (multi-user.target)..."
sudo systemctl isolate multi-user.target
sleep 2

echo "🔊 [D-Bot] Initialisation PulseAudio..."
export XDG_RUNTIME_DIR=/run/user/$(id -u)
pulseaudio -k
sleep 1
pulseaudio --start --exit-idle-time=-1
sleep 2

echo "🎤 [D-Bot] Réveil du micro ReSpeaker..."
SOURCE_NAME=$(pactl list sources short | grep "iec958-stereo" | grep -v "monitor" | cut -f2)
if [ -n "$SOURCE_NAME" ]; then
    pactl suspend-source "$SOURCE_NAME" 0
    pactl set-source-volume "$SOURCE_NAME" 150%
    echo "✅ Micro réveillé : $SOURCE_NAME"
else
    echo "❌ Erreur : Micro ReSpeaker non trouvé dans PulseAudio."
fi

echo "🔊 [D-Bot] Activation de l'amplificateur matériel..."
amixer -c 0 cset numid=3 on
amixer -c 0 cset numid=4 on
amixer -c 0 cset numid=5 60
amixer -c 0 cset numid=6 60

echo "🤖 [D-Bot] Lancement du Chatbot v2 (Mode AUTONOME / ALSA Direct)..."
python3 "$SCRIPT_DIR/../behaviors/chatbot_autonomous_v2.py"

#!/bin/bash
# =================================================================
# D-Bot : Démarrage en Mode AUTONOME (Headless)
# =================================================================

# Chargement des variables d'environnement depuis le .env
if [ -f "$(dirname "$0")/../../../.env" ]; then
    export $(grep -v '^#' "$(dirname "$0")/../../../.env" | xargs)
    echo "✅ Clés API chargées depuis le .env"
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

echo "🤖 [D-Bot] Lancement du Chatbot v2..."
python3 code/scripts/behaviors/chatbot_local_v2.py

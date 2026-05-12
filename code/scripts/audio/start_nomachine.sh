#!/bin/bash
# =================================================================
# D-Bot : Démarrage en Mode DÉVELOPPEMENT (NoMachine)
# =================================================================

# Recherche et export du fichier .env pour les clés API
ENV_FILE=""
SEARCH_DIR=$(dirname "$0")
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
    echo "⚠ Attention : Fichier .env non trouvé."
fi

echo "🖥️  [D-Bot] Lancement dans l'environnement NoMachine actuel..."
# Le passage en graphical.target est retiré car il réinitialise GDM et bloque la carte son ALSA.

echo "🔊 [D-Bot] Activation de l'amplificateur matériel..."
amixer -c 0 cset numid=3 on
amixer -c 0 cset numid=4 on
amixer -c 0 cset numid=5 60
amixer -c 0 cset numid=6 60

echo "🤖 [D-Bot] Lancement du Chatbot v2 (Mode NoMachine / PulseAudio)..."
python3 code/scripts/behaviors/chatbot_nomachine_v2.py
